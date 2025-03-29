from __future__ import absolute_import, unicode_literals
import os
import json

from cas_offinder.models import Job
from cas_offinder.generate_job import dump2class


def add_new_Job(
        UUID,
        job_title=None,
        email=None,
        job_finish=False,
        logs=None,
        job_data_dump=None,
        results_url=None,
        ):
    job_sql = Job(
        UUID          = UUID,
        job_title     = job_title,
        email         = email,
        job_finish    = job_finish,
        logs          = logs,
        job_data_dump = job_data_dump,
        results_url   = results_url,
    )
    job_sql.save()

def save_Job(
        UUID,
        job_title=None,
        email=None,
        job_finish=False,
        error=True,
        logs=None,
        job_data_dump=None,
        results_url = None,
        ):
    try:
        job_sql = Job.objects.get(UUID=UUID)
        job_sql.job_title     = job_title      if job_title     != None  else job_sql.job_title
        job_sql.email         = email          if email         != None  else job_sql.email
        job_sql.job_finish    = job_finish     if job_finish    != False else job_sql.job_finish
        job_sql.logs          = logs           if logs          != None  else job_sql.logs
        job_sql.error         = error          if error         != True  else job_sql.error
        job_sql.job_data_dump = job_data_dump  if job_data_dump != None  else job_sql.job_data_dump
        job_sql.results_url   = results_url    if results_url   != None  else job_sql.results_url

    except:
        job_sql = Job(
            UUID          = UUID,
            job_title     = job_title,
            email         = email,
            job_finish    = job_finish,
            logs          = logs,
            error         = error,
            job_data_dump = job_data_dump,
            results_url   = results_url,
        )

    job_sql.save() 

def update_Job_state(UUID, job_state=True, error=True,logs=None):
    try:
        job_sql = Job.objects.get(UUID=UUID)
        job_sql.job_finish = job_state
        job_sql.logs       = logs
        job_sql.error      = error
        job_sql.save()
        return True
    except:
        return False

def check_output_file(_job_data):
    text_file_path = _job_data.job_output_path()
    parquet_file_path = _job_data.job_parquet_path()
    if os.path.isfile(text_file_path) or os.path.isfile(parquet_file_path):
        return True
    else:
        return False

def find_Job_2_job_data(UUID):
    job_sql    = Job.objects.get(UUID = UUID)
    job_data_dump = job_sql.job_data_dump
    _job_data = dump2class(job_data_dump)
    return _job_data

def check_finish_Job(UUID):
    job_sql    = Job.objects.get(UUID = UUID)
    return job_sql.job_finish
    
    
#def dump_2_job_data(job_data_dump):
#    job_data_dict_json = json.loads(job_data_dict_acceptable)
#    _job_data = dump2class(job_data_dict_json)
#    return _job_data




