#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
import requests
import json
import time
import base64


from .parameters import *

header_ = {}


def set_header(el2go_api_key: str):
    global header_
    header_ = {'accept': 'application/json', 'EL2G-API-Key': el2go_api_key}


def assign_device_to_devicegroup(config: ConfigParameters):
    params = {"deviceIds": [config.device_id]}
    set_header(config.el2go_api_key)

    # assign device to device group operation
    response = requests.post(f"{config.el2go_api_url}/products/{config.nc12}/device-groups/{config.device_group_id}/devices",
                             headers=header_, json=params)
    if response.status_code == 422:
        print_response(response)
        response_json = json.loads(json.dumps(response.json()))

        # if device is already assigned in another device-group, unassign it and try again
        if response_json["details"] == "1 of 1 devices are already registered.":
            print("Device is already assigned in another group")

            print("Get device-group-id of group in which the device is assigned")
            device_group_id_to_unassign = ""
            response = requests.get(f"{config.el2go_api_url}/products/{config.nc12}/device-groups", headers=header_)
            response_json = json.loads(json.dumps(response.json()))
            found = False
            for device_group in response_json["content"]:
                check_id = device_group["id"]
                response = requests.get(f"{config.el2go_api_url}/products/{config.nc12}/device-groups/{check_id}/devices",
                                        headers=header_)
                response_json = json.loads(json.dumps(response.json()))
                for device_json in response_json["content"]:
                    if device_json["device"]["id"] == config.device_id:
                        device_group_id_to_unassign = check_id
                        found = True
                        break
                if found:
                    break
            if found:
                print("Unassign device from devicegroup")
                params = {"deviceIds": [device_group_id_to_unassign]}
                response = requests.post(f"{config.el2go_api_url}/products/{config.nc12}/device-groups/"
                                         f"{device_group_id_to_unassign}/unclaim", headers=header_)
                print_response(response)

                # Try again
                print("Try to assign device to device-group again")

    return handle_response(response)


# Request the generation status of Secure Objects
def wait_secure_objects_generated(config: ConfigParameters):
    params = {"hardware-family-type": [config.hardware_family_type]}
    response = requests.get(f"{config.el2go_api_url}/rtp/devices/{config.device_id}/secure-object-provisionings",
                            headers=header_, params=params)

    response_json = json.loads(json.dumps(response.json()))
    for provisioning in response_json["content"]:
        if provisioning["provisioningState"] != "GENERATION_COMPLETED":
            return provisioning["provisioningState"]
    return "GENERATION_COMPLETED"


# Download Secure Objects
def download_provisionings(config: ConfigParameters):
    params = {"productHardwareFamilyType": str(config.hardware_family_type), "deviceIds": [config.device_id]}
    response = requests.post(f"{config.el2go_api_url}/rtp/device-groups/{config.device_group_id}"
                             f"/devices/download-provisionings", headers=header_, json=params)
    handle_response(response)
    return response.content.decode("utf-8")


def download_secure_objects(config: ConfigParameters):
    time.sleep(2)
    start_time = time.time()
    while time.time() < start_time + config.timeout:
        provisioning_status = wait_secure_objects_generated(config)

        # If generation status is completed download and store objects to a .bin file
        if provisioning_status == "GENERATION_COMPLETED":
            downloaded_provisionings = download_provisionings(config)
            response_json = json.loads(downloaded_provisionings)
            with open("Secure_Objects.bin", "wb") as f:
                for device_provisioning in response_json:
                    for rtp_provisioning in device_provisioning["rtpProvisionings"]:
                        f.write(base64.b64decode(rtp_provisioning["apdus"]["createApdu"]["apdu"]))
            f.close()
            break
        elif provisioning_status == "GENERATION_TRIGGERED":
            # if generation of Secure Objects is triggered retry with a specific delay until timeout
            print("Secure Objects generation is triggered, application will try again till timeout")
        elif provisioning_status != "GENERATION_TRIGGERED":
            # for any other case return an error
            print(f"Error in Secure Objects, some objects has state: " + provisioning_status)
            break
        time.sleep(config.delay)
    return provisioning_status


def print_response(response):
    print("Request: ".ljust(20) + response.url)
    if response.request.body is not None:
        print("Params: ".ljust(20) + response.request.body.decode("utf-8"))
    print("Response: ".ljust(20) + str(response.status_code))
    print("Response body: ".ljust(20) + response.content.decode("utf-8"))
    print("\n")


def handle_response(response):
    if response.status_code < 200 or response.status_code > 299:
        error_msg = "API call " + response.url + " failed with " + str(response.status_code) + ", " + response.content.decode("utf-8")
        print(error_msg)
        return -1

    return response
