import paho.mqtt.client as mqtt
import messagePreparation as mp
import initializeGlobals as ig
import backupCursor as bc
import outputData as od
import pendulum
import time
import sys
import re
import base64
import os
import struct
from queue import Queue

def processMessage(msg, client):

    if msg.topic == ig.CONTROL_GPR_STATE_TOPIC:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')

        if len(split_message) == 2:
            state = split_message[0]
        elif len(split_message) == 4:
            state = split_message[2]

        print("STATE: " + str(state))

        if "idle" in state:
            send_data = False
        else:
            send_data = True

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_GPR_STATE_RESPONSE, response_msg)

        values = {'msg':'control_GPR_msg'}
        values['send_data'] = send_data        

        return values

    if msg.topic == ig.CONTROL_DMI_TOPIC:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')
        state = split_message[3]

        if "idle" in state:
            enable_DMI = False
        else:
            enable_DMI = True

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_DMI_STATE_RESPONSE, response_msg)

        values = {'msg':'control_DMI_msg'}
        values['enable_DMI'] = enable_DMI        

        return values

    if msg.topic == ig.CONTROL_BATTERY_STATE:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')
        state = split_message[0]

        if "idle" in state:
            ig.BATTERY_TELEM_ENABLED = False
        else:
            ig.BATTERY_TELEM_ENABLED = True

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONTROL_BATTERY_STATE_RESPONSE, response_msg)
        values = {'msg':'control_battery_msg'}

        return values

    if msg.topic == ig.CONFIG_GPS_TOPIC:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')

        # check documentation to implement this

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_GPS_RESPONSE, response_msg)
        values = {'msg':'config_gps_msg'}

        return values

    if msg.topic == ig.CONTROL_GPS_TOPIC:

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')
        state = split_message[2]

        if "idle" in state:
            ig.GPS_TELEM_ENABLED = False
        else:
            ig.GPS_TELEM_ENABLED = True

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

        latest_message = str(msg.payload)
        split_message = latest_message.split(',')

        ticksPerMeter = split_message[4]
        ticksPerMeter = re.findall('\d+', ticksPerMeter)
        ticksPerMeter = int(ticksPerMeter[0])

        scansPerMeter = split_message[5]
        scansPerMeter = re.findall('\d+', scansPerMeter)
        scansPerMeter = int(scansPerMeter[0])

        binSize = scansPerMeter / ticksPerMeter

        values = {'msg':'config_dmi'}
        values['ticksPerMeter'] = ticksPerMeter
        values['scansPerMeter'] = scansPerMeter
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
                
        latest_message = str(msg.payload)
        split_message = latest_message.split(',')
                
        samples_per_scan = split_message[8]
        samples_per_scan = re.findall('\d+', samples_per_scan)
        samples_per_scan = int(samples_per_scan[0])

        tx_rate = split_message[9]
        tx_rate = re.findall('\d+', tx_rate)
        tx_rate = int(tx_rate[0])

        scanRate = split_message[12]
        print("SCANRATE: " + str(scanRate))
        scanRate = re.findall('\d+', scanRate)
        scanRate = int(scanRate[0])

        mode = split_message[13]
        if mode.find("swtick") != -1:
            mode = "swtick"
        elif mode.find("freerunsw") != -1:
            mode = "freerunsw"
        elif mode.find("freerun") != -1:
            mode = "freerun"
        elif mode.find("single") != -1:
            mode = "single"
        else:
            mode = "freerun"

        values = {'msg':'config_gpr'}
        values['samples_per_scan'] = samples_per_scan
        values['tx_rate'] = tx_rate
        values['scanRate'] = scanRate
        values['mode'] = mode

        response_msg = msg.payload.decode("utf-8")
        client.publish(ig.CONFIG_GPR_RESPONSE, response_msg)

        return values

    values = {'msg':'nothing'}
    return values
