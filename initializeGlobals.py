import pendulum
import json
import jsonschema
import uuid
from queue import Queue

# function loads schema files as global JSON objects for fast checking 
def getJSONSchemaObject(file_name):
    validation_directory = "./schema_validation/"
    validation_file = validation_directory + file_name
    with open(validation_file) as f:
            schema = f.read()
            f.close()
    schema_object = json.loads(schema)
    return schema_object

# this function initializes variables that are shared between multiple files
def initialize_globals(test_topics, nemaTalker, incoming, outgoing, loopData, debugOutput, web_app):

    global Q

    global VERSION_NUMBER
    global ANTENNA_UUID
    global POINT_MODE_SCAN_NUMBER
    global POINT_MODE_ENABLED
    global POINT_MODE_BYTE_COUNT

    global USE_NEMA_TALKER
    global INCOMING_SCHEMA_VALIDATION
    global OUTGOING_SCHEMA_VALIDATION
    global LOOP_DATA
    global DEBUG_OUTPUT
    global WEB_APP

    global GPS_NMEA_TOPIC
    global BATTERY_TOPIC
    global GPR_TOPIC
    global TELEM_GPR_RAW_TOPIC
    global DMI_TOPIC
    global CONFIG_DEVICE_TOPIC
    global CONFIG_GPR_TOPIC
    global CONFIG_GPR_CHAN_0_TOPIC
    global CONFIG_GPR_CHAN_1_TOPIC
    global CONTROL_GPR_TOPIC
    global DMI_OUTPUT_FORMATTED_TOPIC
    global CONFIG_DMI_TOPIC
    global CONTROL_DMI_TOPIC
    global CONTROL_GPS_TOPIC
    global CONFIG_GPS_TOPIC
    global CONTROL_GPR_STATE_TOPIC
    global CONTROL_BATTERY_STATE
    global STATUS_ID
    global CONFIG_STORAGE_ANTENNA
    global RESTORE_SAVED_SETTINGS

    global CONFIG_GPR_RESPONSE
    global CONFIG_GPR_CHAN_0_RESPONSE
    global CONFIG_GPR_CHAN_1_RESPONSE
    global CONFIG_GPS_RESPONSE
    global CONFIG_DMI_0_RESPONSE
    global CONTROL_DMI_STATE_RESPONSE
    global CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE
    global CONTROL_GPS_STATE_RESPONSE
    global CONTROL_GPR_STATE_RESPONSE
    global CONTROL_BATTERY_STATE_RESPONSE
    global STATUS_ID_RESPONSE
    global CONFIG_STORAGE_ANTENNA_RESPONSE

    global FIFTH_OF_SEC
    global TENTH_OF_SEC
    global HALF_OF_SEC
    global ONE_SEC
    global FIVE_SEC
    global TEN_SEC
    global THIRTY_SEC
    global ONE_MIN

    global SCANS_BEFORE_BACKUP
    global SCANS_TO_BACKUP

    global BATTERY_CAPACITY
    global BATTERY_MINUTES_LEFT
    
    global BATTERY_TELEM_ENABLED
    global GPS_TELEM_ENABLED

    global POSITION_OFFSET
    global TX_RATE

    # schema validation objects
    global GENERAL_CONFIG_SCHEMA
    global CONFIG_GPR_SCHEMA
    global CONFIG_GPS_SCHEMA
    global CONFIG_DMI_SCHEMA
    global CONFIG_DMI_OUTPUT_FORMATTED_SCHEMA
    global CONTROL_GPR_SCHEMA
    global CONTROL_GPS_SCHEMA
    global CONTROL_DMI_SCHEMA
    global CONTROL_BATTERY_SCHEMA
    global ROOT_VALIDATOR_SCHEMA

    global TELEM_GPR_RAW_SCHEMA
    global TELEM_BATTERY_SCHEMA
    global TELEM_DMI_FORMATTED_SCHEMA
    global TELEM_GPS_NMEA_SCHEMA
    global STATUS_ID_SCHEMA
    global FILE_LIST
    global FILE_LIST_PARSED

    ANTENNA_UUID = str(uuid.uuid4())
    VERSION_NUMBER = "1.010"

    print("Low Frequency Antenna Emulator Version: " + str(VERSION_NUMBER))
    print("ANTENNA_UUID: " + str(ANTENNA_UUID) + "\n" )
    
    if incoming == True:
        INCOMING_SCHEMA_VALIDATION = True
    else:
        INCOMING_SCHEMA_VALIDATION = False

    if outgoing == True:
        OUTGOING_SCHEMA_VALIDATION = True
    else:
        OUTGOING_SCHEMA_VALIDATION = False

    if INCOMING_SCHEMA_VALIDATION == True:

        # JSON schema file names
        config_gpr_validation_file = "ConfigGpr.json"
        config_gps_validation_file = "ConfigGps.json"
        config_dmi_validation_file = "ConfigDmi.json"
        config_dmi_output_formatted_validation_file = "ConfigDmiOutputFormatted.json"
        control_gpr_validation_file = "ControlGpr.json"
        control_gps_validation_file = "ControlGps.json"
        control_dmi_validation_file = "ControlDmi.json"
        control_battery_validation_file = "ControlBattery.json"
        
        # creates JSON schema objects to compare with incoming messages for fast validation
        CONFIG_GPR_SCHEMA = getJSONSchemaObject(config_gpr_validation_file)
        CONFIG_GPS_SCHEMA = getJSONSchemaObject(config_gps_validation_file)
        CONFIG_DMI_SCHEMA = getJSONSchemaObject(config_dmi_validation_file)
        CONFIG_DMI_OUTPUT_FORMATTED_SCHEMA = getJSONSchemaObject(config_dmi_output_formatted_validation_file)
        CONTROL_GPR_SCHEMA = getJSONSchemaObject(control_gpr_validation_file)
        CONTROL_GPS_SCHEMA = getJSONSchemaObject(control_gps_validation_file)
        CONTROL_DMI_SCHEMA = getJSONSchemaObject(control_dmi_validation_file)        
        CONTROL_BATTERY_SCHEMA = getJSONSchemaObject(control_battery_validation_file)
    
    if OUTGOING_SCHEMA_VALIDATION == True:

        telem_gpr_raw_validation_file = "TelemGprRaw.json"
        telem_battery_validation_file = "TelemBattery.json"
        telem_dmi_formatted_validation_file = "TelemDmiFormatted.json"
        telem_gps_nmea_validation_file = "TelemGpsNmea.json"
        
        TELEM_GPR_RAW_SCHEMA = getJSONSchemaObject(telem_gpr_raw_validation_file)
        TELEM_BATTERY_SCHEMA = getJSONSchemaObject(telem_battery_validation_file)
        TELEM_DMI_FORMATTED_SCHEMA = getJSONSchemaObject(telem_dmi_formatted_validation_file)
        TELEM_GPS_NMEA_SCHEMA = getJSONSchemaObject(telem_gps_nmea_validation_file)

    if test_topics == True:
        # outgoing messages
        GPS_NMEA_TOPIC = "test/telem/gps/nmea"
        BATTERY_TOPIC = "test/telem/battery"
        GPR_TOPIC = "test/telem/gpr"
        TELEM_GPR_RAW_TOPIC = "test/telem/gpr/raw"
        DMI_TOPIC = "test/telem/dmi/formatted"
        STATUS_ID = "test/status/id"
        CONFIG_STORAGE_ANTENNA = "test/config/storage/ant"

        # incoming messages
        CONFIG_DEVICE_TOPIC = "test/config/device"
        CONFIG_GPR_TOPIC = "test/config/gpr"
        CONFIG_GPR_CHAN_0_TOPIC = "test/config/gpr/chan/0"
        CONFIG_GPR_CHAN_1_TOPIC = "test/config/gpr/chan/1"
        CONFIG_DMI_TOPIC = "test/config/dmi/0"
        DMI_OUTPUT_FORMATTED_TOPIC = "test/config/dmi/0/output/formatted"
        CONFIG_GPS_TOPIC = "test/config/gps"
        CONTROL_GPR_TOPIC = "test/control/gpr"       
        CONTROL_DMI_TOPIC = "test/control/dmi/state" 
        CONTROL_GPS_TOPIC = "test/control/gps/state"
        CONTROL_GPR_STATE_TOPIC = "test/control/gpr/state"
        CONTROL_BATTERY_STATE = "test/control/battery/state"

        # response messages
        CONFIG_GPR_RESPONSE = "test/response/config/gpr"
        CONFIG_GPR_CHAN_0_RESPONSE = "test/response/config/gpr/chan/0"
        CONFIG_GPR_CHAN_1_RESPONSE = "test/response/config/gpr/chan/1"
        CONFIG_GPS_RESPONSE = "test/response/config/gps"
        CONFIG_DMI_0_RESPONSE = "test/response/config/dmi/0"
        CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE = "test/response/config/dmi/0/output/formatted"
        CONTROL_GPS_STATE_RESPONSE = "test/response/control/gps/state"
        CONTROL_GPR_STATE_RESPONSE = "test/response/control/gpr/state"
        CONTROL_BATTERY_STATE_RESPONSE = "test/response/control/battery/state"
        CONTROL_DMI_STATE_RESPONSE = "test/response/control/dmi/state"
        STATUS_ID_RESPONSE = "test/response/status/id"
        CONFIG_STORAGE_ANTENNA_RESPONSE = "test/response/config/storage/ant"

    else:
        # outgoing messages
        GPS_NMEA_TOPIC = "telem/gps/nmea"
        BATTERY_TOPIC = "telem/battery"
        GPR_TOPIC = "telem/gpr"
        TELEM_GPR_RAW_TOPIC = "telem/gpr/raw"
        DMI_TOPIC = "telem/dmi/formatted"
        STATUS_ID = "status/id"
        CONFIG_STORAGE_ANTENNA = "config/storage/ant"

        # incoming messages
        CONFIG_DEVICE_TOPIC = "config/device"
        CONFIG_GPR_TOPIC = "config/gpr"
        CONFIG_GPR_CHAN_0_TOPIC = "config/gpr/chan/0"
        CONFIG_GPR_CHAN_1_TOPIC = "config/gpr/chan/1"
        CONFIG_DMI_TOPIC = "config/dmi/0"
        DMI_OUTPUT_FORMATTED_TOPIC = "config/dmi/0/output/formatted"
        CONFIG_GPS_TOPIC = "config/gps"
        CONTROL_GPR_TOPIC = "control/gpr"
        CONTROL_DMI_TOPIC = "control/dmi/state"
        CONTROL_GPS_TOPIC = "control/gps/state"
        CONTROL_GPR_STATE_TOPIC = "control/gpr/state"
        CONTROL_BATTERY_STATE = "control/battery/state"

        # response messages
        CONFIG_GPR_RESPONSE = "response/config/gpr"
        CONFIG_GPR_CHAN_0_RESPONSE = "response/config/gpr/chan/0"
        CONFIG_GPR_CHAN_1_RESPONSE = "response/config/gpr/chan/1"
        CONFIG_GPS_RESPONSE = "response/config/gps"
        CONFIG_DMI_0_RESPONSE = "response/config/dmi/0"
        CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE = "response/config/dmi/0/output/formatted"
        CONTROL_GPS_STATE_RESPONSE = "response/control/gps/state"
        CONTROL_GPR_STATE_RESPONSE = "response/control/gpr/state"
        CONTROL_BATTERY_STATE_RESPONSE = "response/control/battery/state"
        CONTROL_DMI_STATE_RESPONSE = "response/control/dmi/state"
        STATUS_ID_RESPONSE = "response/status/id"
        CONFIG_STORAGE_ANTENNA_RESPONSE = "response/config/storage/ant"

        RESTORE_SAVED_SETTINGS = "restore/settings"

    if nemaTalker == True:
        USE_NEMA_TALKER = True
    else:
        USE_NEMA_TALKER = False

    if loopData == True:
        LOOP_DATA = True
    else:
        LOOP_DATA = False

    if debugOutput == True:
        DEBUG_OUTPUT = True
    else: 
        DEBUG_OUTPUT = False

    if web_app == True:
        WEB_APP = True
    else:
        WEB_APP = False
    
    NOW = pendulum.now()
    TENTH_OF_SEC = NOW.add(seconds=0.1)
    TENTH_OF_SEC = TENTH_OF_SEC - NOW
    
    NOW = pendulum.now()
    FIFTH_OF_SEC = NOW.add(seconds=0.2)
    FIFTH_OF_SEC = FIFTH_OF_SEC - NOW
    
    NOW = pendulum.now()
    HALF_OF_SEC = NOW.add(seconds=0.5)
    HALF_OF_SEC = HALF_OF_SEC - NOW
    
    NOW = pendulum.now()
    ONE_SEC = NOW.add(seconds=1)
    ONE_SEC = ONE_SEC - NOW

    NOW = pendulum.now()
    FIVE_SEC = NOW.add(seconds=5)
    FIVE_SEC = FIVE_SEC - NOW

    NOW = pendulum.now()
    TEN_SEC = NOW.add(seconds=10)
    TEN_SEC = TEN_SEC - NOW

    NOW = pendulum.now()
    THIRTY_SEC = NOW.add(seconds=30)
    THIRTY_SEC = THIRTY_SEC - NOW
    
    NOW = pendulum.now()
    ONE_MIN = NOW.add(minutes=1)
    ONE_MIN = ONE_MIN - NOW

    POINT_MODE_SCAN_NUMBER = 0
    POINT_MODE_ENABLED = False
    POINT_MODE_BYTE_COUNT = 0

    BATTERY_CAPACITY = 100
    BATTERY_MINUTES_LEFT = 360
    BATTERY_TELEM_ENABLED = False

    GPS_TELEM_ENABLED = False

    SCANS_BEFORE_BACKUP = 300
    SCANS_TO_BACKUP = 100

    # creates a dictionary pairing all data files with valid timerange/sampPerScan combinations 
    # The dictionary key is the currently selected samples underscore timerange, example: "512_256"
    FILE_LIST = {}
    samps = 512
    file_number = 1
    original_timerange = 64
    timerange = 64
    valid_timeranges = [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]
    for x in range(0, 5):
        index = x
        for y in range(0, 5):
            combined = str(samps) + "_" + str(valid_timeranges[index])
            index += 1
            FILE_LIST[combined] = "FILE_" + str(file_number) + ".DZT"
            file_number += 1
        samps *= 2

    Q = Queue() #initialize FIFO queue
