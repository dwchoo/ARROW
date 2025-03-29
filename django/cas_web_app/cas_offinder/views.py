from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, JsonResponse  # Import JsonResponse
from django.urls import reverse

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

#from cas_offinder.models import
import uuid
import sys
import os
from cas_offinder.tasks import *
from cas_offinder.generate_job import *
from cas_offinder.data_class import *
from cas_offinder.default_setting import *
from cas_offinder.management_job import *
from cas_offinder.processing_results import *
from cas_offinder.models import Job

# Create your views here.

#initial_settings = False
#ref_dir = '/root/gen_ref'
#job_data_path = './textfile'
#ref_list = None
#run_device = None

def update_initial_setting(request):
    request = set_initial_setting_session(request)
    #ref_dir       = request.session['ref_dir']
    #job_data_path = request.session['job_data_path']
    #ref_list      = request.session['ref_list']
    run_device    = request.session.get('run_device')
    job_data.job_data_default_setting()
    return request

def index(request):
    request = update_initial_setting(request)
    request = update_ref_list_session(request)
    ref_dir       = request.session.get('ref_dir')
    job_data_path = request.session.get('job_data_path')
    ref_list      = request.session.get('ref_list')
    run_device    = request.session.get('run_device')
    job_title = 'Job_'
    # Get the list of files in the upload directory
    upload_dir = settings.UPLOAD_DIR
    file_list = []
    if os.path.exists(upload_dir):
        file_list = os.listdir(upload_dir)

    context = {'job_title' : job_title, 'gen_ref_list' : ref_list, 'job_data_path':job_data.job_data_path, 'file_list': file_list}
    #context = {'job_title' : job_title, 'gen_ref_list' : ref_list, 'job_data_path':job_data.job_data_path}
    return render(request, 'cas_offinder/index.html', context)

def update_ref_list_session(request):
    ref_dir = request.session.get('ref_dir')
    request.session['ref_list'] = get_ref_list_dir(ref_dir)
    return request


def delete_file(request):
    if request.method == 'POST':
        file_path = request.POST.get('file_path')
        if file_path:
            try:
                os.remove(file_path)
                request = update_ref_list_session(request)
                return JsonResponse({'success': True})
            except FileNotFoundError:
                return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
            except OSError as e: # Add OSError
                return JsonResponse({'success': False, 'error': f'OS Error: {str(e)}'}, status=500)
            except Exception as e:
                return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
        else:
            return JsonResponse({'success': False, 'error': 'File path not provided'}, status=400)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def upload_file(request):
    if request.method == 'POST' and request.FILES['reference_file']:
        reference_file = request.FILES['reference_file']
        upload_dir = settings.UPLOAD_DIR
        os.makedirs(upload_dir, exist_ok=True)  # Create the directory if it doesn't exist
        file_path = os.path.join(upload_dir, reference_file.name)

        try:
            with open(file_path, 'wb+') as destination:
                for chunk in reference_file.chunks():
                    destination.write(chunk)
            request = update_ref_list_session(request)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'An unexpected error occurred: {str(e)}'}, status=500)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

def progress(request):
    request = update_initial_setting(request)
    ref_dir       = request.session.get('ref_dir')
    job_data_path = request.session.get('job_data_path')
    ref_list      = request.session.get('ref_list')
    run_device    = request.session.get('run_device')
    _ref_initial = request.POST['gen_ref_select']
    _ref_data = find_ref(_ref_initial, ref_list)
    _uuid = uuid.uuid1().hex + uuid.uuid4().hex

    data = job_data()
    #   ref_file_path   = _ref_data.path,
    #   job_data_path   = job_data_path,
    #   run_device      = run_device,
    data.UUID = _uuid
    data.results_url   = f"http://{request.META['HTTP_HOST']}/{_uuid}/results/"
    data.job_title  = request.POST['job_title']
    data.seq        = request.POST['query_seq']
    data.ref        = _ref_data['initial']
    data.ref_file_path = _ref_data['path']
    data.PAM_type   = request.POST['PAM']
    #data.mismatch   = request.POST['mismatch_num']
    data.mismatch   = 6
    data.email      = request.POST['email']
    #data._tmp_delay_time = int(request.POST['delay_time'])  #not need

    data_string = f'Sequence : {data.seq}   Reference : {data.ref}'
    
    data_dump = class2dump(data)
    run_cas_offinder.delay(data_dump, run_device)
    
    context = {'input_info' : data, }
    return render(request, 'cas_offinder/progress.html', context)

