#!/usr/bin/env python3
# -*- coding:utf-8 -*-
###
# Filename: /home/jay/git/lab_works/log.py
# Path: /home/jay/git/lab_works
# Created Date: Monday, October 19th 2020, 9:11:55 pm
# Author: Jay
#
# Copyright (c) 2020 Uchiha
###
#

import logging.config
# create formatter


class GetLogger:
    def __init__(self, name):
        logging.getLogger().setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(formatter)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(ch)
        ch.close()

    def get(self):
        return self.logger
