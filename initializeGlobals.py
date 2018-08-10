import pendulum
from queue import Queue

def initialize_globals(test_topics, nemaTalker, incoming, outgoing):

    global q

    global useNemaTalker
    global INCOMING_SCHEMA_VALIDATION
    global OUTGOING_SCHEMA_VALIDATION

    global GPS_NMEA_TOPIC
    global BATTERY_TOPIC
    global GPR_TOPIC
    global TELEM_GPR_RAW_TOPIC
    global DMI_TOPIC
    global CONFIG_DEVICE_TOPIC
    global CONFIG_GPR_TOPIC
    global CONFIG_GPR_CHAN_0_TOPIC
    global CONTROL_GPR_TOPIC
    global DMI_OUTPUT_FORMATTED_TOPIC
    global CONFIG_DMI_TOPIC
    global CONTROL_DMI_TOPIC
    global CONTROL_GPS_TOPIC
    global CONFIG_GPS_TOPIC
    global CONTROL_GPR_STATE_TOPIC
    global CONTROL_BATTERY_STATE

    global CONFIG_GPR_RESPONSE
    global CONFIG_GPS_RESPONSE
    global CONFIG_DMI_0_RESPONSE
    global CONTROL_DMI_STATE_RESPONSE
    global CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE
    global CONTROL_GPS_STATE_RESPONSE
    global CONTROL_GPR_STATE_RESPONSE
    global CONTROL_BATTERY_STATE_RESPONSE

    global FIFTH_OF_SEC
    global TENTH_SEC
    global ONE_SEC
    global ONE_MIN

    global BATTERY_CAPACITY
    global BATTERY_MINUTES_LEFT
    
    global BATTERY_TELEM_ENABLED
    global GPS_TELEM_ENABLED

    if incoming == True:
        INCOMING_SCHEMA_VALIDATION = True

    if outgoing == True:
        OUTGOING_SCHEMA_VALIDATION = True

    if test_topics == True:
        GPS_NMEA_TOPIC = "test/telem/gps/nmea"
        BATTERY_TOPIC = "test/telem/battery"
        GPR_TOPIC = "test/telem/gpr"
        TELEM_GPR_RAW_TOPIC = "test/telem/gpr/raw"
        DMI_TOPIC = "test/telem/dmi/formatted"
        CONFIG_DEVICE_TOPIC = "test/config/device"
        CONFIG_GPR_TOPIC = "test/config/gpr"
        CONFIG_GPR_CHAN_0_TOPIC = "test/config/gpr/chan/0"
        CONTROL_GPR_TOPIC = "test/control/gpr"
        DMI_OUTPUT_FORMATTED_TOPIC = "test/config/dmi/0/output/formatted"
        CONFIG_DMI_TOPIC = "test/config/dmi/0"
        CONTROL_DMI_TOPIC = "test/control/dmi/state" 
        CONTROL_GPS_TOPIC = "test/control/gps/state"
        CONFIG_GPS_TOPIC = "test/config/gps"
        CONTROL_GPR_STATE_TOPIC = "test/control/gpr/state"
        CONTROL_BATTERY_STATE = "test/control/battery/state"

        CONFIG_GPR_RESPONSE = "test/response/config/gpr"
        CONFIG_GPS_RESPONSE = "test/response/config/gps"
        CONFIG_DMI_0_RESPONSE = "test/response/config/dmi/0"
        CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE = "test/response/config/dmi/0/output/formatted"
        CONTROL_GPS_STATE_RESPONSE = "test/response/control/gps/state"
        CONTROL_GPR_STATE_RESPONSE = "test/response/control/gpr/state"
        CONTROL_BATTERY_STATE_RESPONSE = "test/response/control/battery/state"
        CONTROL_DMI_STATE_RESPONSE = "test/response/control/dmi/state"

    else:
        GPS_NMEA_TOPIC = "telem/gps/nmea"
        BATTERY_TOPIC = "telem/battery"
        GPR_TOPIC = "telem/gpr"
        TELEM_GPR_RAW_TOPIC = "telem/gpr/raw"
        DMI_TOPIC = "telem/dmi/formatted"
        CONFIG_DEVICE_TOPIC = "config/device"
        CONFIG_GPR_TOPIC = "config/gpr"
        CONFIG_GPR_CHAN_0_TOPIC = "config/gpr/chan/0"
        CONTROL_GPR_TOPIC = "control/gpr"
        DMI_OUTPUT_FORMATTED_TOPIC = "config/dmi/0/output/formatted"
        CONFIG_DMI_TOPIC = "config/dmi/0"
        CONTROL_DMI_TOPIC = "control/dmi/state"
        CONTROL_GPS_TOPIC = "control/gps/state"
        CONFIG_GPS_TOPIC = "config/gps"
        CONTROL_GPR_STATE_TOPIC = "control/gpr/state"
        CONTROL_BATTERY_STATE = "control/battery/state"

        CONFIG_GPR_RESPONSE = "response/config/gpr"
        CONFIG_GPS_RESPONSE = "response/config/gps"
        CONFIG_DMI_0_RESPONSE = "response/config/dmi/0"
        CONFIG_DMI_0__OUTPUT_FORMATTED_RESPONSE = "response/config/dmi/0/output/formatted"
        CONTROL_GPS_STATE_RESPONSE = "response/control/gps/state"
        CONTROL_GPR_STATE_RESPONSE = "response/control/gpr/state"
        CONTROL_BATTERY_STATE_RESPONSE = "response/control/battery/state"
        CONTROL_DMI_STATE_RESPONSE = "response/control/dmi/state"

    if nemaTalker == True:
        useNemaTalker = True
    else:
        useNemaTalker = False

    NOW = pendulum.now()
    ONE_MIN = NOW.add(minutes=1)
    ONE_MIN = ONE_MIN - NOW

    NOW = pendulum.now()
    ONE_SEC = NOW.add(seconds=1)
    ONE_SEC = ONE_SEC - NOW

    NOW = pendulum.now()
    TENTH_SEC = NOW.add(seconds=0.1)
    TENTH_SEC = TENTH_SEC - NOW

    NOW = pendulum.now()
    FIFTH_OF_SEC = NOW.add(seconds=0.2)
    FIFTH_OF_SEC = FIFTH_OF_SEC - NOW

    BATTERY_CAPACITY = 60
    BATTERY_MINUTES_LEFT = 60
    BATTERY_TELEM_ENABLED = False
    GPS_TELEM_ENABLED = False

    q = Queue() #initialize FIFO queue