def check_job_exists(job_uuid):
    """
    Checks if a job exists in the database and if its folder exists.
    Returns True if both exist, False otherwise.
    """
    try:
        job = Job.objects.get(UUID=job_uuid)
        job_folder_path = os.path.join(settings.JOB_DATA_PATH, str(job_uuid))
        return os.path.exists(job_folder_path)
    except ObjectDoesNotExist:
        return False

def job_page(request, UUID):
    request = update_initial_setting(request)
    if not check_job_exists(UUID):
        return render(request, 'cas_offinder/job_not_found.html')
    if check_finish_Job(UUID) == True: return results(request, UUID)
    _job_data = find_Job_2_job_data(UUID)
    context = {'uuid' : UUID, 'job_data' : _job_data}
    return render(request, 'cas_offinder/job_page.html',context)


def results(request, UUID):
    request = update_initial_setting(request)
    if not check_job_exists(UUID):
        return render(request, 'cas_offinder/job_not_found.html')
    ref_dir       = request.session.get('ref_dir')
    job_data_path = request.session.get('job_data_path')
    ref_list      = request.session.get('ref_list')
    run_device    = request.session.get('run_device')
    if check_finish_Job(UUID) == False: return job_page(request, UUID)
    _job_data = find_Job_2_job_data(UUID)

    _results = visualization_data(_job_data)
    results_cas_offinder_heatmap = _results.plotly_heatmap()
    #results_one_mismatch_heatmap = _results.plotly_one_mismatch()
    results_one_mismatch_heatmap = _results.plot_one_mismatch_heatmap()
    #results_one_mismatch_rank_data_list = _results.one_mismatch_rank_web_table(max_num=20)
    results_mismatch_score_dist = _results.plot_mismatch_score_dist()
    results_total_mismatch_rank_data_list, \
    results_one_mismatch_rank_data_list, \
    results_double_mismatch_rank_data_list \
        = _results.double_mismatch_rank_web_table(max_num=20)
    mismatch_table = _results.mismatch_table().to_html(
        index=False,
        classes=["table-bordered","table-striped","table-hover","mismatch_table"],
        table_id="mismatchTable"
    )

    context = {
        'job_data' : _job_data,
        'cas_offinder_heatmap' : results_cas_offinder_heatmap,
        'one_mismatch_heatmap' : results_one_mismatch_heatmap,
        'plot_mismatch_score_dist' : results_mismatch_score_dist,
        'one_mismatch_rank_data_list' : results_one_mismatch_rank_data_list,
        'double_mismatch_rank_data_list' : results_double_mismatch_rank_data_list,
        'total_mismatch_rank_data_list' : results_total_mismatch_rank_data_list,
        'mismatch_table' : mismatch_table,
    }
    return render(request, 'cas_offinder/results.html', context)

# mispaired gRNA page
def gRNA_detail_table_page(request, UUID, rank):
    _job_data = find_Job_2_job_data(UUID)
    _results = visualization_data(_job_data)
    _results_table = _results.return_MP_gRNA_detail_table(request,rank)
    return HttpResponse(_results_table.as_html(request))

def MP_gRNA_page(request, UUID, rank):
    if rank > 10:
        return HttpResponseNotFound("Rank is provided up to 10.")
    _job_data = find_Job_2_job_data(UUID)
    seq_length = len(_job_data.seq)
    _results = visualization_data(_job_data)
    data_frame_comp, MP_gRNA = _results.return_rank_MP_gRNA_detail_df(rank)
    data_frame_decomp = _results.return_df_for_csv_download(data_frame_comp,MP_gRNA)
    gRNA_dist_heatmap = _results.MP_gRNA_dist_plotly_heatmap(data_frame_comp,MP_gRNA)
    mismatch_table = _results.return_MP_gRNA_mismatch_table(data_frame_comp).to_html(
        index=False,
        classes=["table-bordered","table-striped","table-hover","mismatch_table"],
        table_id="mismatchTable"
    )
    context = {
        'rank' : rank,
        'uuid' : UUID,
        'job_data' : _job_data,
        'mp_gRNA'  : MP_gRNA[:seq_length],
        'cas_offinder_heatmap' : gRNA_dist_heatmap,
        'mismatch_table' : mismatch_table,
        'dataframe' : data_frame_decomp,
    }
    return render(request, 'cas_offinder/mp_gRNA.html', context)


