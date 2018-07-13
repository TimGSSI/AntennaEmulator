from datetime import datetime, timezone
import sys

def prepareTimestamp():

    # UTC 8601 datetime template: 2018-04-03T19:12:14.505Z
    currentTime = datetime.now(timezone.utc).astimezone().isoformat()
    currentTime = currentTime[:-9] + "Z"

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

def prepareGPRSurveyMessage(scan_number, encoded_data):
#def prepareGPRSurveyMessage(scan_number, encoded_data, distanceM):

    timestamp = prepareTimestamp()

    if len(timestamp) < 24:
        print("CRASH - TIMESTAMP FORMAT PROBLEM: " + str(timestamp))
        sys.exit()
    
    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "timestamp": "%s",
  "dmi/0": {
    "timestamp": "%s",
    "binNumber": %s,
    "distanceM": 0
  },
  "gpr/chan/0": {
    "timestamp": "%s",
    "scan_number": %s,
    "data": "%s"
  }
}""" % (timestamp, timestamp, scan_number, timestamp, scan_number, string_encoded_data)
#}""" % (timestamp, timestamp, scan_number, distanceM, timestamp, scan_number, string_encoded_data)

    return GPRMessage

def prepareGPRCombinedMessage(scan_number, rawTickCount, encoded_data):

    timestamp = prepareTimestamp()
    
    string_encoded_data = str(encoded_data)

    GPRMessage = """
{
  "timestamp": "%s",
  "dmi/0": {
    "timestamp": "%s",
    "tickNumber": %s,
    "distanceM": 0
  },
  "gpr/chan/0": {
    "timestamp": "%s",
    "scan_number": %s,
    "data": "%s"
  }
}""" % (timestamp, timestamp, rawTickCount, timestamp, scan_number, string_encoded_data)

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
