#!/usr/bin/env python
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\homej\git\Detection-Dataset-Transformer\piplines\src_loader.py
# Path: c:\Users\homej
# Created Date: Sunday, June 26th 2022, 1:19:37 am
# Author: Shisui
#
# Copyright (c) 2022 Uchiha Inc.
###

#%%
from origin.from_labelimg import FromLabelImg
from destination.to_coco import ToCOCO
from base.logger import GetLogger

log = GetLogger(__name__)
logger = log.get()


class Pipline:
    def __init__(self, args):
        self.args = args
        self.middle = self.src_loader()

    def src_loader(self):
        if self.args.stype == "labelimg":
            return FromLabelImg(self.args.anno).gen()
        else:
            raise Exception("src_type error")

    def transform(self):
        if self.args.dtype == "coco":
            logger.info("transform from labelimg to coco")
            self.tococo()

    def tococo(self):
        if self.args.mode == "json":
            tococo = ToCOCO(data=self.middle)
            tococo.generate_json(self.middle.to_pandas(), "dst")
        elif self.args.mode == "dataset":
            tococo = ToCOCO(data=self.middle, save_path=self.args.dst, img_dir=self.args.img, read_img_size=self.args.read_img_size)
            tococo.generate_dataset()
