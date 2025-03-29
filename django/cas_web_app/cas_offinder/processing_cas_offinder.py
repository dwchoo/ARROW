from __future__ import absolute_import, unicode_literals
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.offline import plot

import numpy as np
import pandas as pd
import os
import functools

from cas_offinder.seq_encoder_decoder import *
import cas_offinder.seq_encoder_decoder as en_de

class cas_offinder_mismatch_data_tmp:
    def __init__(self,
        cas_offinder_output_path,
        parquet_path,
    ):
        self.dataframe = self.__read_output_file(cas_offinder_output_path)
        self.__save_parquet_file(
            self.dataframe,
            parquet_path,
            cas_offinder_output_path,
        )

    def __read_output_file(self, path):
        path = path
        header = ["query","chr","site","seq","direction","mismatch"]
        data_type = {
            'query' : 'category',
            'chr' : 'category',
            'site' : 'uint32',
            'direction' : 'category',
            'mismatch' : 'uint8',
        }
        data_frame = pd.read_csv(
            path,
            sep = "\t",
            names=header,
            dtype=data_type,
        )
        return data_frame

    def __save_parquet_file(self, dataframe, file_name, delete_file):
        dataframe.to_parquet(file_name, engine='pyarrow')
        #os.remove(delete_file)

    @classmethod
    def load_parquet_file(cls,save_path):
        return pd.read_parquet(save_path)


