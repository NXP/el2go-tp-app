#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause
"""Main module."""

import logging

from spsdk.mboot.commands import CmdPacket, TrustProvisioningResponse
from spsdk.mboot.error_codes import StatusCode
from spsdk.mboot.mcuboot import McuBoot
from typing_extensions import Self
from typing import Optional, List

logger = logging.getLogger(__name__)

EL2GO_TP_COMMAND_GROUP = 0x20
EL2GO_TP_GET_FW_VERSION_CMD = 0x01
EL2GO_TP_PROVISIONING_CMD = 0x02


# You don't have to use CmdPacket directly as Mboot does. Here's a helper class
class EL2GoProvisionCMD(CmdPacket):
    def __init__(self, address: int, flag: bool) -> None:
        super().__init__(
            EL2GO_TP_COMMAND_GROUP, 0, EL2GO_TP_PROVISIONING_CMD, address
        )


class EL2GOMboot(McuBoot):
    def el2go_get_version(self) -> Optional[List[int]]:
        logger.info("Getting FW version")
        cmd_packet = CmdPacket(EL2GO_TP_COMMAND_GROUP, 0, EL2GO_TP_GET_FW_VERSION_CMD)
        cmd_response = self._process_cmd(cmd_packet=cmd_packet)
        if isinstance(cmd_response, TrustProvisioningResponse):
            return cmd_response.values
        return None

    def close_device(self, address: int, dry_run: bool = False) -> Optional[List[int]]:
        logger.info(f"CMD: Close device")
        cmd_packet = CmdPacket(EL2GO_TP_COMMAND_GROUP, 0, EL2GO_TP_PROVISIONING_CMD, address, dry_run)
        cmd_response = self._process_cmd(cmd_packet=cmd_packet)
        if isinstance(cmd_response, TrustProvisioningResponse):
            return cmd_response.values
        return None

    # this won't be needed starting SPSDK 2.0
    def __enter__(self) -> Self:
        return super().__enter__()


class EL2GOStatus(StatusCode):
    EL2GO_PROV_SUCCESS = (
        "0x5a5a5a5a",
        "EL2GO_FW_PASS",
        "Device has been successfully provisioned."
    )
