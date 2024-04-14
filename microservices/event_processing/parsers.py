import os

import config


def envFileParser(_env_file_path: str):
    """Read and parse the .env file:
    - Parameters:
        - _env_file_path: .env file path

    - Return:
    result,
    remote_amqp_url, remote_queue_name,
    bucket_name,
    local_image_dir, local_video_dir, cloud_image_dir, cloud_video_dir,
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

    remote_amqp_url = os.environ.get('AMQP_URL')
    remote_queue_name = os.environ.get('QUEUE')

    bucket_name = os.environ.get('BUCKET')

    local_image_dir = os.environ.get('LOCAL_IMAGE_DIR')
    local_video_dir = os.environ.get('LOCAL_VIDEO_DIR')
    cloud_image_dir = os.environ.get('CLOUD_IMAGE_DIR')
    cloud_video_dir = os.environ.get('CLOUD_VIDEO_DIR')

    image_url_start = config.GOOGLEAPI_URL_START + bucket_name + '/' + cloud_image_dir + '/'
    video_url_start = config.GOOGLEAPI_URL_START + bucket_name + '/' + cloud_video_dir + '/'

    #############################

    if (
        remote_amqp_url is None
        or remote_queue_name is None
        or bucket_name is None
        or local_image_dir is None
        or local_video_dir is None
        or cloud_image_dir is None
        or cloud_video_dir is None
        or image_url_start is None
        or video_url_start is None
    ):
        return False, None, None, None, None, None, None, None, None, None

    return True, remote_amqp_url, remote_queue_name, bucket_name, local_image_dir, local_video_dir, cloud_image_dir, cloud_video_dir, image_url_start, video_url_start


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
