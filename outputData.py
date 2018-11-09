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

def output_data(samples_per_scan, timeRange, client, send_data, mode, scanRate, ticksPerMeter, scansPerMeter, soc, fileName, repeats):
    
    print("################################################")    
    print("fileName: " + fileName)
    print("current samples per scan: " + str(samples_per_scan))
    print("current timerange: " + str(timeRange))
    print("################################################")    
    
    time_time = time.time
    start = time_time()
    period = 1.0 / scanRate

    files_dir = "./test_data/"
    full_path = files_dir + fileName
    size = os.path.getsize(full_path) # for 
    data_file = open(full_path, 'rb')
    
    lastBatteryCheck = pendulum.parse(mp.prepareTimestamp())
    lastGPSCheck = pendulum.parse(mp.prepareTimestamp())
    lastCheck = pendulum.parse(mp.prepareTimestamp())

    send_GPS_data = True

    if ig.USE_NEMA_TALKER == False:
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
    
    ###############################
    # Current State of Parameters
    #print("positionOffset: " + str(ig.POSITION_OFFSET))
    #print("time_range: " + str(timeRange))
    #print("samples_per_scan: " + str(samples_per_scan))
    #print("repeats: " + str(repeats)) 
    #print("tx_rate: " + str(ig.TX_RATE)) 
    #####print("enableDither: " + str(enableDither))
    #print("scanRate: " + str(scanRate))
    #print("mode: " + str(mode))
    #print("scansPerMeter: " + str(scansPerMeter))
    #print("ticksPerMeter: " + str(ticksPerMeter))
    ###############################

    currentBinNumber = 0
    fcurrentBinNumber = 0
    newBinNumber = 0 # bin with the highest value
    lastBinNumber = 0 # previous bin

    initial_samples = samples_per_scan
    initial_scanRate = scanRate
    initial_timeRange = timeRange

    if ig.POINT_MODE_ENABLED == False:
        byte_count = 0
    else:
        byte_count = ig.POINT_MODE_BYTE_COUNT
    
    scan_count = 0
    totalTickCount = 0

    #tick_high_end = 250
    #tick_low_end = 150

    tick_high_end = 160
    tick_low_end = 110

    #tick_high_end = int(binSize * 0.8) 
    #tick_low_end = int(binSize * 0.3)
    
    prevent_duplicate = False # this flag protects the nextBackup value from increasing multiple times in a row if it takes multiple ticks to fill a bin

    tickRange = [tick_low_end, tick_high_end]
    forwards = True
    nextBackup = ig.SCANS_BEFORE_BACKUP
    scansToBackup = ig.SCANS_TO_BACKUP
    
    header_skipped = False # flag to skip file header first loop after file open
    skip_to_file_position = False # in point mode, skips to stored file position 

    first_output_bin = False

    while True:

        period = 1.0 / scanRate

        if header_skipped == False:
            data_file.read(131072) # reads to the end of the file header (128 KB)
            header_skipped = True

        currentTime = pendulum.parse(mp.prepareTimestamp())
        batt_time = currentTime - lastBatteryCheck
        GPS_time = currentTime - lastGPSCheck

        if not ig.Q.empty(): 
            
            msg = ig.Q.get()
            
            if msg.topic == "control/gps/state":
                print("\n")
            print("message topic: " + str(msg.topic) + "\nmessage payload: " + str(msg.payload) + "\n===============================\n")

            message = pm.processMessage(msg, client, samples_per_scan, timeRange)

            fileChange = False

            if message['msg'] == "control_GPR_msg":
                send_data = message['send_data']                
            elif message['msg'] == "config_gpr":
                if "tx_rate" in message:
                  tx_rate = message['tx_rate']
                if "scanRate" in message: 
                    scanRate = message['scanRate']
                if "mode" in message:
                    mode = message['mode']
                if "antenna1" in message:
                    if "timeRangeNs" in message['antenna1']:
                        if initial_timeRange != message['antenna1']['timeRangeNs']:
                            fileChange = True
                            initial_timeRange = message['antenna1']['timeRangeNs']
                            timeRange = message['antenna1']['timeRangeNs'] 
                if "currentFile" in message:
                    fileName = message['currentFile']
                    print("currentFile from outputData: " + fileName)
                if "samples_per_scan" in message:
                    if initial_samples != message['samples_per_scan']:
                        fileChange = True
                        initial_samples = message['samples_per_scan']
                        samples_per_scan = message['samples_per_scan']
                #if samples_per_scan == initial_samples:
                #    data_file.close()
                #    time.sleep(0.2)
                #    data_file = open(files_dir + fileName, 'rb')
                #    header_skipped = False
                #    byte_count = 0
                #    scan_count = 0
                if fileChange == True: 
                    ig.POINT_MODE_SCAN_NUMBER = 0
                    ig.POINT_MODE_BYTE_COUNT = 0
                    data_file.close()
                    time.sleep(0.2)
                    #initial_samples = samples_per_scan
                    fileName = ig.FILE_LIST[str(samples_per_scan) + "_" + str(timeRange)]
                    full_path = files_dir + fileName
                    header_skipped = False
                    byte_count = 0
                    scan_count = 0
                    #initial_samples = samples_per_scan
                    size = os.path.getsize(full_path)
                    data_file = open(full_path, 'rb')
                    currentBinNumber = 0
                    fcurrentBinNumber = 0
                    newBinNumber = 0 # bin with the highest value
                    lastBinNumber = 0 # previous bin
                    totalTickCount = 0
                    fileChange = False

                    print("current samples per scan: " + str(samples_per_scan))
                    print("current timerange: " + str(timeRange))
                    print("################################################")
 
            elif message['msg'] == "config_dmi":
                if "ticksPerMeter" in message:
                    ticksPerMeter = message['ticksPerMeter']
                    ticksPerMeter = abs(ticksPerMeter)
                if "scansPerMeter" in message:
                    scansPerMeter = message['scansPerMeter']
                if "binSize" in message:
                    binSize = message['binSize']

                metersPerSecond = scanRate / scansPerMeter
                ticksPerSecond = ticksPerMeter * metersPerSecond
                ticksPerScan = ticksPerMeter / scansPerMeter
                binSize = ticksPerMeter / scansPerMeter

                data_file.close()
                time.sleep(0.2)
                #initial_samples = samples_per_scan
                fileName = ig.FILE_LIST[str(samples_per_scan) + "_" + str(timeRange)]
                full_path = files_dir + fileName
                header_skipped = False
                byte_count = 0
                scan_count = 0
                #initial_samples = samples_per_scan
                size = os.path.getsize(full_path)
                data_file = open(full_path, 'rb')
                currentBinNumber = 0
                fcurrentBinNumber = 0
                newBinNumber = 0 # bin with the highest value
                lastBinNumber = 0 # previous bin
                totalTickCount = 0
                fileChange = False 

                #tick_high_end = int(binSize * 0.8) 
                #tick_low_end = int(binSize * 0.3)

                print("current samples per scan: " + str(samples_per_scan))
                print("current timerange: " + str(timeRange))
                print("current scansPerMeter: " + str(scansPerMeter))
                print("################################################")

        if mode == "swtick":
                
            if (time_time() - start) > period:

                start += period
                newTick = surveyWheelTickSimulator(tickRange, forwards)
                
                totalTickCount += newTick
                    
                distance = totalTickCount / ticksPerMeter

                distance_in_feet = distance * 3.28084
                    
                fcurrentBinNumber = totalTickCount / ticksPerScan

                currentBinNumber = math.floor(fcurrentBinNumber)

                if currentBinNumber > newBinNumber:

                    prevent_duplicate = False

                    if (currentBinNumber - 1) % 50 == 0 and (currentBinNumber - 1) != 0:
                        print("Current Bin Number: " + str(currentBinNumber - 1))
                    
                    data_chunk = data_file.read(samples_per_scan * 4) # unpacks binary data to read as 4-byte int
                    data_chunk_size = samples_per_scan * 4
            
                    data = [data_chunk[0], data_chunk[1], data_chunk[2], data_chunk[3]]
                    data = struct.unpack("I", bytearray(data))
                    data = data[0]

                    byte_count += len(data_chunk) # running byte count
                    encoded_data = base64.b64encode(data_chunk)
                    encoded_data = encoded_data.decode("utf-8")
                        
                    JSON_GPR = mp.prepareGPRSurveyMessage((currentBinNumber - 1), encoded_data, distance)
                    if ig.DEBUG_OUTPUT == True:
                        print(JSON_GPR)
                    json_validate = json.loads(JSON_GPR)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                        jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                    client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                    newBinNumber = lastBinNumber = currentBinNumber
                        
                elif currentBinNumber <= newBinNumber and forwards == False:
                    if currentBinNumber < lastBinNumber:

                        if (currentBinNumber - 1) % 50 == 0 and (currentBinNumber - 1) != 0:
                            print("Current Bin Number: " + str(currentBinNumber - 1))

                        roll_back = mp.prepareDMIMessage((currentBinNumber - 1), distance);
                        json_validate = json.loads(roll_back)
                    
                        if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                            jsonschema.validate(json_validate, ig.TELEM_DMI_FORMATTED_SCHEMA)

                        client.publish(ig.DMI_TOPIC, roll_back)
                        if ig.DEBUG_OUTPUT == True:
                            print(roll_back)
                        time.sleep(0.01)
                        lastBinNumber = currentBinNumber


                elif currentBinNumber <= newBinNumber and forwards == True:
                    if currentBinNumber > lastBinNumber:

                        if (currentBinNumber - 1) % 50 == 0 and (currentBinNumber - 1) != 0:
                            print("Current Bin Number: " + str(currentBinNumber - 1))

                        roll_back = mp.prepareDMIMessage((currentBinNumber - 1) , distance);

                        json_validate = json.loads(roll_back)
                    
                        if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                            jsonschema.validate(json_validate, ig.TELEM_DMI_FORMATTED_SCHEMA)

                        client.publish(ig.DMI_TOPIC, roll_back)
                        if ig.DEBUG_OUTPUT == True:
                            print(roll_back)
                        time.sleep(0.01)
                        lastBinNumber = currentBinNumber
                    
                #if currentBinNumber >= nextBackup:
                #    forwards = False

                if currentBinNumber <= newBinNumber - scansToBackup and prevent_duplicate == False:
                    forwards = True
                    nextBackup += ig.SCANS_BEFORE_BACKUP
                    prevent_duplicate = True

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
                print("data variable: " + str(data))

                byte_count += len(data_chunk) # running byte count
                encoded_data = base64.b64encode(data_chunk)
                encoded_data = encoded_data.decode("utf-8")

                JSON_GPR = mp.prepareGPRCombinedMessage(scan_count, totalTickCount, encoded_data, distance)
                if ig.DEBUG_OUTPUT == True:
                    print(JSON_GPR)

                json_validate = json.loads(JSON_GPR)
                    
                if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                    jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                scan_count+=1

                if scan_count % 50 == 0 and scan_count != 0:
                    print("Scans Published: " + str((scan_count)) + "  Total Tick Count: " + str(totalTickCount))

        elif mode == "freerun":
            if ig.POINT_MODE_ENABLED == False:
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
                    if ig.DEBUG_OUTPUT == True:
                        print(JSON_GPR)
                    json_validate = json.loads(JSON_GPR)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                        jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                    client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                    start += period
                    scan_count+=1

                    if scan_count % 50 == 0 and scan_count != 0:
                        print("Scans Published: " + str((scan_count)))
            else: # if config/gpr enableDither parameter == true 
                if skip_to_file_position == False:
                    data_file.seek((samples_per_scan * 4 * (ig.POINT_MODE_SCAN_NUMBER)), 1)

                    data_chunk = data_file.read(samples_per_scan * 4) # unpacks binary data to read as 4-byte int
                    data_chunk_size = samples_per_scan * 4
                    byte_count += len(data_chunk) # running byte count
                    ig.POINT_MODE_BYTE_COUNT += len(data_chunk)
            
                    data = [data_chunk[0], data_chunk[1], data_chunk[2], data_chunk[3]]
                    data = struct.unpack("I", bytearray(data))
                    data = data[0]

                    encoded_data = base64.b64encode(data_chunk)
                    encoded_data = encoded_data.decode("utf-8")

                    skip_to_file_position = True
                    
                if (time_time() - start) > period:                           
                    JSON_GPR = mp.prepareGPRFreerunMessage(scan_count, encoded_data)
                    #print(JSON_GPR)
                    json_validate = json.loads(JSON_GPR)
                    
                    if ig.OUTGOING_SCHEMA_VALIDATION == True:           
                        jsonschema.validate(json_validate, ig.TELEM_GPR_RAW_SCHEMA)

                    client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR)
                    start += period
                    scan_count+=1
   
        #if GPS_time > ig.FIFTH_OF_SEC and ig.GPS_TELEM_ENABLED == True: 
        if GPS_time > ig.HALF_OF_SEC:            
            
            if ig.USE_NEMA_TALKER == False:
                if send_GPS_data == True:
                    if GPS_file_line == len(GPS_data) - 1:
                        GPS_file_line = 0 # to make gps file loop endlessly uncomment this line and comment out line below
                        #send_GPS_data = False
                        
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
        
        if batt_time > ig.THIRTY_SEC: #and ig.BATTERY_TELEM_ENABLED == True:

            ig.BATTERY_CAPACITY -= 5
            ig.BATTERY_MINUTES_LEFT -= 5 

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
        
        if ig.POINT_MODE_ENABLED == False:
            if ig.LOOP_DATA == True:
                if byte_count == size - 131072:  # when end of file is reached - 131072 is the size of the 128K file header
                    byte_count = 0
                    ig.POINT_MODE_BYTE_COUNT = samples_per_scan * 4
                    ig.POINT_MODE_SCAN_NUMBER = 0
                    data_file.close()
                    data_file = open(full_path, 'rb')
                    header_skipped = False
                    skip_forward = False
                    skip_to_file_position = False
            else:
                if byte_count == size - 131072:
                    send_data = False
        else:
            if data_file.tell() == size:
                byte_count = 0
                ig.POINT_MODE_BYTE_COUNT = 0
                ig.POINT_MODE_SCAN_NUMBER = 0
                data_file.close()
                data_file = open(full_path, 'rb')
                header_skipped = False
                skip_forward = False
                skip_to_file_position = False
                
        if send_data == False:
            data_file.close()
            ig.POINT_MODE_SCAN_NUMBER += 1
            JSON_GPR = mp.prepareGPREOFMessage()
            if scan_count > 1:
                client.publish(ig.TELEM_GPR_RAW_TOPIC, JSON_GPR) # if last scan of file, publish message with scan# -1 and empty data field
            return_values = {'samples_per_scan':samples_per_scan}
            return_values['timeRange'] = timeRange
            return_values['repeats'] = repeats
            return_values['scanRate'] = scanRate
            return_values['ticksPerMeter'] = ticksPerMeter 
            return_values['scansPerMeter'] = scansPerMeter 
            return_values['mode'] = mode
            return return_values
