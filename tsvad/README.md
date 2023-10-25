# TSVAD数据处理

## 流程
### 1. 正常人声对话音频数据
1. replace_nonasrlabel_with_silence.py：用静音替换asr标签中的非说话人声生成新的音频，并将不同说话人的音频分别进行拼接，并将毫秒级asr时间对标签转化为帧级01序列tagrt标签
2. cut_chunk_wav_speech.py：将上一步生成的新的音频进行切割，一般以16.02秒（提取特征后为1600帧）进行切割，并将target标签也进行切割
3. filtrate_target_with_vad.py：提取音频特征，计算能量vad，并根据能量vad结果过滤target标签；
4. kaldi/script/extract_xvector.sh：提取说话人音频对应vector；
5. kaldi/script/run_fbank.sh 或 yb_feature/run_train_8k.sh：提取音频特征（数据增广）；
6. scps_to_hdf5_dataaugment.py：将音频特征表单、说话人vector表单、targte表单转化为hdf5文件；


### 2. 特殊无效音音频数据
1. cut_chunk_wav_noise.py：将无效音音频进行切割，一般以16.02秒进行切割，对应target全为0；
2. kaldi/script/run_fbank.sh 或 yb_feature/run_train_8k.sh：提取音频特征（数据增广）；
3. scps_to_hdf5_dataaugment_noise.py：生成csv和hdf5

### 3. 重叠人声音频数据
1. overlap_audio_gen_replace_nonasrlabel_with_silence.py： 用静音替换asr标签中的非说话人声生成新的音频，并将不同说话人的音频分别进行拼接，并将毫秒级asr时间对标签转化为帧级01序列tagrt标签，会对第一个说话人的音频向前移动3秒，并将这三秒拼接到后面，再将两个说话人音频进行拼接，以生成同一音频段落；
2. cut_chunk_wav_speech.py：将上一步生成的新的音频进行切割，一般以16.02秒（提取特征后为1600帧）进行切割，并将target标签也进行切割
3. kaldi/script/extract_xvector.sh：提取说话人音频对应vector；
4. kaldi/script/run_fbank.sh 或 yb_feature/run_train_8k.sh：提取音频特征（数据增广）；
5. scps_to_hdf5_dataaugment.py：将音频特征表单、说话人vector表单、targte表单转化为hdf5文件；


### 4. finetune音频数据生成
ps: 根据聚类法生成的时间戳结果，生成预训练音频数据
1. finetune/gen_finetune_wav.py：生成模拟音频数据、说话人音频、对应target标签文件
2. cut_chunk_wav_speech.py：将上一步生成的新的音频进行切割，一般以16.02秒（提取特征后为1600帧）进行切割，并将target标签也进行切割
3. kaldi/script/extract_xvector.sh：提取说话人音频对应vector；
4. kaldi/script/run_fbank.sh 或 yb_feature/run_train_8k.sh：提取音频特征（数据增广）；
5. scps_to_hdf5_dataaugment_finetune.py：将音频特征表单、说话人vector表单、targte表单转化为hdf5文件；

### -1. 合并训练数据
1. combine_csv.py：将多个结构相同的csv文件合并为一个csv文件；
2. csv_to_hdf5.py：将csv文件转化为hdf5文件；

## 