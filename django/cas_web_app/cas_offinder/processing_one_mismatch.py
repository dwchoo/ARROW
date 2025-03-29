from __future__ import absolute_import, unicode_literals
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.offline import plot
import numpy as np
import pandas as pd
import ctypes

from cas_offinder.seq_encoder_decoder import *



class one_mismatch_data:
    search_max_mismatch_count = 5
    scoring_max_mismatch = 4
    ideal_mismatch_list = [0,1,1,1,1]
    scoring_mismatch_weight = [1,1,1,1,0.5]
    ideal2query_div_mismatch_vector = [1 for i in range(search_max_mismatch_count)]
    query_L1_norm = 1
    query_mismatch_dict = {
         0 : 0,
         1 : 0,
         2 : 0,
         3 : 0,
         4 : 0,
    }
    
    @classmethod
    def inital_mismatch_dict(cls, mismatch_data_value_counts_dict):
        max_count = cls.search_max_mismatch_count
        mismatch_value_counts_dict = mismatch_data_value_counts_dict
        cls.ideal_mismatch_list = cls.__generate_ideal_mismatch_list(mismatch_value_counts_dict)
        cls.query_mismatch_dict = cls.__generate_query_mismatch_dict(mismatch_value_counts_dict)
        cls.ideal2query_div_mismatch_vector = cls.__generate_ideal2query_div_mismatch_vector(
            mismatch_value_counts_dict,
            cls.ideal_mismatch_list,
        )
        cls.query_L1_norm = cls.__return_L1_norm(cls, mismatch_value_counts_dict)
        
    @classmethod
    def __generate_query_mismatch_dict(cls, mismatch_value_counts_dict):
        max_count = cls.search_max_mismatch_count
        mismatch_count_dict = {}
        for i in range(max_count):
            mismatch_count_dict[i] = mismatch_value_counts_dict.get(i,0)
        return mismatch_count_dict
    
    @classmethod
    def __generate_ideal2query_div_mismatch_vector(cls,mismatch_value_counts_dict, ideal_mismatch_list):
        max_count = cls.search_max_mismatch_count
        div_vector = np.ones(max_count)
        for i in range(max_count):
            div_value = mismatch_value_counts_dict.get(i,1) - ideal_mismatch_list[i]
            if int(div_value) <= 0:
                div_vector[i] = 1
            else:
                div_vector[i] = div_value
        return div_vector
    
    @classmethod
    def __generate_ideal_mismatch_list(cls, mismatch_value_counts_dict):
        search_max_mismatch_count = cls.search_max_mismatch_count
        _ideal_mismatch_list = [0 for _ in range(search_max_mismatch_count)]
        for i in range(len(_ideal_mismatch_list)-1):
            _ideal_mismatch_list[i+1] = mismatch_value_counts_dict.get(i,0)//mismatch_value_counts_dict.get(i,1)
        return _ideal_mismatch_list
    
    
    def __init__(self, seq_one_hot):
        self.seq_one_hot = seq_one_hot
        self.seq = self.__convert_seq_letter(self.seq_one_hot)
        self.index_list = []
        self.score = 0
        
        self.mismatch_count_dict = {
            0 : 0,
            1 : 0,
            2 : 0,
            3 : 0,
            4 : 0,
            #5 : 0,
        }
        self.mismatch_count_index_dict = {
            0 : [],
            1 : [],
            2 : [],
            3 : [],
            4 : [],
        }
        
    # after upgrade onehot encoder
    def __convert_seq_letter(self, seq_one_hot):
        seq_letter = one_hot_decoder.seq_decoder(seq_one_hot)
        return seq_letter
    
    def __add_index_list(self, index, mismatch_count):
        #self.index_list.append(index)
        self.mismatch_count_index_dict[mismatch_count] = self.mismatch_count_index_dict.get(mismatch_count,[]) + [index]
    
    def __update_mismatch_count(self, mismatch_count):
        if mismatch_count <= 4:
            self.mismatch_count_dict[mismatch_count] = self.mismatch_count_dict.get(mismatch_count,0) + 1
        #try:
        #    self.mismatch_count_dict[mismatch_count] += 1
        #except:
        #    print(f"mismatch_count error, mismatch_count: {mismatch_count}")
    
    def __update_score(self, mismatch_count):
        mismatch_count = int(mismatch_count)
        self.__update_mismatch_count(mismatch_count)
        self.score = self.__scoring()
        
    def __scoring(self,):
        _now_mismatch_count_dict = self.mismatch_count_dict
        score = self.__return_score(_now_mismatch_count_dict)
        return score
        
    def __return_L1_norm(self, _now_mismatch_dict):
        max_count = one_mismatch_data.search_max_mismatch_count
        max_mismatch = one_mismatch_data.scoring_max_mismatch + 1
        mismatch_weight = one_mismatch_data.scoring_mismatch_weight
        
        ideal2query_div_mismatch_vector = one_mismatch_data.ideal2query_div_mismatch_vector[:max_mismatch]
        ideal_vector = one_mismatch_data.ideal_mismatch_list[:max_mismatch]
        
        seq_array = np.array([_now_mismatch_dict.get(i,0) for i in range(max_mismatch)])
        norm_ideal2seq_vector = (seq_array - ideal_vector) / ideal2query_div_mismatch_vector
        
        ideal2seq_vector_norm_absolute = np.absolute(norm_ideal2seq_vector) * mismatch_weight
        ideal2seq_vector_norm_L1_norm = ideal2seq_vector_norm_absolute.sum()
        return ideal2seq_vector_norm_L1_norm
    
    def __return_score(self, _now_mismatch_dict):
        query_L1_norm = one_mismatch_data.query_L1_norm
        _L1_norm = self.__return_L1_norm(_now_mismatch_dict)
        score = (query_L1_norm - _L1_norm) / query_L1_norm
        return score
        
        
    
    # show score    
    def __mul__(self,*args,**kwargs):
        return self.score
    # show mismatch count
    def __sub__(self, *args, **kwargs):
        return self.mismatch_count_dict
    def __truediv__(self, *args, **kwargs):
        return self.seq
        
    # + [mismatch_count, mismatch_index]
    def __add__(self, mismatch_count_index):
        mismatch_count, mismatch_index = mismatch_count_index
        self.__add_index_list(mismatch_index, mismatch_count)
        self.__update_score(mismatch_count)
        return self
        
    def __iadd__(self, mismatch_count_index):
        one_mismatch_data.__add__(self, mismatch_count_index)



