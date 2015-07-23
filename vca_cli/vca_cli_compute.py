# vCloud Air CLI 0.1
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
import operator
from vca_cli import cli, utils, default_operation


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[list | use | info]',
                type=click.Choice(['list', 'use', 'info']))
@click.option('-v', '--vdc', default=None, metavar='<vdc>',
              help='Virtual Data Center Name')
def vdc(cmd_proc, operation, vdc):
    """Operations with Virtual Data Centers"""
    result = cmd_proc.re_login()
    if not result:
        utils.print_error('Not logged in', cmd_proc)
        return
    if 'list' == operation:
        headers = ['Virtual Data Center', "Selected"]
        table = ['', '']
        if cmd_proc.vca.vcloud_session and \
           cmd_proc.vca.vcloud_session.organization:
            links = (cmd_proc.vca.vcloud_session.organization.Link if
                     cmd_proc.vca.vcloud_session.organization else [])
            table1 = [[details.get_name(),
                      '*' if details.get_name() == cmd_proc.vdc_name else '']
                      for details in filter(lambda info: info.name and
                      (info.type_ == 'application/vnd.vmware.vcloud.vdc+xml'),
                      links)]
            table = sorted(table1, key=operator.itemgetter(0), reverse=False)
        utils.print_table(
            "Available Virtual Data Centers in org '%s', profile '%s':" %
            (cmd_proc.vca.org, cmd_proc.profile),
            headers, table, cmd_proc)
    elif 'use' == operation:
        the_vdc = cmd_proc.vca.get_vdc(vdc)
        if the_vdc is not None:
            utils.print_message("Using vdc '%s', profile '%s'" %
                                (vdc, cmd_proc.profile), cmd_proc)
            cmd_proc.vdc_name = vdc
        else:
            utils.print_error("Unable to select vdc '%s' in profile '%s'" %
                              (vdc, cmd_proc.profile), cmd_proc)
    elif 'info' == operation:
        if vdc is None:
            vdc = cmd_proc.vdc_name
        the_vdc = cmd_proc.vca.get_vdc(vdc)
        if the_vdc:
            gateways = cmd_proc.vca.get_gateways(vdc)
            headers1 = ['Type', 'Name']
            table1 = cmd_proc.vdc_to_table(the_vdc, gateways)
            headers2 = ['Resource', 'Allocated',
                        'Limit', 'Reserved', 'Used', 'Overhead']
            table2 = cmd_proc.vdc_resources_to_table(the_vdc)
            headers3 = ['Name', 'External IPs', 'DHCP', 'Firewall', 'NAT',
                        'VPN', 'Routed Networks', 'Syslog', 'Uplinks']
            table3 = cmd_proc.gateways_to_table(gateways)
            if cmd_proc.json_output:
                json_object = {'vdc_entities':
                               utils.table_to_json(headers1, table1),
                               'vdc_resources':
                               utils.table_to_json(headers2, table2),
                               'gateways':
                               utils.table_to_json(headers3, table3)}
                utils.print_json(json_object, cmd_proc=cmd_proc)
            else:
                utils.print_table(
                    "Details of Virtual Data Center '%s', profile '%s':" %
                    (vdc, cmd_proc.profile),
                    headers1, table1, cmd_proc)
                utils.print_table("Compute capacity:",
                                  headers2, table2, cmd_proc)
                utils.print_table('Gateways:',
                                  headers3, table3, cmd_proc)
        else:
            utils.print_error("Unable to select vdc '%s' in profile '%s'" %
                              (vdc, cmd_proc.profile), cmd_proc)
    cmd_proc.save_current_config()


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[list | info | create | delete | power-on'
                        ' | power-off | deploy | undeploy | customize'
                        ' | insert | eject | connect | disconnect'
                        ' | attach | detach]',
                type=click.Choice(
                    ['list', 'info', 'create', 'delete', 'power.on',
                     'power.off', 'deploy', 'undeploy', 'customize',
                     'insert', 'eject', 'connect', 'disconnect',
                     'attach', 'detach']))
@click.option('-v', '--vdc', default=None,
              metavar='<vdc>', help='Virtual Data Center Name')
@click.option('-a', '--vapp', 'vapp', default='',
              metavar='<vapp>', help='vApp name')
@click.option('-c', '--catalog', default='',
              metavar='<catalog>', help='Catalog name')
