# vCloud CLI 0.1
#
# Copyright (c) 2014 VMware, Inc. All Rights Reserved.
#
# This product is licensed to you under the
# Apache License, Version 2.0 (the "License").
# You may not use this product except in compliance with the License.
#
# This product may include a number of subcomponents with
# separate copyright notices and license terms. Your use of the source
# code for the these subcomponents is subject to the terms and
# conditions of the subcomponent's license, as noted in the LICENSE file.
#

import click
from lxml import etree
from pyvcloud.vcd.client import QueryResultFormat
import sys
import traceback
from vcd_cli.vcd import as_metavar
from vcd import cli
from vcd_cli.vcd import OPERATIONS


@cli.command()
@click.pass_context
@click.argument('operation',
                default=None,
                type=click.Choice(OPERATIONS),
                metavar=as_metavar(OPERATIONS)
                )
@click.argument('name',
                metavar='[name]',
                required=False)
def extension(ctx, operation, name):
    """Operations with Service Extensions"""
    try:
        raise Exception('not implemented')
    except Exception as e:
        tb = traceback.format_exc()
        click.secho('%s' % e,
                    fg='red', err=True)
