from __future__ import absolute_import, unicode_literals
from django.conf import settings

from cas_offinder.default_setting import check_opencl_device


class job_data:
    job_data_path = settings.JOB_DATA_PATH
    run_device    = None
    def __init__(self):#, ref_file_path, job_data_path, run_device):
        self.UUID = None
        self.results_url  = None
        self.job_title = None
        self.seq       = None
        self.ref       = None
        self.ref_file_path = settings.REF_DIR
        #self.job_data_path = job_data_path
        self.PAM_type  = None
        self.mismatch  = 3
        self.start_time = None
        self.end_time = None
        #self.run_device = run_device
        self.email = None
    def __str__(self):
        return str(self.UUID)
    def job_data_script_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/"
    def job_command_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/{self.job_title}.sh"
    def job_input_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/{self.job_title}_input.txt"
    def job_output_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/{self.job_title}_output.txt"
    def job_search_seq(self):
        seq = self.seq
        pam = self.PAM_type
        return f"{seq}{pam}"
    def job_pickle_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/{self.job_title}_data.pickle"
    def job_parquet_path(self):
        return f"{job_data.job_data_path}/{self.UUID}/{self.job_title}_data.parquet"
    def results_url_link(self):
        return f'<a href="{self.results_url}">Page link</a>'
    @classmethod
    def job_data_default_setting(cls,*args):
        if cls.run_device == None:
            run_device = check_opencl_device()
            cls.run_device    = run_device


class ref_data:
    def __init__(self, initial, path):
        self.initial = initial
        self.explain = None
        self.url     = None
        self.path    = path
    def __str__(self):
        return self.initial

class PAM_data:
    def __init__(self, initial, PAM):
        self.initial = initial 
        self.explain = None
        self.PAM = PAM
    def __str__(self):
        return self.initial



def find_ucsc_initial(file_name):
    import re
    ucsc_list = ['hg38',
    'hg19',
    'hg18',
    'hg17',
    'hg16',
    'vicPac2',
    'vicPac1',
    'dasNov3',
    'papAnu4',
    'papAnu2',
    'papHam1',
    'bisBis1',
    'panPan3',
    'panPan2',
    'panPan1',
    'aptMan1',
    'otoGar3',
    'felCat9',
    'felCat8',
    'felCat5',
    'felCat4',
    'felCat3',
    'panTro6',
    'panTro5',
    'panTro4',
    'panTro3',
    'panTro2',
    'panTro1',
    'criGri1',
    'criGriChoV2',
    'criGriChoV1',
    'manPen1',
    'bosTau9',
    'bosTau8',
    'bosTau6',
    'bosTau4',
    'bosTau3',
    'bosTau2',
    'macFas5',
    'canFam4',
    'canFam3',
    'canFam2',
    'canFam1',
    'turTru2',
    'loxAfr3',
    'musFur1',
    'thaSir1',
    'nomLeu3',
    'nomLeu2',
    'nomLeu1',
    'aquChr2',
    'rhiRox1',
    'gorGor6',
    'gorGor5',
    'gorGor4',
    'gorGor3',
    'chlSab2',
    'cavPor3',
    'neoSch1',
    'eriEur2',
    'eriEur1',
    'equCab3',
    'equCab2',
    'equCab1',
    'dipOrd1',
    'galVar1',
    'triMan1',
    'calJac3',
    'calJac1',
    'pteVam1',
    'myoLuc2',
    'balAcu1',
    'mm10',
    'mm9',
    'mm8',
    'mm7',
    'micMur2',
    'micMur1',
    'hetGla2',
    'hetGla1',
    'monDom5',
    'monDom4',
    'monDom1',
    'ponAbe2',
    'ponAbe3',
    'ailMel1',
    'susScr11',
    'susScr3',
    'susScr2',
    'ochPri3',
    'ochPri2',
    'ornAna2',
    'ornAna1',
    'nasLar1',
    'oryCun2',
    'rn6',
    'rn5',
    'rn4',
    'rn3',
    'rheMac10',
    'rheMac8',
    'rheMac3',
    'rheMac2',
    'proCap1',
    'oviAri4',
    'oviAri3',
    'oviAri1',
    'sorAra2',
    'sorAra1',
    'choHof1',
    'speTri2',
    'saiBol1',
    'tarSyr2',
    'tarSyr1',
    'sarHar1',
    'echTel2',
    'echTel1',
    'tupBel1',
    'macEug2',
    'cerSim1',
    'xenLae2',
    'allMis1',
    'gadMor1',
    'melUnd1',
    'galGal6',
    'galGal5',
    'galGal4',
    'galGal3',
    'galGal2',
    'latCha1',
    'calMil1',
    'fr3',
    'fr2',
    'fr1',
    'petMar3',
    'petMar2',
    'petMar1',
    'anoCar2',
    'anoCar1',
    'oryLat2',
    'geoFor1',
    'oreNil2',
    'chrPic1',
    'gasAcu1',
    'tetNig2',
    'tetNig1',
    'nanPar1',
    'melGal5',
    'melGal1',
    'xenTro9',
    'xenTro7',
    'xenTro3',
    'xenTro2',
    'xenTro1',
    'taeGut2',
    'taeGut1',
    'danRer11',
    'danRer10',
    'danRer7',
    'danRer6',
    'danRer5',
    'danRer4',
    'danRer3',
    'ci3',
    'ci2',
    'ci1',
    'braFlo1',
    'strPur2',
    'strPur1',
    'apiMel2',
    'apiMel1',
    'anoGam3',
    'anoGam1',
    'droAna2',
    'droAna1',
    'droEre1',
    'droGri1',
    'dm6',
    'dm3',
    'dm2',
    'dm1',
    'droMoj2',
    'droMoj1',
    'droPer1',
    'dp3',
    'dp2',
    'droSec1',
    'droSim1',
    'droVir2',
    'droVir1',
    'droYak2',
    'droYak1',
    'caePb2',
    'caePb1',
    'cb3',
    'cb1',
    'ce11',
    'ce10',
    'ce6',
    'ce4',
    'ce2',
    'caeJap1',
    'caeRem3',
    'caeRem2',
    'priPac1',
    'aplCal1',
    'sacCer3',
    'sacCer2',
    'sacCer1',
    'eboVir3',
    'wuhCor1',]
    file_name_spli = re.split('\.', file_name.lower())
    for name in file_name_spli:
        if name in ucsc_list:
            return name
    return name


