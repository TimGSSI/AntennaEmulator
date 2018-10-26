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
    web_app = True

    ig.initialize_globals(test_topics, nemaTalker, incoming_schema_validation, outgoing_schema_validation, loopData, debugOutput, web_app)

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

    client.subscribe(ig.RESTORE_SAVED_SETTINGS)     # restore/settings
    client.subscribe(ig.CONFIG_DEVICE_TOPIC)        # config/device
    client.subscribe(ig.CONFIG_GPR_TOPIC)           # config/gpr
    client.subscribe(ig.CONFIG_GPR_CHAN_0_TOPIC)    # config/gpr/chan/0
    client.subscribe(ig.CONFIG_GPR_CHAN_1_TOPIC)    # config/gpr/chan/1
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
   
    enableDither = False 
    send_data = False
    repeats = 0
    mode = ""
    ticksPerMeter = 1
    scansPerMeter = 1
    samples_per_scan = 0
    depth_range = -1
    reset = 0

    with open('storedParameters.json') as params:
        storedParameters = params.read()
    params.close()
    
    params = json.loads(storedParameters)

    if "positionOffsetPs" in params:
        #positionOffset = params['positionOffsetPs'] 
        ig.POSITION_OFFSET = params['positionOffsetPs'] 
    if "timeRangeNs" in params:
        time_range = params['timeRangeNs']
    if "samples" in params:
        samples_per_scan = params['samples'] 
    if "repeats" in params:
        repeats = params['repeats']
    if "txRateKHz" in params:
        #tx_rate = params['txRateKHz']
        ig.TX_RATE = params['txRateKHz']
    if "enableDither" in params:
        enableDither = params['enableDither']
    if "scanRateHz" in params:
        scanRate = params['scanRateHz']
    if "scanControl" in params:
        mode = params['scanControl']
    if "scansPerMeter" in params: 
        scansPerMeter = params['scansPerMeter']
    if "ticksPerMeter" in params:    
        ticksPerMeter = params['ticksPerMeter']

    ###############################
    # Current State of Parameters
    print("Restoring last-used parameters...") 
    print("positionOffset: " + str(ig.POSITION_OFFSET)) 
    print("time_range: " + str(time_range))
    print("samples_per_scan: " + str(samples_per_scan)) 
    print("repeats: " + str(repeats)) 
    print("tx_rate: " + str(ig.TX_RATE))
    print("enableDither: " + str(enableDither))
    print("scanRate: " + str(scanRate))
    print("mode: " + str(mode))
    print("scansPerMeter: " + str(scansPerMeter))
    print("ticksPerMeter: " + str(ticksPerMeter))
    ###############################

    while True:
        currentTime = pendulum.parse(mp.prepareTimestamp())
        batt_time = currentTime - lastBatteryCheck
        GPS_time = currentTime - lastGPSCheck

        if not ig.Q.empty():

            msg = ig.Q.get()  # get the first message which was received, then delete from queue

            print("message topic: " + str(msg.topic) + "\nmessage payload: " + str(msg.payload) + "\n===============================\n")
            message = pm.processMessage(msg, client, samples_per_scan, time_range) # sends message to processing function, which validates params and extracts nessary values

            if message['msg'] == 'control_GPR_msg':
                send_data = message['send_data']
                control_gpr_message_recieved = True
                
            elif message['msg'] == "config_gpr":
                if "samples_per_scan" in message:
                    if samples_per_scan != message['samples_per_scan']:
                        ig.POINT_MODE_BYTE_COUNT = 0
                        ig.POINT_MODE_SCAN_NUMBER = 0
                    samples_per_scan = message['samples_per_scan']
                if "tx_rate" in message:
                    tx_rate = message['tx_rate']
                if "scanRate" in message:
                    scanRate = message['scanRate']
                if "mode" in message:
                    mode = message['mode']
                if "antenna1" in message:
                    if "timeRangeNs" in message["antenna1"]:
                        time_range = message['antenna1']['timeRangeNs'] 
                if "currentFile" in message:
                    fileName = message['currentFile']
                config_gpr_message_recieved = True
            
            elif message['msg'] == "config_dmi":
                if "ticksPerMeter" in message:
                    ticksPerMeter = message['ticksPerMeter']
                    ticksPerMeter = abs(ticksPerMeter)
                if "scansPerMeter" in message:
                    scansPerMeter = message['scansPerMeter']
                if "binSize" in message:
                    binSize = message['binSize']
                dmi_message_recieved = True

        if mode == "swtick" or mode == "freerunsw":
            #if config_gpr_message_recieved == True and control_gpr_message_recieved == True and dmi_message_recieved == True:
            if True:
                if send_data == True:
                    current_file = ig.FILE_LIST[str(samples_per_scan) + "_" + str(time_range)]
                    currentParams = od.output_data(samples_per_scan, time_range, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc, current_file, repeats)
                    mode = currentParams['mode']
                    samples_per_scan = currentParams['samples_per_scan']
                    time_range = currentParams['timeRange'] 
                    ticksPerMeter = currentParams['ticksPerMeter'] 
                    scansPerMeter = currentParams['scansPerMeter']
                    repeats = currentParams['repeats'] 
                    scanRate = currentParams['scanRate']
                    control_gpr_message_recieved = False
                    send_data = False

        if mode == "freerun":
            #if config_gpr_message_recieved == True and control_gpr_message_recieved == True:
            if True:
                if send_data == True:
                    current_file = ig.FILE_LIST[str(samples_per_scan) + "_" + str(time_range)]
                    currentParams = od.output_data(samples_per_scan, time_range, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc, current_file, repeats)
                    mode = currentParams['mode']
                    samples_per_scan = currentParams['samples_per_scan']
                    time_range = currentParams['timeRange'] 
                    ticksPerMeter = currentParams['ticksPerMeter'] 
                    scansPerMeter = currentParams['scansPerMeter']
                    repeats = currentParams['repeats'] 
                    scanRate = currentParams['scanRate']
                    control_gpr_message_recieved = False
                    send_data = False

        #if GPS_time > ig.FIFTH_OF_SEC and ig.GPS_TELEM_ENABLED == True:
        if GPS_time > ig.HALF_OF_SEC:

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
