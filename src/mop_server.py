import xml
import xml.etree.ElementTree as et
import xml.dom.minidom
from mop import *
from flask import *

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


@app.route('/data', methods=['POST', 'GET'])
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
