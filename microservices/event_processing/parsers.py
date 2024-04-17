import os

import config


def envFileParser(_env_file_path: str):
    """Read and parse the .env file:
    - Parameters:
        - _env_file_path: .env file path

    - Return:
    result,
    cloud_amqp_url, cloud_amqp_queue,
    bucket_name, s3_image_dir, s3_video_dir,
    image_url_start, video_url_start
    """
    try:
        with open(_env_file_path) as f:
            for line in f:
                if line.strip() and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    except Exception as e:
        raise Exception(e)

    #############################

    cloud_amqp_url = os.environ.get('AMQP_URL')
    cloud_amqp_queue = os.environ.get('QUEUE')

    bucket_name = os.environ.get('BUCKET')

    s3_image_dir = os.environ.get('S3_IMAGE_DIR')
    s3_video_dir = os.environ.get('S3_VIDEO_DIR')

    image_url_start = config.DEFAULT_S3_URL.replace(
        config.BUCKET_BRACKET, bucket_name) + '/' + s3_image_dir + '/'

    video_url_start = config.DEFAULT_S3_URL.replace(
        config.BUCKET_BRACKET, bucket_name) + '/' + s3_video_dir + '/'

    #############################

    if (
        cloud_amqp_url is None
        or cloud_amqp_queue is None
        or bucket_name is None
        or s3_image_dir is None
        or s3_video_dir is None
        or image_url_start is None
        or video_url_start is None
    ):
        return False, None, None, None, None, None, None, None

    return True, cloud_amqp_url, cloud_amqp_queue, bucket_name, s3_image_dir, s3_video_dir, image_url_start, video_url_start


def configFileParser(_cfg_file_path: str):
    """Read and parse the message config file:
    - Parameter:
        - _cfg_file_path (config file path)

    - Return:
    result,
    location_id, location_lat, location_lon, location_alt,
    model_id, model_description,
    camera_id, camera_type, camera_description,
    prev_message_idv
    """

    location_id, location_lat, location_lon, location_alt
    model_id, model_description
    camera_id, camera_type, camera_description
    prev_message_id

    try:
        with open(_cfg_file_path) as file:
            for line in file:
                key, value = line.strip().split('=', 1)

                if key == 'LOCATION_ID':
                    location_id = value
                elif key == 'LOCATION_LAT':
                    location_lat = float(value)
                elif key == 'LOCATION_LON':
                    location_lon = float(value)
                elif key == 'LOCATION_ALT':
                    location_alt = float(value)

                elif key == 'MODEL_ID':
                    model_id = value
                elif key == 'MODEL_DESCRIPTION':
                    model_description = value

                elif key == 'CAMERA_ID':
                    camera_id = value
                elif key == 'CAMERA_TYPE':
                    camera_type = value
                elif key == 'CAMERA_DESCRIPTION':
                    camera_description = value

                elif key == 'PREV_MESSAGE_ID':
                    prev_message_id = int(value)
    except Exception as e:
        raise Exception(e)

    #############################

    if (
        location_id is None
        or location_lat is None
        or location_lon is None
        or location_alt is None
        or model_id is None
        or model_description is None
        or camera_id is None
        or camera_type is None
        or camera_description is None
        or prev_message_id is None
    ):
        return False, None, None, None, None, None, None, None, None, None, None

    return True, location_id, location_lat, location_lon, location_alt, model_id, model_description, camera_id, camera_type, camera_description, prev_message_id
