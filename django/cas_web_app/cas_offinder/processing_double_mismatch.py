from __future__ import absolute_import, unicode_literals
import numpy as np
import pandas as pd

from cas_offinder.seq_encoder_decoder import *
import cas_offinder.seq_encoder_decoder as en_de


def query2mismatch_number(mis_query, query, dim=5):
    if len(mis_query) != len(query):
        assert len(mis_query) < len(query), \
                f"mis_query : {len(mis_query)}, query : {len(query)}"
        mis_query_length = len(mis_query)
        query = query[:mis_query_length]

    mis_query_index_list = convert_query2index_list(mis_query)
    query_index_list = convert_query2index_list(query)

    _sub = mis_query_index_list - query_index_list
    with np.errstate(divide='ignore'):
        mis_query_off_index = np.floor_divide(_sub,_sub) * mis_query_index_list
    mis_query_index = int(''.join(map(str,mis_query_off_index)),dim)
    return mis_query_index

def convert_query2index_list(query):
    if type(query) == str:
        query_one_hot = one_hot_encoder.seq_encoder(query)
    else:
        query_one_hot = query
    query_index_list = np.argmax(query_one_hot, axis = -1) + 1
    return query_index_list

def convert_index2query_one_hot(seq_index):
    one_hot_index = seq_index -1
    one_hot = np.eye(4)[one_hot_index]
    return one_hot

def convert_scale(n, scale=5):
    answer_reversed = ''
    while n > 0:
        n, re = divmod(n,scale)
        answer_reversed += str(re)
    answer = answer_reversed[::-1]
    return answer

def index2code(index_num, length=20, scale=5):
    index_rescaled = convert_scale(index_num, scale)
    code = str(index_rescaled).rjust(length, '0')
    return code

def double_mismatch_index_generate(query_index, PAM, dim=5):
    if type(query_index) == str:
        query_index = convert_query2index_list(query_index)
    acgt_list = np.arange(1,dim)
    PAM_length = len(PAM)
    query = query_index[:-PAM_length]
    query_length = len(query)
    double_mis_list = []
    for i in range(query_length):
        for j in range(i+1, query_length):
            _mut_pos_1 = query[i]
            _mut_pos_2 = query[j]
            for _mut_1 in np.delete(acgt_list,_mut_pos_1-1):
                for _mut_2 in np.delete(acgt_list, _mut_pos_2-1):
                    _tmp_query = np.array(query).copy()
                    _tmp_query[i] = _mut_1
                    _tmp_query[j] = _mut_2
                    double_mis_list.append(_tmp_query)
    double_mis_list = np.array(double_mis_list)
    return double_mis_list
    
def one_mismatch_index_generate(query_index, PAM, dim=5):
    if type(query_index) == str:
        query_index = convert_query2index_list(query_index)
    acgt_list = np.arange(1,dim)
    PAM_length = len(PAM)
    query_index = query_index
    query = query_index[:-PAM_length]
    query_length = len(query)
    one_mis_list = []
    for i in range(query_length):
        _mut_pos = query[i]
        for _mut in np.delete(acgt_list, _mut_pos -1):
            _tmp_query = np.array(query).copy()
            _tmp_query[i] = _mut
            one_mis_list.append(_tmp_query)
    one_mis_list = np.array(one_mis_list)
    return one_mis_list


####################################################
#                                                  #
# New mismatch generator and analysis              #
#                                                  #
####################################################

class mm_generator:
    mm_change_dict = {
        1 : np.array([2,3,4], np.int8),
        2 : np.array([1,3,4], np.int8),
        3 : np.array([1,2,4], np.int8),
        4 : np.array([1,2,3], np.int8),
        5 : None,
    }

    @classmethod
    def generator_1_mm(cls,seq):
        seq_index = np.array(en_de.acgt2seq_index(seq,join=False))
        one_mm_list = []
        for _index, _letter in enumerate(seq_index):
            change_list = cls.mm_change_dict.get(_letter,None)
            if change_list is not None:
                for _change_letter in change_list:
                    _tmp_seq = seq_index.copy()
                    _tmp_seq[_index] = _change_letter
                    one_mm_list.append(en_de.seq_index2acgt(_tmp_seq))
        return one_mm_list

    @classmethod
    def generator_2_mm(cls, seq):
        seq_index = np.array(en_de.acgt2seq_index(seq,join=False))
        seq_length = len(seq_index)
        two_mm_list = []
        for _index_1 in range(0,seq_length-1):
            _letter_1 = seq_index[_index_1]
            _change_list_1 = cls.mm_change_dict.get(_letter_1, None)
            if _change_list_1 is None:
                continue
            for _change_letter_1 in _change_list_1:

                for _index_2 in range(_index_1 + 1,seq_length):
                    _letter_2 = seq_index[_index_2]
                    _change_list_2 = cls.mm_change_dict.get(_letter_2, None)
                    if _change_list_2 is None:
                        continue
                    for _change_letter_2 in _change_list_2:
                        _tmp_seq = seq_index.copy()
                        _tmp_seq[_index_1] = _change_letter_1
                        _tmp_seq[_index_2] = _change_letter_2
                        two_mm_list.append(en_de.seq_index2acgt(_tmp_seq))

        return two_mm_list
                