class one_mismatch_table:
    def __init__(self,query):
        self.query = np.array(query, np.uint8)
        self.one_mismatch_matrix_list = self.generate_one_mismatch_matrix(self.query)
        
        
    def generate_one_mismatch_matrix(self,query):
        from copy import deepcopy
        one_mismatch_matrix = []
        for index_position, query_one_letter in enumerate(query):
            for index, _bool in enumerate(query_one_letter != np.ones(4)):
                if _bool:
                    _tmp_list = np.zeros(4)
                    _tmp_list[index] = 1
                    _one_mis_query = deepcopy(query)
                    _one_mis_query[index_position] = _tmp_list
                    one_mismatch_matrix.append(_one_mis_query.tolist())
                else:
                    one_mismatch_matrix.append(deepcopy(query))
                    
        return np.array(one_mismatch_matrix)
    
    def return_mismatch_count_matrix(self, searched_seq):
        one_mismatch_matrix_list = self.one_mismatch_matrix_list
        searched_seq = np.array(searched_seq, np.uint8)
        seq_length = len(one_mismatch_matrix_list[0])
        mismatch_count_list = seq_length - \
            (one_mismatch_matrix_list * searched_seq).reshape(len(one_mismatch_matrix_list),-1).sum(axis=-1)
        mismatch_count_matrix = np.reshape(mismatch_count_list,(-1,4))
        return mismatch_count_matrix
    
    def return_mismatch_count_index_matrix(self, searched_seq, index):
        mismatch_count_matrix = self.return_mismatch_count_matrix(searched_seq)
        matrix_size = np.array(mismatch_count_matrix).shape
        index_matrix = np.ones(matrix_size) * int(index)
        #mismatch_count_index_matrix = np.dstack((mismatch_count_matrix, index_matrix))
        mismatch_count_index_matrix = np.array(list(
            zip(mismatch_count_matrix.ravel(),index_matrix.ravel())
            ), dtype=('i4,i4')).reshape(matrix_size)
        
        return mismatch_count_index_matrix



