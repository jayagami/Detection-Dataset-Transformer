#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\homej\git\lab_works\2020-09-标注文件读取\to_coco_datasets.py
# Path: c:\Users\homej\git\lab_works\2020-09-标注文件读取
# Created Date: Tuesday, September 15th 2020, 2:32:57 pm
# Author: Jay
#
# Copyright (c) 2020 Uchiha
###

# import logging.config
from base.logger import GetLogger
import os

from base.base import ANNO
import numpy as np
import xmltodict
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
import json
import argparse
import shutil
from tqdm import tqdm

# create formatter
# logging.getLogger().setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)
# ch.setFormatter(formatter)
# logger = logging.getLogger(__name__)
# logger.addHandler(ch)
# #
log = GetLogger(__name__)
logger = log.get()


class ToCOCO(ANNO):
    def __init__(
        self,
        data=None,
        load_path=None,
        save_path=None,
        multi_process=False,
        img_dir=None,
        soft_link=True,
        train_ratio=0.8,
    ):
        if data is not None:
            load_path = None
            if isinstance(data, dt.Frame):
                logger.info("Loading data from datatable Frame")
                data = data.to_pandas()
        super().__init__(load_path=load_path, save_path=save_path, img_dir=None)
        self.data = data
        self.save_path = save_path
        self.img_dir = img_dir
        self.soft_link = soft_link
        self.train_ratio = train_ratio
        self.coco_data = {
            "info": "",
            "licenses": [],
            "images": [],
            "annotations": [],
            "categories": [],
            "type": [],
        }
        self.img_name_array = np.array([])
        self.read_img_size = False
        self.images_section = []
        self.annotations_section = []
        self.categories_section = []
        self.info_section = []
        self.multi_process = multi_process

    @classmethod
    def xyminmax2xywh(cls, yolo_box, convert_int=True):
        yolo_box = [float(x) for x in yolo_box]
        xmin, ymin, xmax, ymax = yolo_box
        top_left = xmin
        bottom_left = ymin
        width = xmax - xmin
        height = ymax - ymin
        area = width * height
        if convert_int:
            top_left = int(float(top_left))
            bottom_left = int(float(bottom_left))
            width = int(float(width))
            height = int(float(height))
            area = int(float(area))
        return (top_left, bottom_left, width, height, area)

    def _info_section(self):
        return {
            "description": "",
            "year": 2022,
            "version": 1,
        }

    def _license_section(self, urls="www.inuyasha.xyz"):
        return [{"usl": urls, "id": 1}]

    def _images_section(
        self,
        data,
        license=1,
        coco_url="www.inuyasha.xyz",
        date_captured="",
        width=4000,
        height=3000,
    ):
        logger.info("start to generate images section")
        images_section = []
        self.img_name_array = data["filename"].unique()
        i = 0
        for file_name in self.img_name_array:
            if self.read_img_size:
                width, height = self.img_size()
            img_info = {
                "license": license,
                "file_name": file_name,
                "coco_url": coco_url,
                "width": width,
                "height": height,
                "date_captured": date_captured,
                "id": i,
            }
            i += 1
            images_section.append(img_info)
        logger.info("image section generated.")
        return images_section

    def _categories_section(self, data, supercategory="insect", isthing=0):
        logger.info("start to generate categories section")
        self.categories_name_array = data["label"].unique()
        i = 0
        categories_section = []
        for category in self.categories_name_array:
            category_info = {
                "supercategory": supercategory,
                "isthing": isthing,
                "id": i,
                "name": category,
            }
            categories_section.append(category_info)
            i += 1
        logger.info("category section generated.")
        return categories_section

    def _annotations_section(
        self,
        data,
        iscrowd=0,
        segmentation=[],
    ):
        logger.info("start to generate annotations section.")
        annotations_section = []
        i = 0
        for _, v in data.iterrows():
            xmin = v["xmin"]
            ymin = v["ymin"]
            xmax = v["xmax"]
            ymax = v["ymax"]
            x, y, w, h, area = self.xyminmax2xywh([xmin, ymin, xmax, ymax])
            bbox = [x, y, w, h]
            category_id = np.where(self.categories_name_array == v["label"])[0][0]
            image_id = np.where(self.img_name_array == v["filename"])[0][0]
            annotations_info = {
                "bbox": bbox,
                "category_id": int(category_id),
                "image_id": int(image_id),
                "id": i,
                "area": area,
                "iscrowd": iscrowd,
                "segmentation": segmentation,
            }
            annotations_section.append(annotations_info)
            i += 1
        logger.info("annotations section generated.")
        return annotations_section

    def _type_section(self):
        return "instances"

    def generate_json(self, data, json_path):
        logger.info("Converting to coco json file")
        # using multiprocessing
        if self.multi_process:
            pass
        #    img_job = Process(target=self._images_section)
        #    category_job = Process(target=self._categories_section)
        #    img_job.start()
        #    category_job.start()
        #    img_job.join()
        #    category_job.join()
        #    annotation_job = Process(target=self._annotations_section)
        #    annotation_job.start()
        #    annotation_job.join()
        else:
            # now the annotation job
            images_section = self._images_section(data)
            categories_section = self._categories_section(data)
            annotations_section = self._annotations_section(data)
        type_section = self._type_section()
        license_section = self._license_section()
        info_section = self._info_section()
        coco_data = {}
        coco_data["info"] = info_section
        coco_data["licenses"] = license_section
        coco_data["images"] = images_section
        coco_data["annotations"] = annotations_section
        coco_data["categories"] = categories_section
        coco_data["type"] = type_section
        logger.info("All jobs done")
        if not json_path.endswith(".json"):
            json_path += ".json"
        with open(json_path, "w") as io:
            io.write(json.dumps(coco_data))
        logger.info("json file saved at {}".format(json_path))

    def _make_coco_dir(self, dst):
        self.coco_dir = os.path.join(dst, "coco")
        self.anno_dir = os.path.join(self.coco_dir, "annotations")
        # self.images_dir = os.path.join(self.coco_dir, "images")
        self.train_images_dir = os.path.join(self.coco_dir, "train2017")
        self.val_images_dir = os.path.join(self.coco_dir, "val2017")
        if not os.path.isdir(self.coco_dir):
            os.makedirs(self.coco_dir)
        if not os.path.isdir(self.anno_dir):
            os.makedirs(self.anno_dir)
        # if not os.path.isdir(self.images_dir):
        # os.makedirs(self.images_dir)
        if not os.path.isdir(self.train_images_dir):
            os.makedirs(self.train_images_dir)
        if not os.path.isdir(self.val_images_dir):
            os.makedirs(self.val_images_dir)

    def generate_dataset(self):
        logger.info("Converting to coco dataset")
        if not os.path.isdir(self.save_path):
            raise ValueError("not a directory!")
        self._make_coco_dir(self.save_path)
        train_imgs, val_imgs, train_data, val_data = self.dataset_divide(
            self.train_ratio
        )
        self.generate_json(
            train_data, os.path.join(self.anno_dir, "instances_train2017.json")
        )
        self.generate_json(
            val_data, os.path.join(self.anno_dir, "instances_val2017.json")
        )
        if self.img_dir is not None:
            img_path_dict = self.img_path_dict()
            logger.debug("copy imgs")
            print(len(train_imgs), len(val_imgs))
            for t_img in tqdm(train_imgs):
                shutil.copy(
                    img_path_dict[t_img],
                    os.path.join(self.train_images_dir, t_img),
                    follow_symlinks=self.soft_link,
                )
            for v_img in tqdm(val_imgs):
                shutil.copy(
                    img_path_dict[v_img],
                    os.path.join(self.val_images_dir, v_img),
                    follow_symlinks=self.soft_link,
                )
            logger.info("Images copied to coco dir")
        logger.info("COCO dataset generated!")


