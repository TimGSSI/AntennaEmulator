import paho.mqtt.client as mqtt
import messagePreparation as mp
import initializeGlobals as ig
import processMessage as pm

import pendulum
import time
import sys
import re
import base64
import os
import struct
import socket
import math
import json
import jsonschema
from random import randint
from queue import Queue

def surveyWheelTickSimulator(tickRange, forwards):

    if forwards == True:
        currentTick = randint(tickRange[0], tickRange[1])
    else:
        currentTick = randint(tickRange[0], tickRange[1])
        currentTick = -currentTick

    return currentTick

def output_data(samples_per_scan, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc):
    
    time_time = time.time
    start = time_time()
    period = 1.0 / scanRate

    files_dir = "./test_data/"
    file = str(samples_per_scan) + "_samples.DZT"
    full_path = files_dir + file
    #print("FULL PATH: " + full_path)

    size = os.path.getsize(files_dir + file)
    data_file = open(files_dir + file, 'rb')
    
    lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
    lastGPSCheck = pendulum.parse(mp.prepareTimestamp())
    lastCheck = pendulum.parse(mp.prepareTimestamp())

    send_GPS_data = True

    if ig.useNemaTalker == False:
        GPS_filename = "FILE__001.DZG"
        with open(GPS_filename) as f:
            GPS_data = f.readlines()
        GPS_data = [x.strip() for x in GPS_data]
        GPS_file_line = 0

    metersPerSecond = scanRate / scansPerMeter
    ticksPerSecond = ticksPerMeter * metersPerSecond
    ticksPerScan = ticksPerMeter / scansPerMeter
    binSize = ticksPerMeter / scansPerMeter

    #print("==========Passed Values=======")
    #print("ticksPerMeter: " + str(ticksPerMeter))
    #print("scansPerMeter: " + str(scansPerMeter))
    #print("scanRate: " + str(scanRate))
    #print("=========Derived Values======")
    #print("metersPerSecond: " + str(metersPerSecond))
    #print("ticksPerScan: " + str(ticksPerScan))
    #print("ticksPerSecond: " + str(ticksPerSecond))
    #print("binSize: " + str(binSize))
    #print("=============================")

    currentBinNumber = -1
    fcurrentBinNumber = -1
    newBinNumber = -1 # bin with the highest value
    lastBinNumber = -1 # previous bin

    initial_samples = samples_per_scan
    initial_scanRate = scanRate
    
    scan_count = 0
    scanMessagesSent = 0
    totalTickCount = 0
    lastTickCount = 0

    nextBackup = 300

    #tick_high_end = int(binSize * 0.90) 
    #tick_low_end = int(binSize * 0.40)
    tick_high_end = 250
    tick_low_end = 150
    print("tick_low_end: " + str(tick_low_end))
    print("tick_high_end: " + str(tick_high_end))

    tickRange = [tick_low_end, tick_high_end]
    forwards = True

    byte_count = 0
    header_skipped = False

    lastScancountCheck = 0

    while True:

        period = 1.0 / scanRate

        if header_skipped == False:
            data_file.read(131072) # reads to the end of the file header (128 KB)
            header_skipped = True

        currentTime = pendulum.parse(mp.prepareTimestamp())
        batt_time = currentTime - lastBatteryCheck
        GPS_time = currentTime - lastGPSCheck

        if not ig.q.empty(): 
            msg = ig.q.get()
            print("message topic: " + str(msg.topic) + "\nmessage payload: " + str(msg.payload) + "\n===============================\n")

            message = pm.processMessage(msg, client)

            if message['msg'] == "control_GPR_msg":
                send_data = message['send_data']                

            elif message['msg'] == "config_gpr":
                samples_per_scan = message['samples_per_scan']
                tx_rate = message['tx_rate']
                scanRate = message['scanRate']
                mode = message['mode']

                if samples_per_scan == initial_samples:
                    data_file.close()
                    time.sleep(0.2)
                    data_file = open(files_dir + file, 'rb')
                    header_skipped = False
                    byte_count = 0
                    scan_count = 0
                elif samples_per_scan != initial_samples:

                    data_file.close()
                    time.sleep(0.2)

                    file = str(samples_per_scan) + "_samples.DZT"
                    full_path = files_dir + file
                    header_skipped = False
                    byte_count = 0
                    scan_count = 0
                    initial_samples = samples_per_scan

                    size = os.path.getsize(full_path)
                    data_file = open(full_path, 'rb')
                    
            elif message['msg'] == "config_dmi":

                ticksPerMeter = message['ticksPerMeter']
                ticksPerMeter = abs(ticksPerMeter)
                scansPerMeter = message['scansPerMeter']
                binSize = message['binSize']

        if currentBinNumber == -1 and newBinNumber == -1 and lastBinNumber == -1:
            currentBinNumber = 0
            fcurrentBinNumber = 0
            newBinNumber = 0
            lastBinNumber = 0

        else:
            if mode == "swtick":
                if (time_time() - start) > period:

                    start += period
                    newTick = surveyWheelTickSimulator(tickRange, forwards)
                    totalTickCount += newTick

                    distance = totalTickCount / ticksPerMeter

                    fcurrentBinNumber = totalTickCount / ticksPerScan

                    currentBinNumber = math.floor(fcurrentBinNumber)

                    if currentBinNumber > newBinNumber:

                        newBinNumber = lastBinNumber = currentBinNumber

                        if currentBinNumber % 50 == 0 and currentBinNumber != 0:
                            print("currentBinNumber: " + str(currentBinNumber))
                        
                        data_chunk = data_file.read(samples_per_scan * 4) # unpacks binary data to read as 4-byte int
                        data_chunk_size = samples_per_scan * 4
            
                        data = [data_chunk[0], data_chunk[1], data_chunk[2], data_chunk[3]]
                        data = struct.unpack("I", bytearray(data))
                        data = data[0]

                        byte_count += len(data_chunk) # running byte count
                        encoded_data = base64.b64encode(data_chunk)
                        encoded_data = encoded_data.decode("utf-8")
                    
                        JSON_GPR = mp.prepareGPRSurveyMessage(scan_count, encoded_data, distance)
                        #print(JSON_GPR)

                        json_validate = json.loads(JSON_GPR)
                    
                        if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                            jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                        client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                        scan_count+=1
                        
                    elif currentBinNumber <= newBinNumber and forwards == False:
                        if currentBinNumber < lastBinNumber:
                            if currentBinNumber % 50 == 0 and currentBinNumber != 0:
                                print("currentBinNumber: " + str(currentBinNumber))
                            scan_count-=1
                            roll_back = mp.prepareDMIMessage(scan_count);

                            json_validate = json.loads(roll_back)
                    
                            if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                                jsonschema.validate(json_validate, ig.TELEM_DMI_FORMATTED_SCHEMA)

                            client.publish(ig.DMI_TOPIC, roll_back)
                            time.sleep(0.01)
                            lastBinNumber = currentBinNumber
                    elif currentBinNumber <= newBinNumber and forwards == True:
                        if currentBinNumber > lastBinNumber:
                            if currentBinNumber % 50 == 0 and currentBinNumber != 0:
                                print("currentBinNumber: " + str(currentBinNumber))
                            scan_count+=1
                            roll_back = mp.prepareDMIMessage(scan_count);

                            json_validate = json.loads(roll_back)
                    
                            if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                                jsonschema.validate(json_validate, ig.TELEM_DMI_FORMATTED_SCHEMA)

                            client.publish(ig.DMI_TOPIC, roll_back)
                            time.sleep(0.01)
                            lastBinNumber = currentBinNumber

                    if currentBinNumber >= nextBackup:
                        forwards = False

                    if currentBinNumber <= newBinNumber - 100:
                        forwards = True
                        nextBackup += 300

            if mode == "freerunsw":
                if (time_time() - start) > period:

                    start += period
                    newTick = surveyWheelTickSimulator(tickRange, forwards)

                    totalTickCount += newTick

                    distance = totalTickCount / ticksPerMeter
               
                    data_chunk = data_file.read(samples_per_scan * 4) # unpacks binary data to read as 4-byte int
                    data_chunk_size = samples_per_scan * 4
            
                    data = [data_chunk[0], data_chunk[1], data_chunk[2], data_chunk[3]]
                    data = struct.unpack("I", bytearray(data))
                    data = data[0]

                    byte_count += len(data_chunk) # running byte count
                    encoded_data = base64.b64encode(data_chunk)
                    encoded_data = encoded_data.decode("utf-8")

                    JSON_GPR = mp.prepareGPRCombinedMessage(scan_count, totalTickCount, encoded_data, distance)
                    #print(JSON_GPR)

                    json_validate = json.loads(JSON_GPR)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                        jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                    client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                    scan_count+=1

                    if scan_count % 50 == 0 and scan_count != 0:
                        print("scan_count: " + str(scan_count) + "  totalTickCount: " + str(totalTickCount))

            elif mode == "freerun":
                if (time_time() - start) > period:
                    data_chunk = data_file.read(samples_per_scan * 4) # unpacks binary data to read as 4-byte int
                    data_chunk_size = samples_per_scan * 4
            
                    # unpacks the first 4 bytes which contain current scan number (sanity check)
                    data = [data_chunk[0], data_chunk[1], data_chunk[2], data_chunk[3]]
                    data = struct.unpack("I", bytearray(data))
                    data = data[0]

                    byte_count += len(data_chunk) # running byte count
                    encoded_data = base64.b64encode(data_chunk)
                    encoded_data = encoded_data.decode("utf-8")

                    JSON_GPR = mp.prepareGPRFreerunMessage(scan_count, encoded_data)
                    #print(JSON_GPR)
                    json_validate = json.loads(JSON_GPR)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                        jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                    client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                    start += period
                    scan_count+=1

                    if scan_count % 50 == 0 and scan_count != 0:
                        print("scan_count: " + str(scan_count))
   
        if GPS_time > ig.FIFTH_OF_SEC and ig.GPS_TELEM_ENABLED == True:            
            
            if ig.useNemaTalker == False:
                if send_GPS_data == True:
                    if GPS_file_line == len(GPS_data) - 1:
                        #GPS_file_line = 0 # to make gps file loop endlessly uncomment this line and comment out line below
                        send_GPS_data = False
                        
                    JSON_GPS = mp.prepareGPSMessage(GPS_data[GPS_file_line])
                    
                    json_validate = json.loads(JSON_GPS)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:         
                        jsonschema.validate(json_validate, ig.TELEM_GPS_NMEA_SCHEMA)

                    #print("GPS Message: " + str(JSON_GPS))
                    GPS_file_line += 1

            else:
                GPS, addr = soc.recvfrom(128)
                GPS = GPS.decode("utf-8").strip()

                JSON_GPS = mp.prepareGPSMessage(GPS)
                json_validate = json.loads(JSON_GPS)
                    
                if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                    jsonschema.validate(json_validate, ig.TELEM_GPS_NMEA_SCHEMA)

            if send_GPS_data == True:
                client.publish(ig.GPS_NMEA_TOPIC, JSON_GPS)
            
            lastGPSCheck = pendulum.parse(mp.prepareTimestamp())            
        
        if batt_time > ig.ONE_MIN: #and ig.BATTERY_TELEM_ENABLED == True:

            ig.BATTERY_CAPACITY -= 5
            ig.BATTERY_MINUTES_LEFT -= 5 
   
            JSON_battery = mp.prepareBatteryMessage(ig.BATTERY_CAPACITY, ig.BATTERY_MINUTES_LEFT) 
            
            json_validate = json.loads(JSON_battery)
                    
            if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                jsonschema.validate(json_validate, ig.TELEM_BATTERY_SCHEMA)
            
            client.publish(ig.BATTERY_TOPIC, JSON_battery)
            lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
        
        if byte_count == size - 131072:  # when end of file is reached - 131072 is the size of the 128K file header

            byte_count = 0
            data_file.close()
            data_file = open(files_dir + file, 'rb')
            header_skipped = False
            skip_forward = False
    
        if send_data == False:
            data_file.close()
            JSON_GPR = mp.prepareGPREOFMessage()
            if scan_count > 1:
                client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR) # if last scan of file, publish message with scan# -1 and empty data field
            return_values = {'samples_per_scan':samples_per_scan}
            return_values['mode'] = mode
            return return_values

