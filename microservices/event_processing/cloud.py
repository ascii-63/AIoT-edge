from google.cloud import storage
import pika
import json

import system
import config


def getImageURL(_timestamp_str: str, _image_url_start: str) -> str:
    """Get Image Public URL from Google Storage with a specific timestamp"""

    image_url = _image_url_start

    timestamp_str = system.convertUTC0ToUTC7(_timestamp_str)
    timestamp_str.replace(':', config.COLON_UNICODE)
    image_url = image_url + timestamp_str + config.IMAGE_EXTENTION

    return image_url


def getVideoURL(_timestamp_str: str, _video_url_start: str) -> str:
    """Get Image Public URL from Google Storage with a specific timestamp"""
    return None


def singleBlobUpload(_bucket_name: str, _source_file_name: str, _destination_blob: str) -> bool:
    """
    Uploads a file to the bucket:
    _bucket_name: The ID of your GCS bucket
    _source_file_name: The path to the file to upload
    _destination_blob: The path to the file in GCS bucket
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(_bucket_name)
    destination_blob_name = _destination_blob
    blob = bucket.blob(destination_blob_name)

    generation_match_precondition = 0

    try:
        blob.upload_from_filename(
            _source_file_name, if_generation_match=generation_match_precondition)
    except Exception as e:
        print(f"Error when upload {_source_file_name} to bucket: {e}")
        return False

    print(f"File {_source_file_name} uploaded to bucket: {destination_blob_name}")
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
