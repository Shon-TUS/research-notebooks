from logging import getLogger
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

from .dataset_csv import DATASET_CSVS
from .mean_std import get_mean, get_std, get_raw_mean, get_raw_std
from .sound_length_list import get_sound_length_list
from .joint_list import joint2list, get_joints

__all__ = ["get_dataloader"]

logger = getLogger(__name__)


def get_dataloader(
    dataset_name: str,
    sound_length: int,
    input_feature: str,
    split: str,
    batch_size: int,
    shuffle: bool,
    num_workers: int,
    pin_memory: bool,
    drop_last: bool = False,
    seq_len: int = 12,  # ←追加
    transform: Optional[transforms.Compose] = None,
) -> DataLoader:
    # if dataset_name not in DATASET_CSVS:
    #     message = f"dataset_name should be selected from {list(DATASET_CSVS.keys())}."
    #     logger.error(message)
    #     raise ValueError(message)

    if split not in ["train", "val", "test"]:
        message = "split should be selected from ['train', 'val', 'test']."
        logger.error(message)
        raise ValueError(message)

    logger.info(f"Dataset: {dataset_name}\tSplit: {split}\tBatch size: {batch_size}.")
    try:
        csv_file = getattr(DATASET_CSVS[dataset_name], split)
    except:
        csv_file = f"csv/{dataset_name}/{split}.csv"

    if input_feature == 'raw':
        mean = np.array(get_raw_mean()).astype("float32")
        std = np.array(get_raw_std()).astype("float32")
    elif input_feature == 'logmel':
        mean = np.array(get_mean()).astype("float32")[:4]
        std = np.array(get_std()).astype("float32")[:4]
    else:
        mean = np.array(get_mean()).astype("float32")
        std = np.array(get_std()).astype("float32")
    if input_feature == 'raw':
        data = SoundPoseLSTMDataset(
            csv_file, sound_length, input_feature, mean, std, transform=transform
        )
    else:
        data = SoundPose2DDataset(
            csv_file, sound_length, input_feature, mean, std, transform=transform
        )
    dataloader = DataLoader(
        data,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=pin_memory,
        drop_last=drop_last,
    )

    return dataloader


class SoundPoseDataset(Dataset):
    def __init__(
        self,
        csv_file: str,
        sound_length: int,
        input_feature: str,
        mean: np.array,
        std: np.array,
        transform: Optional[transforms.Compose] = None,
    ) -> None:
        super().__init__()

        try:
            self.df = pd.read_csv(csv_file)
        except FileNotFoundError("csv file not found.") as e:
            logger.exception(f"{e}")

        sound_length_list = get_sound_length_list()

        if sound_length not in sound_length_list:
            message = (
                "There is no sound length appropriate to your choice. "
                "You have to choose %s as sound length." % sound_length_list
            )
            logger.error(message)
            raise ValueError(message)
        self.input_feature = input_feature
        if self.input_feature != 'logmel':
            self.df = self.df[self.df['preprocess'] == self.input_feature]
            self.df = self.df.reset_index(drop=True)
        self.df = (
            self.df[self.df["sound_length"] == sound_length]
            .fillna(method="ffill")
            .fillna(method="bfill")
        )
        self.sound = np.array(
            [(np.load(path) - mean) / std for path in self.df["sound_path"]]
        )
        self.sound = self.sound.transpose(0, 2, 1)
        if input_feature == "logmel":
            self.sound = self.sound[:, :4]
        elif input_feature == "intensity":
            self.sound = self.sound[:, 4:]

        self.transform = transform

        logger.info(f"the number of samples: {len(self.df)}")

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sound = self.sound[idx]

        if self.transform is not None:
            sound = self.transform(sound)

        targets = torch.Tensor(joint2list(self.df.iloc[idx]))
        testee = self.df.iloc[idx * self.seq_len]['testee'].split('_')[-1]
        testee_num = int(testee) - 1
        sample = {
            "sound": sound,
            "targets": targets,
            "testee":testee_num,
        }

        return sample
    
