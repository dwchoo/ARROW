from __future__ import absolute_import, unicode_literals


def return_job_log_celery_format(title, start_time, end_time, logs, _job_data=None):
    if _job_data != None:
        job_info = return_job_data_info(_job_data)
    else:
        job_info = None

    content = \
f"""{job_info}

Job name : {title}
job start_time : {start_time}
===================================================
job_output : {logs}

===================================================
job end_time : {end_time}
"""
    return content

def return_job_data_info(_job_data):
    content = \
f"""Job name  : {_job_data.job_title}
Job seq       : {_job_data.seq}
Job PAM       : {_job_data.PAM_type}
Job ref       : {_job_data.ref}
Job mismatch  : {_job_data.mismatch}
Running device: {_job_data.run_device}
"""
    return content

def return_email_content(_job_data):
    content = \
f"""{_job_data.job_title} finished!
Job seq             : {_job_data.seq}
Job PAM             : {_job_data.PAM_type}
Job ref             : {_job_data.ref}
Job mismatch        : {_job_data.mismatch}
Job finished time   : {_job_data.end_time}
Job link            : {_job_data.results_url}
"""
    return content
