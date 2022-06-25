#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 9/13/2020 10:34 PM
# @Author  : Jay
# @File    : base.py
# @Software: PyCharm

# import logging
from base.logger import GetLogger
import os

# import modin.pandas as pd
from datatable import (
    dt,
    f,
    by,
    ifelse,
    update,
    sort,
    count,
    min,
    max,
    mean,
    sum,
    rowsum,
)
import pickle
import time
from collections import Counter
import pandas as pd
import random
from PIL import Image

# from data_processing.insects_cn2latin import convert_dict
import cv2

from tqdm import tqdm

# from modin import pandas as pd

# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
# logger = logging.getLogger(__name__)
# create formatter
# logging.getLogger().setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# logger = logging.getLogger(__name__)
# logger.addHandler(ch)
log = GetLogger(__name__)
logger = log.get()


def path_dict(dir_path, ext):
    # ! file name must be unique
    pdict = {}
    for root, subFolders, files in os.walk(dir_path):
        for filename in files:
            if not filename.endswith(ext):
                continue
            elif filename in pdict.keys():
                continue
            else:
                pdict[filename] = os.path.join(root, filename)
    return pdict


class OriginBase:
    @staticmethod
    def path_dict(dir_path: str, ext: str):
        """
        dir_path is the root directory of images
        ext is the extension of file.
        """
        pdict = {}
        for root, subFolders, files in os.walk(dir_path):
            for filename in files:
                if not filename.lower().endswith(ext.lower()):
                    continue
                elif filename in pdict.keys():
                    continue
                else:
                    pdict[filename] = os.path.join(root, filename)
        return pdict


class ANNO:
    def __init__(self, load_path=None, save_path=None, img_dir=None):
        print("initial ANNO")
        self.data = pd.DataFrame(
            columns=[
                "filename",
                "width",
                "height",
                "xmin",
                "ymin",
                "xmax",
                "ymax",
                "label",
            ]
        )
        current_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time()))
        self.img_dir = img_dir
        if load_path is not None:
            print("loading from {}".format(load_path))
            self.load(load_path)

        if save_path is None:
            return None
        elif os.path.isdir(save_path):
            save_path = os.path.join(save_path, "{}".format(current_time) + ".csv")
        elif save_path.endswith("/"):
            save_path = os.path.join(save_path, current_time + ".csv")
        elif save_path.endswith(".csv"):
            pass
        if save_path:
            self.save_path = save_path

    @staticmethod
    def path_dict(dir_path: str, ext: str):
        """
        dir_path is the root directory of images
        ext is the extension of file.
        """
        pdict = {}
        for root, subFolders, files in os.walk(dir_path):
            for filename in files:
                if not filename.lower().endswith(ext.lower()):
                    continue
                elif filename in pdict.keys():
                    continue
                else:
                    pdict[filename] = os.path.join(root, filename)
        return pdict

    def img_path_dict(self):
        return self.path_dict(self.img_dir, ".jpg")

    def remove_missing_img(self):
        # ! remvoe annotions without images
        logger.debug("removing images not found on disk")
        disk_imgs = list(self.img_path_dict().keys())
        anno_imgs = self.data["filename"].to_list()
        i = 0
        for img_name in anno_imgs:
            if img_name not in disk_imgs:
                i += 1
                # missing_imgs.append(img_name)
                self.data = self.data[self.data["filename"] != img_name]
        logger.debug("removed {} images".format(i))

    def load(self, load_path):
        if load_path.endswith(".csv"):
            self.data = pd.read_csv(load_path)
        elif load_path.endswith(".pkl"):
            self.data = pd.read_pickle(load_path)
        elif load_path.endswith(".df"):
            self.data = pd.read_pickle(load_path)
        else:
            print("wrong path")

    def dataset_divide(self, train_ratio):
        img_name_list = self.data["filename"].tolist()
        img_num = len(img_name_list)
        assert train_ratio < 1, "train ratio must be less than 1"
        train_num = int(img_num * train_ratio)
        random.shuffle(img_name_list)
        train_imgs = img_name_list[:train_num]
        val_imgs = img_name_list[train_num:]
        train_data = self.data[self.data["filename"].isin(train_imgs)]
        val_data = self.data[self.data["filename"].isin(val_imgs)]
        logger.debug("training data contains {} images".format(len(train_imgs)))
        logger.debug("validation data contains {} images".format(len(val_imgs)))
        return train_imgs, val_imgs, train_data, val_data

    def dataset_devided_by_class(self, train_ratio):
        print("hello")
        train_data = pd.Dataframe({})
        val_data = pd.Dataframe({})
        assert train_ratio < 1, "train ratio must be less than 1"
        category_groups = self.data.groupby("species")
        for category, group in category_groups:
            pass

    def image_checker(self):
        img_name_list = self.data["filename"].unique().tolist()
        img_path_dict = self.img_path_dict()
        empty_img = []
        for img_name in tqdm(img_name_list):
            try:
                img_path = img_path_dict[img_name]
            except KeyError:
                logger.error("img not found in directory")
                continue
            # if img is not None:
            try:
                time.sleep(1)
                img = Image.open(img_path)
                img.verify()
                img.close()
                # print(f"{img_name} passed")
            except Exception as e:
                logger.debug("damaged image: {}".format(img_name))
                empty_img.append(img_name)
                print(e)
                self.data = self.data[self.data["filename"] != img_name]
                continue
        print(empty_img)

    def name_converter(self, column_name, convert_dict):
        """
        convert dataset name according to dict,
        like cn to eng
        """
        data = self.data.copy()
        data["species"] = data.apply(lambda x: convert_dict[x[column_name]], axis=1)
        self.data = data

    def save(self):
        print("saving to {}".format(self.save_path))
        if self.save_path.endswith(".csv"):
            self.data.to_csv(self.save_path, index=None)
            return None
        with open(self.save_path, "wb") as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
