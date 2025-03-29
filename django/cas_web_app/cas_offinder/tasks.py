from __future__ import absolute_import, unicode_literals
import random
from celery import shared_task
import os
from pathlib import Path

from django.conf import settings
import subprocess

import time
from datetime import datetime
from cas_offinder.data_class import *
from cas_offinder.generate_job import *
from cas_offinder.management_job import *
from cas_offinder.raw_text_format import *
from cas_offinder.email_command import send_email
from cas_offinder.processing_results import visualization_data

@shared_task(name="make_tsxtfile_wait")
def mk_file_wait(title, contexts=None, UUID=None, wait_time=5):
    file_path = f'{settings.JOB_DATA_PATH}/{UUID}/{title}.txt'
    dir_path = os.path.dirname(file_path)

    # mkdir
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    time_stamp_start = datetime.fromtimestamp(time.time())
    time.sleep(wait_time)
    time_stamp_end = datetime.fromtimestamp(time.time())

    _contexts = \
f"""task    : {title}
start time      : {time_stamp_start}
end time        : {time_stamp_end}
<contexts>
{contexts}
"""
    with open(file_path, 'w') as f:
        f.write(_contexts)
        return f'Finish {title}     job_time : {time_stamp_start}'


@shared_task(name="Cas_offinder_run")
def run_cas_offinder(job_data_dump, run_device):
    _job_data = dump2class(job_data_dump, run_device)
    _job_data.start_time = datetime.fromtimestamp(time.time())

    assert isinstance(_job_data, job_data), f"check type {type(_job_data)}"

    add_new_Job(
        UUID          = _job_data.UUID,
        job_title     = _job_data.job_title,
        email         = _job_data.email,
        job_finish    = False,
        logs          = None,
        job_data_dump = job_data_dump,
        results_url    = _job_data.results_url
    )

    make_job_files(_job_data)
    output, log, run_finish = run_bash_file(_job_data.job_command_path())

    _job_data.end_time = datetime.fromtimestamp(time.time())

    return_content =  return_job_log_celery_format(
        title   = _job_data.job_title,
        start_time = _job_data.start_time,
        end_time   = _job_data.end_time,
        logs       = f"{output}\n{log}",
        _job_data  = _job_data,
        )


    try:
        # generate_parquet_pickle_file
        __vis_data_gen_pckl = visualization_data(_job_data) 
        __vis_data_gen_pckl.generate_data()
        del __vis_data_gen_pckl
    finally:


        updated_Job = update_Job_state(
            UUID      = _job_data.UUID,
            job_state = True,
            error     = check_output_file(_job_data),
            logs      = return_content,
        )
        assert updated_Job == True, f"Job is not updated check UUID: {_job_data.UUID}"

        if _job_data.email != None: send_email(_job_data.email, _job_data)


        return return_content




def celery_test():
    for i in range(5):
        title = f'Task{i}'
        _ = mk_file_wait.delay(title, None, i)
    return "Finish"



