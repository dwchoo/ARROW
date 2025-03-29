from __future__ import absolute_import, unicode_literals
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.offline import plot
import os
from os.path import isfile
import numpy as np
import pandas as pd
import pickle

import django_tables2 as tables
from django_tables2 import RequestConfig
from django_tables2.views import SingleTableMixin

import django_filters
from django_filters.views import FilterView

from cas_offinder.data_class import job_data, find_ucsc_initial
from cas_offinder.seq_encoder_decoder import *
import cas_offinder.seq_encoder_decoder as en_de
from cas_offinder.processing_one_mismatch import one_mismatch_class, plotly_heatmap_one_mismatch, \
    return_one_mm_heatmap_arrays, plotly_one_mismatch_heatmap, Detail_info_calculater_go
from cas_offinder.processing_cas_offinder import cas_offinder_mismatch_data, plotly_cas_offinder_heatmap
from cas_offinder.processing_cas_offinder import cas_offinder_mismatch_data_tmp, detail_data
from cas_offinder.processing_double_mismatch import mismatch_df

# finished test version, have to remve annotation in generate_parquet
class visualization_data:
    def __init__(self, _job_data):
        self._job_data = _job_data
        self.text_file_path = self._job_data.job_output_path()
        self.parquet_path = self._job_data.job_parquet_path()
        self.pickle_path = self._job_data.job_pickle_path()

        self.cas_offinder_mismatch = cas_offinder_mismatch_data(self.text_file_path)
        self.ref_name = find_ucsc_initial(self._job_data.ref)
        self.MP_gRNA_detail = self.__MP_gRNA_make_idxSeq_csv(
            folder_path   = self._job_data.job_data_script_path(),
        )

    def __read_data2memory(self,):
        if not hasattr(self, 'data_frame_comp'):
            self.data_frame_comp = self.__return_parquet_data(
                text_file_path= self.text_file_path,
                parquet_path= self.parquet_path
            )
        if not hasattr(self, 'pickle_data'):
            self.pickle_data = self.__return_pckle_data(self.pickle_path)

    def generate_data(self,):
        self.__read_data2memory()

    def generate_pckl(self,save_path):
        if hasattr(self, 'data_frame_comp'):
            data_frame_comp = self.data_frame_comp
        else:
            self.data_frame_comp = self.__return_parquet_data(
                text_file_path = self.text_file_path,
                parquet_path   = self.parquet_path,
            )
        save_data = {}
        save_data['one_hot_dist_z'] = self.cas_offinder_mismatch.return_one_hot_dist_z(data_frame_comp)
        save_data['mismatch_table'] = self.cas_offinder_mismatch.return_mismatch_table(
                data_frame_comp,
                self._job_data.job_search_seq()
                )

        #one_mismatch_data
        __one_mis_dict = {}
        __one_mis_dict['data'],__one_mis_dict['rank_df'], \
        __one_mis_dict['rank_list'], __one_mis_dict['rank_list_query'] \
                = self.__return_one_mismatch_data(
                            query_seq = self._job_data.job_search_seq(),
                            mismatch_data = data_frame_comp,
                            PAM = self._job_data.PAM_type,
                        )
        save_data['one_mismatch_data'] = __one_mis_dict

        #####################################
        # new mismatch data generate method #
        #####################################
        mismatch_data = mismatch_df(
            seq= self._job_data.seq,
            cas_offinder_seq_list= np.array(self.data_frame_comp['seq']),
            PAM=self._job_data.PAM_type,
            PAM_end=True,
            max_range=4,
            dis_weight=[1,1,1,1,0.5],
        )
        # one mismatch heatmap data
        #save_data['one_mismatch_data'] = {}
        _score_array, _info_array = self.__return_one_mismatch_heatmap_data(
            input_seq = self._job_data.seq,
            mm_df     = mismatch_data.mismatch_df_one,
        )
        save_data['one_mismatch_data']['score_array'] = _score_array
        save_data['one_mismatch_data']['info_array'] = _info_array

        save_data['double_mismatch_data'] = {}
        save_data['double_mismatch_data']['total_df']       = mismatch_data.mismatch_df_total
        save_data['double_mismatch_data']['one_mm_df']      = mismatch_data.mismatch_df_one
        save_data['double_mismatch_data']['two_mm_df']      = mismatch_data.mismatch_df_two
        #save_data['double_mismatch_data']['query_mm_dict']  = mismatch_data.query_mm_dict

        
        with open(save_path,"wb") as fw:
            pickle.dump(save_data, fw)

        self.pickle_data = save_data
        return save_data

    # Make mispared gRNA's detail page
    def __MP_gRNA_make_idxSeq_csv(self,folder_path):
        self.__read_data2memory()

        MP_gRNA_detail = Detail_info_calculater_go(
            folder_path   = folder_path,
            org_dataframe = self.data_frame_comp,
        )
        return MP_gRNA_detail
        
    def __return_MP_gRNA(self,rank, MP_gRNA):
        MP_gRNA_detail_class = self.MP_gRNA_detail
        org_df = MP_gRNA_detail_class.read_idx_seq_csv(MP_gRNA_detail_class.org_csv_path)
        rank_IdxSeqMM_df, IdxSeqMM_csv_path = MP_gRNA_detail_class.return_rank_IdxSeqMM_df(rank,MP_gRNA)
        os.remove(IdxSeqMM_csv_path)

        return rank_IdxSeqMM_df

    def return_rank_MP_gRNA_detail_df(self, rank, max_num = 10, max_mm = 4):
        __tt, one_web_list, __two = self.double_mismatch_rank_web_table(max_num)
        del(__tt)
        del(__two)
        MP_gRNA = one_web_list[rank]['target']

        rank_IdxSeqMM_df = self.__return_MP_gRNA(rank, MP_gRNA)

        self.__read_data2memory()
        df = self.MP_gRNA_detail.generate_new_detail_df(
            rank_gRNA     = MP_gRNA,
            org_df        = self.data_frame_comp,
            idx_seq_mm_df = rank_IdxSeqMM_df,
        )
        df = df.loc[df['mismatch'] <= max_mm]
        df = df.drop(columns=['index'])
        df = df.reset_index(drop=True)
        df.index += 1
        df.reset_index(level=0, inplace=True)
        rank_detail_df = df.astype({'index' : 'uint32'})
        return rank_detail_df, MP_gRNA

    def return_MP_gRNA_mismatch_table(self, data_frame_comp):
        mismatch_table = self.cas_offinder_mismatch.return_mismatch_table(
            data_frame_comp,
            None
        )
        return mismatch_table


    def MP_gRNA_dist_plotly_heatmap(self, data_frame_comp, mp_gRNA, html=True):
        self.__read_data2memory()
        seq = mp_gRNA
        #data = self.pickle_data['one_hot_dist_z']
        #data_frame_comp = self.return_rank_MP_gRNA_detail_df(rank)
        data = self.cas_offinder_mismatch.return_one_hot_dist_z(data_frame_comp)
        fig = plotly_cas_offinder_heatmap(
                seq,
                data
                )
        if html:
            plot_div = plot(fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
            result_plot = plot_div
        else:
            result_plot = fig
        return result_plot
    
    def return_MP_gRNA_detail_table(self, request, rank):
        detail_df, MP_gRNA = self.return_rank_MP_gRNA_detail_df(rank)
        ref_name = self.ref_name
        data = self.cas_offinder_mismatch.return_detail_web_table(
            detail_df,
            ref_name
        )

        table = dataframe_table(data,ref_name)
        RequestConfig(request).configure(table)
        return table



    def __regenerate_pickle(self,):
        return self.generate_pckl(self.pickle_path)

    def load_pckl(self, save_path):
        with open(save_path,"rb") as fr:
            data = pickle.load(fr)
        return data

    def __return_pckle_data(self, pickle_path):
        if isfile(pickle_path):
            pickle_data = self.load_pckl(pickle_path)
        else:
            pickle_data = self.generate_pckl(pickle_path)
        return pickle_data

    def df_html(self,):
        self.__read_data2memory()
        data_frame_comp = self.data_frame_comp
        html_df = self.cas_offinder_mismatch.return_df_html(data_frame_comp)
        return html_df

    def detail_df_table(self,request):
        ref_name = self.ref_name
        self.__read_data2memory()
        data_frame_comp = self.data_frame_comp
        data = self.cas_offinder_mismatch.return_detail_web_table(
                data_frame_comp,
                ref_name
                )
        table = dataframe_table(data, ref_name)
        RequestConfig(request).configure(table)
        return table
        

    def plotly_heatmap(self, html=True):
        self.__read_data2memory()
        seq = self._job_data.job_search_seq()
        data = self.pickle_data['one_hot_dist_z']
        fig = plotly_cas_offinder_heatmap(
                seq,
                data
                )
        if html:
            plot_div = plot(fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
            result_plot = plot_div
        else:
            result_plot = fig
        return result_plot

    def mismatch_table(self,):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        try:
            mismatch_table_df = pickle_data['mismatch_table']
        except:
            mismatch_table_df = self.__regenerate_pickle()['mismatch_table']
        return mismatch_table_df
        

    def generate_parquet(self,data_frame, save_path, delete_file):
        data_frame['index'] = data_frame.index
        data_frame.to_parquet(save_path, engine='pyarrow')
        #os.remove(delete_file) ## remove annotation

    def load_parquet(self, save_path,text_file_path):
        def regenerateNreload():
            data_frame_decomp = self.cas_offinder_mismatch.return_parquet_df()
            self.generate_parquet(
                data_frame  = data_frame_decomp,
                save_path   = save_path,
                delete_file = text_file_path,
            )
            return pd.read_parquet(save_path)
        # check index column
        if isfile(text_file_path) and not isfile(save_path):
            df = regenerateNreload()
        else:
            df = pd.read_parquet(save_path)
        if not 'index' in df.columns:
            df = regenerateNreload()
        if not df['direction'].dtype == 'O':
            df = regenerateNreload()
        return df

    def __return_parquet_data(self,text_file_path, parquet_path):
        data_frame_decomp = self.load_parquet(parquet_path,text_file_path)
        data_frame_comp = cas_offinder_mismatch_data.return_compressed_data_frame(data_frame_decomp)
        return data_frame_comp
    
    def return_df_for_csv(self,):
        query_seq = self._job_data.seq

        self.__read_data2memory()
        data_frame_comp = self.data_frame_comp
        selected_dataframe = self.cas_offinder_mismatch.return_df_for_csv(
                data_frame_comp,
                query_seq
                )
        return selected_dataframe

    def return_df_for_csv_download(self, data_frame_comp,query_seq):
        selected_dataframe = self.cas_offinder_mismatch.return_df_for_csv(
                data_frame_comp,
                query_seq
                )
        return selected_dataframe





    # one_mismatch_data
    def __return_one_mismatch_data(self, query_seq, mismatch_data, PAM='NGG'):
        query_seq = query_seq
        mismatch_data = mismatch_data
        PAM = PAM
        #rank_range = 4 * (len(query_seq) - len(PAM))
        one_mismatch = one_mismatch_class(query_seq, mismatch_data, PAM)
        
        one_mismatch_dict    = one_mismatch.data_matrix_dict
        rank_data            = one_mismatch.rank_data
        rank_data_list       = one_mismatch.rank_data_list
        rank_data_list_query = one_mismatch.rank_data_list_query
        rank_dataframe       = one_mismatch.return_rank_dataframe()

        return one_mismatch_dict, rank_dataframe, rank_data_list, rank_data_list_query

    def plotly_one_mismatch(self, html=True):
        def load_data(pickle_data):
            data_score_array = pickle_data['one_mismatch_data']['data']['score']
            data_mismatch_count_array = pickle_data['one_mismatch_data']['data']['mismatch_count']
            data_score2rank_round_6_dict = pickle_data['one_mismatch_data']['data']['score2rank_round_6_dict'] 
            return data_score_array, data_mismatch_count_array, data_score2rank_round_6_dict

        self.__read_data2memory()
        pickle_data = self.pickle_data
        
        query_seq = self._job_data.job_search_seq()
        PAM = self._job_data.PAM_type
        try:
            #data_score_array = pickle_data['one_mismatch_data']
            data_score_array, data_mismatch_count_array, data_score2rank_round_6_dict \
                    = load_data(pickle_data)
        except:
            pickle_data = self.__regenerate_pickle()
            data_score_array, data_mismatch_count_array, data_score2rank_round_6_dict \
                    = load_data(pickle_data)
        #data_score_array = pickle_data['one_mismatch_data']['data']['score']
        #data_mismatch_count_array = pickle_data['one_mismatch_data']['data']['mismatch_count']
        #data_score2rank_round_6_dict = pickle_data['one_mismatch_data']['data']['score2rank_round_6_dict'] 
        _fig = plotly_heatmap_one_mismatch(
                    query_seq = query_seq,
                    PAM = PAM,
                    data_score_array = data_score_array,
                    data_mismatch_count_array = data_mismatch_count_array,
                    score2rank_round_6_dict = data_score2rank_round_6_dict,
                )
        if html:
            plot_result = plot(_fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
        else:
            plot_result = _fig
        return plot_result

    def one_mismatch_rank_web_table(self,max_num=5):
        self.__read_data2memory()
        pickle_data = self.pickle_data

        try:
            _ = pickle_data['one_mismatch_data']['rank_list_query']
        except:
            pickle_data = self.__regenerate_pickle()

        rank_data_list_query = pickle_data['one_mismatch_data']['rank_list_query']
        rank_data_list = pickle_data['one_mismatch_data']['rank_list'][:max_num]
        rank_data_web_table = [rank_data_list_query] + rank_data_list
        return rank_data_web_table

    def return_one_mismatch_rank_dataframe(self,):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        if not 'rank_df' in pickle_data['one_mismatch_data'].keys():
            pickle_data = self.__regenerate_pickle()
            self.__read_data2memory()
        rank_df = pickle_data['one_mismatch_data']['rank_df']
        return rank_df



    # one mismatch heatmap
    def __return_one_mismatch_heatmap_data(self,input_seq, mm_df):
        score_array, info_array = return_one_mm_heatmap_arrays(input_seq,mm_df)
        return score_array, info_array

    def plot_one_mismatch_heatmap(self, html=True):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        try:
            _score_array = pickle_data['one_mismatch_data']['score_array']
            _info_array  = pickle_data['one_mismatch_data']['info_array']
        except:
            pickle_data = self.__regenerate_pickle()
            _score_array = pickle_data['one_mismatch_data']['score_array']
            _info_array  = pickle_data['one_mismatch_data']['info_array']
        fig = plotly_one_mismatch_heatmap(
            input_seq   = self._job_data.seq,
            score_array = _score_array,
            info_array  = _info_array,
        )
        if html:
            plot_div = plot(fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
            result_fig = plot_div
        else:
            result_fig = fig

        return result_fig
        




    # new mismatch generator
    # new double mismatch
    def double_mismatch_rank_web_table(self,max_num=10):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        try:
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']
        except:
            pickle_data = self.__regenerate_pickle()
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']

        sorted_total_web_list = visualization_mismatch.return_rank_list_for_wb(
            total_mismatch_df,max_num)
        sorted_one_web_list = visualization_mismatch.return_rank_list_for_wb(
            one_mismatch_df,max_num)
        sorted_two_web_list = visualization_mismatch.return_rank_list_for_wb(
            two_mismatch_df,max_num)
        return sorted_total_web_list, sorted_one_web_list, sorted_two_web_list

    def double_mismatch_rank_df(self,):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        try:
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']
        except:
            pickle_data = self.__regenerate_pickle()
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']

        sorted_total_df = visualization_mismatch.return_rank_df_for_download(
            total_mismatch_df)
        sorted_one_df = visualization_mismatch.return_rank_df_for_download(
            one_mismatch_df)
        sorted_two_df = visualization_mismatch.return_rank_df_for_download(
            two_mismatch_df)
        return sorted_total_df, sorted_one_df, sorted_two_df

    def plot_mismatch_score_dist(self, html = True):
        self.__read_data2memory()
        pickle_data = self.pickle_data
        try:
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']
        except:
            pickle_data = self.__regenerate_pickle()
            total_mismatch_df   = pickle_data['double_mismatch_data']['total_df']
            one_mismatch_df     = pickle_data['double_mismatch_data']['one_mm_df']
            two_mismatch_df     = pickle_data['double_mismatch_data']['two_mm_df']
        fig = visualization_mismatch.plot_score_distribution(
            total_mm_df =total_mismatch_df,
            one_mm_df   =one_mismatch_df,
            two_mm_df   =two_mismatch_df,
        )
        if html:
            plot_div = plot(fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
            result_fig = plot_div
        else:
            result_fig = fig

        return result_fig

        


        



class dataframe_table(tables.Table):
    index       = tables.Column(accessor='index')
    #query       = tables.Column(accessor='query')
    seq_compare = tables.TemplateColumn(
            '''<p style="text-align:right; line-height:0.8">crRNA: {{record.query}}</p>
            <p style="text-align:right; line-height:0.8" >
                <span>DNA: </spane>
                <a href="https://genome.ucsc.edu/cgi-bin/hgTracks?db={{record.ref_name}}&position={{record.chr}}:{{record.search_position}}" target="_blank">{{record.seq}}</a>
            </p>''',
        accessor='seq',
        verbose_name='Sequence',
    )
    chromosome  = tables.Column(accessor='chr', verbose_name='Chromosome')
    site        = tables.Column(accessor='site')
    sequence    = tables.TemplateColumn(
        '<a href="https://genome.ucsc.edu/cgi-bin/hgTracks?db={{record.ref_name}}&position={{record.chr}}:{{record.search_position}}" target="_blank">{{record.seq}}</a>',
        verbose_name='Sequence_',
        visible=False,
    )
    #sequence    = tables.Column(accessor='seq', verbose_name='Sequence')
    direction   = tables.Column(accessor='direction')
    mismatch    = tables.Column(accessor='mismatch')
    class Meta:
        template_name = 'django_tables2/bootstrap.html'




class visualization_mismatch:
    @classmethod
    def return_rank_list_for_wb(cls,dataframe,max_rank):
        '''
        args:
            dataframe   : 1 & 2 mismatch inforamtion dataframe,
                            columns : mm_index, target, mm_info, seq_index,
                                     rank, score, mismatch_0~4
            max_rank    : max rank to show
        return:
            rank_list_wb: list of dictionary,
                            [{'target': 'TTTTGGGCCGGCGAAACTGC',
                              'num_mm' : 2,
                              'mm_info': '9:G>C,13:C>G',
                              'mismatch_0': 0,
                              'mismatch_1': 0,
                              'mismatch_2': 1,
                              'mismatch_3': 0,
                              'mismatch_4': 23,
                              'score': 0.9494505494505495,
                              'rank': 1}, {...}, ... ]
        '''
        df_drop_indexs  = dataframe.drop(columns=['mm_index','seq_index'])
        df_sorted       = df_drop_indexs.sort_values('rank')[:max_rank+1]
        rank_list_wb    = df_sorted.to_dict('records')
        return rank_list_wb

    @classmethod
    def return_rank_df_for_download(cls,dataframe):
        '''
        args:
            dataframe   : 1 & 2 mismatch inforamtion dataframe,
                            columns : mm_index, target, mm_info, seq_index,
                                     rank, score, mismatch_0~4
            max_rank    : max rank to show
        return:
            df_sorted   : Dataframe,
                            [{'rank' : 1,
                              'Sequence': 'TTTTGGGCCGGCGAAACTGC',
                              'Mismatch' : 2,
                              'Mismatch_info': '9:G>C,13:C>G',
                              'score': 0.9494505494505495,
                              'mismatch_0': 0,
                              'mismatch_1': 0,
                              'mismatch_2': 1,
                              'mismatch_3': 0,
                              'mismatch_4': 23,
                               ]
        '''
        df_drop_indexs  = dataframe.drop(columns=['mm_index','seq_index'])
        df_rename       = df_drop_indexs.rename(
            columns={
                'target' : 'Sequence',
                'num_mm':'Mismatch',
                'mm_info':'Mismatch_info',
                'score' : 'Score'
            },errors='ignore')
        #reorder columns
        df_sorted       = df_rename.sort_values('rank')
        df_col          = df_rename.columns.tolist()
        df_col.remove('rank')
        df_col       = ['rank',  *df_col]
        df_sorted       = df_sorted[df_col]
        return df_sorted

    @classmethod
    def return_one_mm_heatmap_index_table(cls,seq):
        '''
        args:
            seq             : query sequence, 'ATCTGGGCGGGCCAAACTGC'
        return:
            defualt_table   : mismatch index table, shape: (4, seq_length)
                            array([['10000000000000000000', '01000000000000000000',
                                    ....
                                    '00000000000000000010', '00000000000000000001'],
                                   ['20000000000000000000', '00000000000000000000',
                                    ....
                                    '00000000000000000000', '00000000000000000002'],
                                   ['30000000000000000000', '03000000000000000000',
                                    ....
                                    '00000000000000000030', '00000000000000000000'],
                                   ['00000000000000000000', '04000000000000000000',
                                    ....
                                    '00000000000000000040', '00000000000000000004']], dtype=object)
        '''
        def return_one_mm_table_index(pos, change,length=20):
            assert change > 0 and change < 6, f'Check change : {change}'
            zeros = np.zeros(length,np.int8)
            zeros[pos] = change
            return ''.join(list(map(str,zeros)))
        def default_mm_table(seq):
            seq_length = len(seq)
            table = np.zeros((4,seq_length),'object')
            for i in range(seq_length):
                for j in range(4):
                    table[j][i] = return_one_mm_table_index(i,j+1,seq_length)
            return table
        seq_length = len(seq)
        default_table = default_mm_table(seq)
        indexed_seq = en_de.acgt2seq_index(seq,join=False)
        query_mm_index = ''.join(list(map(str,np.zeros(seq_length,np.int))))
        for _pos, _base in enumerate(indexed_seq):
            default_table[_base-1][_pos] = query_mm_index
        return default_table

    @classmethod
    def return_one_hot_dist_z(cls,dataframe):
        df_seq_list = list(dataframe['seq'])
        one_hot_dist_z = en_de.one_hot_encoder.average_distribution(df_seq_list)
        return one_hot_dist_z

    @classmethod
    def return_mismatch_table(cls,dataframe,query_seq=None):
        mismatch_table = cls.__make_mismatch_table_df(
            cls,
            dataframe,
            query_seq
        )
        return mismatch_table

    def __make_mismatch_table_df(self,
            dataframe,
            query_seq = None,
            col_name = 'mismatch',
            ):
        if query_seq == None:
            query_seq = dataframe['query'][0]
        df_mis_num = dataframe[col_name].value_counts(sort=False)
        df_mis_rate = dataframe[col_name].value_counts(normalize=True,sort=False) * 100
        mismatch_table_header = [
            'Sequence',
            'Mismatch',
            'Number of found targets',
            'Rate of found targets(%)'
        ]
        mismatch_table_dtype  = {
            'Sequence' : 'category',
            'Mismatch' : 'int8',
            'Number of found targets' : 'uint32',
            'Rate of found targets(%)' : 'float',
        }
        mismatch_table_length = len(df_mis_num)
        target_seq = [query_seq] * mismatch_table_length
        mismatch = list(df_mis_num.index)
        num_target = list(df_mis_num)
        rate_target = np.round(list(df_mis_rate),4)
        mismatch_table = pd.DataFrame(
            zip(target_seq, mismatch, num_target,rate_target),
            columns = mismatch_table_header,
        )
        mismatch_table = mismatch_table.astype(mismatch_table_dtype)
        mismatch_table = mismatch_table.sort_values(by=['Mismatch'])
        mismatch_table = np.round(mismatch_table, 4)
        return mismatch_table

    @classmethod
    def plot_score_distribution(cls,total_mm_df, one_mm_df, two_mm_df):
        '''
        args :
            total_mm_df     : One & Two mismatch dataframe, it must have score.
            one_mm_df       : One mismatch dataframe, it must have score.
            two_mm_df       : Two mismatch dataframe, it must have score.
        return :
            plot_div        : Plotly violin plot HTML, show score distribution.
        '''
        total_scores = total_mm_df['score'].to_numpy()
        one_scores = one_mm_df['score'].to_numpy()
        two_scores = two_mm_df['score'].to_numpy()

        x_label_list   = ['One & Two mismatch','One mismatch / Two mismatch','One mismatch / Two mismatch']
        legend_list    = ['One & Two mismatch', 'One mismatch','Two mismatch']
        y_data_list    = [total_scores, one_scores, two_scores]
        side_list      = ['both','negative','positive']
        point_pos_list = [-1.5,-1.5,1.5]
        data_zip = zip(x_label_list, legend_list, y_data_list, side_list, point_pos_list)


        fig = go.Figure()
        for x, legend, y, side, point_pos in data_zip:
            fig.add_trace(go.Violin(
                x0=x,
                y = y,
                name = legend,
                side = side,
                pointpos = point_pos,

                points='all',
                spanmode='hard',
                box_visible=True,
                meanline_visible=True,
            ))
        fig.update_layout(
        title=dict(
            text='NCS distribution',
            x = 0.45,
            y = 0.85,
            xanchor='center',
            yanchor='top',
        ))
        fig.update_yaxes(
            title=dict(
                text='Score',
                standoff=0,
            ),
            range=[-1.2,1.2],
        )

        fig.add_hline(
            y=1,
            annotation_text='Ideal sequence score',
            line=dict(color='Red'),
            line_width=0.8
        )
        fig.add_hline(
            y=0,
            annotation_text='Input sequence score',
            line=dict(color='Red'),
            line_width=0.4
        )

        #plot_div = plot(fig, output_type='div', show_link=False, link_text="", include_plotlyjs=False)
        return fig



    
class processing_data:
    def __init__(self, _job_data):
        self._job_data = _job_data
        self.text_file_path = self._job_data.job_output_path()
        self.parquet_path = self._job_data.job_parquet_path()
        self.pickle_path = self._job_data.job_pickle_path()

    def __load_cas_offinder(self,):
        dataframe = cas_offinder_mismatch_data_tmp.load_parquet_file(self.parquet_path)
        return dataframe

    def __save_cas_offinder_df(self,):
        _ = cas_offinder_mismatch_data_tmp(
            cas_offinder_output_path=self.text_file_path,
            parquet_path=self.parquet_path
        )

    def __save_pickle_data(self,dataframe,save_path):
        _job_data = self._job_data
        __pickle_data = {}

        # one mismatch distribution heatmap and mismatch table
        __pickle_data['distribution'] = visualization_mismatch.return_one_hot_dist_z(dataframe)
        __pickle_data['mm_table']  = visualization_mismatch.return_mismatch_table(dataframe)

        # mismatch rank table save
        __pickle_data['rank_table'] = {}
        mismatch_rank_data = mismatch_df(
            seq= _job_data.seq,
            cas_offinder_seq_list= dataframe.loc[:,'seq'].to_numpy(),
            PAM=_job_data.PAM_type,
            PAM_end=True,
            max_range=4,
            dis_weight=[1,1,1,1,0.5],
        )


class find_by_mm_index:
    '''
        Find sequence data in dataframe by mm_index
    '''
    def __init__(self,dataframe):
        self.dataframe = dataframe
        
    def __find_seq(self,mm_index):
        return self.dataframe.query(f'mm_index == "{mm_index}"')
    
    def get_data_dict(self,
        mm_index,
        search_list=[['num_mm','score','rank', 'mm_info',\
                      'mismatch_0','mismatch_1','mismatch_2','mismatch_3','mismatch_4']]
    ):
        '''
        args:
            mm_index    : mismatch index, '100000'
            search_list   : Column name, 'score', 'mismatch_0'...
        return
            _data_dict  : dictionary data, {num_mm : 1, score : 0.513, mismatch_0 : 0, mismatch_1 : 1...}
        '''
        _seq_info = self.__find_seq(mm_index)
        _data_dict = _seq_info.get(*search_list).to_dict('records')[0]
        return _data_dict



#class dataframe_filter(django_filters.FilterSet):
#    index       = django_filters.NumberFilter(field_name='index')
#    seq         = django_filters.CharFilter(field_name='seq')
#    chromosome  = django_filters.ChoiceFilter(field_name='chr')
#    site        = django_filters.NumberFilter(field_name='site')
#    direction   = django_filters.ChoiceFilter(field_name='direction')
#    mismatch    = django_filters.ChoiceFilter(field_name='mismatch')
#    class Meta:
#        fields = ['index','seq','chr','site','direction','mismatch']
#
#class dataframe_list(SingleTableMixin, FilterView):
#    table_class = dataframe_table
#    filterset_class = dataframe_filter
