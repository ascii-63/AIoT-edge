import pika
import json

import cloud
import config
import parsers
import system
import streams


cloud_amqp_url = None
cloud_queue_name = None

bucket_name = None

s3_image_dir = None
s3_video_dir = None

image_url_start = None
video_url_start = None

rtsp_url = None

##################################

location_id = None
location_lat = None
location_lon = None
location_alt = None

model_id = None
model_description = None

camera_id = None
camera_type = None
camera_description = None

prev_message_id = None

##################################


class Object:
    def __init__(self, id, topleftx, toplefty, bottomrightx, bottomrighty):
        self.id = str(id)
        self.topleftx = float(topleftx)
        self.toplefty = float(toplefty)
        self.bottomrightx = float(bottomrightx)
        self.bottomrighty = float(bottomrighty)


class Person(Object):
    def __init__(self, id, topleftx, toplefty, bottomrightx, bottomrighty, obj_type, gender, age, hair_color, confidence):
        super().__init__(id, topleftx, toplefty, bottomrightx, bottomrighty)
        self.gender = gender
        self.age = age
        self.hair_color = hair_color
        self.confidence = confidence


class Vehicle(Object):
    def __init__(self, id, topleftx, toplefty, bottomrightx, bottomrighty, type, brand, color, licence, confidence):
        super().__init__(id, topleftx, toplefty, bottomrightx, bottomrighty)
        self.type = type
        self.brand = brand
        self.color = color
        self.licence = licence
        self.confidence = confidence

##################################


def getTimestampFromMessage(_message: str) -> str:
    """Get the timestamp of the original message"""

    data = json.loads(_message)
    timestamp_str = data.get('@timestamp')

    return timestamp_str


def streamHandle(_timestamp: str, _get_image: bool, _get_video: bool) -> bool:
    """
    Capture, upload image and video to AWS S3, return `True` if successful
    """
    image_bytes = None
    video_path = None

    image_des = s3_image_dir + '/' + _timestamp + config.IMAGE_EXTENTION
    video_des = s3_video_dir + '/' + _timestamp + config.VIDEO_EXTENTION

    img_re = False
    vid_re = False

    if _get_image:
        image_bytes = streams.imageCapture_toBytes()
        if image_bytes is None:
            return False
        img_re = cloud.singleBinaryObjectUpload(
            bucket_name, image_bytes, image_des)

    if _get_video:
        video_file = streams.videoCapture_toFile(_timestamp)
        if video_file == None:
            return False
        if not system.searchFileInDirectory(config.TEMP_VIDEO_DIR, str(_timestamp+config.VIDEO_EXTENTION)):
            return False
        vid_re = cloud.singleVideoFileUpload(
            bucket_name, video_file, video_des)
        if vid_re:
            system.removeTempVideoFileWithTimestamp(_timestamp)

    if (_get_image == img_re) and (_get_video == vid_re):
        return True

    return False


def rawMessageParsing(_raw_msg: str):
    """
    Parse the raw JSON message in `str`, \n
    return timestamp in `str`; `list` of objects and events
    """

    data = json.loads(_raw_msg)

    timestamp_str = data["@timestamp"]
    events_list = []
    objects_list = []

    ###########################
    try:
        objects_data = data["objects"]

        for object_str in objects_data:
            fields = object_str.split('|')
            object_type = fields[5]

            if object_type == 'Person':
                fields.pop(config.PERSON_MESSAGE_FIELD_REMOVE_LIST[0])
                fields.pop(config.PERSON_MESSAGE_FIELD_REMOVE_LIST[1] - 1)
                fields.pop(config.PERSON_MESSAGE_FIELD_REMOVE_LIST[2] - 2)

                person = Person(*fields)
                objects_list.append(person)
            elif object_type == 'Vehicle':
                pass
                # vehicle = Vehicle(*fields)
                # objects_list.append(vehicle)

        events_data = data["events"]
    except Exception as e:
        pass

    ###########################

    return timestamp_str, objects_list, events_list