class SoundPoseLSTMDataset(Dataset):
    def __init__(
        self,
        csv_file: str,
        sound_length: int,
        input_feature: str,
        mean: np.array,
        std: np.array,
        transform: Optional[transforms.Compose] = None,
        is_train = False,
        aug:str = ''
    ) -> None:
        super().__init__()

        try:
            self.df = pd.read_csv(csv_file)
        except FileNotFoundError("csv file not found.") as e:
            logger.exception(f"{e}")

        sound_length_list = get_sound_length_list()
        self.seq_len = 1
        if sound_length not in sound_length_list:
            message = (
                "There is no sound length appropriate to your choice. "
                "You have to choose %s as sound length." % sound_length_list
            )
            logger.error(message)
            raise ValueError(message)
        self.input_feature = input_feature
        if (self.input_feature != 'logmel') & (self.input_feature != 'all')& (self.input_feature != 'intensity'):
            self.df = self.df[self.df['preprocess'] == self.input_feature]
            self.df = self.df.reset_index(drop=True)
        else:
            # Logmel特徴量はintensityとともに作られる。特徴量選択は self.sound = self.sound[:, :, :4]によって実施
            self.df = self.df[self.df['preprocess'] == 'intensity']
            self.df = self.df.reset_index(drop=True)
        self.df = (
            self.df[self.df["sound_length"] == sound_length]
            .fillna(method="ffill")
            .fillna(method="bfill")
        )
        self.df = self.df.iloc[:self.seq_len * (self.df.shape[0]//self.seq_len)]
        self.sound = np.array(
            [(np.load(path) - mean) / std for path in self.df["sound_path"]]
        )
        self.sound = self.sound.transpose(0, 2, 1) #[sample_size, channels, sound_length]
        self.sound = self.sound.reshape(self.df.shape[0]//self.seq_len, self.seq_len, self.sound.shape[1], self.sound.shape[-1])
        self.targets = self.df[get_joints()].values.reshape(self.df.shape[0]//self.seq_len, self.seq_len, len(get_joints()))
        assert self.sound.shape[0] == self.targets.shape[0]
        if input_feature == "logmel":
            self.sound = self.sound[:, :, :4]
        elif input_feature == "intensity":
            self.sound = self.sound[:, :, 4:]
        self.input_feature = input_feature
        self.transform = transform
        self.is_train = is_train
        self.aug = aug
        if is_train:
            self.max_noise_amp = 0.2
        logger.info(f"the number of samples: {len(self.df)}")

    def __len__(self) -> int:
        return len(self.sound)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sound = torch.Tensor(self.sound[idx]).float() #[seq_len, channels, 1024]
        if self.transform is not None:
            sound = self.transform(sound)
        targets = torch.Tensor(self.targets[idx]) #[seq_len, num_joints * 3]
        testee = self.df.iloc[idx * self.seq_len]['testee'].split('_')[-1]
        testee_num = int(testee) - 1
        sample = {
            "sound": sound,
            "targets": targets,
            "testee":testee_num
        }
        return sample

'''
class SoundPose2DDataset(Dataset):
    def __init__(
        self,
        csv_file: str,
        sound_length: int,
        input_feature: str,
        mean: np.array,
        std: np.array,
        transform: Optional[transforms.Compose] = None,
        is_train = False,
        aug:str = ''
    ) -> None:
        super().__init__()

        try:
            self.df = pd.read_csv(csv_file)
        except FileNotFoundError("csv file not found.") as e:
            logger.exception(f"{e}")

        sound_length_list = get_sound_length_list()
        self.seq_len = 12
        if sound_length not in sound_length_list:
            message = (
                "There is no sound length appropriate to your choice. "
                "You have to choose %s as sound length." % sound_length_list
            )
            logger.error(message)
            raise ValueError(message)
        self.input_feature = input_feature
        if (self.input_feature != 'logmel') & (self.input_feature != 'all')& (self.input_feature != 'intensity'):
            self.df = self.df[self.df['preprocess'] == self.input_feature]
            self.df = self.df.reset_index(drop=True)
        else:
            # Logmel特徴量はintensityとして作られる。特徴量選択は self.sound = self.sound[:, :, :4]によって実施
            self.df = self.df[self.df['preprocess'] == 'intensity']
            self.df = self.df.reset_index(drop=True)
        self.df = (
            self.df[self.df["sound_length"] == sound_length]
            .fillna(method="ffill")
            .fillna(method="bfill")
        )
        self.df = self.df.iloc[:self.seq_len * (self.df.shape[0]//self.seq_len)]
        # ToDo: logmelとallで場合分け
        if input_feature == 'logmel':
            self.sound = np.array(
                [(np.load(path)[:, :4] - mean) / std for path in self.df["sound_path"]]
            )
        else:
            self.sound = np.array(
                [(np.load(path) - mean) / std for path in self.df["sound_path"]]
            )
        self.sound = self.sound.transpose(0, 2, 1) #[sample_size, channels, sound_length]
        self.sound = self.sound.reshape(self.df.shape[0]//self.seq_len, self.seq_len, self.sound.shape[1], self.sound.shape[-1])
        # [sample_size', seq_len, channels, freq_bins] -> [sample_size', channels, seq_len, freq_bins]
        self.sound = self.sound.transpose(0, 2, 1, 3)
        self.targets = self.df[get_joints()].values.reshape(self.df.shape[0]//self.seq_len, self.seq_len, len(get_joints()))
        assert self.sound.shape[0] == self.targets.shape[0]
        # if input_feature == "logmel":
        #     self.sound = self.sound[:, :, :4]
        # elif input_feature == "intensity":
        #     self.sound = self.sound[:, :, 4:]
        self.input_feature = input_feature
        self.transform = transform
        self.is_train = is_train
        self.aug = aug
        if is_train:
            self.max_noise_amp = 0.2
        logger.info(f"the number of samples: {len(self.df)}")
'''
class SoundPose2DDataset(Dataset):
    def __init__(
        self,
        csv_file: str,
        sound_length: int,
        input_feature: str,
        mean: np.array,
        std: np.array,
        transform: Optional[transforms.Compose] = None,
        is_train=False,
        aug: str = '',
        seq_len: int = 12,  # ←追加
    ) -> None:
        super().__init__()
        self.seq_len = seq_len  # ←固定値ではなく引数で設定

        # CSV 読み込み
        try:
            self.df = pd.read_csv(csv_file)
        except FileNotFoundError as e:
            logger.exception("CSV file not found.")
            raise e

        sound_length_list = get_sound_length_list()
        #self.seq_len = 12
        if sound_length not in sound_length_list:
            raise ValueError(f"Choose sound_length from {sound_length_list}")

        self.input_feature = input_feature

        # preprocess に応じて CSV を絞り込み
        if self.input_feature in ['logmel', 'all', 'intensity']:
            if self.input_feature == 'logmel':
                self.df = self.df[self.df['preprocess'] == 'original'].reset_index(drop=True)
            else:
                self.df = self.df[self.df['preprocess'] == 'intensity'].reset_index(drop=True)
        else:
            self.df = self.df[self.df['preprocess'] == self.input_feature].reset_index(drop=True)

        # sound_length で絞り込み
        self.df = self.df[self.df["sound_length"] == sound_length].fillna(method="ffill").fillna(method="bfill")
        self.df = self.df.iloc[:self.seq_len * (self.df.shape[0] // self.seq_len)]

        # npy 読み込み
        if input_feature == 'logmel':
            # メルスペクトログラムのみ
            self.sound = np.array(
                [(np.load(path)[:, :4] - mean) / std for path in self.df["sound_path"]]
            )  # shape: [num_samples, time_steps, channels]

            # shape を [num_samples, channels, time] に変更
            self.sound = self.sound.transpose(0, 2, 1)
        else:
            # intensity または all
            self.sound = np.array(
                [(np.load(path) - mean) / std for path in self.df["sound_path"]]
            )
            self.sound = self.sound.transpose(0, 2, 1)
        '''
        # seq_len に分割して [batch, seq_len, channels, time] に reshape
        self.sound = self.sound.reshape(
            self.df.shape[0] // self.seq_len,
            self.seq_len,
            self.sound.shape[1],  # channels
            self.sound.shape[2]   # time
        )
        # [batch, seq_len, channels, time] → [batch, channels, seq_len, time]
        self.sound = self.sound.transpose(0, 2, 1, 3)

        # 目標値
        self.targets = self.df[get_joints()].values.reshape(
            self.df.shape[0] // self.seq_len,
            self.seq_len,
            len(get_joints())
        )
        '''
        n_samples = self.df.shape[0] // self.seq_len
        if n_samples == 0:
            raise ValueError(f"seq_len={self.seq_len} が大きすぎてサンプルが作れません。")
        self.df = self.df.iloc[: n_samples * self.seq_len]  # DataFrame も切り捨て

        self.sound = self.sound[: n_samples * self.seq_len]  # np.array も切り捨て
        self.sound = self.sound.reshape(
            n_samples,
            self.seq_len,
            self.sound.shape[1],  # channels
            self.sound.shape[2],  # time
        )
        self.sound = self.sound.transpose(0, 2, 1, 3)  # [batch, channels, seq_len, time]

        self.targets = self.df[get_joints()].values[: n_samples * self.seq_len]
        self.targets = self.targets.reshape(
            n_samples,
            self.seq_len,
            len(get_joints())
        )
        assert self.sound.shape[0] == self.targets.shape[0]

        # その他設定
        self.transform = transform
        self.is_train = is_train
        self.aug = aug
        if is_train:
            self.max_noise_amp = 0.2

        logger.info(f"Number of samples: {len(self.df)}")


    def __len__(self) -> int:
        return len(self.sound)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        sound = torch.Tensor(self.sound[idx]).float() #[seq_len, channels, 1024]
        if self.transform is not None:
            sound = self.transform(sound)
        targets = torch.Tensor(self.targets[idx]) #[seq_len, num_joints * 3]
        testee = self.df.iloc[idx * self.seq_len]['testee'].split('_')[-1]
        testee_num = int(testee) - 1
        sample = {
            "sound": sound,
            "targets": targets,
            'testee':testee_num
        }
        return sample