class one_mismatch_class:
    def __init__(self, query_seq, mismatch_data, PAM = 'NGG'):
        self.query_seq = query_seq#self.__return_changed_query_seq(query_seq, PAM)
        self.mismatch_data = mismatch_data
        self.selected_data = mismatch_data[mismatch_data['mismatch'] <= 5]
        self.__init_one_mismatch_data()
        
        self.__class_size = (len(self.query_seq) - len(PAM),4) 
        self.__init_one_mismatch_data()
        self.__selected_data_encoding()
        self.__init_one_mismatch_table_data()
        self.class_matrix = self.__return_class_matrix()[:-len(PAM),:]
        #self.tmp_class_matrix = self.__return_class_matrix()[:-len(PAM),:]


        self.data_matrix_dict = self.__return_class_matrix_dict()
        self.rank_data, self.rank_data_list, self.rank_data_list_query  \
                = self.__return_calc_rank()

    def return_rank_dataframe(self,):
        query_seq = self.query_seq
        rank_data = self.rank_data
        mismatch_count_length = len(rank_data['mismatch_count'][0].keys())
        data_length = len(rank_data['score'])
        
        new_rank_data_dict = {
            'rank' : np.array(range(1,data_length+1)),
            f'sequence({query_seq})' : rank_data['seq'],
            'score' : rank_data['score'].astype(np.float32),
        }
        
        for i in range(mismatch_count_length):
            new_rank_data_dict[f"mismatch_{i}"] = [ _data[i] for _data in rank_data['mismatch_count']]
            
        data_type = {
            'rank' : 'uint8',
            'score' : 'float32',
        }
        for i in range(mismatch_count_length):
            data_type[f"mismatch_{i}"] = 'uint32'
            
        dataframe = pd.DataFrame(new_rank_data_dict).astype(data_type)
        return dataframe
        
        
    def __return_class_matrix_dict(self,):
        data = {}
        data['seq'] = self.__return_mismatch_seq()
        data['score'] = self.__return_score()
        data['mismatch_count'] = self.__return_mismatch_count()
        data['score2rank_round_6_dict'] = self.__return_score2rank_round_6_dict(data['score'])
        
        return data
    
    def __return_calc_rank(self,):
        query_seq = self.query_seq

        score_reshape = self.__return_score().reshape(-1,)
        class_reshape = self.class_matrix.T.reshape(-1,)
        all_rank_seq = class_reshape / np.ones(len(class_reshape))
        rm_query_index = np.nonzero(all_rank_seq != query_seq)[0]
        single_query_index = np.nonzero(all_rank_seq == query_seq)[0][0]

        rm_dup_query_index = np.append(rm_query_index, single_query_index)

        rm_query_score = score_reshape[rm_dup_query_index]
        rm_query_class = class_reshape[rm_dup_query_index]


        rank_index = np.flip(rm_query_score.argsort())
        rank_length = len(rank_index)

        
        rank_data = {}
        rank_data['seq'] = rm_query_class[rank_index] / np.ones(rank_length)
        rank_data['score'] = rm_query_class[rank_index] * np.ones(rank_length) 
        rank_data['mismatch_count'] = rm_query_class[rank_index] - np.ones(rank_length)
        
        rank_data_list = []
        for i in range(rank_length):
            rank_data_list += [{
                'seq'            : rank_data['seq'][i],
                'score'          : rank_data['score'][i],
                'mismatch_count' : rank_data['mismatch_count'][i],
            }]

        #find query for webpage
        _query_index_rank = np.nonzero(rank_data['seq'] == query_seq)[0][0]
        rank_data_list_query = rank_data_list[_query_index_rank]
        
        return rank_data, rank_data_list, rank_data_list_query
        
    def __return_score(self,):
        return (self.class_matrix * np.ones(self.__class_size)).T
    
    def __return_mismatch_count(self,):
        return (self.class_matrix - np.ones(self.__class_size)).T
    
    def __return_mismatch_seq(self,):
        return (self.class_matrix / np.ones(self.__class_size)).T
        
        
    def __init_one_mismatch_data(self,):
        one_mismatch_data.inital_mismatch_dict(
            self.selected_data['mismatch'].value_counts().to_dict()
        )
        
    def __selected_data_encoding(self,):
        self.__query_seq_onehot = one_hot_encoder.seq_encoder(self.query_seq)
        selected_data_seq = self.selected_data['seq']
        self.__selected_data_index = np.array(selected_data_seq.keys())
        self.__selected_data_seq_one_hot = one_hot_encoder.batch_seq_encoder(list(selected_data_seq))
        
    def __init_one_mismatch_table_data(self,):
        self.__table_data = one_mismatch_table(self.__query_seq_onehot)
        self.__table_data_one_hot = self.__table_data.one_mismatch_matrix_list
        
    def __return_class_matrix(self,):
        table_data_one_hot = self.__table_data_one_hot
        selected_data_seq_one_hot = self.__selected_data_seq_one_hot
        selected_data_index = self.__selected_data_index
        table_data = self.__table_data
        
        #self.__class_size = (len(self.query_seq),4) 
        class_size = (len(self.query_seq),4) 
        class_matrix = []
        for i in range(class_size[0]):
            class_matrix += [[one_mismatch_data(table_data_one_hot[4*i+j]) for j in range(4)]]
        for _seq_one_hot, _index in zip(selected_data_seq_one_hot, selected_data_index):
            class_matrix += table_data.return_mismatch_count_index_matrix(_seq_one_hot,_index)
        return np.array(class_matrix)

    def __return_changed_query_seq(self, query_seq, PAM):
        query_seq = query_seq
        PAM = PAM

        PAM_length = len(PAM)
        changed_query_seq = query_seq[:-PAM_length] + 'N'*PAM_length
        return changed_query_seq

    def __return_score2rank_round_6_dict(self,score):
        score = np.array(score, dtype=np.float32).flatten()
        score_round = np.round(score,6)
        score_unique = np.unique(score_round)
        score_rank = np.flip(score_unique.argsort()) + 1
        score2rank_round_6_dict = {}
        for i in range(len(score_rank)):
            score2rank_round_6_dict[score_unique[i]] = score_rank[i]
        return score2rank_round_6_dict



    
