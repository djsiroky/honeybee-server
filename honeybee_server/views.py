import os
import json

from flask import render_template, redirect, request, url_for, abort, flash
from flask import render_template, request
from flask.json import jsonify
from werkzeug.utils import secure_filename
from bson import json_util
from bson.objectid import ObjectId

from .utils import new_uuid, unzip_file, respond, JSONEncoder
from .logger import log
from .job import Job
from . import flask_app, mongo


# @flask_app.route('/<path:path>')
@flask_app.route('/', defaults={'path': ''})
def catch_all(path):
    return render_template("index.html")


@flask_app.route('/api/jobs', methods=['GET'])
def get_all_jobs():
    jobs = [doc for doc in mongo.db.jobs.find({})]
    [j.pop('_id') for j in jobs]
    [j.pop('data', None) for j in jobs]
    return respond(200, jobs)


@flask_app.route('/api/job/<string:job_id>', methods=['GET'])
def get_one_job(job_id):
    m_job = mongo.db.jobs.find_one({"job_id": job_id})
    m_job.pop('_id')
    if m_job.get('data'):
        m_job['data'] = json.loads(m_job['data'])
    return respond(200, m_job)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in flask_app.config['ALLOWED_EXTENSIONS']

# create a job
@flask_app.route('/job/create', methods=['POST'])
def create_job():
    job_id = new_uuid()
    log.debug('Job Received: {}'.format(job_id))

    file = request.files.get('file', None)
    if not file:
        return respond(400, 'No file sent with request')

    if not allowed_file(file.filename):
        return respond(400, 'Invalid file type: {}'.format(filename))

    log.debug('Creating Mongo Entry')
    new_job = mongo.db.jobs.insert_one({
        "job_id": job_id,
        "created_by": "webuser",
        "status": 0,
        "tasks": []
    })
    log.debug('Mongo Entry Created')

    jobs_folder = flask_app.config['JOBS_FOLDER']
    filename = secure_filename(file.filename)
    file_ext = filename.split('.')[-1]
    folder_path = os.path.join(jobs_folder, job_id)
    os.mkdir(folder_path)

    job_filepath = os.path.join(folder_path, 'job.{}'.format(file_ext))
    file.save(job_filepath)

    # job
    job = Job(job_filepath, job_id)
    results = job.run()
    # TODO: create a new record in the DB with UUID

    # return respond(201, job_id)
    return respond(201, results)


# get job data or delete a job
@flask_app.route('/job/<uuid:job_id>', methods=['GET', 'DELETE'])
def job(job_id):
    if request.method == 'DELETE':
        # logic to halt radiance running this job and delete it from server
        return respond(201, job_id)

    if request.method == 'GET':
        # log to send back completed job data
        return respond(200, 'data here')


# get a job's status
@flask_app.route('/jobs/')
def jobs():
    return jsonify(os.listdir('jobs'))

# get a job's status
@flask_app.route('/job/<string:job_id>/status')
def job_status(job_id):
    jobs_path = os.path.join(flask_app.config['JOBS_FOLDER'])
    if job_id not in os.listdir(jobs_path):
        return respond(404, 'not found')
    else:
        job_path = os.path.join(jobs_path, job_id)
        return respond(200, os.listdir(job_path))

    # return jsonify(
    #     # placeholder info for Mingbo
    #     {
    #         "JobId": str(job_id),
    #         "Simulations": [
    #             {
    #                 "childId": "pkkrjle",
    #                 "Status": "running",
    #                 "isDone": False
    #             },
    #             {
    #                 "childId": "udfgdfe",
    #                 "Status": "done",
    #                 "isDone": True
    #             },

    #         ]
    #     })


# get a task's data
@flask_app.route('/job/<uuid:job_id>/<taskId>')
def get_task(taskId):
    # logic to send back task data
    return taskId


# delete a task
@flask_app.route('/job/<uuid:job_id>/<taskId>', methods=['DELETE'])
def delete_task(taskId):
    # logic to halt radiance running this task
    return taskId + " has been deleted"


@flask_app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@flask_app.route('/job/create', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # flash('No file part')
            # return redirect(request.url)
            return 'No file sent with request'
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], filename))
            return str(filename) + " uploaded."
    return


@flask_app.route('/design/<string:job_id>')
def dd_status(job_id):

    jobs = [doc for doc in mongo.db.jobs.find({})]
    response =  {
                 "JobID": job_id,
                 "Simulations": []
                }
    for job in jobs:
        job = {
                "ChildID": new_uuid(),
                "Status": bool(job['status']),
              }
        response['Simulations'].append(job)

    return respond(200, response)
