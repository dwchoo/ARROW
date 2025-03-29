from django.urls import path, include
from cas_offinder import views

app_name = 'cas_offinder'
urlpatterns = [
    path('',views.index, name='index'),
    path('upload/', views.upload_file, name='upload_file'),
    path('delete/', views.delete_file, name='delete_file'),
    path('progress/', views.progress, name='progress'),
    path('<str:UUID>/job_page/', views.job_page, name='job_page'),
    path('<str:UUID>/results/', views.results, name='results_page'),
    path('<str:UUID>/results/<int:rank>', views.MP_gRNA_page, name='MP_gRNA_page'),
    path('<str:UUID>/results/<int:rank>/table', views.gRNA_detail_table_page, name='gRNA_detail_page'),
    path('<str:UUID>/results/<int:rank>/table/down_detail_csv', views.download_csv.mp_gRNA_csv, name='MP_gRNA_detail_csv_link'),


    path('<str:UUID>/table/', views.data_table_page, name='data_table_page'),
    #path('<str:UUID>/down_detail_csv/', views.download_detail_csv_link, name='download_detail_csv_link'),
    path('<str:UUID>/down_detail_csv/', views.download_csv.detail_csv, name='download_detail_csv_link'),
    path('<str:UUID>/down_OneMisRank_csv/', views.download_csv.one_mismatch_csv, name='download_OneMisRank_csv_link'),
    path('<str:UUID>/down_DoubleMisRank_csv/', views.download_csv.double_mismatch_csv, name='download_DoubleMisRank_csv_link'),
    path('<str:UUID>/down_TotalMisRank_csv/', views.download_csv.total_mismatch_csv, name='download_TotalMisRank_csv_link'),
    ]