class mismatch_df:
    def __init__(self,
        seq,
        cas_offinder_seq_list,
        PAM='NGG',
        PAM_end=True,
        max_range=4,
        dis_weight = [1,1,1,1,0.5],
    ):
        '''
        args : 
            seq             : query sequence, Not contain PAM! , TTTTGGGCGGGCCAAACTGC
            cas_offinder    : cas_offinder result, only mismatch site,
                                array(['TgTgGGGCGGcaCAAACTcCAGG', 'cTTTGGGaGGcCCAggCTGCAGG',
                                       'TTTTGtGtGtGCCAAAgTGaTGG', 'TTTTaGGgGGGCCcAcCTcCTGG',
                                       'cTTTGGGCGGcCaAgACTGgAGG', 'TTTgGaGtGGGCCAAgCTGtGGG',
                                       'TcTTGGGCctcCCAAAgTGCTGG', 'ggcTGGGtGGGCCAAAgTGCGGG', ...)
            PAM             : CRISPR PAM type, SpCas9(NGG), AsCpf1(TTTN)
            PAM_end         : PAM position, SpCAs9 - PAM_end=True, AsCpf1 - PAM_end=False
            max_range       : maxinum number of mismatch to show
            dis_weight      : weight of mismatch number,
                                [-1,1,1,1,0.5] -> mismatch_0~3 : weight 1
                                                 mismatch_4   : weight 0.5
        '''
        self.seq = seq
        self.max_range = max_range
        self.cas_offinder_seq_list = cas_offinder_seq_list
        one_mm_list = mm_generator.generator_1_mm(self.seq)
        two_mm_list = mm_generator.generator_2_mm(self.seq)
        self.one_mm_length = len(one_mm_list)
        self.two_mm_length = len(two_mm_list)
        self.__mm_list = one_mm_list + two_mm_list

        self.__mm_list_mm_index = self.__mm_indexing(self.__mm_list)
        self.__mm_list_seq_index = self.__seq_indexing(self.__mm_list)
        self.__mm_list_mm_info = self.__mm_info(self.__mm_list)

        self.mismatch_count_df = self.return_mm_count_df(
            max_range=max_range,
            mm_list = self.__mm_list,
            seq_list = self.cas_offinder_seq_list,
            PAM = PAM,
            PAM_end = PAM_end,
        )
        _mm_count_list = self.mismatch_count_df[[f'mismatch_{i}' for i in range(max_range+1)]].to_numpy()
        self.query_mm_list = self.__return_query_mm_list(
            query=self.seq,
            seq_list = self.cas_offinder_seq_list,
            PAM=PAM,
            PAM_end=PAM_end,
            max_range=max_range
        )
        self.query_mm_dict = self.__return_query_mm_dict(
            query_PAM = mismatch_df.mm_seq_add_PAM(self.seq,PAM,PAM_end),
            query     = self.seq,
            mm_list   = self.query_mm_list,
        )

        self.mm_score = self.return_score_list(
            query_mm_count = self.query_mm_list,
            mm_count_list = _mm_count_list,
            dis_weight= dis_weight,
        )
        #self.mm_score_one, self.mm_rank_one = self.return_score_rank_list(
        #    query_mm_count = self.query_mm_list[:len(one_mm_list)],
        #    mm_count_list = _mm_count_list[:len(one_mm_list)],
        #    dis_weight= dis_weight,
        #)

        __mismatch_df = mismatch_df.dataframe_add_PAM(
            dataframe   = self.__return_mm_df(),
            PAM         = PAM,
            PAM_end     = PAM_end
        )
        self.mismatch_df_one   = self.__return_mm_df_one(__mismatch_df)
        self.mismatch_df_two   = self.__return_mm_df_two(__mismatch_df)
        self.mismatch_df_total = self.__return_mm_df_total(__mismatch_df)

    def __return_mm_df(self,):
        mm_index_list   = self.__mm_list_mm_index
        mm_seq_list     = self.__mm_list
        mm_list         = np.append(
            np.ones(self.one_mm_length,np.int8),
            np.ones(self.two_mm_length,np.int8)*2)
        mm_info_list    = self.__mm_list_mm_info
        seq_index_list  = self.__mm_list_seq_index
        mm_count_df     = self.mismatch_count_df
        mm_score_list   = self.mm_score
        #mm_rank_list    = self.mm_rank

        #query_info_dict = self.query_mm_dict

        mm_dict = {
            'mm_index'  : mm_index_list  ,
            'target'    : mm_seq_list    ,
            'num_mm'    : mm_list        ,
            'mm_info'   : mm_info_list   ,
            'seq_index' : seq_index_list ,
            #'rank'      : mm_rank_list   ,
            'score'     : mm_score_list  ,
        }
        mm_df = pd.DataFrame(mm_dict)
        #mm_df = pd.concat([mm_df,mm_count_df], axis=1)
        for i in range(len(mm_count_df.columns)):
            mm_df.loc[:,f'mismatch_{i}'] = mm_count_df[f'mismatch_{i}']
        #mm_df = mm_df.append(query_info_dict,ignore_index=True)
        #mm_df = self.__compress_dataframe(mm_df,self.max_range)
        return mm_df

    def __return_mm_df_condition(self,mm_dataframe,num_mm):
        if num_mm is not None:
            mm_df = mm_dataframe[mm_dataframe['num_mm']==num_mm]
        else:
            mm_df = mm_dataframe
        mm_df.insert(0, 'rank',self.return_rank_list(mm_df.loc[:,'score'].to_numpy()))
        query_info_dict = self.query_mm_dict
        mm_df = mm_df.append(query_info_dict,ignore_index=True)
        mm_df = self.__compress_dataframe(mm_df,self.max_range)
        return mm_df

    def __return_mm_df_one(self,mm_dataframe):
        mm_df = self.__return_mm_df_condition(mm_dataframe,1)
        return mm_df

    def __return_mm_df_two(self, mm_dataframe):
        mm_df = self.__return_mm_df_condition(mm_dataframe,2)
        return mm_df

    def __return_mm_df_total(self, mm_dataframe):
        mm_df = self.__return_mm_df_condition(mm_dataframe,None)
        return mm_df

    def __compress_dataframe(self,dataframe,max_range):
        compress_rule = {
            'rank'      : 'integer',
            'score'     : 'float',
            'num_mm'    : 'integer',
        }
        for i in range(max_range+1):
            compress_rule[f'mismatch_{i}'] = 'integer'
        for _key, _value in compress_rule.items():
            dataframe[_key] = pd.to_numeric(dataframe[_key],errors='ignore',downcast=_value)
        return dataframe

    def __mm_indexing(self,mm_list):
        mm_index_list = list(map(
            lambda mm_seq : en_de.mismatch_calculator.mm_indexing(self.seq,mm_seq),
            mm_list))
        return mm_index_list

    def __seq_indexing(self,mm_list):
        seq_index_list = list(map(
            lambda mm_seq : en_de.acgt2seq_index(mm_seq,join=True,convert_int=True),
            mm_list))
        return seq_index_list

    def __mm_info(self,mm_list):
        mm_info_list = list(map(
            lambda mm_seq : en_de.mismatch_calculator.seq_mismatch_info_str(self.seq,mm_seq),
            mm_list))
        return mm_info_list

    def __return_query_mm_list(self,query,seq_list, PAM='NGG',PAM_end=True, max_range=4):
        query_mm_dict = self.__calc_mm_dict_list([query], seq_list,'NGG',True)
        return [query_mm_dict[0].get(i,0) for i in range(max_range+1)]
    
    def __return_query_mm_dict(self,query_PAM, query, mm_list):
        info_dict = {
            'mm_index' : ''.join(['0' for _ in range(len(query))]),
            'target'   : query_PAM,
            'num_mm'   : np.int8(0),
            'mm_info'  : '',
            'seq_index': en_de.acgt2seq_index(query,True,True),
            'score'    : 0.,
            'rank'     : 0,
        }
        for index, num in enumerate(mm_list):
            info_dict[f'mismatch_{index}'] = num
        return info_dict
    
    @classmethod
    def mm_seq_list_rm_PAM(cls, seq_list, PAM='NGG', PAM_end=True):
        def remove_PAM(seq_list, PAM, PAM_end):
            PAM_len = len(PAM)
            if not PAM_end:
                return list(map(lambda mm_seq : mm_seq[PAM_len:],seq_list))
            else:
                return list(map(lambda mm_seq : mm_seq[:-PAM_len],seq_list))
        seq_list_rmd = remove_PAM(seq_list, PAM, PAM_end)
        #seq_list_encoded = en_de.one_hot_encoder.batch_seq_encoder(seq_list_rmd)
        return seq_list_rmd
    @classmethod
    def mm_seq_add_PAM(cls, seq, PAM='NGG', PAM_end=True):
        PAM_len = len(PAM)
        if not PAM_end:
            return f'{PAM}{seq}'
        else:
            return f'{seq}{PAM}'
    @classmethod
    def dataframe_add_PAM(cls, dataframe, PAM='NGG', PAM_end=True):
        target_list = np.array(dataframe['target'])
        target_add_PAM_list = list(map(
            lambda target : cls.mm_seq_add_PAM(target,PAM,PAM_end),
            target_list
        ))
        dataframe['target'] = target_add_PAM_list
        return dataframe

    def __calc_mm_dict_list(self, mm_list, seq_list, PAM='NGG', PAM_end=True):
        rm_PAM_list = self.mm_seq_list_rm_PAM(seq_list,PAM,PAM_end)
        mm_target_encoded = en_de.one_hot_encoder.batch_seq_encoder(mm_list)
        seq_list_encoded  = en_de.one_hot_encoder.batch_seq_encoder(rm_PAM_list)

        mm_seq_mm_dict = []
        for _mm_target in mm_target_encoded:
            _sub = _mm_target[None,:] - seq_list_encoded[:]
            _clip = np.clip(_sub,0, None)
            _calc_mm_list = np.sum(_clip, axis=(1,2), dtype=np.int8)
            _unique, _count = np.unique(_calc_mm_list, return_counts=True)
            mm_seq_mm_dict.append(dict(zip(_unique, _count)))
        return mm_seq_mm_dict

    def return_mm_count_df(self,
        max_range,
        mm_list,
        seq_list,
        PAM='NGG',
        PAM_end=True,
    ):
        mm_dict_list = self.__calc_mm_dict_list(mm_list,seq_list,PAM,PAM_end)
        mm_info_df = pd.DataFrame(mm_dict_list,dtype=np.int32).fillna(0).astype(np.int32)
        mm_info_df = mm_info_df.reindex(sorted(mm_info_df.columns),axis=1)
        
        drop_start = max_range + 1
        drop_end   = max(mm_info_df.columns) + 1
        mm_info_df = mm_info_df.drop(columns=range(drop_start,drop_end))
        _columns = list(mm_info_df.columns)
        for i in range(drop_start):
            if not i in _columns:
                mm_info_df[i] = pd.Series(np.zeros(len(mm_info_df)),dtype=np.int32)
            mm_info_df = mm_info_df.rename(columns={i : f'mismatch_{i}'})

        return mm_info_df

    def return_score_list(self,
        query_mm_count,
        mm_count_list,
        dis_weight,
    ):
        div_query_mm_count = np.clip(query_mm_count,1,None)
        ideal_mm_count = return_ideal_mm_count(query_mm_count,len(dis_weight)-1)
        
        query_distance = np.sum(np.absolute(
            ideal_mm_count/div_query_mm_count - query_mm_count/div_query_mm_count
        )*dis_weight, dtype=np.float32)
        distance_list = np.sum(np.absolute(
            ideal_mm_count/div_query_mm_count - mm_count_list/div_query_mm_count
        )* dis_weight,axis=1,dtype=np.float32)
        score_list = ((query_distance - distance_list)/query_distance).astype(np.float32)
        #rank_list = (len(score_list)- score_list.argsort().argsort()).astype(np.int32)
        #return score_list, rank_list
        return score_list

    def return_rank_list(self,
        score_list
    ):
        scroe_list = np.array(score_list,np.float32)
        rank_list = (len(score_list)- score_list.argsort().argsort()).astype(np.int32)
        return rank_list



def return_ideal_mm_count(query_mm_count_list, max_range=4):
    query_mm_count = np.array(query_mm_count_list, np.int32)
    ideal_mm_count = np.zeros(max_range + 1, np.int32)
    for _index, _num in enumerate(query_mm_count):
        if int(_num) != 0 and _index+1 < max_range+1:
            ideal_mm_count[_index+1] = 1
            break
    return ideal_mm_count

def return_ideal_2mm_count(query_mm_count_list, max_range=4):
    query_mm_count = np.array(query_mm_count_list, np.int32)
    ideal_mm_count = np.zeros(max_range + 1, np.int32)
    for _index, _num in enumerate(query_mm_count):
        if int(_num) != 0 and _index+2 < max_range+1:
            ideal_mm_count[_index+2] = 1
            break
    return ideal_mm_count