def data_table_page(request, UUID):
    _job_data = find_Job_2_job_data(UUID)
    _results = visualization_data(_job_data)
    _results_table = _results.detail_df_table(request)
    return HttpResponse(_results_table.as_html(request))

class download_csv:
    def __download_csv_link(self, request,dataframe,file_name,index=False):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f"attachment; filename={file_name}.csv"
        dataframe.to_csv(path_or_buf=response, sep=',',index=index)
        return response

    @classmethod
    def detail_csv(cls, request, UUID):
        _job_data = find_Job_2_job_data(UUID)
        _job_name = _job_data.job_title
        file_name = f'{_job_name}_detail'
        _results = visualization_data(_job_data)
        dataframe = _results.return_df_for_csv()
        return cls.__download_csv_link(cls,request,dataframe,file_name,True)

    @classmethod
    def one_mismatch_csv(cls, request, UUID):
        _job_data = find_Job_2_job_data(UUID)
        _job_name = _job_data.job_title
        file_name = f'{_job_name}_OneMismatchRank'
        _results = visualization_data(_job_data)
        dataframe_total, dataframe_one, dataframe_double = _results.double_mismatch_rank_df()
        dataframe = dataframe_one
        return cls.__download_csv_link(cls,request,dataframe,file_name,False)

    @classmethod
    def double_mismatch_csv(cls, request, UUID):
        _job_data = find_Job_2_job_data(UUID)
        _job_name = _job_data.job_title
        file_name = f'{_job_name}_DoubleMismatchRank'
        _results = visualization_data(_job_data)
        dataframe_total, dataframe_one, dataframe_double = _results.double_mismatch_rank_df()
        dataframe = dataframe_double
        return cls.__download_csv_link(cls,request,dataframe,file_name,False)

    @classmethod
    def total_mismatch_csv(cls, request, UUID):
        _job_data = find_Job_2_job_data(UUID)
        _job_name = _job_data.job_title
        file_name = f'{_job_name}_TotalMismatchRank'
        _results = visualization_data(_job_data)
        dataframe_total, dataframe_one, dataframe_double = _results.double_mismatch_rank_df()
        dataframe = dataframe_total
        return cls.__download_csv_link(cls,request,dataframe,file_name,False)

    @classmethod
    def mp_gRNA_csv(cls,request, UUID, rank):
        _job_data = find_Job_2_job_data(UUID)
        file_name = f'{_job_data.job_title}_mispaired_gRNA_{rank}'
        _results = visualization_data(_job_data)
        data_frame_comp, MP_gRNA = _results.return_rank_MP_gRNA_detail_df(rank)
        dataframe = _results.return_df_for_csv_download(data_frame_comp,MP_gRNA)
        return cls.__download_csv_link(cls,request,dataframe,file_name,False)


#def download_detail_csv_link(request, UUID):
#    _job_data = find_Job_2_job_data(UUID)
#    file_name = _job_data.job_title
#    _results = visualization_data(_job_data)
#    dataframe = _results.return_df_for_csv()
#
#    response = HttpResponse(content_type='text/csv')
#    response['Content-Disposition'] = f"attachment; filename={file_name}_detail.csv"
#
#    dataframe.to_csv(path_or_buf=response, sep=',',index=True)
#    return response
#
#
#def download_MisRank_csv_link(request, UUID):
#    _job_data = find_Job_2_job_data(UUID)
#    file_name = _job_data.job_title
#    _results = visualization_data(_job_data)
#    #dataframe = _results.return_one_mismatch_rank_dataframe()
#    dataframe_total, dataframe_one = _results.double_mismatch_rank_df()
#
#    dataframe = dataframe_total
#
#    response = HttpResponse(content_type='text/csv')
#    response['Content-Disposition'] = f"attachment; filename={file_name}_OneMisRank.csv"
#
#    #dataframe.to_csv(path_or_buf=response, sep=',',index=False)
#    dataframe.to_csv(path_or_buf=response, sep=',',index=False)
#    return response

