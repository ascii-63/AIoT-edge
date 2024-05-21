import pika
import boto3

import system
import config


def getImageURL(_timestamp_str: str, _image_url_start: str) -> str:
    """Get image public URL from S3 with a specific timestamp"""

    image_url = _image_url_start

    timestamp_str = system.convertUTC0ToUTC7(_timestamp_str)+'Z'
    timestamp_url = timestamp_str.replace(':', config.COLON_UNICODE)
    image_url = image_url + timestamp_url + config.IMAGE_EXTENTION

    print(image_url)
    return image_url


def getVideoURL(_timestamp_str: str, _video_url_start: str) -> str:
    """Get video Public URL from S3 with a specific timestamp"""

    video_url = _video_url_start

    timestamp_str = system.convertUTC0ToUTC7(_timestamp_str)
    timestamp_url = timestamp_str.replace(':', config.COLON_UNICODE)
    video_url = video_url + timestamp_url + config.VIDEO_EXTENTION

    return video_url


def singleBinaryObjectUpload(_bucket: str, _src_bytes: bytes, _destination_obj: str) -> bool:
    """
    Uploads a file to the bucket:
    #     _bucket: S3 bucket name
    #     _src_bytes: Binary form of object (image/JPEG or video/MP4)
    #     _destination_obj: The path to the object in S3 bucket
    """
    try:
        client = boto3.client('s3')

        res = client.put_object(
            Bucket=_bucket,
            Key=_destination_obj,
            Body=_src_bytes)
    except Exception as e:
        print(f"Error when upload to S3: {e}")
        return False

    if res == None:
        return False
    return True


def singleVideoFileUpload(_bucket: str, _file: str, _des: str) -> bool:
    """
    Uploads a file to the bucket:
        _bucket: S3 bucket name
        _file: Path to file
        _des: Path to the object in S3 bucket
    """

    if not (system.searchFileInDirectory(config.TEMP_VIDEO_DIR, _file)):
        return False

    try:
        client = boto3.client('s3')

        res = client.put_object(
            Bucket=_bucket,
            Key=_des,
            Body=_file
        )
    except Exception as e:
        print(f"Error when upload to S3: {e}")
        return False

    if res == None:
        return False
    return True


def sendMessage(_message: str, _remote_amqp_url, _remote_queue_name) -> bool:
    """Send message to the remote AMQP server"""

    try:
        # Create a connection to the remote AMQP server using the configuration
        remote_connection_parameters = pika.URLParameters(_remote_amqp_url)
        remote_connection = pika.BlockingConnection(
            remote_connection_parameters)
        remote_channel = remote_connection.channel()

        # Publish the received message to the remote queue
        remote_channel.basic_publish(
            exchange='',
            routing_key=_remote_queue_name,
            body=_message
        )

        # Close the connection to the remote AMQP server
        remote_connection.close()
    except Exception as e:
        return False

    return True
