from datetime import datetime
from datetime import timezone
import initializeGlobals as ig
import sys

def prepareTimestamp():

    # UTC 8601 datetime template: 2018-04-03T19:12:14.505Z
    unparsed_time = datetime.now(timezone.utc).astimezone().isoformat()
    currentTime = unparsed_time[:-9] + "Z"

    if len(currentTime) < 24:
        currentTime = unparsed_time[:-6] + ".000Z"

    return currentTime

def prepareGPSMessage(NMEA):

    timestamp = prepareTimestamp()

    GPSMessage = """
{
  "timestamp": "%s",
  "nmeaRecord": "%s"
}""" % (timestamp, NMEA)
    
    return GPSMessage

def prepareBatteryMessage(capacity, battery_time):

    timestamp = prepareTimestamp()

    battMessage = """
{
  "timestamp": "%s",
  "temp": 0,
  "capacity": %s,
  "voltageNow": 0,
  "timeToEmptyAvg": %s
}""" % (timestamp, capacity, battery_time)

    #print(battMessage)

    return battMessage

def prepareEmptyConfigDeviceResponse():

    timestamp = prepareTimestamp()

    configMessage = """
{
  "timestamp": "%s", 
  "request": {}, 
  "result": {
    "firmware": "RTS200-RAW8KE.rbf", 
    "model": "LF18", 
    "serial": "95676", 
    "version": "0.1.dev560+g5492283"
  }
}""" % (timestamp) 

    #print(battMessage)

    return configMessage
def prepareEmptyConfigGprResponse(current_settings):

    timestamp = prepareTimestamp()

    configMessage = """
{
  "uuid": "%s",
  "timestamp": "%s",
  "channels":[{
    "positionOffsetPs": %s,
    "timeRangeNs": %s}],
  "samples": %s,
  "repeats": %s,
  "txRateKHz": %s,
  "enableDither": "%s",
  "scanRateHz": %s,
  "scanControl": "%s"
}""" % (ig.ANTENNA_UUID, timestamp, current_settings['positionOffsetPs'], current_settings['timeRangeNs'], current_settings['samples'], current_settings['repeats'], current_settings['txRateKHz'], current_settings['enableDither'], current_settings['scanRateHz'], current_settings['scanControl']) 

    #print(battMessage)

    return configMessage

def prepareEmptyConfigDmiResponse(current_settings):

    timestamp = prepareTimestamp()

    configMessage = """
{
  "uuid": "%s",
  "timestamp": "%s",
  "scansPerMeter": %s,
  "ticksPerMeter": %s
}""" % (ig.ANTENNA_UUID, timestamp, current_settings['scansPerMeter'], current_settings['ticksPerMeter']) 

    #print(battMessage)

    return configMessage

def prepareConfigIdMessage(deviceId, model, antennaGain, positionOffset, survey_cal):

    UUID = ig.ANTENNA_UUID

    configIdMessage = """
{
  "datasheet": {
    "manufactureId": 0,
    "manufactureModel": %s,
    "manufactureVersion": 0,
    "name": "%s",
    "serial": 12345,
    "size": 0,
    "uuid": "%s",
    "version": 0
  },
  "payload": {
    "gainDb": %s,
    "positionOffsetPs": %s,
    "surveyTicksPerM": %s
  },
  "uuid": "%s"
}""" % (deviceId, model, UUID, antennaGain, positionOffset, survey_cal, UUID)

    #print(configIdMessage)

    return configIdMessage

def prepareGPRSurveyMessage(scan_number, encoded_data, distance):

    timestamp = prepareTimestamp()
    
    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "timestamp": "%s",
  "dmi/0": {
    "timestamp": "%s",
    "binNumber": %s,
    "distanceM": %s
  },
  "gpr/chan/0": {
    "timestamp": "%s",
    "scanNumber": %s,
    "dataScan": "%s"
  }
}""" % (timestamp, timestamp, scan_number, distance, timestamp, scan_number, string_encoded_data)

    return GPRMessage

def prepareGPRCombinedMessage(scan_number, rawTickCount, encoded_data, distance):

    timestamp = prepareTimestamp()
    
    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "timestamp": "%s",
  "dmi/0": {
    "timestamp": "%s",
    "tickNumber": %s,
    "distanceM": %s
  },
  "gpr/chan/0": {
    "timestamp": "%s",
    "scanNumber": %s,
    "dataScan": "%s"
  }
}""" % (timestamp, timestamp, rawTickCount, distance, timestamp, scan_number, string_encoded_data)

    return GPRMessage

def prepareGPRFreerunMessage(scan_number, encoded_data):
    
    timestamp = prepareTimestamp()

    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "gpr/chan/0": {
    "timestamp": "%s",
    "scanNumber": %s,
    "dataScan": "%s"
  }
}""" % (timestamp, scan_number, string_encoded_data)

    return GPRMessage

def prepareGPREOFMessage():

    timestamp = prepareTimestamp()

    GPRMessage = """
{
  "timestamp": "%s",
  "gpr/chan/0": {
    "timestamp": "%s",
    "scanNumber": -1,
    "dataScan": ""
  }
}""" % (timestamp, timestamp)

    return GPRMessage

def prepareGPRRawMessage(scan_number, encoded_data):
    
    timestamp = prepareTimestamp()
    
    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "timestamp": "%s",
  "dmi": {
    "timestamp": "%s",
    "binNumber": %s,
    "distanceM": 0
  },
  "gpr": {
    "channels": {
      "0": {
        "timestamp": "%s",
        "scanNumber": %s,
        "dataScan": "%s"
      }
    }
  }
}""" % (timestamp, timestamp, scan_number, timestamp, scan_number, string_encoded_data)

    return GPRMessage

def prepareDMIMessage(scan_number, distance):

    timestamp = prepareTimestamp()

    DMIMessage = """
{
  "timestamp": "%s",
  "binNumber": %s,
  "distanceM": %s
}"""  % (timestamp, scan_number, distance)
    
    return DMIMessage

def prepareControlResponseMessage(incomingMessage, messageWithoutDate):

    timestamp = prepareTimestamp()

    controlResponseMessage = """{ 
  "uuid": "%s", 
  "timestamp": "%s", 
  "request": %s,  
  "result": %s
}"""  % (ig.ANTENNA_UUID, timestamp, incomingMessage, messageWithoutDate)

    return controlResponseMessage

def prepareConfigResponseMessageWithErrors(incomingMessage, messageWithoutDate, errors):

    timestamp = prepareTimestamp()

    controlResponseMessage = """{ 
  "uuid": "%s", 
  "timestamp": "%s", 
  "request": %s,  
  "result": %s,
  "errors":[%s]
}"""  % (ig.ANTENNA_UUID, timestamp, incomingMessage, messageWithoutDate, errors)

    return controlResponseMessage
