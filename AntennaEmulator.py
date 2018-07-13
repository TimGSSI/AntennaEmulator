import messagePreparation as mp
import initializeGlobals as ig
import backupCursor as bc
import outputData as od
import processMessage as pm

import paho.mqtt.client as mqtt
from queue import Queue
import pendulum
import socket
import time
import sys

def on_connect(client, userdata, flags, rc):
    if rc==0:
        print("Connection Successful.\n")
    else:
        print("Bad connection. Return Code=", rc)

def on_message(client, userdata, message):

    ig.q.put(message) # add message to global queue

def main(argv):

    test_topics = True
    nemaTalker = False

    ig.initialize_globals(test_topics, nemaTalker)

    #broker="10.0.0.140" # home pc
    broker="10.40.11.7" # work PC
    #broker="10.40.11.184" # gssitest2
    #broker="10.40.11.138" # gssitest3    
    #broker="10.40.11.161" # gssitest6

    client = mqtt.Client("antenna_client") # create new instance
    client.on_connect=on_connect # bind call back functions
    client.on_message=on_message
    print("Connecting to broker...", broker)    

    lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
    lastGPSCheck = pendulum.parse(mp.prepareTimestamp())
   
    client.connect(broker)
    client.loop_start()

    client.subscribe(ig.CONFIG_GPR_TOPIC)           #"config/gpr"
    client.subscribe(ig.CONTROL_GPS_TOPIC)          #"config/gps"
    client.subscribe(ig.CONFIG_DMI_TOPIC)           #"config/dmi/0"
    client.subscribe(ig.DMI_OUTPUT_FORMATTED_TOPIC) #"config/dmi/output/formatted"
    client.subscribe(ig.CONTROL_GPS_TOPIC)          #"control/gps/state"
    client.subscribe(ig.CONTROL_GPR_STATE_TOPIC)    #"control/gpr/state"
    client.subscribe(ig.CONTROL_BATTERY_STATE)      #"control/battery/state"
    client.subscribe(ig.CONTROL_DMI_TOPIC)          #"control/dmi/state"

    if ig.useNemaTalker == False:
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

    config_gpr_message_recieved = False
    control_gpr_message_recieved = False
    dmi_message_recieved = False
    
    send_data = False
    mode = ""
    ticksPerMeter = 1
    scansPerMeter = 1
    samples_per_scan = 0
    #reset = {'samples_per_scan':samples_per_scan}
    #reset['mode'] = ""
    reset = 0

    while True:

        #print("WE GET BACK")
        """print("mode: " + str(mode))
        print("config_gpr_message_recieved: " +  str(config_gpr_message_recieved))
        print("control_gpr_message_recieved: " + str(control_gpr_message_recieved))
        print("dmi_message_recieved: " + str(dmi_message_recieved))
        print("=============================")"""

        currentTime = pendulum.parse(mp.prepareTimestamp())
        batt_time = currentTime - lastBatteryCheck
        GPS_time = currentTime - lastGPSCheck

        if not ig.q.empty(): 
 
            msg = ig.q.get()  #get the first message which was received and delete
            print("message topic: " + str(msg.topic) + "\nmessage payload: " + str(msg.payload) + "\n===============================\n")
            message = pm.processMessage(msg, client)

            if message['msg'] == 'control_GPR_msg':
                
                send_data = message['send_data']
                control_gpr_message_recieved = True
                
            elif message['msg'] == "config_gpr":
                samples_per_scan = message['samples_per_scan']
                tx_rate = message['tx_rate']
                scanRate = message['scanRate']
                mode = message['mode']
                config_gpr_message_recieved = True

            elif message['msg'] == "config_dmi":
                ticksPerMeter = message['ticksPerMeter']
                ticksPerMeter = abs(ticksPerMeter)
                scansPerMeter = message['scansPerMeter']
                binSize = message['binSize']
                dmi_message_recieved = True

        if mode == "swtick":
            if config_gpr_message_recieved == True and control_gpr_message_recieved == True and dmi_message_recieved == True:    
                if samples_per_scan == 512 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 1024 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 2048 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 4096 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 8192 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 16384 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False

        if mode == "freerunsw":
            if config_gpr_message_recieved == True and control_gpr_message_recieved == True and dmi_message_recieved == True:    
                if samples_per_scan == 512 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 1024 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 2048 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 4096 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 8192 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 16384 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                
        elif mode == "freerun":
            if config_gpr_message_recieved == True and control_gpr_message_recieved == True:    
                if samples_per_scan == 512 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 1024 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 2048 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 4096 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 8192 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False
                elif samples_per_scan == 16384 and send_data == True:
                    reset = od.output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc)
                    mode = reset['mode']
                    samples_per_scan = reset['samples_per_scan']
                    control_gpr_message_recieved = False

        if GPS_time > ig.FIFTH_OF_SEC and ig.GPS_TELEM_ENABLED == True:            
        
            if ig.useNemaTalker == False:
                JSON_GPS = mp.prepareGPSMessage(GPS_data[GPS_file_line])
                GPS_file_line += 1
            else:
                GPS, addr = soc.recvfrom(128)
                GPS = GPS.decode("utf-8").strip()

                JSON_GPS = mp.prepareGPSMessage(GPS)

            client.publish(ig.GPS_NMEA_TOPIC, JSON_GPS)
            
            lastGPSCheck = pendulum.parse(mp.prepareTimestamp())

        if batt_time > ig.ONE_MIN and ig.BATTERY_TELEM_ENABLED == True:
            ig.BATTERY_CAPACITY -= 5
            ig.BATTERY_MINUTES_LEFT -= 5

            JSON_battery = mp.prepareBatteryMessage(ig.BATTERY_CAPACITY, ig.BATTERY_MINUTES_LEFT) 

            client.publish(ig.BATTERY_TOPIC, JSON_battery)

            lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
           
    #client.loop_stop() # stop loop
    #client.disconnect() # disconnect

if __name__ == "__main__":
    main(sys.argv)