def arguments():
    parser = argparse.ArgumentParser(description="convert csv to coco")
    parser.add_argument("-s", help="src file path", required=True)
    parser.add_argument("-d", help="dst josn path or coco directory", required=True)
    parser.add_argument("-img", help="img dir path", default=None)
    parser.add_argument("-r", help="ratio of training images", default=0.9, type=float)
    parser.add_argument(
        "-sl", action="store_true", help="using soft link", default=False
    )
    parser.add_argument(
        "-data",
        action="store_true",
        help="generate coco dataset instead of json",
        default=False,
    )
    parser.add_argument(
        "-f",
        help="filter data, make sure images can be found",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-c",
        help="convert name",
        default=None,
    )
    return parser.parse_args()


if __name__ == "__main__":
    # load_path = r"C:\Users\homej\Desktop\2020-10-05-yolo数据集\2020-10-18-文章保留数据_27分类.csv"
    # save_path = r"C:\Users\homej\Desktop\2020-10-05-yolo数据集\2020-10-18-文章保留数据_27分类.json"
    # save_path = r"C:\Users\homej\Desktop\2020-10-05-yolo数据集\coco"
    # coco_data = ToCoco(load_path, save_path)
    # coco_data.generate_data()
    args = arguments()
    coco_data = ToCOCO(
        load_path=args.s,
        save_path=args.d,
        img_dir=args.img,
        soft_link=args.sl,
        train_ratio=args.r,
    )
    if args.c is not None:
        coco_data.name_converter(args.c)
    if args.f:
        coco_data.remove_missing_img()
    if args.data:
        coco_data.generate_dataset()
    else:
        data = coco_data.data
        coco_data.generate_json(data, args.d)
