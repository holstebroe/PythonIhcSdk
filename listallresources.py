"""
Test example showing how to use the ihcsdk to connect to the ihc controller
To run the example create a file '.parameters' in this folder and add:
ihcurl username password resourceid
The resourceid is an ihc resource id of any boolean resource in you controller.
The resource will be toggled when the test starts, and after this you can set it
using '1' and '2'. 'q' to quit
"""
from datetime import datetime
import time
from xml.etree import ElementTree
from ihcsdk.buttoneventtracker import ButtonEventTracker
from ihcsdk.ihcclient import IHCSoapClient

from ihcsdk.ihccontroller import IHCController

resource_map = {}
wireless_serial_map = {}

def receive_line_event(resource_id, value):
    print (f"{datetime.now()} Event received for {resource_map[resource_id]}[{resource_id}]: {value}")



button_events = {}
def receive_airlink_event(resource_id, value):
    if not resource_id in button_events:
        # First event. This usually happens when the event is initially subscribed to.
        name = f"{resource_map[resource_id]}[{resource_id}]"
        button_events[resource_id] = ButtonEventTracker(resource_id, name, value)
    else:
        button_events[resource_id].RegisterEvent(value)

def to_int_id(idStr):
    return int(idStr.strip("_"), 0)

def get_int_id(name, node):
    id = to_int_id(node.get("id"))
    resource_map[id] = name
    return id

def foo():
    return input()

def main():
    """Do the test"""

    starttime = datetime.now()

    def on_ihc_change(ihcid, value):
        """Callback when ihc resource changes"""
        print(
            "Resource change " + str(ihcid) + "->" + str(value) + " time: " + gettime()
        )

    def gettime():
        dif = datetime.now() - starttime
        return str(dif)

    
    cmdline = open(".parameters", "rt").read()
    args = cmdline.split(" ")
    if len(args) < 4:
        print(
            "The '.parameters' file should contain: ihcurl username password resourceid"
        )
        exit()
    url = args[0]
    username = args[1]
    password = args[2]

    if not IHCController.is_ihc_controller(url):
        print("The device in this url does not look like a IHC controller")
        exit()
    print("Url response like a IHC controller - now authenticating")

    ihc = IHCController(url, username, password)
    if not ihc.authenticate():
        print("Authenticate failed")
        exit()

    print("Authenticate succeeded\r\n")

    print("--------------- System info ---------------")
    info = ihc.client.get_system_info()
    print(info)

    print("--------------- Project ---------------")

    # read the ihc project
    project_xml = ihc.get_project()
    if project_xml is False:
        print("Failed to read project")
    else:
        print("Project downloaded successfully")

    project = ElementTree.fromstring(project_xml)

    groups = project.findall(".//group")
    for group in groups:
        group_name = group.attrib["name"]
        print (group_name)
        print ("    --- data lines ---")
        product_datalines = group.findall('.//product_dataline')        
        for dataline in product_datalines:
            id = dataline.attrib["id"]
            name = dataline.attrib["name"]
            position = dataline.attrib["position"]
            product_identifier = dataline.attrib["product_identifier"]
            print (f"    {name} @ {position} [{product_identifier}:{id}]")
            ihc.add_notify_event( get_int_id(f"Dataline {name}", dataline), receive_line_event, True)

#            for dataline_output in dataline.findall("dataline_output"):
#                ihc.add_notify_event(get_int_id(f"Dataline out {name}", dataline_output), receive_line_event, True)

        print ("    --- air links ---")
        product_airlinks = group.findall('.//product_airlink')        
        for airlink in product_airlinks:
            id = airlink.attrib["id"]
            name = airlink.attrib["name"]
            position = airlink.attrib["position"]
            product_identifier = airlink.attrib["product_identifier"]
            device_type = airlink.attrib["device_type"]
            serial = int(airlink.get("serialnumber").strip("_"), 0) # _0x640208193098
            full_name = f"{name} @ {group_name}:{position}"
            wireless_serial_map[serial] = full_name
            print (f"    {full_name} [{product_identifier}:{device_type}:{id}]. Serial {serial}")

#            if (serial == 109959888580760):
            ihc.add_notify_event( get_int_id(f"Airlink {name}", airlink), receive_line_event, True)
            

            airlink_inputs = airlink.findall(".//airlink_input")
            for input in airlink_inputs:
                input_name = input.get("name")
                print (f"    {input_name} - {input.get('name')} - {input.get('id')}")
                #if (serial == 109959888580760):
                ihc.add_notify_event(get_int_id(f"Airlink in {name} {input_name}", input), receive_airlink_event, True)
            

    # print ("------ DEVICES -----")
    # devices = ihc.get_detected_devices()

    # for device in devices.findall("./SOAP-ENV:Body/ns1:getDetectedDeviceList1/ns1:arrayItem", IHCSoapClient.ihcns):
    #     serial = int(device.find('ns1:serialNumber', IHCSoapClient.ihcns).text)
    #     battery = device.find('ns1:batteryLevel', IHCSoapClient.ihcns).text
    #     detected = device.find('ns1:detected', IHCSoapClient.ihcns).text
    #     signal = device.find('ns1:signalStrength', IHCSoapClient.ihcns).text
    #     if serial in wireless_serial_map:
    #         name = wireless_serial_map[serial]
    #     else:
    #         name = "<unknown>"

#        print (f"Wireless {name} - {serial} - Detected: {detected}, Battery {battery}, Signal {signal}")

# <ns1:getDetectedDeviceList1>
# <ns1:arrayItem xsi:type="ns1:WSRFDevice">
# <ns1:batteryLevel xsi:type="xsd:int">1</ns1:batteryLevel>
# <ns1:deviceType xsi:type="xsd:int">2062</ns1:deviceType>
# <ns1:serialNumber xsi:type="xsd:long">110011428841875</ns1:serialNumber>
# <ns1:version xsi:type="xsd:int">1</ns1:version>
# <ns1:detected xsi:type="xsd:boolean">true</ns1:detected>
# <ns1:signalStrength xsi:type="xsd:int">25</ns1:signalStrength>
# </ns1:arrayItem>

    print ("Waiting - press 'q' to quit")

    while True:
        user_input = foo()
        if user_input == 'q':
            break

    ihc.disconnect()
    ihc.client.connection.session.close()

    print ("Done")

main()


#    def get_detected_devices(self):
#        conn = self.client.connection
#        ws_service = '/ws/AirlinkManagementService'
#        ws_method = 'getDetectedDeviceList'
#        xdoc = conn.soap_action(ws_service, ws_method, "")
#        return xdoc
        # if xdoc is not False:
        #     return xdoc.find(
        #         "./SOAP-ENV:Body/ns1:getState1/ns1:state", IHCSoapClient.ihcns
        #     ).text
        # return False

