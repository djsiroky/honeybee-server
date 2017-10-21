import os
from flask import render_template, redirect, request, url_for
from werkzeug.utils import secure_filename

from . import flask_app
from .utils import new_uuid

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in flask_app.config['ALLOWED_EXTENSIONS']

@flask_app.route('/job/create', methods=['POST'])
def upload_file():
    if request.method == 'POST':

        jobId = new_uuid()

        file = request.files.get('file', None)
        if not file:
            return 'No file sent with request'

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.mkdir(os.path.join(flask_app.config['UPLOAD_FOLDER'], jobId))
            file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], jobId, filename))
            return str(filename) + " uploaded. jobId is " +jobId
        # create a new record in the DB with UUID
    return
def new_job():
    return 'Hello World'
    return render_template('index.html')
