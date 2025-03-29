from __future__ import absolute_import, unicode_literals
import numpy as np


class one_hot_encoder:
    one_hot_encoder_dict = {
        'A' : np.array([1,0,0,0],dtype=np.int8),
        'a' : np.array([1,0,0,0],dtype=np.int8),
        'C' : np.array([0,1,0,0],dtype=np.int8),
        'c' : np.array([0,1,0,0],dtype=np.int8),
        'G' : np.array([0,0,1,0],dtype=np.int8),
        'g' : np.array([0,0,1,0],dtype=np.int8),
        'T' : np.array([0,0,0,1],dtype=np.int8),
        't' : np.array([0,0,0,1],dtype=np.int8),
        
        'R' : np.array([1,0,1,0],dtype=np.int8),
        'Y' : np.array([0,1,0,1],dtype=np.int8),
        'S' : np.array([0,1,1,0],dtype=np.int8),
        'W' : np.array([1,0,0,1],dtype=np.int8),
        'K' : np.array([0,0,1,1],dtype=np.int8),
        'M' : np.array([1,1,0,0],dtype=np.int8),
        
        'B' : np.array([0,1,1,1],dtype=np.int8),
        'D' : np.array([1,0,1,1],dtype=np.int8),
        'H' : np.array([1,1,0,1],dtype=np.int8),
        'V' : np.array([1,1,1,0],dtype=np.int8),
        
        'N' : np.array([1,1,1,1],dtype=np.int8),
        'n' : np.array([1,1,1,1],dtype=np.int8), #'n'????
    }
    
    @classmethod
    def letter_encoder(cls, letter):
        return cls.one_hot_encoder_dict[letter]
    
    @classmethod
    def seq_encoder(cls, sequence):
        one_hot_seq = list(map(cls.letter_encoder, sequence))
        one_hot_seq = np.array(one_hot_seq)
        return one_hot_seq
    
    @classmethod
    def batch_seq_encoder(cls, batch_seq):
        batch_seq_one_hot = []
        for seq in batch_seq:
            batch_seq_one_hot.append(cls.seq_encoder(seq))
        return np.array(batch_seq_one_hot)
    
    @classmethod
    def average_distribution(cls, seq_list):
        seq_num     = len(seq_list)
        seq_length  = len(seq_list[0])

        dist_arr = np.zeros((seq_length, 4))
        for seq in seq_list:
            dist_arr += cls.seq_encoder(seq)
        return dist_arr.T/seq_num
    
    
class one_hot_decoder:
    one_hot_decoder_dict = {
        '1000' : 'A',
        '0100' : 'C',
        '0010' : 'G',
        '0001' : 'T',
        
        '1010' : 'R',
        '0101' : 'Y',
        '0110' : 'S',
        '1001' : 'W',
        '0011' : 'K',
        '1100' : 'M',
        
        '0111' : 'B',
        '1011' : 'D',
        '1101' : 'H',
        '1110' : 'V',
        
        '1111' : 'N'
    }
    
    @classmethod
    def letter_decoder(cls, letter_code):
        return cls.one_hot_decoder_dict[letter_code]
    
    @classmethod
    def seq_decoder(cls, seq_one_hot):
        seq_letter_list = []
        for letter_one_hot in seq_one_hot:
            one_hot_pos_list = np.array(letter_one_hot, dtype=np.int8)
            one_hot_pos_code = ''.join(map(str,one_hot_pos_list))
            seq_letter_list += cls.letter_decoder(one_hot_pos_code)
        seq = ''.join(seq_letter_list)
        return seq



def acgt2seq_index(seq, join=False, convert_int=False):
    '''
    input : ACGT
    ouput : 12345

    convert Sequence to number
    '''
    acgt_dict = {
        'A' : 1,
        'a' : 1,
        'C' : 2,
        'c' : 2,
        'G' : 3,
        'g' : 3,
        'T' : 4,
        't' : 4,
        'N' : 5,
        'n' : 5,
    }
    seq_index_list =  list(map(lambda x: acgt_dict.get(x,None),seq))
    if join:
        result = ''.join(list(map(str,seq_index_list)))
        if convert_int: return int(result)
        else: return result
    else:
        return np.array(seq_index_list)

def seq_index2acgt(seq_index, join=True):
    '''
    input : 1234
    output : ACGT

    convert sequence index to sequence
    '''
    num_acgt_dict = {
        1 : 'A',
        2 : 'C',
        3 : 'G',
        4 : 'T',
        5 : 'N',
    }
    result = list(map(lambda x : num_acgt_dict.get(x,'-'),seq_index))
    if join:
        result = ''.join(result)
    else:
        result = np.array(result)
    return result


