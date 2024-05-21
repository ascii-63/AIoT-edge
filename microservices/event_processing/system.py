import sys
import os
from datetime import datetime, timedelta


def searchFileInDirectory(_directory: str, _file_name: str):
    """
    Search for a file in a directory.

    Parameters:
    - _directory: The directory to search in.
    - _file_name: The name of the file to search for.

    Returns:
    - True if the file is found, False otherwise.
    """
    # Get the list of files in the directory
    try:
        files_in_directory = os.listdir(_directory)
    except Exception as e:
        print(f"Some error: {e}")
        return False

    # Check if the file is in the list
    if _file_name in files_in_directory:
        return True
    else:
        return False


def convertUTC0ToUTC7(timestamp):
    """Convert ts str from UTC+0 to UTC+7"""

    dt_utc0 = datetime.strptime(timestamp[:-1], '%Y-%m-%dT%H:%M:%S.%f')

    utc0 = timedelta(hours=0)
    utc7 = timedelta(hours=7)
    dt_utc7 = dt_utc0 + (utc7 - utc0)

    timestamp_utc7 = dt_utc7.strftime('%Y-%m-%dT%H:%M:%S.%f')
    final_timestamp = timestamp_utc7[0:-3]

    return final_timestamp
