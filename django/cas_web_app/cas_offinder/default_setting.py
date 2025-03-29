from __future__ import absolute_import, unicode_literals
import subprocess
import os
import random
from pathlib import Path
from fnmatch import fnmatch

from django.conf import settings

#from cas_offinder.data_class import ref_data
    
def check_opencl_device():
    cas_offinder_command = subprocess.Popen(
        ["cas-offinder"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    output, log = cas_offinder_command.communicate()
    avail_device_log = output[output.find("Available device list:"):]
    avail_cpu = True if avail_device_log.find('CPU') != -1 else False
    avail_gpu = True if avail_device_log.find('GPU') != -1 else False
    if avail_gpu:
        return 'G'
    elif avail_cpu:
        return 'C'
    else:
        return False

def get_ref_list_dir(root_dir):
    find_root = root_dir
    pattern = "*.fa"
    ref_list = []

    for path, subdirs, files in os.walk(find_root):
        for name in files:
            if fnmatch(name, pattern):
                file_path = f"{path}/{name}"
                #_ref_data = ref_data(name,file_path)
                _ref_data = {'initial' : name, 'path' : file_path}
                ref_list.append(_ref_data)

    return ref_list

def find_ref(initial, ref_list):
    for _ref_data in ref_list:
        if _ref_data['initial'] == initial:
            return _ref_data
    return None

def set_initial_setting(ref_dir, run_device, check_device=True):
    if run_device == None and check_device == True:
        run_device = check_opencl_device()
    assert run_device == 'G' or run_device == 'C', f"Check opencl device, {run_device}"
    ref_list = get_ref_list_dir(ref_dir)
    return ref_list,  run_device

def set_initial_setting_session(request):
    if request.session.get('initial_set') is None:
        request.session['ref_dir']       = settings.REF_DIR
        request.session['job_data_path'] = settings.JOB_DATA_PATH
        request.session['ref_list']      = get_ref_list_dir(request.session.get('ref_dir'))
        request.session['run_device']    = check_opencl_device()
        request.session['initial_set']   = True
        return request
    else:
        return request

