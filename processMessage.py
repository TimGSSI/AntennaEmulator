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

    if msg.topic == ig.CONTROL_GPR_STATE_TOPIC:

        json_msg = json.loads(msg.payload.decode('utf-8'))
                
        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_GPR_SCHEMA)  

        if json_msg["newState"] == "run":
            send_data = True
        else:
            send_data = False    

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

        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))

        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)

        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)

        client.publish(ig.CONTROL_GPS_STATE_RESPONSE, responseMessage)
        values = {'msg':'control_gps_msg'}

        return values

    if msg.topic == ig.CONTROL_BATTERY_STATE:

        json_msg = json.loads(msg.payload.decode('utf-8'))

        if ig.INCOMING_SCHEMA_VALIDATION == True:           
            jsonschema.validate(json_msg, ig.CONTROL_BATTERY_SCHEMA)

        if json_msg["newState"] == "run":
            ig.BATTERY_TELEM_ENABLED = True
        else:
            ig.BATTERY_TELEM_ENABLED = False

        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = stripDateFromJSONObject(incomingMessage)

        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)

        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)

        client.publish(ig.CONTROL_BATTERY_STATE_RESPONSE, responseMessage)
        
        values = {'msg':'control_battery_msg'}
        # this topic does nothing right now because this message does not exist yet

        return values

    if msg.topic == ig.CONFIG_GPS_TOPIC:

        # this message does not get sent to me yet

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
            #jsonschema.validate(json_msg, ig.CONFIG_GPS_SCHEMA) # Tests incorrect schema validation file

        values = {'msg':'config_gpr'}
        values['samples_per_scan'] = json_msg["samples"]
        values['tx_rate'] = json_msg["txRateKHz"]
        values['scanRate'] = json_msg["scanRateHz"]
        values['mode'] = json_msg["scanControl"]
        values['numberOfChannels'] = len(json_msg['channels'])

        # this section collects configuration values for multiple antennas if there are mor than 1 
    
        antenna1 = {}
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

        #incomingMessage = msg.payload.decode("utf-8")
        
        fullMessage = msg.payload.decode("utf-8")
        messageWithoutTimestamp = json.loads(msg.payload.decode('utf-8'))

        del messageWithoutTimestamp['timestamp']
        messageWithoutTimestamp = json.dumps(messageWithoutTimestamp)

        responseMessage = mp.prepareControlResponseMessage(fullMessage, messageWithoutTimestamp)

        client.publish(ig.CONFIG_GPR_RESPONSE, responseMessage)

        return values

    values = {'msg':'nothing'}
    return values