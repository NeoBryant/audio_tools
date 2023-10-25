import os, sys
import tqdm
import collections
import json

import copy
import logging
import numpy as np

# import egs.kaldi_io as kaldi_io
# import libs.support.kaldi_common as kaldi_common
import kaldiio
# Logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

### Class
class KaldiDataset():
    """
    Parameters:
        data_dir: datadir in kaldi data/.
        expected_files: use this free config carefully.
        more: if true, ignore expected_files and load all available files which are exist.

    Possible attr:
    == Mapping files ==
        self.utt2spk: dict{str:str}
        self.spk2utt: dict{str:list[str]}
        self.feats_scp: dict{str:str}
        self.utt2num_frames: dict{str:int}
        self.vad_scp: dict{str:str}
        self.wav_scp: dict{str:str}
        self.utt2dur: dict{str:float}
        self.utt2spk_int: dict{str:int}

    == Variables ==
        self.data_dir: str
        self.num_utts, self.num_spks, self.num_frames, self.feat_dim: int
    """
    def __init__(self, data_dir:str="", 
                       expected_files:list=["utt2spk", "spk2utt", "feats.scp", "utt2num_frames"],
                       more=False):
        # Fixed definition of str-first mapping files.
        # Tuple(Attr:str, FileName:str, Value_type:str, Vector:bool).
        self.utt_first_files = [
            ("wav_scp", "wav.scp", "str", False),
            ("utt2spk", "utt2spk", "str", False),
            # ("utt2spk_int", "utt2spk_int", "int", False),
            ("feats_scp", "feats.scp", "str", False),
            ("utt2num_frames", "utt2num_frames", "int", False),
            ("utt2dur", "utt2dur", "float", False),
            ("vad_scp", "vad.scp", "str", False),
            ("text", "text", "str", True)]

        # Should keep spk2utt only now.
        self.spk_first_files = [
            ("spk2utt", "spk2utt", "str", True), 
            ("spk2int", "spk2int", "int", False)]

        # Process parameters
        if data_dir == "": # Here should use "." rather than "" to express current directory.
            self.data_dir = None
        else:
            self.data_dir = data_dir

        self.expected_files = expected_files
        self.more = more

        # Init and Load files
        self.loaded_attr = []
        
        # use load_data_ funtion make file dict
        if self.data_dir is not None:
            self.load_data_()

        self.get_base_attribute_()

    @classmethod
    def load_data_dir(self, data_dir:str, expected_files:list=["utt2spk", "spk2utt", "feats.scp", "utt2num_frames"]):
        return self(data_dir, expected_files)

    def load_data_(self):
        if not os.path.exists(self.data_dir):
            raise ValueError("The datadir {0} is not exist.".format(self.data_dir))

        if self.more:
            logger.info("Load mapping files form {0} as more as possible with more=True".format(self.data_dir))
        else:
            logger.info("Load mapping files form {0} w.r.t expected files {1}".format(self.data_dir, self.expected_files))

        for attr, file_name, value_type, vector in self.utt_first_files + self.spk_first_files:
            file_path = "{0}/{1}".format(self.data_dir, file_name)
            if self.more:
                if os.path.exists(file_path) and attr not in self.loaded_attr:
                    print("Load data from {0} ...".format(file_path))
                    logger.info("Load data from {0} ...".format(file_path))
                    setattr(self, attr, read_str_first_ark(file_path, value_type, vector))
                    self.loaded_attr.append(attr)
            elif file_name in self.expected_files:
                if os.path.exists(file_path) and attr not in self.loaded_attr:
                    print("Load data from {0} ...".format(file_path))
                    logger.info("Load data from {0} ...".format(file_path))
                    setattr(self, attr, read_str_first_ark(file_path, value_type, vector))
                    self.loaded_attr.append(attr)
                else:
                    raise ValueError("The file {0} is not exist.".format(file_path))

    def get_base_attribute_(self):
        ## Base attribute
        # Total utts
        self.num_utts = len(self.utt2spk) if "utt2spk" in self.loaded_attr else None

        # Total spks
        self.num_spks = len(self.spk2utt) if "spk2utt" in self.loaded_attr else None

        # Total frames
        if "utt2num_frames" in self.loaded_attr:
            self.num_frames = 0
            for utt, num_frames in self.utt2num_frames.items():
                self.num_frames += num_frames
        else:
            self.num_frames = None

        # Feature dim
        self.feat_dim = kaldiio.load_mat(
            self.feats_scp[list(self.feats_scp.keys())[0]]).shape[1] if "feats_scp" in self.loaded_attr else None

    def generate(self, attr:str):
        if attr == "spk2int":
            if attr not in self.loaded_attr:
                self.spk2int = {}
                # self.utt2spk_int = {}
                for index, spk in enumerate(self.spk2utt):
                    self.spk2int[spk] = index
                # for utt, spk in self.utt2spk.items():
                #     self.utt2spk_int[utt] =  spk2int[spk]
                self.loaded_attr.append(attr)
            else:
                logger.warn("The utt2spk_int is exist.")
        else:
            raise ValueError("Do not support attr {0} now.".format(attr))


    @classmethod
    def load(self, file_path:str):
        pass

    def save(self, file_dir:str, kaldi_dataset=None):
        if kaldi_dataset is None:
            kaldi_dataset = copy.deepcopy(self)
        os.makedirs(file_dir, exist_ok=True)

        for attr, file_name, value_type, vector in self.utt_first_files + self.spk_first_files:
            
            if attr in kaldi_dataset.loaded_attr:
                this_file_dict = getattr(kaldi_dataset, attr)                
                f = open(os.path.join(file_dir, file_name), "w")
                for key, value in this_file_dict.items():
                    if type(value).__name__ == "list":
                        f.write(key + " " + " ".join(value) + "\n")
                    else:
                        f.write(key + " " + str(value) + "\n")


