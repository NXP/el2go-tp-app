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
from spsdk.apps.utils import (
    INT,
    MBootInterface,
    catch_spsdk_error,
    get_interface,
    isp_interfaces,
    spsdk_apps_common_options,
    spsdk_logger,
)

from .el2go_tp_app import EL2GOMboot, EL2GOStatus


# This is pretty much a carbon copy of blhost
@click.group(no_args_is_help=True)
# this decorator is responsible for interface selection in CLI (--port/--usb etc.)
# at this point, everything this this decorator produces must be explicitly handled in user code
# in the future, this will no longer be the case and the decorator will return MBootInterface directly
@isp_interfaces(uart=True, usb=True, lpcusbsio=False, json_option=False)
# this one is for simple --verbose/--debug/--help/--version options
@spsdk_apps_common_options
@click.pass_context
def main(
    ctx: click.Context,
    port: str,
    usb: str,
    timeout: int,
    log_level: int,
):
    """Use EdgeLock 2GO service to provision a device."""
    log_level = log_level or logging.WARNING
    # our logger provides some fancy colors and some basic timing (run the app with -vv/--debug to see it)
    spsdk_logger.install(level=log_level)

    # no need to scan for interfaces if we only want to show a help message
    if "--help" not in sys.argv[1:]:
        # anything stored in `ctx.obj` can be later retrieved via `click.pass_obj` decorator
        ctx.obj = get_interface(module="mboot", port=port, usb=usb, timeout=timeout)


@main.command(name="get-fw-version")
@click.pass_obj
# The subcommand name doesn't necessarily has to match the function name
def get_version(device: MBootInterface) -> None:
    """ Return EL2GO NXP Provisioning Firmware's version. """
    with EL2GOMboot(device=device) as el2go_mboot:
        version = el2go_mboot.el2go_get_version()
    display_output(el2go_mboot.status_code)
    if el2go_mboot.status_code == EL2GOStatus.SUCCESS:
        version = '{}'.format(', '.join(hex(x) for x in version))
        version = "v" + version[2] + "." + version[3:5] + "." + version[5:7]
        click.echo(f"Firmware version: {version}")


@main.command()
@click.pass_obj
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
def close_device(
    device: MBootInterface,
    address: int,
    dry_run: bool,
) -> None:
    """Launch EL2GO NXP Provisioning Firmware."""

    with EL2GOMboot(device=device) as mboot:
        response = mboot.close_device(address, dry_run)
        display_output(mboot.status_code)
        if mboot.status_code == EL2GOStatus.SUCCESS:
            hex_response = '{}'.format(', '.join(hex(x) for x in response))
            if hex_response == EL2GOStatus.EL2GO_PROV_SUCCESS:
                click.echo(f"Device has been successfully provisioned.")
            else:
                click.echo(f"Provision of device has failed with error code :{hex_response}.")


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
