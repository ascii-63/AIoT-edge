IMAGE_EXTENTION = '.jpg'
VIDEO_EXTENTION = '.mp4'
VIDEO_LENGTH_SEC = 2

ENV_FILE_PATH = '.env'
CFG_FILE_PATH = 'message_config.txt'

DEFAULT_S3_URL = 'https://[].s3.ap-southeast-1.amazonaws.com/'
BUCKET_BRACKET = '[]'

DEFAULT_LOCAL_RABBITMQ_HOST = '192.168.0.201'
DEFAULT_LOCAL_RABBITMQ_PORT = 5672
DEFAULT_LOCAL_RABBITMQ_VH = '/'
DEFAULT_LOCAL_RABBITMQ_USER = 'admin'
DEFAULT_LOCAL_RABBITMQ_PWD = 'admin'
DEFAULT_LOCAL_RABBITMQ_MSG_QUEUE = 'message'

MAX_MESSAGE_ID = 999999
# In the person object of model message, these field index is empty/not useable
PERSON_MESSAGE_FIELD_REMOVE_LIST = [6, 10, 11]

COLON_UNICODE = '%3A'


##########################################

sample_raw_message = '{"version": "4.0","id": "0","@timestamp": "2023-12-25T09:02:45.820Z","sensorId": "","objects": ["18446744073709551615|1126.77|447.984|1276.23|717.798|Person|#|Male|20|Black|||0.873829"]}'

##########################################
