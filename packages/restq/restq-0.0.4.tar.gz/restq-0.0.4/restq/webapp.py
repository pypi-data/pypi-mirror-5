from __future__ import print_function
import sys
import traceback
import json
import inspect
import functools
if sys.version_info[0] < 3:
    import httplib as client
else: 
    from http import client

import sys
from getopt import getopt

import bottle
from bottle import request
bottle.BaseRequest.MEMFILE_MAX = 1600000000

from restq import realms 
from restq import config


class JSONError(bottle.HTTPResponse):
    def __init__(self, status, message='', exception='Exception'):
        if inspect.isclass(exception) and issubclass(exception, Exception):
            exception = exception.__name__
        elif isinstance(exception, Exception):
            exception = exception.__class__.__name__
        elif not type(exception) in [str, unicode]:
            raise Exception("unknown exception type %s" % type(exception))
        body = json.dumps({'error': status,
                            'exception': exception,
                            'message': message})
        bottle.HTTPResponse.__init__(self, status=status, 
                header={'content-type':'application/json'}, body=body)


def wrap_json_error(f):
    @functools.wraps(f)
    def wrapper(*a, **k):
        try:
            return f(*a, **k)
        except JSONError:
            raise 
        except Exception as exc:
            raise JSONError(client.INTERNAL_SERVER_ERROR,
                    exception=exc,
                    message=traceback.format_exc())
    return wrapper


@bottle.delete('/<realm_id>/job/<job_id>')
@wrap_json_error
def remove_job(realm_id, job_id):
    """Remove a job from a realm"""
    realm = realms.get(realm_id)
    realm.remove_job(job_id)
    return {}


@bottle.delete('/<realm_id>/tag/<tag_id>')
@wrap_json_error
def remove_tagged_jobs(realm_id, tag_id):
    """Remove a tag and all of its jobs from a realm"""
    realm = realms.get(realm_id)
    realm.remove_tagged_jobs(tag_id)
    return {}


@bottle.put('/<realm_id>/job/<job_id>')
@wrap_json_error
def add(realm_id, job_id):
    """Put a job into a queue
    JSON requires:  
        queue_id   -  
    Optional fields:
        data - input type='file' - data returned on GET job request
             - Max size data is JOB_DATA_MAX_SIZE
    """
    #validate input
    try:
        body = json.loads(request.body.read())
        try:
            tags = body.get('tags', [])
            queue_id = body['queue_id']
            data = body.get('data', None)
            realm = realms.get(realm_id)
            realm.add(job_id, queue_id, data, tags=tags)
        except KeyError:
            raise JSONError(client.BAD_REQUEST,
                            exception='KeyError',
                            message='Require queue_id & data')
    except ValueError:
        raise JSONError(client.BAD_REQUEST,
                        exception='ValueError',
                        message='Require json object in request body')
    return {}


@bottle.post('/<realm_id>/job')
@wrap_json_error
def post_multiple_jobs(realm_id):
    """Multiple job post

    body contains jobs=[job, job, job, ...]
            where job={job_id, queue_id, data=None, tags=[]}

    """
    #validate input
    try:
        body = json.loads(request.body.read())
        try:
            jobs = body['jobs']
            realm = realms.get(realm_id)
            for job in jobs:
                job_id = job['job_id']
                queue_id = job['queue_id']
                data = job.get('data', None)
                tags = job.get('tags', [])
                realm.add(job_id, queue_id, data, tags=tags)
        except KeyError:
            raise JSONError(client.BAD_REQUEST,
                            exception='KeyError',
                            message='Require queue_id & data')
    except ValueError:
        raise JSONError(client.BAD_REQUEST,
                        exception='ValueError',
                        message='Require json object in request body')
    return {}


@bottle.get('/<realm_id>/job/<job_id>')
@wrap_json_error
def get_job(realm_id, job_id):
    """Get the status of a job"""
    realm = realms.get(realm_id)
    job = realm.get_job(job_id)
    return job


@bottle.get('/<realm_id>/tag/<tag_id>')
@wrap_json_error
def get_tagged_jobs(realm_id, tag_id):
    """return a dict of all jobs tagged by tag_id"""
    realm = realms.get(realm_id)
    jobs = realm.get_tagged_jobs(tag_id)
    return jobs


@bottle.get('/<realm_id>/tag/<tag_id>/status')
@wrap_json_error
def get_tag_status(realm_id, tag_id):
    """return an int of the number of jobs related to tag_id"""
    realm = realms.get(realm_id)
    status = realm.get_tag_status(tag_id)
    return status


@bottle.get('/<realm_id>/job')
@wrap_json_error
def pull(realm_id):
    """pull the next set of jobs from the realm"""
    realm = realms.get(realm_id)
    count = request.GET.get('count', default=1, type=int)
    job = realm.pull(count=count)
    return job


# Get the status of the realm
@bottle.get('/<realm_id>/status')
@wrap_json_error
def get_realm_status(realm_id):
    """return the status of a realm"""
    realm = realms.get(realm_id)
    status = realm.status
    return status


@bottle.post('/<realm_id>/config')
@wrap_json_error
def update_realm_config(realm_id):
    """update the configuration of a realm"""
    realm = realms.get(realm_id)
    try:
        body = json.loads(request.body.read(4096))
    except Exception as exc:
        raise JSONError(client.BAD_REQUEST,
                        exception=exc,
                        message='Require JSON in request body')

    lease_time = body.get('default_lease_time', None)
    if lease_time is not None:
        if type(lease_time) not in (long, int):
            raise JSONError(client.BAD_REQUEST,
                    exception='TypeError',
                    message="default_lease_time not int")
        realm.set_default_lease_time(lease_time)
    
    queue_lease_time = queue_lease_time = body.get('queue_lease_time', None)
    if queue_lease_time is not None:
        try:
            queue_id, lease_time = queue_lease_time 
        except (ValueError, TypeError) as err:
            raise JSONError(client.BAD_REQUEST,
                    exception='ValueError',
                    message='queue_lease_time err - %s' % err)
        if type(lease_time) not in (long, int):
            raise JSONError(client.BAD_REQUEST,
                    exception='TypeError',
                    message="default_lease_time not int")
        realm.set_queue_lease_time(queue_id, lease_time)
    return {}


@bottle.delete('/<realm_id>/')
@wrap_json_error
def delete_realm(realm_id):
    realms.delete(realm_id)
    return {}


# Get the status from all of the realms
@bottle.get('/')
@wrap_json_error
def realms_status():
    """return all of the realms and their statuses""" 
    return realms.get_status()


app = bottle.default_app()
def run():
    global proxy_requests
    bottle_kwargs = dict(debug=config.webapp['debug'],
                         quiet=config.webapp['quiet'],
                         host=config.webapp['host'],
                         port=config.webapp['port'],
                         server=config.webapp['server'])
    bottle.run(app=app, **bottle_kwargs)

