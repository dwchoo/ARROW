from __future__ import absolute_import, unicode_literals
import subprocess
import os
import random
from pathlib import Path
from fnmatch import fnmatch
import json

from cas_offinder.data_class import *
    
def cas_offinder_input_txt(ref, PAM_type='NGG',seq='AAAAA', mismatch=3, ref_file_path='/root/gen_ref/hg38.fa'):
    ref_file_path=ref_file_path
    search_type = 'N'*len(seq)+PAM_type
    search_seq = seq + PAM_type
    contexts = \
f"""{ref_file_path}
{search_type}
{search_seq} {mismatch}
"""
    return contexts


def make_input_file(_job_data, input_file_path):
    file_path=input_file_path
    contexts = cas_offinder_input_txt(
        ref      = _job_data.ref,
        PAM_type = _job_data.PAM_type,
        seq      = _job_data.seq,
        mismatch = _job_data.mismatch,
        ref_file_path = _job_data.ref_file_path,
    )
    with open(file_path, 'w') as f:
        f.write(contexts)
    
def make_command_file(command_file_path, input_file_path, output_file_path, run_device):
    contexts = \
f"""#!/bin/bash
command=`cas-offinder {input_file_path} {run_device} {output_file_path}`
echo $command
"""
    with open(command_file_path, 'w') as f:
        f.write(contexts)
    


def make_job_files(_job_data):
    command_file_path = _job_data.job_command_path()
    input_file_path   = _job_data.job_input_path()
    output_file_path  = _job_data.job_output_path()

    input_file_command = f'$(dirname "$0")/{_job_data.job_title}_input.txt'
    output_file_command = f'$(dirname "$0")/{_job_data.job_title}_output.txt'
    run_device = _job_data.run_device

    # mkdir
    Path(_job_data.job_data_script_path()).mkdir(parents=True, exist_ok=True)

    make_input_file(_job_data=_job_data, input_file_path= input_file_path)
    make_command_file(
        command_file_path   = command_file_path,
        input_file_path     = input_file_command,
        output_file_path    = output_file_command,
        run_device          = run_device,
    )



def run_bash_file(run_command_file_path):
    bash_command = ["bash", run_command_file_path]
    run = subprocess.Popen(
        bash_command,
        stdin   = subprocess.PIPE,
        stdout  = subprocess.PIPE,
        stderr  = subprocess.PIPE,
        text    = True,
    )
    output, log = run.communicate()
    run_finish = True if run.poll() == 0 else False
    return output, log, run_finish

def class2dump(_job_data):
    return json.dumps(_job_data.__dict__)

def dump2class(job_data_dump, run_device=None):
    job_data.job_data_default_setting()
    _job_data = job_data()
    job_data_dict = json.loads(job_data_dump)
    dict_keys = list(job_data_dict.keys())
    dict_values = list(job_data_dict.values())
    for key, value in zip(dict_keys, dict_values):
        setattr(_job_data, key, value)
    return _job_data



