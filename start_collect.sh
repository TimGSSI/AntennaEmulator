mosquitto_pub -t 'control/gps/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:54.968Z","newState":"idle","delay":0}'

mosquitto_pub -t 'control/dmi/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:54.968Z","newState":"idle","delay":0}'

mosquitto_pub -t 'control/gpr/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:54.968Z","newState":"idle","delay":0}'

mosquitto_pub -t 'config/gpr' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.055Z","channels":[{"enable":true,"positionOffsetPs":8000,"timeRangeNs":128}],"samples":1024,"repeats":768,"txRateKHz":200.0,"enableDither":false,"scanRateHz":50.0,"scanControl":"swtick","channelSync":"immediate","enableDeadman":false,"rcConfig":"monostatic"}'

mosquitto_pub -t 'config/dmi/0' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.055Z","enable":true,"deadband":0,"scansPerMeter":10.0,"ticksPerMeter":3452.0}'

mosquitto_pub -t 'config/dmi/0/output/formatted' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.056Z","publish":true,"messagesPerSec":0}'

mosquitto_pub -t 'control/gps/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.056Z","newState":"run","delay":0}'

mosquitto_pub -t 'control/dmi/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.056Z","newState":"run","delay":0}'

mosquitto_pub -t 'control/gpr/state' -m '{"uuid":"888075c5-a044-4b9c-a1a9-ed3f63abe085","timestamp":"2018-10-10T14:02:55.056Z","newState":"run","delay":0}'