def return_one_mm_heatmap_arrays(
    input_seq,
    mm_df,
):
    '''
    args:
        input_seq   : input_sequence without PAM, TGGGAGGGCCTGGATGGGGC
        mm_df       : one mismatch gRNA dataframe, contain rank, mm_index, seq, mm, mm_info..
    return:
        score_array : one mismatch gRNA score, shape: (4,seq_len)
        info_array  : one mismatch gRNA info[match, score, mm_0~4], shape: (4,seq_len)
    '''    
    from cas_offinder.processing_results import visualization_mismatch, find_by_mm_index

    index_table = visualization_mismatch.return_one_mm_heatmap_index_table(input_seq)
    mismatch_info = find_by_mm_index(mm_df)
    x = list(input_seq)
    y = ['A','C','G','T']

    score_array = np.zeros((len(y),len(x)),np.float32)
    info_array  = np.zeros(score_array.shape, 'O')

    for i in range(len(y)):
        for j in range(len(x)):
            _index = index_table[i,j]
            _mismatch_info_dict = mismatch_info.get_data_dict(_index)
            _score = _mismatch_info_dict['score']
            _num_mm = _mismatch_info_dict['num_mm']
            _mm_info = _mismatch_info_dict['mm_info']
            _rank = _mismatch_info_dict['rank']
            _mm_0 = _mismatch_info_dict['mismatch_0']
            _mm_1 = _mismatch_info_dict['mismatch_1']
            _mm_2 = _mismatch_info_dict['mismatch_2']
            _mm_3 = _mismatch_info_dict['mismatch_3']
            _mm_4 = _mismatch_info_dict['mismatch_4']

            score_array[i,j] = np.round(_score,2)
            if _num_mm == 0:
                match_flag = 'The original gRNA'
            else:
                match_flag = f'<b style="color:#CD5C5C">Mispaired </b>{_mm_info}'
            info_array[i,j] = f"{match_flag}\
            <br>score : {np.round(_score,4)}\
            <br>rank : {_rank}\
            <br>0: {_mm_0:>4d}\
            <br>1: {_mm_1:>4d}\
            <br>2: {_mm_2:>4d}\
            <br>3: {_mm_3:>4d}\
            <br>4: {_mm_4:>4d}"
    return score_array, info_array

