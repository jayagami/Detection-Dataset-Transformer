#!/usr/bin/env python
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\homej\git\Detection-Dataset-Transformer\piplines\labelimg_to_coco.py
# Path: c:\Users\homej
# Created Date: Sunday, June 26th 2022, 1:05:54 am
# Author: Shisui
# 
# Copyright (c) 2022 Uchiha Inc.
###

#%%
from origin.from_labelimg import FromLabelImg
from destination.to_coco import ToCOCO

#%%

def to_coco_piplines(args):
    if args.mode == 'json':
        tococo=ToCOCO(data=middle)
        tococo.generate_json(middle, "dst")
    elif args.mode =="dataset":
        tococo=ToCOCO(data=middle, save_path=args.dst)
        tococo.generate_dataset()