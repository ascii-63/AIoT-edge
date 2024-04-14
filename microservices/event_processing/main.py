from google.cloud import storage

import sys
import os
import pika
import json
from datetime import datetime, timedelta
import time

import cloud
import config
import parsers
import system


remote_amqp_url = None
remote_queue_name = None

bucket_name = None

local_image_dir = None
local_video_dir = None
cloud_image_dir = None
cloud_video_dir = None

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
