# VMware vCloud Director CLI
#
# Copyright (c) 2017 VMware, Inc. All Rights Reserved.
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
from pyvcloud.vcd.vdc import VDC
from vcd_cli.utils import restore_session
from vcd_cli.utils import stderr
from vcd_cli.utils import stdout
from vcd_cli.vcd import vcd


@vcd.group(short_help='work with vcd network')
@click.pass_context
def network(ctx):
    """Work with networks in vCloud Director.

\b
    Examples
        vcd network create 'direct-net1' --type 'vdc-direct' \\
            --description 'directly connected orgvdc network' \\
            --parent 'ext-net1'
            Create an org vdc network which is directly connected \\
                to an external network
    """

    if ctx.invoked_subcommand is not None:
        try:
            restore_session(ctx)
        except Exception as e:
            stderr(e, ctx)


@network.command('create', short_help='create a new network in vcd')
@click.pass_context
@click.argument('name', metavar='<name>', required=True)
@click.option(
    '-t',
    '--type',
    'type',
    required=True,
    metavar='<type>',
    default=None,
    help='Type of the network to be created (viz. '
         'vdc-direct/vdc-isolated).')
@click.option(
    '-d',
    '--description',
    'description',
    required=False,
    metavar='<description>',
    default='',
    help='Description of the network.')
@click.option(
    '-P',
    '--parent',
    'parent_network_name',
    required=False,
    metavar='<external network>',
    help='Name of the external network to be connected to.')
def create(ctx, name, type, description, parent_network_name):
    try:
        client = ctx.obj['client']
        in_use_vdc_href = ctx.obj['profiles'].get('vdc_href')
        vdc = VDC(client, href=in_use_vdc_href)
        if type.casefold() == 'vdc-direct'.casefold():
            result = vdc.create_directly_connected_vdc_network(
                network_name=name,
                description=description,
                parent_network_name=parent_network_name)
            stdout(result.Tasks.Task[0], ctx)
        else:
            raise Exception('Invalid supplied network type %s'
                             % type)
    except Exception as e:
        stderr(e, ctx)
