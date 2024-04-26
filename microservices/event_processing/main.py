from google.cloud import storage

import sys
import os
import pika
import json
from datetime import datetime, timedelta
import time
import cv2
import numpy as np

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


def S3ImageUpload(_bucket_name: str, _image: np.ndarray) -> bool:
    """Upload image `np.ndarray` to AWS S3 bucket"""

    pass


def S3VideoUpload(_bucket_name: str, _video: list) -> bool:
    """Upload video `list` of `np.ndarray` to AWS S3 bucket"""

    pass


def rawMessageParsing(_raw_msg: str):
    """
    Parse the raw JSON message in `str`, \n
    return timestamp in `str`; `list` of objects and events
    """

    data = json.loads(_raw_msg)

    timestamp_str = data["@timestamp"]

    ###########################

    objects_data = data["objects"]
    objects_list = []

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

    ###########################

    events_data = data["events"]
    events_list = []

    pass

    ###########################

    return timestamp_str, objects_list, events_list


def messageGenerator(_raw_msg: str):
    """
    Parse the raw JSON message in `str`, \n
    return the `str` message, which will be uploaded to CloudAMQP in JSON format.
    """

    global location_id, location_lat, location_lon, location_alt
    global model_id, model_description
    global camera_id, camera_type, camera_description
    global prev_message_id

    timestamp_str, objects_list, events_list = rawMessageParsing(_raw_msg)
    num_obj = len(objects_list)
    num_event = len(events_list)

    if prev_message_id > config.MAX_MESSAGE_ID:
        prev_message_id %= (config.MAX_MESSAGE_ID+1)
    message_id = location_id + '-' + model_id + '-' + \
        camera_id + '-' + '{:06d}'.format(prev_message_id)
    prev_message_id += 1

    image_url = cloud.getImageURL(timestamp_str)
    video_url = cloud.getVideoURL(timestamp_str)

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
        "video_URL": video_url
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


def sendMessage(_message):
    """Send a `str` message to the cloud RabbitMQ message broker"""

    global cloud_amqp_url, cloud_queue_name

    try:
        # Create a connection to the remote AMQP server using the configuration
        remote_connection_parameters = pika.URLParameters(cloud_amqp_url)
        remote_connection = pika.BlockingConnection(
            remote_connection_parameters)
        remote_channel = remote_connection.channel()

        # Publish the received message to the remote queue
        remote_channel.basic_publish(
            exchange='',
            routing_key=cloud_queue_name,
            body=_message
        )

        remote_connection.close()
    except Exception as e:
        print(f"Exception when send a message to cloud RabbitMQ")


def messageProcessing():
    """
    Recive message from local RabbitMQ, then: \n
    1. Re-format it, then publish it to cloud RabbitMQ \n
    2. Get timestamp, create image and/or video with that timestamp, then send them to AWS S3 bucket
    """

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
        print(f"[WARN] Null local_callback function!")

    # Set up the consumer and specify the callback function
    local_channel.basic_consume(
        queue=str(config.DEFAULT_LOCAL_RABBITMQ_MSG_QUEUE), on_message_callback=local_callback)

    try:
        local_channel.start_consuming()
    except KeyboardInterrupt:
        local_channel.stop_consuming()


if __name__ == '__main__':
    if (not parsers.envFileParser() or not parsers.configFileParser()):
        print(f'Error while parsing .env or message_config.txt file', file=sys.stderr)
        sys.exit(1)

    messageProcessing()
