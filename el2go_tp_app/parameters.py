#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
from dataclasses import dataclass
import os
import xml.etree.ElementTree as eT


def str_little_endian(val):
    return f"{(val >> 0) & 0xFF:02x}{(val >> 8) & 0xFF:02x}{(val >> 16) & 0xFF:02x}{(val >> 24) & 0xFF:02x}"


@dataclass
class ConfigParameters:
    el2go_api_hostname: str
    el2go_api_key: str
    el2go_api_url: str
    device_group_id: str
    device_id: str
    nc12: str
    hardware_family_type: str
    uuid_fuse_start: int
    uuid_fuse_end: int
    delay: int
    timeout: int

    def parse_config_file(self, config_file_path) -> int:
        if not os.path.exists(config_file_path):
            print("ERROR: Config file path " + config_file_path + " not found")
            return -1

        config_file_path = os.path.abspath(config_file_path)
        print("Location of config file: " + config_file_path)

        try:
            tree = eT.parse(config_file_path)
        except:
            print("ERROR: Could not parse " + config_file_path + " as a .xml file")
            return -1

        root = tree.getroot()

        # Parse device id
        self.device_group_id = root.find("deviceGroupId").text
        if self.device_group_id is None:
            print("ERROR: deviceGroupId cannot be empty")
            return -1

        try:
            self.nc12 = root.find("nc12").text
        except:
            print("12NC not present in the configuration file; this is needed just in case tests are done on RW61x")

        # Parse hardware family type
        self.hardware_family_type = root.find("hardwareFamilyType").text
        if self.hardware_family_type is None:
            print("ERROR: hardwareFamilyType cannot be empty")
            return -1

        # Parse UUID first and last fuse address
        self.uuid_fuse_start = int(root.find("firstFuseAddress").text)
        if self.uuid_fuse_start <= 0:
            print("ERROR: firstFuseAddress cannot be empty or negative")
            return -1

        self.uuid_fuse_end = int(root.find("lastFuseAddress").text)
        if self.uuid_fuse_end <= 0:
            print("ERROR: lastFuseAddress cannot be empty or negative")
            return -1

        # Parse delay and timeout values
        self.delay = int(root.find("delay").text)
        if self.delay < 0:
            print("ERROR: delay cannot be negative")
            return -1

        self.timeout = int(root.find("timeout").text)
        if self.timeout < 0:
            print("ERROR: timeout cannot be negative")
            return -1

        # Parse EL2GO backend settings
        el2go_settings_node = root.find("el2goSettings")
        self.el2go_api_hostname = el2go_settings_node.find("edgelock2goHostname").text
        if self.el2go_api_hostname is None:
            print("ERROR: edgelock2goHostname cannot be empty")
            return -1
        self.el2go_api_key = el2go_settings_node.find("edgelock2goApiKey").text
        if self.el2go_api_key is None:
            print("ERROR: edgelock2goApiKey cannot be empty")
            return -1
        self.el2go_api_url = el2go_settings_node.find("edgelock2goApiUrl").text
        if self.el2go_api_url is None:
            print("ERROR: edgelock2goApiUrl cannot be empty")
            return -1

        return 0

    def __init__(self) -> None:
        self.device_id = ""
        self.device_group_id = ""
        self.nc12 = ""
        self.el2go_api_hostname = ""
        self.el2go_api_key = ""
        self.el2go_api_url = ""
        self.hardware_family_type = ""
        self.uuid_fuse_start = 0
        self.uuid_fuse_end = 0
        self.delay = 0
        self.timeout = 0

