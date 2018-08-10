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
import jsonschema
import json
from queue import Queue

def processMessage(msg, client):

    if msg.topic == ig.CONTROL_GPR_STATE_TOPIC:

        json_msg = json.loads(msg.payload)  

        if json_msg["newState"] == "run":
            send_data = True
        else:
            send_data = False    

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_GPR_STATE_RESPONSE, response_msg)

        values = {'msg':'control_GPR_msg'}
        values['send_data'] = send_data

        return values

    if msg.topic == ig.CONTROL_DMI_TOPIC:

        json_msg = json.loads(msg.payload)

        if json_msg["newState"] == "run":
            enableDMI = True
        else:
            enableDMI = False

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_DMI_STATE_RESPONSE, response_msg)

        values = {'msg':'control_DMI_msg'}
        values['enable_DMI'] = enableDMI        

        return values

    if msg.topic == ig.CONTROL_BATTERY_STATE:

        json_msg = json.loads(msg.payload)

        if json_msg["newState"] == "run":
            ig.BATTERY_TELEM_ENABLED = True
        else:
            ig.BATTERY_TELEM_ENABLED = False

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_BATTERY_STATE_RESPONSE, response_msg)
        
        values = {'msg':'control_battery_msg'}
        # this does nothing right now because this message does not exist yet

        return values

    if msg.topic == ig.CONFIG_GPS_TOPIC:

        # this message is not sent to me yet

        json_msg = json.loads(msg.payload)  

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_GPS_RESPONSE, response_msg)
        values = {'msg':'config_gps_msg'}

        return values

    if msg.topic == ig.CONTROL_GPS_TOPIC:

        json_msg = json.loads(msg.payload)  

        if json_msg["newState"] == "run":
            ig.GPS_TELEM_ENABLED = True
        else:
            ig.GPS_TELEM_ENABLED = False

        response_msg = msg.payload.decode("utf-8")

        """if ig.GPS_TELEM_ENABLED == False:
            test = str(split_message[0]) + ",\"newState\":\"run\"," + str(split_message[2])
        else:
            test = str(split_message[0]) + ",\"newState\":\"idle\"," + str(split_message[2])

        test = test[2:]
        test = test[:-1]

        client.publish(ig.CONTROL_GPS_STATE_RESPONSE, test)"""

        client.publish(ig.CONTROL_GPS_STATE_RESPONSE, response_msg)
        values = {'msg':'control_gps_msg'}

        return values

    if msg.topic == ig.CONFIG_DMI_TOPIC:

        json_msg = json.loads(msg.payload)

        binSize =  json_msg["ticksPerMeter"] / json_msg["scansPerMeter"]

        values = {'msg':'config_dmi'}
        values['ticksPerMeter'] = json_msg["ticksPerMeter"]
        values['scansPerMeter'] = json_msg["scansPerMeter"]
        values['binSize'] = binSize

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_DMI_0_RESPONSE, response_msg)

        return values

    if msg.topic == ig.DMI_OUTPUT_FORMATTED_TOPIC:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')

        if split_message[1] == True:
            publish = True
        else:
            publish = False

        values = {'msg':'config_dmi_0_output_formatted'}
        values['publish'] = publish

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE, response_msg)

        return values
                
    if msg.topic == ig.CONFIG_GPR_TOPIC:
                
        json_msg = json.loads(msg.payload)

        values = {'msg':'config_gpr'}
        values['samples_per_scan'] = json_msg["samples"]
        values['tx_rate'] = json_msg["txRateKHz"]
        values['scanRate'] = json_msg["scanRateHz"]
        values['mode'] = json_msg["scanControl"]
        values['numberOfChannels'] = len(json_msg['channels'])

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
            values['antenna2'] = antenna1

        elif len(json_msg['channels']) == 3:
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

            antenna2['enable'] = json_msg['channels'][1]['enable']
            antenna2['positionOffsetPs'] = json_msg['channels'][1]['positionOffsetPs']
            antenna2['timeRangeNs'] = json_msg['channels'][1]['timeRangeNs']
            values['antenna2'] = antenna1

            antenna3['enable'] = json_msg['channels'][2]['enable']
            antenna3['positionOffsetPs'] = json_msg['channels'][2]['positionOffsetPs']
            antenna3['timeRangeNs'] = json_msg['channels'][2]['timeRangeNs']
            values['antenna3'] = antenna1
        
        elif len(json_msg['channels']) == 4:
            antenna1['enable'] = json_msg['channels'][0]['enable']
            antenna1['positionOffsetPs'] = json_msg['channels'][0]['positionOffsetPs']
            antenna1['timeRangeNs'] = json_msg['channels'][0]['timeRangeNs']
            values['antenna1'] = antenna1

            antenna2['enable'] = json_msg['channels'][1]['enable']
            antenna2['positionOffsetPs'] = json_msg['channels'][1]['positionOffsetPs']
            antenna2['timeRangeNs'] = json_msg['channels'][1]['timeRangeNs']
            values['antenna2'] = antenna1

            antenna3['enable'] = json_msg['channels'][2]['enable']
            antenna3['positionOffsetPs'] = json_msg['channels'][2]['positionOffsetPs']
            antenna3['timeRangeNs'] = json_msg['channels'][2]['timeRangeNs']
            values['antenna3'] = antenna1

            antenna4['enable'] = json_msg['channels'][3]['enable']
            antenna4['positionOffsetPs'] = json_msg['channels'][3]['positionOffsetPs']
            antenna4['timeRangeNs'] = json_msg['channels'][3]['timeRangeNs']
            values['antenna4'] = antenna1

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_GPR_RESPONSE, response_msg)

        return values

    values = {'msg':'nothing'}
    return values