class detail_data:
    @classmethod
    def return_df_for_csvfile(cls, dataframe,query_seq):
        selected_column = ["seq","chr","site","direction","mismatch"]
        changed_column = [f"Sequence({query_seq})","chromosome","site","direction", "mismatch"]
        
        selected_dataframe = dataframe[selected_column]
        selected_dataframe.columns = changed_column
        return selected_dataframe

    @classmethod
    def return_detail_web_table(cls,dataframe,ref_name,max_mm=4):
        df = dataframe.copy()
        df = df.loc[df['mismatch'] <= max_mm]
        df = df.drop(columns=['index'])
        df = df.reset_index(drop=True)
        df.index += 1
        df.reset_index(level=0, inplace=True)
        df = df.astype({'index' : 'uint32'})

        df = df.assign(
                ref_name        = ref_name,
                search_position = list(map(
                    functools.partial(cls.__return_search_site,self=cls),
                    list(df['site']))),
            ).astype({
                    "ref_name" : 'category',
                })
        data = df.to_dict('records')
        return data

    @classmethod
    def return_df_html(cls,dataframe,condition=None,value=None,sort_up=None):
        if value is not None:
            selected_dataframe = dataframe[dataframe[f'condition'] == value]
        else:
            selected_dataframe = dataframe
        if sort_up is not None:
            selected_dataframe = selected_dataframe.sort_values(condition,ascending=sort_up)

        html_df = selected_dataframe.to_html(classes='table table-striped')
        return html_df

    def __return_search_site(self, position,length = 1000):
        length_half = int(length//2)
        search_string = f"{position - length_half}-{position + length_half}"
        return search_string




class cas_offinder_mismatch_data:
    def __init__(self,
            cas_offinder_output_path,
        ):
        self.output_text_file_path = cas_offinder_output_path


    def read_data_return_comp_df(self,):
        file_path = self.output_text_file_path
        raw_data_frame = self.__read_output_file(file_path)
        comp_data_frame = self.__return_compressed_data_frame(raw_data_frame)
        del raw_data_frame
        return comp_data_frame

    def return_parquet_df(self,):
        file_path = self.output_text_file_path
        raw_data_frame = self.__read_output_file(file_path)
        decomp_data_frame = self.__return_decompressed_data_frame(raw_data_frame)
        del raw_data_frame
        return decomp_data_frame


    def return_df_for_csv(self,data_frame_comp, query_seq):
        data_frame = self.__return_decompressed_data_frame(data_frame_comp)
        query_seq = query_seq
        selected_column = ["seq","chr","site","direction","mismatch"]
        changed_column = [f"Sequence({query_seq})","chromosome","site","direction", "mismatch"]
        
        selected_data_frame = data_frame[selected_column]
        selected_data_frame.columns = changed_column
        return selected_data_frame

    def return_detail_web_table(self,data_frame_comp, ref_name, max_mm=4):
        data_frame_decomp = self.__return_decompressed_data_frame(data_frame_comp)
        df = data_frame_decomp.copy()
        df = df.loc[df['mismatch'] <= max_mm]
        df = df.drop(columns=['index'])
        df = df.reset_index(drop=True)
        df.index += 1
        df.reset_index(level=0, inplace=True)
        df = df.astype({'index' : 'uint32'})

        df = df.assign(
                ref_name        = ref_name,
                search_position = list(map(self.__return_search_site, list(df['site']))),
            ).astype({
                    "ref_name" : 'category',
                })
        data = df.to_dict('records')
        return data


    def return_one_hot_dist_z(self,data_frame, max_mm=4):
        df_seq_list = list(data_frame['seq'].loc[data_frame['mismatch']<=max_mm])
        one_hot_dist_z = one_hot_encoder.average_distribution(df_seq_list)
        return one_hot_dist_z

    def return_mismatch_table(self,data_frame, query_seq=None, max_mm=4):
        df = data_frame.copy()
        df = df.loc[df['mismatch'] <= max_mm]
        df = df.drop(columns=['index'])
        df = df.reset_index(drop=True)
        df.index += 1
        df.reset_index(level=0, inplace=True)
        df = df.astype({'index' : 'uint32'})
        mismatch_table = self.__make_mismatch_table_df(
                df,
                query_seq
                )
        return mismatch_table
    
    def return_df_html(self, data_frame_comp):
        data_frame = self.__return_decompressed_data_frame(data_frame_comp)
        html_df = data_frame.to_html(classes='table table-striped')
        return html_df

    def __read_output_file(self, path):
        path = path
        header = ["query","chr","site","seq","direction","mismatch"]
        data_type = {
            'query' : 'category',
            'chr' : 'category',
            'site' : 'uint64',
            'mismatch' : 'uint8',}
        data_frame = pd.read_csv(
            path,
            sep = "\t",
            names=header,
            dtype=data_type,
        )
        return data_frame

    def __return_compressed_data_frame(self, data_frame):
        data_frame = data_frame
        if data_frame['direction'].dtype == 'bool':
            return data_frame
        data_frame['direction'] = list(map(self.__direction_bool, data_frame['direction']))
        return data_frame

    @classmethod
    def return_compressed_data_frame(cls, data_frame):
        data_frame = data_frame
        if data_frame['direction'].dtype == 'bool':
            return data_frame
        data_frame['direction'] = list(map(cas_offinder_mismatch_data.__direction_bool, data_frame['direction']))
        return data_frame

    def __return_decompressed_data_frame(self, data_frame):
        data_frame = data_frame
        if data_frame['direction'].dtype != 'bool':
            return data_frame
        data_frame['direction'] = list(map(self.__direction_cross, data_frame['direction']))
        return data_frame

    @staticmethod
    def __direction_bool(direction):
        if direction == "+":
            return True
        else:
            return False

    def __direction_cross(self, direct_bool):
        if direct_bool:
            return "+"
        else:
            return "-"

    def __return_search_site(self, position,length = 1000):
        length_half = int(length//2)
        search_string = f"{position - length_half}-{position + length_half}"
        return search_string



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


        

def plotly_cas_offinder_heatmap(
        search_seq,
        data,
    ):
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    from plotly.offline import plot

    seq = search_seq
    x = list(seq)
    y = ['A','C','G','T']
    z = np.array(data,dtype=np.float32)

    mat_flag = return_heatmap_match_flag(x,y)

    
    fig = go.Figure(
    data = go.Heatmap(
            z=z,
            colorscale ='pubu',
            showscale  = False,
            text = mat_flag,
            hovertemplate="%{text}<br>%{x}->%{y}<extra></extra>",
        ),
    )
    ff_fig_annotation = ff.create_annotated_heatmap(
            z = np.round(z,2),
            reversescale=True,
        ).layout.annotations
    fig.layout.annotations = ff_fig_annotation
    fig.layout.yaxis.autorange = "reversed"
    fig.update_yaxes(tickmode = 'array',
                     tickvals = np.arange(0, len(y)),
                     ticktext= y,
                     fixedrange=True
                     )

    fig.update_xaxes(tickmode = 'array',
                     tickvals = np.arange(0, len(x)),
                     ticktext= x,
                     side='top',
                     fixedrange=True,
                     )
    return fig



def return_heatmap_match_flag(x,y):
    x = x
    y = y
    mat_flag = np.empty([len(y), len(x)], dtype=object)
    
    site_type = {
        'A' : ['A'],
        'C' : ['C'],
        'G' : ['G'],
        'T' : ['T'],
        
        'R' : ['A','G'],
        'Y' : ['C','T'],
        'S' : ['G','C'],
        'W' : ['A','T'],
        'K' : ['G','T'],
        'M' : ['A','C'],
        
        'B' : ['C','G','T'],
        'D' : ['A','G','T'],
        'H' : ['A','C','T'],
        'V' : ['A','C','G'],
        
        'N' : ['A','C','G','T']
    }

    for j in range(len(y)):
        for i in range(len(x)):
            if y[j] in site_type[x[i]]:
                mat_flag[j][i] = '<b style="color:#CD5C5C">Match</b>'
            else:
                mat_flag[j][i] = f'Mismatch {x[i]}{y[j]}:{i+1}'

    return mat_flag

