from datetime import datetime
from datetime import timezone
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
  "temperature": 0,
  "voltage": 0,
  "capacity": %s,
  "time": %s
}""" % (timestamp, capacity, battery_time)

    print(battMessage)

    return battMessage

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
    "scan_number": %s,
    "data": "%s"
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
    "scan_number": %s,
    "data": "%s"
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
    "scan_number": %s,
    "data": "%s"
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
    "scan_number": -1,
    "data": ""
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

def prepareDMIMessage(scan_number):

    timestamp = prepareTimestamp()

    DMIMessage = """
{
  "timestamp": "%s",
  "binNumber": %s,
  "distanceM": 0
}"""  % (timestamp, scan_number)
    
    return DMIMessage
