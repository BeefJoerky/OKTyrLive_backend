from enum import Enum
import xml.etree.ElementTree as et
import mysql.connector
import xmltodict

MOP_XML_PREFIX = '<?xml version="1.0"?>'

MOP_STATUS = Enum("MOP_STATUS", [
    "OK",
    "BADCMP",
    "NOZIP",
    "BADPWD",
    "ERROR"
])

MOP_COMPETITOR = Enum("MOP_COMPETITOR", [
    ("UNKNOWN", 0),
    ("OK", 1),
    ("NT", 2),
    ("MP", 3),
    ("DNF", 4),
    ("DQ", 5),
    ("OT", 6),
    ("OCC", 15),
    ("DNS", 20),
    ("CANCEL", 21),
    ("NP", 99)
])

def mop_response(mop_status_code: MOP_STATUS):
    """
    Returnerar ett xml-träd med svarsdata enligt MOP
    """

    builder = et.TreeBuilder()

    builder.start("MOPStatus", {"status": mop_status_code.name})
    builder.end("MOPStatus")

    tree = builder.close()
    return tree


def strip_namespace(tag):
    return tag.split('}')[-1] if '}' in tag else tag    # AI code. It just works


class MOPService:

    def __init__(self, dbname, dbhost, dbusr, dbpwd, competition_id):
        self.connection = mysql.connector.connect(
            host=dbhost,
            user=dbusr,
            password=dbpwd,
            database=dbname,
            charset="utf8mb3"
        )
        self.cursor = self.connection.cursor()
        self.competition_id = competition_id    # Support for multiple competitions in persistent layer


    def _nice_xml_iterator(self, xml_root):
        for node in xml_root:
            yield (strip_namespace(node.tag), xmltodict.parse(et.tostring(node)))


    def handle_get(self, request_class, is_team):
        """
        Get data in json-format based on a competition class. If <strong>is_team</strong> is true, team-related data is passed
        """
        pass


    def handle_post(self, xml_post_data: et.ElementTree):
        """
        Save data from MeOS and save it into the database
        """

        for node_tagname, xml_dict in self._nice_xml_iterator(xml_post_data):
            if node_tagname == "cmp":
                self.process_competitor(xml_dict)
            elif node_tagname == "tm":
                self.process_team(xml_dict)
            elif node_tagname == "cls":
                self.process_class(xml_dict)
            elif node_tagname == "org":
                self.process_organization(xml_dict)
            elif node_tagname == "ctrl":
                self.process_control(xml_dict)
            elif node_tagname == "competition":
                self.process_competition(xml_dict)

        return mop_response(MOP_STATUS.OK)
                

    # DAO functions

    def make_nice(self, data_string):
        return data_string      # No-op


    def save(self, table, id, sql):
        selector = f"`cid`={self.competition_id} AND `id`={id}"
        self.cursor.execute(f"SELECT id FROM {table} WHERE {selector}")
        rows = len(self.cursor.fetchall())

        # Update the table if there is already data, else insert new
        if rows > 0:
            statement = f"UPDATE `{table}` SET {sql} where {selector}"
        else:
            statement = f"INSERT INTO `{table}` SET `cid`={self.competition_id}, `id`={id}, {sql}"

        self.cursor.execute(statement)
        self.connection.commit()


    def delete(self, table, id):
        selector = f"`cid`={self.competition_id} AND `id`={id}"
        statement = f"DELETE FROM `{table}` WHERE {selector}"
        self.cursor.execute(statement)
        

    def update_link_table(self, table, id, column, encoded_data):
        self.delete(table, id)

        leg_number = 1
        legs = encoded_data.split(";")

        statement = f"INSERT INTO {table} (`cid`, `id`, `leg`, `ord`, `{column}`) VALUES ({self.competition_id}, {id}, " + "%s, %s, %s)"

        # SHIT CODE, COPIED FROM functions.php.
        # "leg" means the course, since the class can have multiple courses
        # for relays, it means the relay leg, because a relay class has multiple legs
        data = []
        for leg in legs:
            if len(leg) > 0:
                runners = leg.split(",")
                for key, runner in enumerate(runners):
                    data.append((leg_number, key, runner))

            leg_number += 1

        self.cursor.executemany(statement, data)


    def process_radio_distances_individual(self, data_json):
        classes = data_json.get("classes")

        # For individual competitions, assume every class has roughly equal split distances, regardless of course
        # For qualifiqations, this can differ more, but is ignored and considered within margin of error
        # Each (class)id-control pair thus has a unique split distance

        statement = f"UPDATE mopClassControl SET distance=%s WHERE cid={self.competition_id} AND id=%s AND ctrl=%s"
        persist_data = []
        for cls, radios in classes.items():
            for radio in radios:
                radio_control_number = radio.get("controlId")
                radio_distance = radio.get("distance")
                persist_data.append((radio_distance, int(cls), radio_control_number))

        self.cursor.executemany(statement, persist_data)
        self.connection.commit()


    def process_radio_distances_relay(self, data_json):
        classes = data_json.get("classes")

        # For relays, assume each leg has roughly equal split distances, regardless of forked course
        # Each (class)id-leg-control pair thus has a unique split distance

        statement = f"UPDATE mopClassControl SET distance=%s WHERE cid={self.competition_id} AND id=%s AND leg=%s AND ctrl=%s"
        persist_data = []
        for cls, legs in classes.items():
            for leg, radios in legs.items():
                for radio in radios:
                    radio_control_number = radio.get("controlId")
                    radio_distance = radio.get("distance")
                    persist_data.append((radio_distance, int(cls), int(leg), int(radio_control_number)))
        
        self.cursor.executemany(statement, persist_data)
        self.connection.commit()


    def process_competitor(self, competitor: dict):
        id = self.make_nice(competitor["cmp"]["@id"])

        if (competitor["cmp"].get("@delete") is not None and competitor["cmp"]["@delete"] == "true"):    # MOP2.0 support
            self.delete("mopCompetitor", id)
            return
        
        name = self.make_nice(competitor["cmp"]["base"]["#text"])
        organization = self.make_nice(competitor["cmp"]["base"]["@org"])
        _class = self.make_nice(competitor["cmp"]["base"]["@cls"])
        status = self.make_nice(competitor["cmp"]["base"]["@stat"])
        start_time = self.make_nice(competitor["cmp"]["base"]["@st"])
        running_time = self.make_nice(competitor["cmp"]["base"]["@rt"])     # Goal time
        bib = self.make_nice(competitor["cmp"]["base"].get("@bib"))


        statement = f"`name`='{name}', `org`={organization}, `cls`={_class}, `stat`={status}, `st`={start_time}, `rt`={running_time}"
            
        if bib is not None:
            statement += f", `bib`={bib}"


        if "input" in competitor["cmp"]:
            input = competitor["cmp"]["input"]
            it = input["@it"]                   # No idea what this is. No documentation for it
            tstat = input["@tstat"]

            statement += f", `it`={it}, `tstat`={tstat}"


        self.save("mopCompetitor", id, statement)


        # This is bad code copied from PHP example, but I don't care to change it
        # It removes all occurences of radio times in the database with the competitors id
        # and then inserts all radio times as they are updated
        if "radio" in competitor["cmp"]:
            statement = f"DELETE FROM `mopRadio` WHERE `cid`={self.competition_id} AND `id`={id}"
            self.cursor.execute(statement)
            radios = self.make_nice(competitor["cmp"]["radio"]).split(";")     # Split into many radio times

            statement = "REPLACE INTO `mopRadio` (`cid`, `id`, `ctrl`, `rt`) VALUES (" + self.competition_id + ", + " + id + ", %s, %s)"

            radio_data = []
            for radio in radios:
                radio_pair = radio.split(",")   # Split each radio time into control number and running time
                radio_id = radio_pair[0]
                radio_time = radio_pair[1]
                radio_data.append((radio_id, radio_time))

            self.cursor.executemany(statement, radio_data)


    def process_team(self, team: dict):
        id = team["tm"]["@id"]

        if (team["tm"].get("@delete") is not None and team["tm"]["@delete"] == "true"):  # MOP 2.0 support
            self.delete("mopTeam", id)
            return
        
        name = team["tm"]["base"]["#text"]

        organization = team["tm"]["base"]["@org"]
        _class = team["tm"]["base"]["@cls"]
        status = team["tm"]["base"]["@stat"]
        start_time = team["tm"]["base"]["@st"]
        running_time = team["tm"]["base"]["@rt"]
        bib = team["tm"]["base"].get("@bib")

        statement = f"`name`='{name}', `org`={organization}, `cls`={_class}, `stat`={status}, `st`={start_time}, `rt`={running_time}"
        if bib is not None:
            statement += f", `bib`={bib}"

        self.save("mopTeam", id, statement)

        if "r" in team["tm"]:     # If there is a Runner in the team. "r" contains semicolon-separated runner ids
            self.update_link_table("mopTeamMember", id, "rid", self.make_nice(team["tm"]["r"]))


    def process_class(self, _class: dict):
        id = self.make_nice(_class["cls"]["@id"])
        order_index = self.make_nice(_class["cls"]["@ord"])     # Ordering index for ordering, of course?
        class_name = self.make_nice(_class["cls"]["#text"])
        
        statement = f"`name`='{class_name}', `ord`={order_index}"
        self.save("mopClass", id, statement)

        # If the class contains radios, make sure they are linked correctly in the database
        if "@radio" in _class["cls"]:
            radio = self.make_nice(_class["cls"]["@radio"])
            self.update_link_table("mopClassControl", id, "ctrl", radio)


    def process_organization(self, organization: dict):
        id = self.make_nice(organization["org"]["@id"])
        
        if (organization["org"].get("@delete") is not None and organization["org"]["@delete"] == "true"):    # MOP2.0 support
            self.delete("mopOrganization", id)
            return
        
        org_name = self.make_nice(organization["org"]["#text"])

        statement = f"`name`='{org_name}'"
        self.save("mopOrganization", id, statement)


    def process_control(self, control: dict):
        name = self.make_nice(control["ctrl"]["#text"])
        id = self.make_nice(control["ctrl"]["@id"])
        statement = f"`name`='{name}'"
        self.save("mopControl", id, statement)
    

    def process_competition(self, competition: dict):
        name = self.make_nice(competition["competition"]["#text"])
        date = self.make_nice(competition["competition"]["@date"])
        organizer = self.make_nice(competition["competition"]["@organizer"])
        homepage = self.make_nice(competition["competition"]["@homepage"])

        statement = f"`name`='{name}', `date`='{date}', `organizer`='{organizer}', `homepage`='{homepage}'"
        self.save("mopCompetition", 1, statement)  # id=1 because cid, that is, competition_id, is always different between competitions