def messageGenerator(_raw_msg: str) -> str:
    """
    Parse the raw JSON message in `str`, \n
    return the `str` message, which will be uploaded to CloudAMQP in JSON format.
    """

    global location_id, location_lat, location_lon, location_alt
    global model_id, model_description
    global camera_id, camera_type, camera_description
    global prev_message_id

    global image_url_start, video_url_start

    timestamp_str, objects_list, events_list = rawMessageParsing(_raw_msg)
    num_obj = len(objects_list)
    num_event = len(events_list)

    if prev_message_id > config.MAX_MESSAGE_ID:
        prev_message_id %= (config.MAX_MESSAGE_ID+1)
    message_id = location_id + '-' + model_id + '-' + \
        camera_id + '-' + '{:06d}'.format(prev_message_id)
    prev_message_id += 1

    image_url = cloud.getImageURL(timestamp_str, image_url_start)
    video_url = cloud.getVideoURL(timestamp_str, video_url_start)

    ###########################

    message = {
        "message_id": message_id,
        "timestamp": timestamp_str,
        "location": {
            "id": location_id,
            "lat": location_lat,
            "lon": location_lon,
            "alt": location_alt
        },
        "model": {
            "id": model_id,
            "description": model_description
        },
        "camera": {
            "id": camera_id,
            "type": camera_type,
            "description": camera_description
        },
        "number_of_objects": num_obj,
        "object_list": [],
        "number_of_events": num_event,
        "event_list": [],
        "image_URL": image_url,
        # "video_URL": video_url
    }

    ###########################

    obj_idx = 0
    for obj in objects_list:
        if (isinstance(obj, Person)):
            message["object_list"].append({
                config.PERSON_RENAME: {
                    "id": '{:02d}'.format(obj_idx),
                    "gender": obj.gender,
                    "age": obj.age,
                    "bbox": {
                        "topleftx": obj.topleftx,
                        "toplefty": obj.toplefty,
                        "bottomrightx": obj.bottomrightx,
                        "bottomrighty": obj.bottomrighty
                    }
                }
            })
            obj_idx += 1
        # elif (isinstance(obj, Vehicle)):
        #     message["object_list"].append({
        #         config.VEHICLE_RENAME: {
        #             "id": '{:02d}'.format(obj_idx),
        #             "type": obj.type,
        #             "brand": obj.brand,
        #             "color": obj.color,
        #             "licence": obj.licence,
        #             "bbox": {
        #                 "topleftx": obj.topleftx,
        #                 "toplefty": obj.toplefty,
        #                 "bottomrightx": obj.bottomrightx,
        #                 "bottomrighty": obj.bottomrighty
        #             }
        #         }
        #     })
        #     obj_idx += 1

    return json.dumps(message)


def messageProcessing():
    """
    Recive message from local RabbitMQ, then: \n
    1. Re-format it, then publish it to cloud RabbitMQ \n
    2. Get timestamp, create image and/or video with that timestamp, then send them to AWS S3 bucket
    """

    global cloud_amqp_url, cloud_queue_name

    # Define the local AMQP server connection parameters
    local_connection_parameters = pika.ConnectionParameters(
        host=str(config.DEFAULT_LOCAL_RABBITMQ_HOST),
        port=int(config.DEFAULT_LOCAL_RABBITMQ_PORT),
        virtual_host=str(config.DEFAULT_LOCAL_RABBITMQ_VH),
        credentials=pika.PlainCredentials(
            str(config.DEFAULT_LOCAL_RABBITMQ_USER), str(config.DEFAULT_LOCAL_RABBITMQ_PWD))
    )

    # Create a connection to the local AMQP server
    local_connection = pika.BlockingConnection(local_connection_parameters)
    local_channel = local_connection.channel()

    # Declare the queue to receive messages from
    local_channel.queue_declare(
        queue=str(config.DEFAULT_LOCAL_RABBITMQ_MSG_QUEUE), durable=True)

    # Define a callback function to process received messages
    def local_callback(ch, method, properties, body):
        timestamp = getTimestampFromMessage(body)

        if timestamp == None:
            return

        timestamp = system.convertUTC0ToUTC7(timestamp)
        print(f"\n>_____  {timestamp}")

        _, objects, events = rawMessageParsing(body)
        get_image = False
        get_video = False
        if len(objects) != 0:
            get_image = True
        if len(events) != 0:
            get_video = True

        if not streamHandle(timestamp, get_image, get_video):
            return
        print(f">_____ UP")

        res = cloud.sendMessage(
            messageGenerator(body), cloud_amqp_url, cloud_queue_name)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        if res:
            print(f">_____ PUB")

    # Set up the consumer and specify the callback function
    local_channel.basic_consume(
        queue=str(config.DEFAULT_LOCAL_RABBITMQ_MSG_QUEUE), on_message_callback=local_callback)

    try:
        local_channel.start_consuming()
    except KeyboardInterrupt:
        local_channel.stop_consuming()


if __name__ == '__main__':
    env_result, cloud_amqp_url, cloud_queue_name, bucket_name, s3_image_dir, s3_video_dir, image_url_start, video_url_start, rtsp_url = parsers.envFileParser(
        config.ENV_FILE_PATH)

    cfg_result, location_id, location_lat, location_lon, location_alt, model_id, model_description, camera_id, camera_type, camera_description, prev_message_id = parsers.configFileParser(
        config.CFG_FILE_PATH)

    messageProcessing()