@click.option('-t', '--template', default='',
              metavar='<template>', help='Template name')
@click.option('-n', '--network', default='',
              metavar='<network>', help='Network name')
@click.option('-m', '--mode', default='POOL',
              metavar='[pool, dhcp, manual]', help='Network connection mode',
              type=click.Choice(['POOL', 'pool', 'DHCP', 'dhcp', 'MANUAL',
                                 'manual']))
@click.option('-V', '--vm', 'vm_name', default=None,
              metavar='<vm>', help='VM name')
@click.option('-f', '--file', 'cust_file',
              default=None, metavar='<customization_file>',
              help='Guest OS Customization script file', type=click.File('r'))
@click.option('-e', '--media', default='',
              metavar='<media>', help='Virtual media name (ISO)')
@click.option('-d', '--disk', 'disk_name', default=None,
              metavar='<disk_name>', help='Disk Name')
@click.option('-o', '--count', 'count', default=1,
              metavar='<count>', help='Number of vApps to create')
@click.option('-p', '--cpu', 'cpu', default=None,
              metavar='<virtual CPUs>', help='Virtual CPUs')
@click.option('-r', '--ram', 'ram', default=None,
              metavar='<MB RAM>', help='Memory in MB')
@click.option('-i', '--ip', default='', metavar='<ip>', help='IP address')
def vapp(cmd_proc, operation, vdc, vapp, catalog, template,
         network, mode, vm_name, cust_file,
         media, disk_name, count, cpu, ram, ip):
    """Operations with vApps"""
    result = cmd_proc.re_login()
    if not result:
        utils.print_error('Not logged in', cmd_proc)
        return
    if vdc is None:
        vdc = cmd_proc.vdc_name
    the_vdc = cmd_proc.vca.get_vdc(vdc)
    if 'list' == operation:
        headers = ['vApp', "VMs", "Status", "Deployed", "Description"]
        table = cmd_proc.vapps_to_table(the_vdc)
        if cmd_proc.json_output:
            json_object = {'vapps':
                           utils.table_to_json(headers, table)}
            utils.print_json(json_object, cmd_proc=cmd_proc)
        else:
            utils.print_table("Available vApps in '%s', profile '%s':" %
                              (vdc, cmd_proc.profile),
                              headers, table, cmd_proc)
    elif 'create' == operation:
        for x in xrange(1, count + 1):
            vapp_name = vapp
            if count > 1:
                vapp_name += '-' + str(x)
            utils.print_message("creating vApp '%s' in VDC '%s'"
                                " from template '%s' in catalog '%s'" %
                                (vapp_name, vdc, template, catalog), cmd_proc)
            task = None
            if vm_name is not None:
                if (cmd_proc.vca.version == "1.0") or \
                   (cmd_proc.vca.version == "1.5") or \
                   (cmd_proc.vca.version == "5.1") or \
                   (cmd_proc.vca.version == "5.5"):
                    task = cmd_proc.vca.create_vapp(vdc, vapp_name,
                                                    template, catalog)
                else:
                    task = cmd_proc.vca.create_vapp(vdc, vapp_name,
                                                    template, catalog,
                                                    vm_name=vm_name)
            if task:
                utils.display_progress(task, cmd_proc,
                                       cmd_proc.vca.vcloud_session.
                                       get_vcloud_headers())
            else:
                utils.print_error("can't create the vApp", cmd_proc)
                return
            the_vdc = cmd_proc.vca.get_vdc(vdc)
            the_vapp = cmd_proc.vca.get_vapp(the_vdc, vapp_name)
            if ((vm_name is not None) and
                ((cmd_proc.vca.version == "1.0") or
                 (cmd_proc.vca.version == "1.5") or
                 (cmd_proc.vca.version == "5.1") or
                 (cmd_proc.vca.version == "5.5"))):
                if vm_name is not None:
                    utils.print_message(
                        "setting VM name to '%s'"
                        % (vm_name), cmd_proc)
                    task = the_vapp.modify_vm_name(1, vm_name)
                    if task:
                        utils.display_progress(task, cmd_proc,
                                               cmd_proc.vca.vcloud_session.
                                               get_vcloud_headers())
                    else:
                        utils.print_error("can't set VM name", cmd_proc)
                        return
                    the_vapp = cmd_proc.vca.get_vapp(the_vdc, vapp_name)
            if vm_name is not None:
                utils.print_message(
                    "setting computer name for VM '%s'"
                    % (vm_name), cmd_proc)
                task = the_vapp.customize_guest_os(vm_name,
                                                   computer_name=vm_name)
                if task:
                    utils.display_progress(task, cmd_proc,
                                           cmd_proc.vca.vcloud_session.
                                           get_vcloud_headers())
                else:
                    utils.print_error("can't set computer name", cmd_proc)
                the_vapp = cmd_proc.vca.get_vapp(the_vdc, vapp_name)
            if cpu is not None:
                utils.print_message(
                    "configuring '%s' vCPUs for VM '%s', vApp '%s'"
                    % (cpu, vm_name, vapp_name), cmd_proc)
                task = the_vapp.modify_vm_cpu(vm_name, cpu)
                if task:
                    utils.display_progress(task, cmd_proc,
                                           cmd_proc.vca.vcloud_session.
                                           get_vcloud_headers())
                else:
                    utils.print_error("can't configure virtual CPUs", cmd_proc)
                the_vapp = cmd_proc.vca.get_vapp(the_vdc, vapp_name)
            # if ram is not None:
            #     print_message("configuring '%s' MB of memory"
            #                   " for VM '%s', vApp '%s'"
            #                   % (ram, vm_name, vapp_name), ctx)
            #     task = the_vapp.modify_vm_memory(vm_name, ram)
            #     if task:
            #         display_progress(task, ctx,
            #                          vca.vcloud_session.get_vcloud_headers())
            #     else:
            #         ctx.obj['response'] = the_vapp.response
            #         print_error("can't configure RAM", ctx)
            #     the_vapp = vca.get_vapp(the_vdc, vapp_name)
            # if '' != network:
            #     print_message("disconnecting VM from networks"
            #                   " pre-defined in the template", ctx)
            #     task = the_vapp.disconnect_vms()
            #     if task:
            #         display_progress(task, ctx,
            #                          vca.vcloud_session.get_vcloud_headers())
            #     else:
            #         ctx.obj['response'] = the_vapp.response
            #         print_error("can't disconnect VM from networks", ctx)
            #         return
            #     print_message("disconnecting vApp from networks"
            #                   " pre-defined in the template", ctx)
            #     task = the_vapp.disconnect_from_networks()
            #     if task:
            #         display_progress(task, ctx,
            #                          vca.vcloud_session.get_vcloud_headers())
            #     else:
            #         ctx.obj['response'] = the_vapp.response
            #         print_error("can't disconnect vApp from networks", ctx)
            #         return
            #     nets = filter(lambda n: n.name == network,
            #                   vca.get_networks(vdc))
            #     if len(nets) == 1:
            #         print_message(
            #             "connecting vApp to network"
            #             " '%s' with mode '%s'" % (network, mode), ctx)
            #         task = the_vapp.connect_to_network(
            #             nets[0].name, nets[0].href)
            #         if task:
            #             display_progress(
            #                 task, ctx,
            #                 vca.vcloud_session.get_vcloud_headers())
            #         else:
            #             ctx.obj['response'] = the_vapp.response
            #             print_error("can't connect the vApp to the network",
            #                         ctx)
            #             return
            #         print_message("connecting VM to network '%s'"
            #                       " with mode '%s'" % (network, mode), ctx)
            #         task = the_vapp.connect_vms(
            #             nets[0].name,
            #             connection_index=0,
            #             ip_allocation_mode=mode.upper(),
            #             mac_address=None, ip_address=ip)
            #         if task:
            #             display_progress(
            #                 task, ctx,
            #                 vca.vcloud_session.get_vcloud_headers())
            #         else:
            #             ctx.obj['response'] = the_vapp.response
            #             print_error(
            #                 "can't connect the VM to the network", ctx)
    elif 'delete' == operation:
        utils.print_message("deleting vApp '%s' from VDC '%s'" % (vapp, vdc),
                            cmd_proc)
        task = cmd_proc.vca.delete_vapp(vdc, vapp)
        if task:
            utils.display_progress(task, cmd_proc,
                                   cmd_proc.vca.vcloud_session.
                                   get_vcloud_headers())
        else:
            utils.print_error("can't delete the vApp", cmd_proc)
    else:
        utils.print_message('not implemented', cmd_proc)
    cmd_proc.save_current_config()