class mismatch_calculator:

    prime_main_encoder_dict = {
        'A' : 1,
        'a' : 1,
        'C' : 2,
        'c' : 2,
        'G' : 3,
        'g' : 3,
        'T' : 5,
        't' : 5,
        
        'N' : 0,
        'n' : 0, #'n'????
    }

    prime_sub_encoder_dict = {
        'A' : 7,
        'a' : 7,
        'C' : 11,
        'c' : 11,
        'G' : 13,
        'g' : 13,
        'T' : 17,
        't' : 17,
        
        'N' : 0,
        'n' : 0, #'n'????
    }

    prime_mm_index_sub_encoder_dict = {
        '0' : 0,
        '1' : 7,
        '2' : 11,
        '3' : 13,
        '4' : 17,
    }
    
    prime_multi_encoder_dict = {
        7  : None,
        11 : 'A>C',
        13 : 'A>G',
        17 : 'A>T',
        14 : 'C>A',
        22 : None,
        26 : 'C>G',
        34 : 'C>T',
        21 : 'G>A',
        33 : 'G>C',
        39 : None,
        51 : 'G>T',
        35 : 'T>A',
        55 : 'T>C',
        65 : 'T>G',
        85 : None,
        
        0  : None, # N,n
    }

    prime_mm_index_encoder_dict = {
        7  : '0', #None,
        11 : '2', #'A>C',
        13 : '3', #'A>G',
        17 : '4', #'A>T',
        14 : '1', #'C>A',
        22 : '0', #None,
        26 : '3', #'C>G',
        34 : '4', #'C>T',
        21 : '1', #'G>A',
        33 : '2', #'G>C',
        39 : '0', #None,
        51 : '4', #'G>T',
        35 : '1', #'T>A',
        55 : '2', #'T>C',
        65 : '3', #'T>G',
        85 : '0', #None,
        
        0  : '0', #None, # N,n
    }

    @classmethod
    def seq_prime_encoder(cls, query, type_dict):
        '''
        args:
            query       : query sequence, ACGTAAA
            type_dict   : convert type dictionary, prime main or sub
        return:
            prime_encoded_query : encoded sequence, [1,2,3,4,1,1,1]
        '''
        prime_encoded_query = list(map(type_dict.get,query))
        prime_encoded_query = np.array(prime_encoded_query,dtype=np.int8)
        return prime_encoded_query

    @classmethod
    def __seq_mismatch_info_list(cls, query_1, query_2):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : query sequence, AAGT
        return:
            mismatch_list : mismatch information, [None, C>A, None, None]
        '''
        query_1_prime_encoded = cls.seq_prime_encoder(query_1, cls.prime_main_encoder_dict)
        query_2_prime_encoded = cls.seq_prime_encoder(query_2, cls.prime_sub_encoder_dict)

        query_multiply = query_1_prime_encoded * query_2_prime_encoded
        mismatch_list = list(map(cls.prime_multi_encoder_dict.get,query_multiply))
        return mismatch_list

    @classmethod
    def __seq_mismatch_position_info_list(cls, query_1, query_2):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : query sequence, AAGT
        return:
            mismatch_info_list : mismatch information with position, [2:C>A]
        '''
        mismatch_list = cls.__seq_mismatch_info_list(query_1, query_2)
        mismatch_info_list = []
        for index, _info in enumerate(mismatch_list):
            if _info:
                _info_str = f"{index+1}:{_info}"
                mismatch_info_list.append(_info_str)
        return mismatch_info_list

    @classmethod
    def seq_mismatch_info_list(cls, query_1, query_2):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : query sequence, AAGT
        return:
            mismatch_info_list : list, mismatch information with position, [2:C>A]
        '''
        mismatch_info_list = cls.__seq_mismatch_position_info_list(query_1, query_2)
        return mismatch_info_list

    @classmethod
    def seq_mismatch_info_str(cls, query_1, query_2):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : query sequence, AACT
        return:
            mismatch_info_str : str, mismatch information with position, '2:C>A,3:G>C'
        '''
        mismatch_info_list = cls.__seq_mismatch_position_info_list(query_1, query_2)
        mismatch_info_str = ','.join(mismatch_info_list)
        return mismatch_info_str

    @classmethod
    def seq_mismatch_count(cls,query_1, query_2):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : query sequence, AACT
        return:
            mismatch_count : mismatch count, 2
        '''
        query_1_one_hot = one_hot_encoder.seq_encoder(query_1)
        query_2_one_hot = one_hot_encoder.seq_encoder(query_2)
        mismatch_matrix = np.clip(query_1_one_hot - query_2_one_hot, 0, None)
        mismatch_count = np.sum(mismatch_matrix)
        return mismatch_count

    @classmethod
    def seq_mismatch_count_list(cls,query, mismatch_seq_list):
        '''
        args:
            query_1     : query sequence, ACGT
            query_2     : mismatch sequence list, [AACT, AACG, AACC]
        return:
            mismatch_count_list : mismatch count list, [2,3,3]
        '''
        mismatch_count_list = list(map(
            lambda mismatch_seq: cls.seq_mismatch_count(query,mismatch_seq),
            mismatch_seq_list
        ))
        return mismatch_count_list

    @classmethod
    def mm_indexing(cls, query, mm_seq):
        '''
        args:
            query       : query seq, ACGT
            mm_seq      : mismatch sequence, ACGG
        return:
            mm_index    : mismatch sequence index, str, '0003'
        '''
        query_1_prime_encoded = cls.seq_prime_encoder(query, cls.prime_main_encoder_dict)
        query_2_prime_encoded = cls.seq_prime_encoder(mm_seq, cls.prime_sub_encoder_dict)
        query_multiply = query_1_prime_encoded * query_2_prime_encoded
        mismatch_list = list(map(cls.prime_mm_index_encoder_dict.get,query_multiply))
        mm_index = ''.join(mismatch_list)
        return mm_index

    @classmethod
    def seq_mismatch_change_from_mm_index(cls,mm_index, query):
        query_1_prime_encoded = cls.seq_prime_encoder(query, cls.prime_main_encoder_dict)
        query_2_prime_encoded = cls.seq_prime_encoder(mm_index, cls.prime_mm_index_sub_encoder_dict)
        assert len(query_1_prime_encoded) == len(query_2_prime_encoded), \
            f'Check seq or query length, Q {len(query_1_prime_encoded)}, I {len(query_2_prime_encoded)}'

        query_multiply = query_1_prime_encoded * query_2_prime_encoded
        mismatch_list = list(map(cls.prime_multi_encoder_dict.get,query_multiply))
        mismatch_info_list = list()
        for index, _info in enumerate(mismatch_list):
            if _info:
                _info_str = f"{index+1}:{_info}"
                mismatch_info_list.append(_info_str)
        return mismatch_info_list
