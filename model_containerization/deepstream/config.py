PGIE_CLASS_ID_VEHICLE = 2
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 0
PGIE_CLASS_ID_ROADSIGN = 3
MUXER_OUTPUT_WIDTH = 1280
MUXER_OUTPUT_HEIGHT = 720
MUXER_BATCH_TIMEOUT_USEC = 4000000
CODEC = "H264"
BITRATE = 4000000
TILED_OUTPUT_WIDTH = MUXER_OUTPUT_WIDTH
TILED_OUTPUT_HEIGHT = MUXER_OUTPUT_HEIGHT
SINK_QOS = 0
SINK_SYNC = 0
MSGCONV_SCHEMA_TYPE = 1  # 0 for Full, 1 for Minimal

MIN_CONFIDENCE = 0.5
MAX_CONFIDENCE = 1
MAX_DISPLAY_LEN = 64
MAX_TIME_STAMP_LEN = 32
STREAM_FPS = 24
MESSAGE_RATE = 1
FRAMES_PER_MESSAGE = STREAM_FPS * MESSAGE_RATE
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
RTSP_OUT_PORT = 8554
RTSP_OUT_FACTORY = "/out"
RTSP_OUT_DELAY_USECS = 0

PGIE_CONFIG_FILE = "../model__engine/DeepStream-Yolo/config_infer_primary_yoloV8.txt"
AMQP_CONFIG_FILE = "amqp_config.txt"
MSGCONV_CONFIG_FILE = "message_convert_config.txt"
AMQP_LIB_FILE = "/opt/nvidia/deepstream/deepstream-6.3/lib/libnvds_amqp_proto.so"