def plotly_one_mismatch_heatmap(
    input_seq,
    score_array,
    info_array,
):
    '''
    args:
        input_seq   : input_sequence without PAM, TGGGAGGGCCTGGATGGGGC
        score_array : one mismatch gRNA score, shape: (4,seq_len)
        info_array  : one mismatch gRNA info[match, score, mm_0~4], shape: (4,seq_len)
    return:
        plotly_fig  : plotly heatmap

    '''
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    from plotly.offline import plot

    x = list(input_seq)
    y = ['A','C','G','T']

    fig = go.Figure(
        data = go.Heatmap(
            z = score_array,
            colorscale= 'pubu',
            showscale = False,
            text = info_array,
            hovertemplate = "%{text}<extra></extra>"
        ),
    )
    ff_fig_annotation = ff.create_annotated_heatmap(
        z = score_array,
        reversescale=True,
    ).layout.annotations
    fig.layout.annotations = ff_fig_annotation
    fig.layout.yaxis.autorange = "reversed"
    fig.update_yaxes(
        tickmode = 'array',
        tickvals = np.arange(0,len(y)),
        ticktext = y,
        fixedrange=True,
    )
    fig.update_xaxes(
        tickmode = 'array',
        tickvals = np.arange(0,len(x)),
        ticktext = x,
        side = 'top',
        fixedrange = True,
    )
    fig.update_layout(
        hovermode = "closest",
        clickmode = "select",
    )
    return fig



