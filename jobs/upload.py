import os
import logging
from threading import Thread
from functools import wraps
from queue import Queue

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

import settings
from .utils import to_relative_path


logger = logging.getLogger(__name__)


def check_storage_settings(func):
    """
    Check whether the storage credentials are defined before trying to upload
    a file.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        if settings.STORAGE_ENDPOINT is None:
            logger.error("STORAGE_ENDPOINT is not defined")

        if settings.STORAGE_ACCESS_KEY is None:
            logger.error("STORAGE_ACCESS_KEY is not defined")

        if settings.STORAGE_ACCESS_SECRET is None:
            logger.error("STORAGE_ACCESS_SECRET is not defined")

        if settings.STORAGE_BUCKET_NAME is None:
            logger.error("STORAGE_BUCKET_NAME is not defined")

        return func(*args, **kwargs)

    return wrapper


def get_bucket():
    """
    Returns the bucket based on the credentialls from the settings.
    """

    # connect to remote storage and get the bucket
    storage = boto3.resource(
        service_name="s3",
        endpoint_url=settings.STORAGE_ENDPOINT,
        aws_access_key_id=settings.STORAGE_ACCESS_KEY,
        aws_secret_access_key=settings.STORAGE_ACCESS_SECRET,
        config=Config(signature_version="s3v4"),
    )

    return storage.Bucket(settings.STORAGE_BUCKET_NAME)


@check_storage_settings
def get_files():
    """
    Get list of files in the storage bucket.
    """

    try:
        bucket = get_bucket()

        for obj in bucket.objects.all():
            url = "%s/%s/%s" % (
                settings.STORAGE_ENDPOINT,
                settings.STORAGE_BUCKET_NAME,
                obj.key,
            )
            print(url)

    except ClientError as e:
        logger.error(e)


@check_storage_settings
def upload_file(file_name: str):
    """
    Upload a file to the storage bucket.
    """
    try:
        bucket = get_bucket()
        bucket.upload_file(file_name, file_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True


def upload_worker(file_path_queue: Queue):
    while True:
        logger.info("GETTING FILE")
        file_path = file_path_queue.get()
        logger.info(f"GOT IT {file_path}")
        relative_path = to_relative_path(file_path, os.getcwd())
        if upload_file(relative_path.as_posix()):
            logger.info(f"Uploaded file: {relative_path}")
        else:
            logger.error(f"Error uploading file: {relative_path}")
        file_path_queue.task_done()


def set_uploader(file_path_queue: Queue):
    uploader = Thread(target=upload_worker, args=(file_path_queue,))
    return uploader
