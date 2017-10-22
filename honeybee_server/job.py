from .logger import log
from celery.utils.log import get_task_logger

from . import celery


@celery.task()
def process_job(filepath):
    task_log = get_task_logger(__name__)
    print('Started')
    task_log.debug('Job START: {}'.format(filepath))
    import time
    time.sleep(10)
    task_log.debug('Job END: {}'.format(filepath))
    print('Ended')


class Job():

    def __init__(self, job_filepath):
        self.job_filepath = job_filepath

    def run(self):
        process_job.delay(self.job_filepath)

