from enum import Enum
import xml.etree.ElementTree as et
import mysql.connector
import xmltodict
from collections import namedtuple

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

runnerData = namedtuple("variables", ["place", "team_place", "team_running_time", "timeplus", "splits", "status", "team_status"])

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


def format_time(time_seconds, format):
    hours = time_seconds // 3600
    minutes = (time_seconds % 3600) // 60
    seconds = time_seconds % 60
    return f"{hours}:{minutes}:{seconds}"


class MOPService:

    def __init__(self, dbname, dbhost, dbusr, dbpwd, competition_id):
        self.connection = mysql.connector.connect(
            host=dbhost,
            user=dbusr,
            password=dbpwd,
            database=dbname,
            charset= "utf8",
            collation="utf8mb4_general_ci"
        )
        self.cursor = self.connection.cursor(dictionary=True)
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

        statement = f"UPDATE mopclasscontrol SET distance=%s WHERE cid={self.competition_id} AND id=%s AND leg=%s AND ctrl=%s"
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


    def get_runners_by_class(self, cmp, cls):
        statement = "SELECT cmp.name AS competition, cls.name AS class, runner.bib, runner.name, orgs.name AS club, runner.st AS start_time "
        statement += "FROM mopcompetitor AS runner "
        statement += "LEFT JOIN moporganization AS orgs ON orgs.id=runner.org AND orgs.cid=runner.cid "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=runner.cid "
        statement += "JOIN mopclass AS cls ON cls.id=runner.cls AND cls.cid=runner.cid "
        statement += f"WHERE runner.cls={cls} AND runner.cid={cmp} "
        statement += "ORDER BY start_time"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0].get("competition"),
            "class": data[0].get("class"),
            "runners": []
        }

        for runner in data:
            #runner["start_time"] = format_time(runner["start_time"], "hh:mm:ss")
            out["runners"].append({
                "bib": runner["bib"],
                "runner_club": runner["club"],
                "name": runner["name"],
                "start_time": runner["start_time"]
            })

        return out
    

    def get_runner_with_bib_by_class(self, cmp, cls, bib):
        statement = "SELECT cmp.name AS competition, cls.name AS class, runner.bib, runner.name, orgs.name AS club, runner.st AS start_time "
        statement += "FROM mopcompetitor AS runner "
        statement += "LEFT JOIN moporganization AS orgs ON orgs.id=runner.id AND orgs.cid=runner.cid "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=runner.cid "
        statement += "JOIN mopclass AS cls ON cls.id=runner.cls AND cls.cid=runner.cid "
        statement += f"WHERE runner.cls={cls} AND runner.bib={bib} AND runner.cid={cmp} "
        statement += "ORDER BY start_time"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0].get("competition"),
            "runner_class": data[0].get("class"),
            "runners": [
                {
                    "bib": data[0]["bib"],
                    "runner_club": data[0]["club"],
                    "name": data[0]["name"],
                    "start_time": data[0]["start_time"]
                }
            ]
        }

        #for runner in data:
        #    #runner["start_time"] = format_time(runner["start_time"], "hh:mm:ss")
        #    out["runners"].append({
        #        "bib": runner["bib"],
        #        "runner_class": runner["class"],
        #        "club": runner["club"],
        #        "name": runner["name"],
        #        "start_time": runner["start_time"]
        #    })

        return out


    def get_radiocontrols_by_class(self, cmp, cls, is_relay):
        statement = "SELECT cmp.name AS competition, cls.name AS class, ctrl.name AS radio_name, clctrl.ctrl AS id, clctrl.distance, clctrl.ord, clctrl.leg "
        statement += "FROM mopclass AS cls "
        statement += "JOIN mopclasscontrol AS clctrl ON cls.cid=clctrl.cid AND cls.id=clctrl.id "
        statement += "JOIN mopcompetition as cmp ON cls.cid=cmp.cid "
        statement += "JOIN mopcontrol AS ctrl ON ctrl.id=clctrl.ctrl AND ctrl.cid=cls.cid "
        statement += f"WHERE cls.id={cls} AND cls.cid={cmp} "
        statement += "ORDER BY leg, ord"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0].get("competition"),
            "runner_class": data[0].get("class"),
            "radiocontrols": []
        }


        if not is_relay:
            for radio in data:
                if radio["distance"] is not None:
                    distance = f"{radio["radio_name"]} {radio["distance"]}"
                else:
                    distance = radio["radio_name"]
                out["radiocontrols"].append({
                    "id": radio["id"],
                    "name": distance
                })
        else:
            out["radiocontrols"] = dict()
            leg = -1
            for radio in data:
                if radio["distance"] is not None:
                    distance = f"{radio["radio_name"]} {radio["distance"]}"
                else:
                    distance = radio["radio_name"]
                if radio["leg"] != leg:  # New relay leg
                    leg = radio["leg"]
                    out["radiocontrols"][f"leg{leg}"] = [{"id": radio["id"], "name": distance}]
                else:
                    out["radiocontrols"][f"leg{leg}"].append({"id": radio["id"], "name": distance})

        return out
    

    def get_runners_for_split_relay(self, cmp, cls, radio):
        statement = "SELECT DISTINCT cmp.name as competition, cls.name as class, tm.leg, "
        statement += "radio.ctrl as id, clctrl.distance, team.`name` AS team, runner.bib, org.name as club, "
        statement += "runner.name, runner.st AS start_time, radio.rt AS split_time "
        statement += "FROM mopradio as radio "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=radio.cid "
        statement += "JOIN mopteammember AS tm ON tm.rid=radio.id AND tm.cid=radio.cid "
        statement += "JOIN mopcompetitor as runner ON runner.id=tm.rid AND runner.cid=radio.cid "
        statement += "JOIN mopclass AS cls ON cls.id=runner.cls "
        statement += "JOIN mopclasscontrol AS clctrl ON clctrl.leg=tm.leg AND clctrl.ctrl=radio.ctrl AND clctrl.id=runner.cls AND clctrl.cid=radio.cid "
        statement += "LEFT JOIN mopteam AS team ON team.id=tm.id AND tm.cid=radio.cid "
        statement += "JOIN moporganization AS org ON org.id=team.org AND org.cid=radio.cid "
        statement += f"WHERE runner.cls={cls} AND radio.cid={cmp} AND radio.ctrl={radio} "
        statement += "ORDER by leg, split_time"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0]["competition"],
            "runner_class": data[0]["class"],
            "splits": {
                
            }
        }

        leg = -1
        for time in data:
            if time["leg"] != leg:   # New relay leg
                leg = time["leg"]
                out["splits"][f"leg{leg}"] = {
                    "id": time["id"],
                    "name": time["distance"],
                    "runners": []
                }
            out["splits"][f"leg{leg}"]["runners"].append({
                "team": time["team"],
                "bib": time["bib"],
                "name": time["name"],
                "club": time["club"],
                "start_time": time["start_time"],
                "split_time": time["split_time"]
            })

        return out
    

    def get_runners_for_split_individual(self, cmp, cls, radio):
        statement = "SELECT DISTINCT cmp.name as competition, cls.name as class, "
        statement += "radio.ctrl AS id, ctrl.name as radio, clctrl.distance, runner.bib, runner.id as runner_id, org.`name` AS club, "
        statement += "runner.name, runner.st AS start_time, radio.rt AS split, radio.rt as running_time, 1 as status " #runner.stat as status "
        statement += "FROM mopradio as radio "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=radio.cid "
        statement += "JOIN mopcompetitor as runner ON runner.id=radio.id AND runner.cid=radio.cid "
        statement += "JOIN mopclass AS cls ON cls.id=runner.cls AND cls.cid=radio.cid "
        statement += "JOIN mopclasscontrol AS clctrl ON clctrl.ctrl=radio.ctrl AND clctrl.id=runner.cls AND clctrl.cid=radio.cid "
        statement += "JOIN mopcontrol AS ctrl ON ctrl.id=clctrl.ctrl AND ctrl.cid=radio.cid "
        statement += "JOIN moporganization AS org ON org.id=runner.org AND org.cid=radio.cid "
        statement += f"WHERE runner.cls={cls} AND radio.cid={cmp} AND radio.ctrl={radio} "
        statement += "ORDER by split"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"
        
        if data[0]["distance"] is not None:
            distance = f"{data[0]["radio"]} {data[0]["distance"]}"
        else:
            distance = data[0]["radio"]

        out = {
            "competition": data[0]["competition"],
            "runner_class": data[0]["class"],
            "split": {
                "radio_name": distance,
                "id": data[0]["id"],
                "runners": []
            }
        }

        runner_data = self.calculate_results(data)

        for runner in data:
            out["split"]["runners"].append({
                "place": runner_data[runner["runner_id"]].place,
                "bib": runner["bib"],
                "name": runner["name"],
                "club": runner["club"],
                "start_time": runner["start_time"],
                "split_time": runner["split"],
            })

        return out
    

    def get_results_by_class(self, cmp, cls):
        statement = "SELECT cmp.name AS competition, cls.name AS class, runner.id AS runner_id, runner.bib, runner.name, org.name AS club, "
        statement += "split.rt AS split, runner.st AS start_time, runner.rt AS running_time, runner.stat AS `status` "
        statement += "FROM mopcompetitor AS runner "
        statement += "JOIN mopradio AS split ON split.id=runner.id AND split.cid=runner.cid "
        statement += "LEFT JOIN moporganization AS org ON org.id=runner.org AND org.cid=runner.cid "
        statement += "JOIN mopclass AS cls ON cls.cid=runner.cid AND cls.id=runner.cls "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=runner.cid "
        statement += f"WHERE runner.cls={cls} AND runner.cid={cmp} "
        statement += "ORDER BY running_time, split"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0]["competition"],
            "runner_class": data[0]["class"],
            "results": []
        }

        runner_data = self.calculate_results(data)

        runner_id = -1
        for runner in data:
            if runner["runner_id"] == runner_id:    # Same runner
                continue
            else:                                   # New runner
                runner_id = runner["runner_id"]

            out["results"].append({
                "place": runner_data[runner_id].place,
                "bib": runner["bib"],
                "name": runner["name"],
                "club": runner["club"],
                "splits": runner_data[runner_id].splits,
                "start_time": runner["start_time"],
                "running_time": runner["running_time"],
                "timeplus": runner_data[runner_id].timeplus,
                "status": runner_data[runner_id].status
            })

        return out
    

    def get_results_by_class_with_bib(self, cmp, cls, bib):
        statement = "SELECT cmp.name AS competition, cls.name AS class, runner.id as runner_id, runner.bib, runner.name, org.name AS club, "
        statement += "split.rt AS split, runner.st AS start_time, runner.rt AS running_time, runner.stat AS `status` "
        statement += "FROM mopcompetitor AS runner "
        statement += "JOIN mopradio AS split ON split.id=runner.id AND split.cid=runner.cid "
        statement += "LEFT JOIN moporganization AS org ON org.id=runner.org AND org.cid=runner.cid "
        statement += "JOIN mopclass AS cls ON cls.cid=runner.cid AND cls.id=runner.cls "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=runner.cid "
        statement += f"WHERE runner.cls={cls} AND runner.cid={cmp} " #AND runner.bib={bib} "
        statement += "ORDER BY running_time, split"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        runner = None
        runner_id = -1
        for a_runner in data:             # Get the runner id for the specific runner. Assume that bib is unique. Relays need different implementation
            if str(a_runner["bib"]) == bib:
                runner_id = a_runner["runner_id"]
                runner = a_runner
                break
        else:
            return "No data"


        runner_data = self.calculate_results(data)
        #if runner_data[runner_id][3] == True:    # Don't show place number if runner is disqualified. See calculate_results for definition of runner_data
        #    place = ""
        #else:
        #    place = runner_data[runner_id][0]

        out = {
            "competition": runner["competition"],
            "runner_class": runner["class"],
            "results": [
                {
                    "place": runner_data[runner_id].place,
                    "bib": runner["bib"],
                    "name": runner["name"],
                    "club": runner["club"],
                    "splits": runner_data[runner_id].splits,
                    "start_time": runner["start_time"],
                    "running_time": runner["running_time"],
                    "timeplus": runner_data[runner_id].timeplus,
                    "status": runner_data[runner_id].status
                }
            ]
        }

        return out
    

    def calculate_results(self, data: list) -> dict[int, runnerData]:
        runner_data = {}
        best_time = 0 
        runner_id = -1
        place_counter = -1
        number_disqualified = 0
        for runner in data:
            if runner["runner_id"] != runner_id:    # New runner
                place_counter += 1
                status = runner["status"]
                if status != MOP_COMPETITOR.OK.value:
                    number_disqualified += 1
                    place = ""
                else:
                    place = str(place_counter+1 - number_disqualified)

                if place != "" and best_time == 0:
                    best_time = runner["running_time"]

                runner_id = runner["runner_id"]
                runner_data[runner_id] = runnerData(place, None, None, runner["running_time"] - best_time, [], MOP_COMPETITOR(status).name, None)

            runner_data[runner_id].splits.append(runner["split"])

        return runner_data
    

    def calculate_results_relay(self, data: list) -> dict[int, runnerData]:
        runner_data = {}

        leg = 0
        leg_team_best_times = []
        team_best_time = 0
        best_time = 0 
        runner_id = -1
        place_counter = -1
        number_disqualified = 0
        for runner in data:
            if runner["leg"] != leg:    # New leg. Order is guaranteed
                leg = runner["leg"]
                leg_team_best_times.insert(leg, team_best_time)
                best_time = 0           # Reset counters
                place_counter = -1

            if runner["runner_id"] != runner_id:    # New runner
                place_counter += 1
                status = runner["status"]
                if status != MOP_COMPETITOR.OK.value:
                    number_disqualified += 1
                    place = ""
                else:
                    place = str(place_counter+1 - number_disqualified)

                if place != "" and best_time == 0:
                    best_time = runner["running_time"]
                    if runner["team_status"] == MOP_COMPETITOR.OK.value:
                        team_best_time = best_time + (runner["start_time"] - runner["team_start_time"])


                runner_id = runner["runner_id"]
                runner_data[runner_id][f"leg{leg}"] = runnerData(place, None, None, runner["running_time"] - best_time, [], MOP_COMPETITOR(status).name, None)

            runner_data[runner_id].splits.append(runner["split"])

        place_counter = -1
        for leg in runner_data.keys():
            for runner in runner_data[leg]:
                # tilldela en plats till varje löpare baserat på löparens lag-tid
                pass



        return runner_data
    

    def get_runners_by_class_spx(self, cmp, cls):
        statement = "SELECT cmp.name as competition, runner.bib, runner.name, org.name AS club, cls.name AS class, runner.st AS start_time "
        statement += "FROM mopcompetitor AS runner "
        statement += "JOIN mopclass AS cls ON cls.id=runner.cls AND cls.cid=runner.cid "
        statement += "JOIN moporganization AS org ON org.id=runner.org AND org.cid=runner.cid "
        statement += "JOIN mopcompetition AS cmp on cmp.cid=runner.cid "
        statement += f"WHERE runner.cid={cmp} AND runner.cls={cls} "
        statement += "ORDER BY start_time"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"
        
        out = {
            "competition": data[0]["competition"],
            "runner_class": data[0]["class"]
        }

        i = 0
        for runner in data:
            i += 1
            out[f"item{i}"] = [
                {"field": "f0", "ftype": "number", "title": "Bib", "value": runner["bib"]},
                {"field": "f1", "ftype": "textfield", "title": "Fullname", "value": runner["name"]},
                {"field": "f2", "ftype": "textfield", "title": "Runnerclub", "value": runner["club"]},
                {"field": "f4", "ftype": "textfield", "title": "Class", "value": runner["class"]},
                #TODO: make correct time format
                {"field": "f5", "ftype": "textfield", "title": "Starttime", "value": runner["start_time"]}
            ]

        return out
    

    def get_results_by_class_relay(self, cmp, cls):
        statement = "SELECT cmp.name AS competition, cls.name AS class, runner.id as runner_id, runner.bib, tm.leg, team.name AS team, "
        statement += "runner.name, org.name AS club, split.rt AS split, runner.st AS start_time, team.st AS team_start_time, team.stat AS team_status, "
        statement += "runner.rt AS running_time, runner.stat AS `status` "
        statement += "FROM mopcompetitor AS runner "
        statement += "JOIN mopradio AS split ON split.id=runner.id AND split.cid=runner.cid "
        statement += "LEFT JOIN moporganization AS org ON org.id=runner.org AND org.cid=runner.cid "
        statement += "JOIN mopteammember AS tm ON tm.rid=runner.id AND tm.cid=runner.cid "
        statement += "JOIN mopteam AS team ON team.id=tm.id "
        statement += "JOIN mopclass AS cls ON cls.cid=runner.cid AND cls.id=runner.cls "
        statement += "JOIN mopcompetition AS cmp ON cmp.cid=runner.cid "
        statement += f"WHERE runner.cls={cls} AND runner.cid={cmp} "
        statement += "ORDER BY leg, running_time, split"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"

        out = {
            "competition": data[0]["competition"],
            "runner_class": data[0]["class"],
            "results": {}
        }

        runner_data = self.calculate_results_relay(data)

        runner_id = -1
        for runner in data:
            if runner["runner_id"] == runner_id:    # Same runner
                continue
            else:                                   # New runner
                runner_id = runner["runner_id"]


            leg = runner["leg"]
            
            #if runner_data[runner_id]. == True:    # Don't show place number if runner is disqualified. See calculate_results for definition of runner_data
            #    place = ""
            #else:
            #    place = runner_data[runner_id][0]
            place = runner_data[runner_id].place
            team_place = runner_data[runner_id].team_place

            if out["results"][f"leg{leg}"] is None:
                out["results"][f"leg{leg}"] = []

            out["results"][f"leg{leg}"].append({
                "leg_place": place,
                "team_place": team_place,
                "bib": runner["bib"],
                "name": runner["name"],
                "team": runner["team"],
                "club": runner["club"],
                "splits": runner_data[runner_id].splits,
                "start_time": runner["start_time"],
                "running_time": runner["running_time"],
                "timeplus": runner_data[runner_id].timeplus,
                "status": runner_data[runner_id].status,
                "team_status": runner_data[runner_id].team_status
            })

        return out


    def get_all_classes(self, cmp):
        statement = "SELECT class.id, class.name, cmp.name as competition "
        statement += "FROM mopclass AS class JOIN mopcompetition as cmp on cmp.cid=class.cid "
        statement += f"WHERE class.cid={cmp} ORDER BY class.ord"
        self.cursor.execute(statement)
        data = self.cursor.fetchall()

        if data is None or len(data) == 0:
            return "No data"
        
        out = {
            "competition": data[0]["competition"],
            "classes": {}
        }

        for cls in data:
            out["classes"][cls["id"]] = cls["name"]

        return out