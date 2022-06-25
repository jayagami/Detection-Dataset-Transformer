#!/usr/bin/env python
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\homej\git\Detection-Dataset-Transformer\origin\from_labelimg.py
# Path: c:\Users\homej
# Created Date: Saturday, June 25th 2022, 9:47:47 pm
# Author: Shisui
#
# Copyright (c) 2022 Uchiha Inc.
###

from datatable import (dt, f, by, ifelse, update, sort,
                       count, min, max, mean, sum, rowsum)
import numpy as np
import os
import xmltodict
from tqdm import tqdm
# import xml.etree.cElementTree as ET


class FromLabelImg:
    def __init__(self, anno_dir, image_dir=None):
        super().__init__()
        self.anno_dir = anno_dir
        self.image_dir = image_dir
        self.database = dt.Frame()
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

    @staticmethod
    def read_xml(xml_file):
        img_name = os.path.basename(xml_file)
        with open(xml_file, "rb") as xml:
            content = xmltodict.parse(xml)
        if "object" not in content["annotation"]:
            raise Exception("{} has no object".format(img_name))

        img_path = content["annotation"]["path"]
        # img_path = os.path.join(
        # img_path.split("/")[0], "JPEGImages", img_path.split("/")[2]
        # )
        # img_path = os.path.join("/".join(xml_file.split("/")[:-3]), img_path)

        boxes = content["annotation"]["object"]
        filename = os.path.basename(img_path)
        height = int(content["annotation"]["size"]["height"])
        width = int(content["annotation"]["size"]["width"])

        bbox_list = []
        if type(boxes) is list:
            for box in boxes:
                # print('---Box is',box)
                xmin = box["bndbox"]["xmin"]
                ymin = box["bndbox"]["ymin"]
                xmax = box["bndbox"]["xmax"]
                ymax = box["bndbox"]["ymax"]
                label = box["name"]
                bbox_data = {
                    "filename": [
                        filename,
                    ],
                    "width": [
                        width,
                    ],
                    "height": [
                        height,
                    ],
                    "label": [
                        label,
                    ],
                    "xmin": [
                        xmin,
                    ],
                    "ymin": [
                        ymin,
                    ],
                    "xmax": [
                        xmax,
                    ],
                    "ymax": [
                        ymax,
                    ],
                }
                bbox_list.append(bbox_data)
        return bbox_list

    def gen(self):
        xml_path_dict = self.path_dict(self.anno_dir, ext=".xml")
        for k, v in tqdm(xml_path_dict.items()):
            bbox_list = self.read_xml(v)
            for bbox in bbox_list:
                self.database.rbind(dt.Frame(bbox))
        return self.database


if __name__ == "__main__":
    annodir = r"C:\Users\homej\Desktop\hau\2022-06-25-廖秀辉\annotation"
    fli = FromLabelImg(annodir)
    result = fli.gen()
