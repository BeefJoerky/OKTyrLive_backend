import xml
import xml.etree.ElementTree as et
import xml.dom.minidom
from mop import *
from flask import *

PASSWORD = "sm2025mop"
COMPETITION_ID = "10"


app = Flask(__name__)
mop_service = MOPService("mop", "localhost", "mop", "mop", COMPETITION_ID)

et.register_namespace('', 'http://www.melin.nu/mop')


def xml_response(xml):
    xml_string = MOP_XML_PREFIX + et.tostring(xml, encoding="unicode")
    print(xml_string)
    return Response(xml_string, mimetype="application/xml", status=200)

def pretty_print(root):
    rough_string = et.tostring(root, encoding='utf-8', method='xml')
    reparsed = xml.dom.minidom.parseString(rough_string)
    ugly = reparsed.toprettyxml(indent="  ")
    # Remove empty lines, AI CODE
    return "\n".join([line for line in ugly.split("\n") if line.strip()])


@app.route('/data', methods=['POST'])
def post_comp_data():
    competition_id = request.environ.get('HTTP_COMPETITION')
    pwd = request.environ.get('HTTP_PWD')
    if competition_id != COMPETITION_ID:
        return xml_response(mop_response(MOP_STATUS.BADCMP))
    if pwd != PASSWORD:
        return xml_response(mop_response(MOP_STATUS.BADPWD))
    
    data = request.get_data(as_text=True)
    xml_root = et.fromstring(data)
    print(pretty_print(xml_root))

    response = mop_service.handle_post(xml_root)

    response = xml_response(response)
    return response



@app.route('/data/radiodistances/individual', methods=['POST'])
def load_radio_distances_individual():
    """
    For loading the distance to a radio control for each class
    MeOS orders classes as in the GUI. Assume that distances to splits for each course in every class is roughly equal
    For relays, require data about class AND leg, because different legs can have different split distances
    Example, individual competition w
    {
        "classes": {
            "1": [
                {"controlId": 50, "distance": "2,9 km"},
                {"controlId": 150, "distance": "5,5 km"},
                {"controlId": 100, "distance": "Last Control"}
            ],
            "2": [
                {"controlId": 50, "distance": "1,8 km"},
                {"controlId": 150, "distance": "4,3 km"},
                {"controlId": 100, "distance": "Last Control"}
            ],
            "3": [
                {"controlId": 50, "distance": "4,3 km"},
                {"controlId": 150, "distance": "7,7 km"},
                {"controlId": 100, "distance": "Last Control"}
            ],
            "2": [
                {"controlId": 50, "distance": "3,0 km"},
                {"controlId": 150, "distance": "5,8 km"},
                {"controlId": 100, "distance": "Last Control"}
            ],
            "2": [
                {"controlId": 50, "distance": "1,9 km"},
                {"controlId": 150, "distance": "4,1 km"},
                {"controlId": 100, "distance": "Last Control"}
            ],
            "3": [
                {"controlId": 50, "distance": "4,7 km"},
                {"controlId": 150, "distance": "9,1 km"},
                {"controlId": 100, "distance": "Last Control"}
            ]
        }
    }
    """
    competition_id = request.headers.get("Competition-Id")
    pwd = request.headers.get("Password")
    if competition_id != COMPETITION_ID:
        return xml_response(mop_response(MOP_STATUS.BADCMP))
    if pwd != PASSWORD:
        return xml_response(mop_response(MOP_STATUS.BADPWD))
    
    data = request.get_json()
    mop_service.process_radio_distances_individual(data)

    return Response(status=200)


@app.route('/data/radiodistances/relay', methods=['POST'])
def load_radio_distances_relay():
    """
    For loading the distance to a radio control for each class. Expects a json with the format:
    MeOS orders classes as in the GUI. Assume that distances to splits for each course in every class is roughly equal
    For relays, require data about class AND leg, because different legs can have different split distances
    Example, relay with three legs:
    {
        "classes": {
            "1": {
                "1": [
                    {"controlId": 50, "distance": "2,9 km"},
                    {"controlId": 150, "distance": "5,5 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ],
                "2": [
                    {"controlId": 50, "distance": "1,8 km"},
                    {"controlId": 150, "distance": "4,3 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ],
                "3": [
                    {"controlId": 50, "distance": "4,3 km"},
                    {"controlId": 150, "distance": "7,7 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ]
            },
            "2": {
                "1": [
                    {"controlId": 50, "distance": "3,0 km"},
                    {"controlId": 150, "distance": "5,8 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ],
                "2": [
                    {"controlId": 50, "distance": "1,9 km"},
                    {"controlId": 150, "distance": "4,1 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ],
                "3": [
                    {"controlId": 50, "distance": "4,7 km"},
                    {"controlId": 150, "distance": "9,1 km"},
                    {"controlId": 100, "distance": "Last Control"}
                ]
            }
        }
    }
    """
    competition_id = request.headers.get("Competition-Id")
    pwd = request.headers.get("Password")
    if competition_id != COMPETITION_ID:
        return xml_response(mop_response(MOP_STATUS.BADCMP))
    if pwd != PASSWORD:
        return xml_response(mop_response(MOP_STATUS.BADPWD))
    
    data = request.get_json()
    mop_service.process_radio_distances_relay(data)

    return Response(status=200)


# For getting all runners in a class
@app.route('/api/<competition>/<cls>/runners', methods=["GET"])
def get_runners_for_class(competition, cls):
    # TODO: correct encoding and make correct return format
    data = mop_service.get_runners_by_class(cls)
    return jsonify(data)
    


@app.route('/api/<competition>/<cls>/runners/<bib>', methods=["GET"])
def get_runner_with_bib_for_class(competition, cls, bib):
    pass


@app.route('/api/<competition>/<cls>/<radio>/runners', methods=["GET"])
def get_radio_passed_runners(competition, cls, radio):
    pass


@app.route('/api/<competition>/<cls>/radiocontrols', methods=["GET"])
def get_radio_controls_for_class(competition, cls):
    pass