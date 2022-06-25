#!/usr/bin/env python
# -*- coding:utf-8 -*-
###
# Filename: c:\Users\homej\git\Detection-Dataset-Transformer\main.py
# Path: c:\Users\homej
# Created Date: Saturday, June 25th 2022, 9:47:14 pm
# Author: Shisui
# 
# Copyright (c) 2022 Uchiha Inc.
###

#%%
from origin.from_labelimg import FromLabelImg
from destination.to_coco import ToCOCO
import os
from piplines.pipline import Pipline
import argparse

#%%

def parse_args():
    parser = argparse.ArgumentParser(description="Detection Dataset Transformer")
    parser.add_argument("-dtype", type=str, help="source type of dst dataset")
    parser.add_argument("-stype", type=str, help="destination type of dst dataset")
    parser.add_argument("-anno", type=str, help="annonation src path")
    parser.add_argument("-img", type=str, help="image src path")
    parser.add_argument("-mode", type=str, help="transform mode")
    parser.add_argument("-dst", type=str, help="dst path")
    parser.add_argument("-save_middle", type=str, help="middle data save path")
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    p = Pipline(args)
    p.transform()
    #%%
if __name__ == "__main__":
    dir = r"C:\Users\homej\Desktop\hau\2022-06-25-廖秀辉\annotation"
    main()
# %%

# %%