def to(to_type:str, value):
    if to_type == "str" or to_type == "float" or to_type == "int":
        return eval("{0}('{1}')".format(to_type, value))
    else:
        raise ValueError("Do not support {0} to_type".format(to_type))


def read_str_first_ark(file_path:str, value_type="str", vector=False, every_bytes=10000000):
    this_dict = {}

    with open(file_path, 'r') as reader:
            while True :
                lines = reader.readlines(every_bytes)
                if not lines:
                    break
                for line in lines:
                    if vector:
                        # split_line => n
                        split_line = line.split()
                        # split_line => n-1
                        key = split_line.pop(0)
                        value = [ to(value_type, x) for x in split_line ]
                        this_dict[key] = value
                    else:
                        key, value = line.split()
                        this_dict[key] = to(value_type, value)

    return this_dict


class ChunkSamples():
    def __init__(self, dataset:KaldiDataset, chunk_size:int, chunk_type='speaker_balance', chunk_num_selection=0, 
                 chunk_min=600, chunk_max=1500, scale=1.5, overlap=0.1, drop_last=False, seed=1024):
        '''
        Parameters:
            self.dataset: the object which contain the dicts such as utt2spk, utt2spk_int and so on.
            self.chunk_size: the number of frames in a chunk.
            self.chunk_type: which decides how to chunk the feats for training.
            chunk_num_selection: -1->suggestion scale, 0->max, >0->specify.
            self.overlap: the proportion of overlapping for every chunk.
        '''
        self.dataset = dataset
        self.chunk_size = chunk_size
        self.chunk_type = chunk_type
        self.chunk_num_selection = chunk_num_selection
        self.chunk_min = chunk_min
        self.chunk_max = chunk_max
        self.scale = scale
        self.overlap = overlap
        self.drop_last = drop_last

        assert 0<= self.overlap < 1

        np.random.seed(seed)

        # chunk_samples: table [[]]
        self.head = ['utt-id', 'ark-path', 'start-position', 'end-position']
        self.chunk_samples = self.__sample()

    def __sample(self):
        # JFZhou: speaker_balance and sequential.
        chunk_samples = []

        if self.chunk_type == 'speaker_balance':
            spk2chunks = collections.defaultdict(list)
            total_chunks = 0
            max_chunk_num = 0
            chunk_counter = {}
            for key in self.dataset.spk2utt.keys():
                utt_selected = self.dataset.spk2utt[key]
                spk_chunk_num = 0
                for utt in utt_selected:
                    ark_path = self.dataset.feats_scp[utt]
                    num_frames = self.dataset.utt2num_frames[utt]

                    if num_frames < self.chunk_size:
                        logger.warn('The num frames {0} of {1} is less than chunk size {2}, so skip it.'.format(utt, num_frames, self.chunk_size))
                    else:
                        chunk_counter[utt] = 0
                        offset = 0
                        overlap_size = int(self.overlap * self.chunk_size)
                        while offset + self.chunk_size <= num_frames:
                            chunk = "{0} {1} {2} {3}".format(utt+'-'+str(chunk_counter[utt]),ark_path,offset,offset+self.chunk_size-1)
                            offset += self.chunk_size - overlap_size
                            spk2chunks[key].append(chunk)

                            chunk_counter[utt] += 1
                            total_chunks += 1
                            spk_chunk_num += 1

                        if not self.drop_last and offset + overlap_size < num_frames - 1:
                            chunk = "{0} {1} {2} {3}".format(utt+'-'+str(chunk_counter[utt]),ark_path,num_frames-self.chunk_size,num_frames-1)
                            total_chunks += 1
                            spk_chunk_num += 1
                            chunk_counter[utt] += 1
                            spk2chunks[key].append(chunk)

                if spk_chunk_num > max_chunk_num:
                    max_chunk_num = spk_chunk_num

            for key in spk2chunks.keys():
                chunk_selected = spk2chunks[key]

                # num_chunks_selected 表示每个spk选择多少chunk
                if self.chunk_num_selection==0:
                    num_chunks_selected = max_chunk_num
                elif self.chunk_num_selection==-1: # 默认训练集采用此方式
                    num_chunks_selected = int(total_chunks//len(self.dataset.spk2utt)*self.scale)
                else:
                    num_chunks_selected = self.chunk_num_selection

                num_chunks = len(chunk_selected)
                if num_chunks < num_chunks_selected:
                    valid_utts = [ utt for utt in self.dataset.spk2utt[key] if self.dataset.utt2num_frames[utt] >= self.chunk_size ]
                    utts = np.random.choice(valid_utts,num_chunks_selected - num_chunks,replace=True)
                    for utt in utts:
                        start = np.random.randint(0, self.dataset.utt2num_frames[utt]-self.chunk_size+1)
                        end = start + self.chunk_size - 1
                        chunk_selected.append("{0} {1} {2} {3}".format(utt+'-'+str(chunk_counter[utt]),self.dataset.feats_scp[utt],start,end))
                        chunk_counter[utt] += 1
                else:
                    chunk_selected = np.random.choice(spk2chunks[key],num_chunks_selected,replace=False)

                for chunk in chunk_selected:
                    chunk_samples.append(chunk.split())

        elif self.chunk_type == 'sequential':
            for utt in self.dataset.feats_scp.keys():

                ark_path = self.dataset.feats_scp[utt]
                num_frames = self.dataset.utt2num_frames[utt]

                if num_frames < self.chunk_min:
                    logger.warn('The num frames {0} of {1} is less than chunk size {2}, so skip it.'.format(utt, num_frames, self.chunk_size))
                elif num_frames >= self.chunk_min and num_frames <= self.chunk_max:
                    chunk_samples.append([utt+'-'+str(0),ark_path,0,num_frames-1])
                else:
                    chunk_counter = 0
                    offset = 0
                    overlap_size = int(self.overlap * self.chunk_size)
                    while offset + self.chunk_size <= num_frames:
                        chunk_samples.append([utt+'-'+str(chunk_counter),ark_path,offset,offset+self.chunk_size-1])
                        chunk_counter += 1
                        offset += self.chunk_size - overlap_size

                    chunk_left = num_frames - offset
                    if not self.drop_last and chunk_left > 1 and chunk_left <= self.chunk_min:
                        chunk_samples.append([utt+'-'+str(chunk_counter), ark_path,num_frames-self.chunk_min, num_frames-1])
                    elif not self.drop_last and chunk_left > self.chunk_min:
                        chunk_samples.append([utt+'-'+str(chunk_counter), ark_path,num_frames-chunk_left, num_frames-1])

                    # if not self.drop_last and offset + overlap_size < num_frames - (self.chunk_size / 4) - 1:
                    #     chunk_samples.append([utt+'-'+str(chunk_counter), ark_path,num_frames-self.chunk_size, num_frames-1])

        # every_utt for valid
        elif self.chunk_type == "every_utt":
            chunk_selected = []
            for utt in self.dataset.utt2spk.keys():
                ark_path = self.dataset.feats_scp[utt]
                num_frames = self.dataset.utt2num_frames[utt]

                if num_frames < self.chunk_size:
                    logger.warn('The num frames {0} of {1} is less than chunk size {2}, so skip it.'.format(utt, num_frames, self.chunk_size))
                else:
                    starts = range(0, num_frames - self.chunk_size, self.chunk_size)
                    if len(starts) >= self.chunk_num_selection:
                        starts_select = random.sample(starts, self.chunk_num_selection)
                    else:
                        starts_select = random.sample(range(num_frames-self.chunk_size+1), self.chunk_num_selection)
                    
                    for chunk_counter, start in enumerate(starts_select):
                        end = start + self.chunk_size - 1
                        chunk_selected.append("{0} {1} {2} {3}".format(utt+'-'+str(chunk_counter),self.dataset.feats_scp[utt],start,end))

            for chunk in chunk_selected:
                    chunk_samples.append(chunk.split())

        else:
            raise TypeError("Do not support chunk type {0}.".format(self.chunk_type))

        return chunk_samples

    def save(self, save_path:str, force=True):
        if os.path.exists(save_path) and not force:
            raise ValueError("The path {0} is exist. Please rm it by yourself.".format(save_path))

        save_dir = os.path.dirname(save_path)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        data_frame = pd.DataFrame(self.chunk_samples, columns=self.head)
        data_frame.to_csv(save_path, sep=" ", header=True, index=False)


def generate_list_file(feats_scp, save_list_dir, raw_utt2spk, raw_utt2num_frames="", is_cut=False):
    """
    generate spk2utt, uid2classes and utt2spk according to feats.scp
    (the subset of raw feats.scp or the feats.scp of cut data) and raw utt2spk

    Args:
        feats_scp: path of feats.scp
        save_list_dir: the directory to save spk2utt, uid2classes and utt2spk
        raw_utt2spk: the path of raw utt2spk
    """
    feats_dict = read2data(feats_scp)
    raw_utt2spk_dict = read2data(raw_utt2spk)
    if os.path.exists(raw_utt2num_frames):
        raw_utt2frames_dict = read2data(raw_utt2num_frames)
        f_utt2frames = open(os.path.join(save_list_dir, "utt2num_frames"), "w")

    spk2utt = collections.defaultdict(list)
    f_utt2spk = open(os.path.join(save_list_dir, "utt2spk"), "w")
    f_spk2utt = open(os.path.join(save_list_dir, "spk2utt"), "w")
    f_spk2num = open(os.path.join(save_list_dir, "spk2num"), "w")
    f_spk2label = open(os.path.join(save_list_dir, "spk2label"), "w")
    print("Writing utt2spk utt2num_frames")
    for utt in tqdm.tqdm(feats_dict.keys()):
        if is_cut:
            data_utt = "-".join(utt.split("-")[0:-1])
        else:
            data_utt = utt
        try:
            spk = raw_utt2spk_dict[data_utt]
        except Exception:
            print("can not find the utt of feats.scp in raw_utt2spk")
        f_utt2spk.write(utt + " " + spk + "\n")
        if os.path.exists(raw_utt2num_frames):
            f_utt2frames.write(utt + " " + raw_utt2frames_dict[utt] + "\n")
        spk2utt[spk].append(utt)
    f_utt2spk.close()

    print("Writing spk2utt spk2num spk2label")
    for i, (spk, utt_list) in tqdm.tqdm(enumerate(spk2utt.items())):
        f_spk2utt.write(spk + " " + " ".join(utt_list) + "\n")
        f_spk2num.write(spk + " " + str(len(utt_list)) + "\n")
        f_spk2label.write(spk + " " + str(i) + "\n")
    f_spk2utt.close()
    f_spk2num.close()
    f_spk2label.close()


def read2data(path, is_list=False, data_type="dict", value_type="str"):
    if data_type == "dict":
        data = {}
    elif data_type == "list":
        data = []
    else:
        RuntimeError("no this data_type !")
    with open(path, "r") as f:
        for line in f.readlines():
            line = line.strip()
            key = line.split()[0]
            if is_list:
                value = line.split()[1:]
            else:
                value = line.split()[1]

            if value_type == "int":
                value = int(value)
            elif value_type == "float":
                value = float(value)
            else:
                RuntimeError("no this value_type !")

            if data_type == "dict":
                data[key] = value
            else:
                data.append((key, value))
    return data


def check_file(data_dir, except_file=["feats.scp", "spk2utt", "utt2spk", "utt2num_frames"]):
    file_lists = []
    print("except file: {}".format(" ".join(except_file)))
    for file_name in except_file:
        file_list = os.path.join(data_dir, file_name)
        if os.path.exists(file_list):
            print("check {} exists".format(file_list))
            file_lists.append(file_list)
        else:
            raise Exception("not found {}".format(file_list))
    return file_lists