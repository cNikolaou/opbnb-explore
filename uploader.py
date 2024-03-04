import os
import logging
from queue import Queue
from threading import Thread

from utils import to_relative_path
from upload import upload_file


logger = logging.getLogger("UploadHander")


class UploadHandler:
    """
    Handle mutliple threads for uploading files to a storage bucket. The paths
    of where the files are locates are in the `file_path_queue`.
    """

    def __init__(self, file_path_queue: Queue, max_workers: int = 1):

        self.file_path_queue = file_path_queue

        # thread management variables
        self.max_workers = max_workers
        self.worker_threads = []

        # to get the relative paths
        self._cwd = os.getcwd()

    def upload(self):
        """
        Task that worker threads run.
        """
        while True:
            file_path = self.file_path_queue.get()

            if file_path is None:
                self.file_path_queue.task_done()
                break

            relative_path = to_relative_path(file_path, self._cwd)

            if upload_file(relative_path.as_posix()):
                logger.info(f"Uploaded file: {relative_path}")
            else:
                logger.error(f"Error uploading file: {relative_path}")
            self.file_path_queue.task_done()

    def start(self):
        for _ in range(self.max_workers):
            thread = Thread(target=self.upload)
            thread.start()
            self.worker_threads.append(thread)

    def stop(self):
        """
        Stop all threads.
        """
        for _ in range(self.max_workers):
            self.file_path_queue.put(None)

        for thread in self.worker_threads:
            thread.join()

    def wait_for_uploads(self):
        """
        Wait for all the files from the queue to be uploaded.
        """
        self.file_path_queue.join()
