import xml
import xml.etree.ElementTree as et
import xml.dom.minidom
from mop import *
from flask import *

PASSWORD = "sm2025mop"
COMPETITION_ID = "11"


app = Flask(__name__)
mop_service = MOPService("mop", "localhost", "mop", "mop", COMPETITION_ID)

et.register_namespace('', 'http://www.melin.nu/mop')


def xml_response(xml):
    xml_string = MOP_XML_PREFIX + et.tostring(xml, encoding="unicode")
    response = Response(xml_string, mimetype="application/xml", status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def json_response(data):
    out = json.dumps(data, ensure_ascii=False, indent=2)
    response = Response(out, content_type='application/json', status=200)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


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
    data = mop_service.get_runners_by_class(competition, cls)
    return json_response(data)


@app.route('/api/<competition>/<cls>/runners/<bib>', methods=["GET"])
def get_runner_with_bib_for_class(competition, cls, bib):
    data = mop_service.get_runner_with_bib_by_class(competition, cls, bib)
    return json_response(data)


@app.route('/api/<competition>/<cls>/splits/<radio>', methods=["GET"])
def get_radio_passed_runners(competition, cls, radio):
    if request.args.get("relay") is not None:
        data = mop_service.get_runners_for_split_relay(competition, cls, radio)
    else:
        data = mop_service.get_runners_for_split_individual(competition, cls, radio)
    return json_response(data)


@app.route('/api/<competition>/<cls>/radiocontrols', methods=["GET"])
def get_radio_controls_for_class(competition, cls):
    is_relay = request.args.get("relay") is not None
    data = mop_service.get_radiocontrols_by_class(competition, cls, is_relay)
    return json_response(data)

# Get start lists with specific format for application in broadcasting software SPX
@app.route('/api/<competition>/<cls>/spx', methods=["GET"])
def get_runners_for_class_spx(competition, cls):
    data = mop_service.get_runners_by_class_spx(competition, cls)
    return json_response(data)


@app.route('/api/<competition>/<cls>/results', methods=["GET"])
def get_results_for_class(competition, cls):
    is_relay = request.args.get("relay") is not None
    get_total = is_relay and request.args.get("total") is not None

    if get_total:
        pass
    elif is_relay:
        pass
    else:
        data = mop_service.get_results_by_class(competition, cls)
    return json_response(data)


@app.route('/api/<competition>/<cls>/results/<bib>', methods=["GET"])
def get_results_with_bib_for_class(competition, cls, bib):
    data = mop_service.get_results_by_class_with_bib(competition, cls, bib)
    return json_response(data)