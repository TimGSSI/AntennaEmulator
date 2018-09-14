import paho.mqtt.client as mqtt
import messagePreparation as mp
import initializeGlobals as ig
import outputData as od

import pendulum
import time
import sys
import re
import base64
import os
import struct
import json
import jsonschema
from queue import Queue

def processMessage(msg, client):

    if msg.topic == ig.CONFIG_STORAGE_ANTENNA:

        json_msg = json.loads(msg.payload.decode('utf-8'))
        config_msg = ""

        if len(json_msg) == 0:        
            ant_config_file = "persistent_config_values.txt"        
            with open(ant_config_file) as f:
                values = f.read()
                f.close()
            values = values.strip().split(",")
            config_msg = mp.prepareConfigIdMessage(values[0].strip(), values[1].strip(), values[2].strip(), values[3].strip())
            print("config_msg: ")
            print(config_msg)

        else:
            ant_config_file = "persistent_config_values.txt"
            with open(ant_config_file) as f:
                values = f.read()
                f.close()
            values = values.strip().split(",")

            current_dev_id = values[0].strip()
            current_ant_model = values[1].strip()
            current_gain = values[2].strip()
            current_pos_off = values[3].strip()
            current_survey = values[4].strip()
            
            with open(ant_config_file, "w") as f:
                f.write(current_dev_id.strip() + ",\n")
                f.write(current_ant_model.strip() + ",\n")
                
                if 'payload' in json_msg:
                    if 'gainDb' in json_msg['payload']:
                        if json_msg['payload']['gainDb'] >= -200 and json_msg['payload']['gainDb'] <= 200:
                            f.write(str(json_msg['payload']['gainDb']) + ",\n")
                        else:
                            print("gain is not in acceptable range, retaining previous value")
                            f.write(current_gain.strip() + ",\n")
                    else:
                        f.write(current_gain.strip() + ",\n")

                    if 'positionOffsetPs' in json_msg['payload']:
                        if json_msg['payload']['positionOffsetPs'] >= 0 and json_msg['payload']['positionOffsetPs'] <= 800000:
                            f.write(str(json_msg['payload']['positionOffsetPs']) + ",\n")
                        else:
                            print("position offset is not within acceptable range, retaining previous value")
                            f.write(current_pos_off.strip() + ",\n")                        
                    else:
                        f.write(current_pos_off.strip() + ",\n")
                    
                    if 'surveyTicksPerM' in json_msg['payload']:
                        if json_msg['payload']['surveyTicksPerM'] >= -100000 and json_msg['payload']['surveyTicksPerM'] <= 100000:
                            f.write(str(json_msg['payload']['surveyTicksPerM']) + "\n")
                        else:
                            print("survey wheel calibration value is not within acceptable range, retaining previous value")
                            f.write(current_survey.strip() + "\n")                        
                    else:
                        f.write(current_survey.strip() + "\n")

                else:                     
                    f.write(current_gain.strip() + ",\n")
                    f.write(current_pos_off.strip() + ",\n")
                    f.write(current_survey.strip() + "\n")
                f.close()
            
            if 'payload' in json_msg:
                if 'gainDb' in json_msg['payload']:
                    current_gain = json_msg['payload']['gainDb']
                    print(current_gain)
                if 'positionOffsetPs' in json_msg['payload']:
                    current_pos_off = json_msg['payload']['positionOffsetPs']
                    print(current_pos_off)
                if 'surveyTicksPerM' in json_msg['payload']:
                    current_survey = json_msg['payload']['surveyTicksPerM']
                    print(current_survey)

            config_msg = mp.prepareConfigIdMessage(current_dev_id, current_ant_model, current_gain, current_pos_off, current_survey)

        fullMessage = config_msg
        
        messageWithoutTimestamp = json.loads(fullMessage)
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)

        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        
        client.publish(ig.CONFIG_STORAGE_ANTENNA_RESPONSE, responseMessage)

    if msg.topic == ig.CONTROL_GPR_STATE_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))
                
        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_GPR_SCHEMA)  

        if json_msg["newState"] == "run":
            send_data = True
        else:
            send_data = False    

        # response message
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONTROL_GPR_STATE_RESPONSE, responseMessage)

        values = {'msg':'control_GPR_msg'}
        values['send_data'] = send_data

        return values

    if msg.topic == ig.CONTROL_DMI_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_DMI_SCHEMA)

        if json_msg["newState"] == "run":
            enableDMI = True
        else:
            enableDMI = False

        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONTROL_DMI_STATE_RESPONSE, responseMessage)

        values = {'msg':'control_DMI_msg'}
        values['enable_DMI'] = enableDMI        

        return values

    if msg.topic == ig.CONTROL_GPS_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))  

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_GPS_SCHEMA)

        if json_msg["newState"] == "run":
            ig.GPS_TELEM_ENABLED = True
        else:
            ig.GPS_TELEM_ENABLED = False

        # response message block
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONTROL_GPS_STATE_RESPONSE, responseMessage)
        
        values = {'msg':'control_gps_msg'}

        return values

    if msg.topic == ig.CONTROL_BATTERY_STATE:  # this message does not get sent to me yet

        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_BATTERY_SCHEMA)

        if json_msg["newState"] == "run":
            ig.BATTERY_TELEM_ENABLED = True
        else:
            ig.BATTERY_TELEM_ENABLED = False

        # response message block
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = stripDateFromJSONObject(incomingMessage)
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONTROL_BATTERY_STATE_RESPONSE, responseMessage)
        
        values = {'msg':'control_battery_msg'}

        return values

    if msg.topic == ig.CONFIG_GPS_TOPIC:  # this message does not get sent to me yet

        json_msg = json.loads(msg.payload.decode('utf-8'))  

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONFIG_GPS_SCHEMA)

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_GPS_RESPONSE, response_msg)
        values = {'msg':'config_gps_msg'}

        return values

    if msg.topic == ig.CONFIG_DMI_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONFIG_DMI_SCHEMA)

        binSize =  json_msg["ticksPerMeter"] / json_msg["scansPerMeter"]

        values = {'msg':'config_dmi'}
        values['ticksPerMeter'] = json_msg["ticksPerMeter"]
        values['scansPerMeter'] = json_msg["scansPerMeter"]
        values['binSize'] = binSize

        # response message block
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONFIG_DMI_0_RESPONSE, responseMessage)

        return values

    if msg.topic == ig.DMI_OUTPUT_FORMATTED_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONFIG_DMI_OUTPUT_FORMATTED_SCHEMA)

        values = {'msg':'config_dmi_0_output_formatted'}
        values['publish'] = json_msg["publish"]

        # response message block
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))
        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)
        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)
        client.publish(ig.CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE, responseMessage)

        return values
                
    if msg.topic == ig.CONFIG_GPR_TOPIC:
                
        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:  
            jsonschema.validate(json_msg, ig.CONFIG_GPR_SCHEMA)

        values = {'msg':'config_gpr'}
        values['samples_per_scan'] = json_msg["samples"]
        values['tx_rate'] = json_msg["txRateKHz"]
        values['scanRate'] = json_msg["scanRateHz"]
        values['mode'] = json_msg["scanControl"]
        
        if json_msg["enableDither"] == True:
            ig.POINT_MODE_ENABLED = True
        elif json_msg["enableDither"] == False:
            ig.POINT_MODE_ENABLED = False
            ig.POINT_MODE_SCAN_NUMBER = 0
            ig.POINT_MODE_BYTE_COUNT = 0

        values['numberOfChannels'] = len(json_msg['channels'])
        
        antenna1 = {} # this section collects configuration values for multiple antennas
        antenna2 = {}
        antenna3 = {}
        antenna4 = {}

        if len(json_msg['channels']) == 1:            
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

        elif len(json_msg['channels']) == 2:
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

            antenna2['enable'] = json_msg['channels'][1]['enable']
            antenna2['positionOffsetPs'] = json_msg['channels'][1]['positionOffsetPs']
            antenna2['timeRangeNs'] = json_msg['channels'][1]['timeRangeNs']
            values['antenna2'] = antenna2

        elif len(json_msg['channels']) == 3:
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

            antenna2['enable'] = json_msg['channels'][1]['enable']
            antenna2['positionOffsetPs'] = json_msg['channels'][1]['positionOffsetPs']
            antenna2['timeRangeNs'] = json_msg['channels'][1]['timeRangeNs']
            values['antenna2'] = antenna2

            antenna3['enable'] = json_msg['channels'][2]['enable']
            antenna3['positionOffsetPs'] = json_msg['channels'][2]['positionOffsetPs']
            antenna3['timeRangeNs'] = json_msg['channels'][2]['timeRangeNs']
            values['antenna3'] = antenna3
        
        elif len(json_msg['channels']) == 4:
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

            antenna2['enable'] = json_msg['channels'][1]['enable']
            antenna2['positionOffsetPs'] = json_msg['channels'][1]['positionOffsetPs']
            antenna2['timeRangeNs'] = json_msg['channels'][1]['timeRangeNs']
            values['antenna2'] = antenna2

            antenna3['enable'] = json_msg['channels'][2]['enable']
            antenna3['positionOffsetPs'] = json_msg['channels'][2]['positionOffsetPs']
            antenna3['timeRangeNs'] = json_msg['channels'][2]['timeRangeNs']
            values['antenna3'] = antenna3

            antenna4['enable'] = json_msg['channels'][3]['enable']
            antenna4['positionOffsetPs'] = json_msg['channels'][3]['positionOffsetPs']
            antenna4['timeRangeNs'] = json_msg['channels'][3]['timeRangeNs']
            values['antenna4'] = antenna4
        
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))

        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)

        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)

        file_dictionary_position = str(json_msg["samples"]) + "_" + str(json_msg['channels'][0]['timeRangeNs'])
        values['currentFile'] = ig.FILE_LIST[file_dictionary_position]
        
        current_sampPerScan = json_msg["samples"]
        current_timeRange = json_msg['channels'][0]['timeRangeNs']
        current_positionOffsetNs = json_msg['channels'][0]['positionOffsetPs']
        valid_timeRange = 0
        
        #print("current_positionOffsetNs: " + str(current_positionOffsetNs))
        #if current_positionOffsetNs % 0x2000 == 0:
        #    print("positionOffsetNs is evenly divisible by 0x2000")
        #    print(current_positionOffsetNs % 0x2000)
        #else:
        #    print("positionOffsetNs is NOT evenly divisible by 0x2000")
        #    print(current_positionOffsetNs % 0x2000)

        #print("current_sampPerScan: " + str(current_sampPerScan))
        #print("current_timeRange: " + str(current_timeRange))
        
        # this section ensures that selected samples/scan and timerange pairing is legal 
        if current_sampPerScan == current_timeRange:
            valid_timeRange = current_timeRange
        elif (current_sampPerScan * 2) == current_timeRange:
            valid_timeRange = current_timeRange
        elif (current_sampPerScan / 2) == current_timeRange:
            valid_timeRange = current_timeRange
        elif (current_sampPerScan / 4) == current_timeRange:
            valid_timeRange = current_timeRange
        elif (current_sampPerScan / 8) == current_timeRange:
            valid_timeRange = current_timeRange
        else:
            raise ValueError('timeRangeNs value does not fall within acceptable range.  Current timeRangeNs value: ' + struct(current_timeRange))
            # publish response timerange error message to UI here 
            # need to catch Jeremy's error message and mimic the format, it is not published in any documentation
        
        if valid_timeRange != 0:
            client.publish(ig.CONFIG_GPR_RESPONSE, responseMessage)

        return values

    values = {'msg':'nothing'}
    return values