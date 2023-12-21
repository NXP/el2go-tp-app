#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause

"""Console script for el2go_tp_app."""
import logging
import sys

import click

# Some of the app utilities from SPSDK may come quite handy
from spsdk.apps.utils.utils import (
    INT,
    catch_spsdk_error,
)

from spsdk.apps.utils import spsdk_logger
from spsdk.apps.utils.common_cli_options import (
    isp_interfaces,
    spsdk_apps_common_options,
    is_click_help
)

from .el2go_tp_app import EL2GOMboot, EL2GOStatus
from spsdk.mboot.mcuboot import McuBoot
from spsdk.mboot.scanner import get_mboot_interface
from .api_utils import *


# This is pretty much a carbon copy of blhost
@click.group(no_args_is_help=True)
# this decorator is responsible for interface selection in CLI (--port/--usb etc.)
# at this point, everything this this decorator produces must be explicitly handled in user code
# in the future, this will no longer be the case and the decorator will return MBootInterface directly
@isp_interfaces(uart=True, usb=True, lpcusbsio=True)
# this one is for simple --verbose/--debug/--help/--version options
@spsdk_apps_common_options
@click.pass_context
def main(
    ctx: click.Context,
    port: str,
    usb: str,
    lpcusbsio: str,
    use_json: bool,
    log_level: int,
    timeout: int,
) -> int:
    """Use EdgeLock 2GO service to provision a device."""
    log_level = log_level or logging.WARNING
    # our logger provides some fancy colors and some basic timing (run the app with -vv/--debug to see it)
    spsdk_logger.install(level=log_level)

    # no need to scan for interfaces if we only want to show a help message
    # anything stored in `ctx.obj` can be later retrieved via `click.pass_obj` decorator
    if not is_click_help(ctx, sys.argv):
        ctx.obj = {
            "interface": get_mboot_interface(
            port=port,
            usb=usb,
            timeout=timeout,
            lpcusbsio=lpcusbsio,
        ),
        "use_json": use_json,
        "suppress_progress_bar": use_json or log_level < logging.WARNING,
    }


@main.command(name="get-fw-version")
@click.pass_context
# The subcommand name doesn't necessarily has to match the function name
def get_version(ctx: click.Context) -> None:
    """ Return EL2GO NXP Provisioning Firmware's version. """
    with EL2GOMboot(ctx.obj["interface"]) as el2go_mboot:
        version = el2go_mboot.el2go_get_version()
    display_output(el2go_mboot.status_code)
    if el2go_mboot.status_code == EL2GOStatus.SUCCESS:
        version = '{}'.format(', '.join(hex(x) for x in version))
        version = "v" + version[2] + "." + version[3:5] + "." + version[5:7]
        click.echo(f"Firmware version: {version}")


@main.command()
@click.argument("address", type=INT(), required=True)
@click.option(
    "-d",
    "--dry-run",
    is_flag=True,
    default=False,
    help=(
        "Enable Provisioning Firmware dry run, meaning that no fuses will be burned "
    ),
)
@click.pass_context
def close_device(
    ctx: click.Context,
    address: int,
    dry_run: bool,
) -> None:
    """Launch EL2GO NXP Provisioning Firmware."""

    with EL2GOMboot(ctx.obj["interface"]) as mboot:
        response = mboot.close_device(address, dry_run)
        display_output(mboot.status_code)
        if mboot.status_code == EL2GOStatus.SUCCESS:
            hex_response = '{}'.format(', '.join(hex(x) for x in response))
            if hex_response == EL2GOStatus.EL2GO_PROV_SUCCESS:
                click.echo(f"Device has been successfully provisioned.")
            else:
                click.echo(f"Provision of device has failed with error code :{hex_response}.")


@main.command()
@click.argument("file", type=str, required=True)
@click.pass_context
def get_secure_objects(
    ctx: click.Context,
    file: str,
) -> None:
    """Download Secure Objects."""
    response = ""

    config = ConfigParameters()

    if config.parse_config_file(file) == -1:
        click.echo(f"ERROR: Parsing config file failed")
        exit()

    with McuBoot(ctx.obj["interface"]) as mboot:
        for x in range(config.uuid_fuse_start, config.uuid_fuse_end + 1):
            response += str_little_endian(mboot.efuse_read_once(x))
    response = int(response, 16)
    config.device_id = str(response)

    assign_device_to_devicegroup(config)
    status = download_secure_objects(config)

    if status == "GENERATION_TRIGGERED":
        click.echo(f"Secure Objects generation timeout")


# just a little thing to get a nicer-looking status code string
def display_output(status_code: int) -> None:
    click.echo(
        f"Response status = {status_code} ({status_code:#x}) "
        f"{EL2GOStatus.desc(status_code, f'Unknown error code ({status_code})')}."
    )


@catch_spsdk_error
def safe_main() -> None:
    """Calls the main function."""
    sys.exit(main())  # pylint: disable=no-value-for-parameter


if __name__ == "__main__":
    safe_main()  # pragma: no cover