def plotly_heatmap_one_mismatch(
        query_seq, 
        PAM,
        data_score_array, 
        data_mismatch_count_array,
        score2rank_round_6_dict,
    ):
    import plotly.graph_objects as go
    import plotly.figure_factory as ff
    from plotly.offline import plot


    #pickle_data = data
    #score = data['score']
    #mismatch_count_dict_array = data['mismatch_count']
    PAM_len = len(PAM)
    seq = query_seq[:-PAM_len]
    score = data_score_array#[:,:-PAM_len]
    mismatch_count_dict_array = data_mismatch_count_array#[:,:-PAM_len]
    score2rank_round_6_dict = score2rank_round_6_dict

    #seq = query_seq[:PAM_length]
    x = list(seq)
    y = ['A','C','G','T']
    z = np.array(score, dtype=np.float32)

    count_flag = return_heatmap_mismatch_count_flag(
            mismatch_count_dict_array,
            score,
            score2rank_round_6_dict,
            x,
            y
        )

    fig = go.Figure(
    data = go.Heatmap(
            z=z,
            colorscale ='pubu',
            showscale  = False,
            text = count_flag,
            hovertemplate= "%{text}<extra></extra>",
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
    fig.update_layout(
        hovermode="closest",
        clickmode='select',
    )
    return fig
    

def return_heatmap_mismatch_count_flag(
        mismatch_count_dict_array,
        score,
        score2rank_round_6_dict,
        x,
        y
    ):
    x = x
    y = y
    dict_array = np.array(mismatch_count_dict_array)
    score = np.round(np.array(score,dtype=np.float32),6)
    score2rank_round_6_dict = score2rank_round_6_dict

    str_array = np.empty(dict_array.shape, dtype=object)
    shape = dict_array.shape
    for i in range(shape[0]):
        for j in range(shape[1]):
            if return_match_mismatch_tf(x[j],y[i]):
                match_flag = 'The original gRNA'
            else:
                match_flag = f'<b style="color:#CD5C5C">Mispaired </b> {x[j]}{y[i]}:{j+1}'
            j_item = dict_array[i][j]
            _score = str(np.round(score[i][j],4))
            _rank = score2rank_round_6_dict[score[i][j]]
            str_array[i][j] = f"{match_flag}\
            <br>score : {_score}\
            <br>rank : {_rank}\
            <br>0: {j_item[0]:>4d}\
            <br>1: {j_item[1]:>4d}\
            <br>2: {j_item[2]:>4d}\
            <br>3: {j_item[3]:>4d}\
            <br>4: {j_item[4]:>4d}"
    return str_array

def return_match_mismatch_tf(x,y):
    x = x
    y = y
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
    if y in site_type[x]:
        return True
    else:
        return False

    

def return_heatmap_match_flag(x,y):
    x = x
    y = y
    mat_flag = np.empty([len(y),len(x)], dtype=object)

    for j in range(len(y)):
        for i in range(len(x)):
            if return_match_mismatch_tf(x[i],y[j]):
                mat_flag[j][i] = '<b style="color:#CD5C5C">Match</b>'
            else:
                mat_flag[j][i] = 'Mismatch'

    return mat_flag




##################################################################
#                                                                #
# Generate Detail table By Golang library                        #
#                                                                #
##################################################################
class Detail_info_calculater_go:
    lib_path = './cas_offinder/library.so'
    def __init__(self,folder_path,org_dataframe):
        self.folder_path = folder_path
        self.org_csv_path = f'{self.folder_path}idx_seq.csv'
        self.org_dataframe = org_dataframe
        
        idx_seq_df = self.index_seq_df(org_dataframe)
        self.save_df(self.org_csv_path,idx_seq_df)
        
    
    def index_seq_df(self, dataframe):
        index_col = 'index'
        seq_col   = 'seq'
        new_df = dataframe[[index_col,seq_col]]
        return new_df

    def save_df(self,file_name,dataframe):
        dataframe.to_csv(
            file_name,
            index=False,
            header=True,
        )

    def read_idx_seq_csv(self,file_name):
        result_csv = pd.read_csv(file_name)
        return result_csv



    def return_rank_IdxSeqMM_df(self, rank, rank_gRNA):
        IdxSeqMM_csv_path = f'{self.folder_path}/rank_{rank}_IdxSeqMM.csv'
        result_csv_path = self.make_idx_seq_mm_df_go(
            input_seq=rank_gRNA,
            idx_seq_path=self.org_csv_path,
            save_path=IdxSeqMM_csv_path,
            lib_path=Detail_info_calculater_go.lib_path,
        )

        rank_detail_df = self.read_result_csv(result_csv_path)
        return rank_detail_df, IdxSeqMM_csv_path

    def read_result_csv(self, file_name):
        data_type = {
            'mismatch' : 'int8'
        }
        result_csv = pd.read_csv(file_name).astype(data_type)
        return result_csv

    def generate_new_detail_df(self, rank_gRNA, org_df, idx_seq_mm_df):
        org_gRNA = org_df['query'][0]
        idx_seq_mm_df = idx_seq_mm_df.sort_values(by='index')
        rank_detail_df = org_df.sort_values(by='index')
        rank_detail_df['query'] = rank_detail_df['query'].replace({org_gRNA: rank_gRNA})
        rank_detail_df['seq'] = idx_seq_mm_df['seq']
        rank_detail_df['mismatch'] = idx_seq_mm_df['mismatch']
        return rank_detail_df



    def make_idx_seq_mm_df_go(self, input_seq, idx_seq_path, save_path, lib_path):
        #import ctypes
        #lib_path = '/root/volume/golang/workspace/compare_seq/library.so'
        class GoString(ctypes.Structure):
            _fields_ = [("p", ctypes.c_char_p), ("n", ctypes.c_longlong)]

        library = ctypes.cdll.LoadLibrary(lib_path)
        result_path = save_path
        query = input_seq
        data_path = idx_seq_path
        print(input_seq)



        result_path_go = GoString(result_path.encode('utf-8'), len(result_path))
        query_go = GoString(query.encode('utf-8'), len(query))
        data_path_go = GoString(data_path.encode('utf-8'), len(data_path))

        library.ResultSaveCSV.argtypes = [GoString, GoString, GoString]
        library.ResultSaveCSV.restype = GoString

        _ = library.ResultSaveCSV(result_path_go, query_go, data_path_go)
        return save_path











if __name__ == '__main__':
    _dir =  '/root/volume/cas-offinder-web-tmp/django/test_script'
    #file_name = "Job1-test0216_output.txt"
    file_name = 'Job1_no_match.txt'
    path = f"{_dir}/{file_name}"
    header = ["query", "chr", "site", "seq", "direction", "mismatch"]
    column_type = {'query' : 'category',
                   'chr' : 'category',
                   'site' : 'uint32',
                   'direction' : 'category',
                   'mismatch' : 'uint32',
                  }

    data = pd.read_csv(path, sep='\t', names=header, dtype=column_type)
    
    #query_seq = 'TGGGAGGGCCTGGATGGGGCNGG'
    query_seq = 'TGGGAGGGCCATGATGGGGCNGG'#
    searched_data = data
    tmp_one_mismatch = one_mismatch_class(query_seq, searched_data)
