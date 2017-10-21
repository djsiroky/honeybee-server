import os
import uuid
import zipfile
from flask.json import jsonify
from celery import Celery


from . import flask_app

def make_celery(app):
    # create context tasks in celery
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

def new_uuid():
    return str(uuid.uuid4())

def unzip_file(filepath):
    filename = os.path.basename(filepath)
    folder_name = filename.split('.')[0]

    job_folderpath = os.path.dirname(filepath)
    folder_path = os.path.join(job_folderpath, folder_name)
    with zipfile.ZipFile(filepath,"r") as zip_ref:
        zip_ref.extractall(folder_path)

def respond(code, message):
    response = jsonify({'message': message})
    response.status_code = code
    return response
