import messagePreparation as mp
import initializeGlobals as ig
import outputData as od
import processMessage as pm

import paho.mqtt.client as mqtt
from queue import Queue
import pendulum
import socket
import time
import sys
import os
import json
import jsonschema

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connection Successful.\n")
    else:
        print("Bad connection. Return Code=", rc)

def on_message(client, userdata, message):

    ig.Q.put(message) # add message to global queue

def main(argv):

    # when systemd starts this script on linux board, it is necessary to change present 
    # working directory to where the project resides
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

    # Set global debug options
    test_topics = False
    nemaTalker = False
    incoming_schema_validation = True
    outgoing_schema_validation = True
    loopData = True
    debugOutput = False

    ig.initialize_globals(test_topics, nemaTalker, incoming_schema_validation, outgoing_schema_validation, loopData, debugOutput)

    broker="localhost"

    client = mqtt.Client("antenna_client") # create new instance
    client.on_connect=on_connect # bind call back functions
    client.on_message=on_message
    client.will_set("stack/clientstatus", "LOST_CONNECTION", 0, False)
    print("Connecting to broker:", broker)    

    lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
    lastGPSCheck = pendulum.parse(mp.prepareTimestamp())
   
    client.connect(broker)
    client.loop_start()

    client.subscribe(ig.CONFIG_DEVICE_TOPIC)        # config/device
    client.subscribe(ig.CONFIG_GPR_TOPIC)           # config/gpr
    client.subscribe(ig.CONTROL_GPS_TOPIC)          # config/gps
    client.subscribe(ig.CONFIG_DMI_TOPIC)           # config/dmi/0
    client.subscribe(ig.DMI_OUTPUT_FORMATTED_TOPIC) # config/dmi/0/output/formatted
    client.subscribe(ig.CONTROL_GPS_TOPIC)          # control/gps/state
    client.subscribe(ig.CONTROL_GPR_STATE_TOPIC)    # control/gpr/state
    client.subscribe(ig.CONTROL_BATTERY_STATE)      # control/battery/state
    client.subscribe(ig.CONTROL_DMI_TOPIC)          # control/dmi/state
    client.subscribe(ig.STATUS_ID)                  # status/id
    client.subscribe(ig.CONFIG_STORAGE_ANTENNA)     # config/storage/antenna

    if ig.USE_NEMA_TALKER == False:
        GPS_filename = "FILE__001.DZG"
        with open(GPS_filename) as f:
            GPS_data = f.readlines()
        GPS_data = [x.strip() for x in GPS_data]
        GPS_file_line = 0
        soc = ""
    else:
        port = 1100
        soc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        soc.bind(("", port))

    # depending on the mode, certain messages MUST be recieved before collection can begin
    config_gpr_message_recieved = False
    control_gpr_message_recieved = False
    dmi_message_recieved = False
    
    send_data = False
    mode = ""
    ticksPerMeter = 1
    scansPerMeter = 1
    samples_per_scan = 0
    depth_range = -1
    reset = 0

    while True:

        currentTime = pendulum.parse(mp.prepareTimestamp())
        batt_time = currentTime - lastBatteryCheck
        GPS_time = currentTime - lastGPSCheck

        if not ig.Q.empty():

            msg = ig.Q.get()  # get the first message which was received, then delete from queue

            print("message topic: " + str(msg.topic) + "\nmessage payload: " + str(msg.payload) + "\n===============================\n")
            message = pm.processMessage(msg, client) # sends message to processing function, which validates params and extracts nessary values

            if message['msg'] == 'control_GPR_msg':
                send_data = message['send_data']
                control_gpr_message_recieved = True
                
            elif message['msg'] == "config_gpr":
                if samples_per_scan != message['samples_per_scan']:
                    ig.POINT_MODE_BYTE_COUNT = 0
                    ig.POINT_MODE_SCAN_NUMBER = 0
                samples_per_scan = message['samples_per_scan']
                tx_rate = message['tx_rate']
                scanRate = message['scanRate']
                mode = message['mode']
                time_range = message['antenna1']['timeRangeNs'] 
                config_gpr_message_recieved = True
                fileName = message['currentFile']

            elif message['msg'] == "config_dmi":
                ticksPerMeter = message['ticksPerMeter']
                ticksPerMeter = abs(ticksPerMeter)
                scansPerMeter = message['scansPerMeter']
                binSize = message['binSize']
                dmi_message_recieved = True

        if mode == "swtick" or mode == "freerunsw":
            if config_gpr_message_recieved == True and control_gpr_message_recieved == True and dmi_message_recieved == True:    
                if send_data == True:
                    current_file = ig.FILE_LIST[str(samples_per_scan) + "_" + str(time_range)]
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc, current_file)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False

        if mode == "freerun":
            if config_gpr_message_recieved == True and control_gpr_message_recieved == True:    
                if send_data == True:
                    current_file = ig.FILE_LIST[str(samples_per_scan) + "_" + str(time_range)]
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc, current_file)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False

        if GPS_time > ig.FIFTH_OF_SEC and ig.GPS_TELEM_ENABLED == True:            
            # this debug flag will feed in GPS strings from a .DZG file that was collected with a production UtilityScan system 
            if ig.USE_NEMA_TALKER == False:
                if GPS_file_line == len(GPS_data):
                    GPS_file_line = 0
                JSON_GPS = mp.prepareGPSMessage(GPS_data[GPS_file_line])
                json_validate = json.loads(JSON_GPS)
                    
                if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                    jsonschema.validate(json_validate, ig.TELEM_GPS_NMEA_SCHEMA)
                GPS_file_line += 1
            # this debug flag allows you to read fake, generated GPS strings over a virtual serial port using the "NemaTalker" application     
            else:
                GPS, addr = soc.recvfrom(128)
                GPS = GPS.decode("utf-8").strip()
                JSON_GPS = mp.prepareGPSMessage(GPS)
                json_validate = json.loads(JSON_GPS)
                    
                if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                    jsonschema.validate(json_validate, ig.TELEM_GPS_NMEA_SCHEMA)

            client.publish(ig.GPS_NMEA_TOPIC, JSON_GPS)
            
            lastGPSCheck = pendulum.parse(mp.prepareTimestamp())

        if batt_time > ig.THIRTY_SEC: #and ig.BATTERY_TELEM_ENABLED == True:
            ig.BATTERY_CAPACITY -= 5
            ig.BATTERY_MINUTES_LEFT -= 5

            # endlessly loops battery values over full possible range
            if ig.BATTERY_CAPACITY == 0:
                ig.BATTERY_CAPACITY = 100
            if ig.BATTERY_MINUTES_LEFT == 0:
                ig.BATTERY_MINUTES_LEFT = 360

            JSON_battery = mp.prepareBatteryMessage(ig.BATTERY_CAPACITY, ig.BATTERY_MINUTES_LEFT) 

            json_validate = json.loads(JSON_battery)
                    
            if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                jsonschema.validate(json_validate, ig.TELEM_BATTERY_SCHEMA)

            client.publish(ig.BATTERY_TOPIC, JSON_battery)

            lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())

if __name__ == "__main__":
    main(sys.argv)
