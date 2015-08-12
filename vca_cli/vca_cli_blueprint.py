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


import sys
import click
import yaml
import json
import operator
from vca_cli import cli, utils, default_operation
from pyvcloud.score import Score
from pyvcloud import exceptions
from dsl_parser.exceptions import \
    MissingRequiredInputError, \
    UnknownInputError, \
    FunctionEvaluationError, \
    DSLParsingException
from pyvcloud import Log
import print_utils
from tabulate import tabulate
import collections


def _authorize(cmd_proc):
    result = cmd_proc.re_login()
    if not result:
        utils.print_error('Not logged in', cmd_proc)
        sys.exit(1)
    scoreclient = cmd_proc.vca.get_score_service(cmd_proc.host_score)
    if scoreclient is None:
        utils.print_error('Unable to login to the blueprinting service.',
                          cmd_proc)
        sys.exit(1)
    return scoreclient


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[list | info | validate | upload | delete | status]',
                type=click.Choice(['list', 'info', 'validate', 'upload',
                                   'delete', 'status']))
@click.option('-b', '--blueprint', default='',
              metavar='<blueprint-id>',
              help='Name of the blueprint to create')
@click.option('-f', '--file', 'blueprint_file',
              default=None, metavar='<blueprint-file>',
              help='Local file name of the blueprint to upload',
              type=click.Path(exists=True))
@click.option('-p', '--include-plan', is_flag=True, default=False,
              metavar="include_plan",
              help="Include blueprint plan in INFO operation")
def blueprint(cmd_proc, operation, blueprint, blueprint_file, include_plan):
    """Operations with Blueprints"""
    scoreclient = None
    if 'validate' != operation:
        scoreclient = _authorize(cmd_proc)
    else:
        scoreclient = Score(cmd_proc.host_score)
        Log.debug(cmd_proc.logger, 'using host score: %s' %
                  cmd_proc.host_score)

    if 'validate' == operation:
        _validate(cmd_proc, blueprint_file, scoreclient)

    elif 'list' == operation:
        _list_blueprints(cmd_proc, scoreclient)

    elif 'upload' == operation:
        _upload(cmd_proc, blueprint, blueprint_file, scoreclient)

    elif 'delete' == operation:
        _delete_blueprint(cmd_proc, blueprint, scoreclient)

    elif 'info' == operation:
        _info_blueprint(cmd_proc, scoreclient,
                        include_plan=include_plan)


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[status]',
                type=click.Choice(['status']))
def score(cmd_proc):
    try:
        scoreclient = _authorize(cmd_proc)
        status = scoreclient.get_status()
        print_utils.print_dict(status)
    except exceptions.ClientException as e:
        utils.print_error("Unable to get Score status. Reason: {0}"
                          .format(str(e)), cmd_proc)


def _info_blueprint(cmd_proc, scoreclient, include_plan=False):
    try:
        b = scoreclient.blueprints.get(blueprint)
        headers = ['Id', 'Created']
        table = cmd_proc.blueprints_to_table([b])
        if cmd_proc.json_output:
            json_object = {'blueprint':
                           utils.table_to_json(headers, table)}
            utils.print_json(json_object, cmd_proc=cmd_proc)
        else:
            utils.print_table("Details of blueprint '%s', profile '%s':" %
                              (blueprint, cmd_proc.profile),
                              headers, table, cmd_proc)
        if include_plan:
            utils.print_json(b['plan'], "Blueprint plan", cmd_proc)
    except exceptions.ClientException as e:
                utils.print_error("Blueprint not found. Reason: %s." %
                                  str(e))


def _delete_blueprint(cmd_proc, blueprint_id, scoreclient):
    try:
        scoreclient.blueprints.delete(blueprint_id)
        utils.print_message("successfully deleted blueprint '%s'" %
                            blueprint_id, cmd_proc)
    except exceptions.ClientException as e:
        utils.print_error("Failed to delete blueprint. Reason: %s." %
                          str(e), cmd_proc)


def _upload(cmd_proc, blueprint, blueprint_file, scoreclient):
    try:
        b = scoreclient.blueprints.upload(blueprint_file, blueprint)
        utils.print_message("Successfully uploaded blueprint '%s'." %
                            b.get('id'), cmd_proc)
    except exceptions.ClientException as e:
        utils.print_error("Failed to upload blueprint. Reason: %s." %
                          str(e), cmd_proc)


def _list_blueprints(cmd_proc, scoreclient):
    try:
        blueprints = scoreclient.blueprints.list()
        headers = ['Id', 'Created']
        table = cmd_proc.blueprints_to_table(blueprints)
        if cmd_proc.json_output:
            json_object = {'blueprints':
                           utils.table_to_json(headers, table)}
            utils.print_json(json_object, cmd_proc=cmd_proc)
        else:
            utils.print_table("Available blueprints, profile '%s':" %
                              cmd_proc.profile,
                              headers, table, cmd_proc)
    except exceptions.ClientException as e:
        utils.print_message('Unable to list blueprints. Reason %s.' %
                            str(e), cmd_proc)


def _validate(cmd_proc, blueprint_file, scoreclient):
    try:
        scoreclient.blueprints.validate(blueprint_file)
        utils.print_message("The blueprint is valid.", cmd_proc)
    except MissingRequiredInputError as mrie:
        utils.print_error('Invalid blueprint: ' +
                          str(mrie)[str(mrie).rfind('}') + 1:].
                          strip())
    except UnknownInputError as uie:
        utils.print_error('Invalid blueprint: ' +
                          str(uie)[str(uie).rfind('}') + 1:].
                          strip())
    except FunctionEvaluationError as fee:
        utils.print_error('Invalid blueprint: ' +
                          str(fee)[str(fee).rfind('}') + 1:].
                          strip())
    except DSLParsingException as dpe:
        utils.print_error('Invalid blueprint: ' +
                          str(dpe)[str(dpe).rfind('}') + 1:].
                          strip())
    except Exception as ex:
        utils.print_error('Failed to validate %s:\n %s' %
                          (blueprint_file, str(ex)))


def print_table(msg, obj, headers, table, ctx):
    if (ctx is not None and ctx.obj is not
            None and ctx.obj['json_output']):
        data = [dict(zip(headers, row)) for row in table]
        print(json.dumps(
            {"Errorcode": "0", "Details": msg, obj: data},
            sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        click.echo(click.style(msg, fg='blue'))
        print(tabulate(table, headers=headers,
                       tablefmt="orgtbl"))


def print_deployments(deployments):
    for dep in deployments:
        inputs_view = []
        inputs_line = "%s : %s"
        for i in range(len(dep['inputs'].keys())):
            value = dep['inputs'].values()[i]
            if 'password' in dep['inputs'].keys()[i]:
                value = '************'
            if len(str(value)) > 50:
                value = value[:50] + '...'
            inputs_view.append(inputs_line % (
                dep['inputs'].keys()[i],
                value))
        dep['inputs'] = "\n".join(inputs_view)
        print_utils.print_list(
            [dep],
            ['blueprint_id', 'id', 'created_at', 'inputs'],
            obj_is_dict=True)


def print_deployment_info(deployment, executions, events, ctx=None):
    headers = ['Blueprint Id', 'Deployment Id', 'Created', 'Workflows']
    table = []
    workflows = []
    for workflow in deployment.get('workflows'):
        workflows.append(workflow.get('name').encode('utf-8'))
    table.append(
        [deployment.get('blueprint_id'), deployment.get('id'),
         deployment.get('created_at')[:-7], utils.beautified(workflows)])
    print_table("Deployment information:\n-----------------------",
                'deployment',
                headers, table, ctx)
    print("\n")
    headers = ['Workflow', 'Created', 'Status', 'Id']
    table = []
    if executions is None or len(executions) == 0:
        utils.print_message('no executions found', ctx)
        return
    for e in executions:
        table.append([e.get('workflow_id'),
                      e.get('created_at')[:-7],
                      e.get('status'), e.get('id')])
    sorted_table = sorted(table, key=operator.itemgetter(1), reverse=False)
    print_table("Workflow executions for deployment: '%s'"
                "\n----------------------------------"
                % deployment.get('id'), 'executions', headers, sorted_table,
                ctx)
    if events:
        headers = ['Type', 'Started', 'Message']
        table = []
        for event in events:
            if isinstance(
                    event, collections.Iterable) and 'event_type' in event:
                table.append(
                    [event.get('event_type'), event.get('timestamp'),
                     event.get('message').get('text')])
        print_table("Events for workflow '%s'" %
                    deployment.get('workflow_id'), 'events',
                    headers, table, ctx)


def print_execution(execution, ctx=None):
    if execution:
        headers = ['Workflow', 'Created', 'Status', 'Message']
        table = []
        table.append([
            execution.get('workflow_id'),
            execution.get('created_at')[:-7],
            execution.get('status'),
            execution.get('error')])
        sorted_table = sorted(table,
                              key=operator.itemgetter(1),
                              reverse=False)
        print_table(
            "Workflow execution '%s' for deployment '%s'"
            % (execution.get('id'), execution.get('deployment_id')),
            'execution', headers, sorted_table, ctx)
    else:
        utils.print_message("No execution", ctx)


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[list | info | create | delete | execute | cancel]',
                type=click.Choice(['list', 'info',
                                   'create', 'delete', 'execute', 'cancel']))
@click.option('-w', '--workflow', default=None,
              metavar='<workflow-id>', help='Workflow Id')
@click.option('-d', '--deployment', default='',
              metavar='<deployment-id>', help='Deployment Id')
@click.option('-b', '--blueprint', default=None,
              metavar='<blueprint-id>', help='Blueprint Id')
@click.option('-f', '--file', 'input_file', default=None,
              metavar='<input-file>',
              help='Local file with the input values '
                   'for the deployment (YAML)',
              type=click.File('r'))
@click.option('-s', '--show-events', 'show_events',
              is_flag=True, default=False, help='Show events')
@click.option('-e', '--execution', default=None,
              metavar='<execution-id>', help='Execution Id')
@click.option('--force-cancel', 'force_cancel',
              is_flag=True, default=False, help='Force cancel execution')
@click.option('--force-delete', 'force_delete',
              is_flag=True, default=False, help='Force delete deployment')
def deployment(cmd_proc, operation, deployment, blueprint,
               input_file, workflow, show_events, execution,
               force_cancel, force_delete):
    """Operations with Deployments"""
    scoreclient = _authorize(cmd_proc)

    if 'list' == operation:
        _list_deployments(cmd_proc, scoreclient)

    elif 'create' == operation:
        _create_deployment(cmd_proc, blueprint, deployment, input_file,
                           scoreclient)

    elif 'delete' == operation:
        _delete_deployment(cmd_proc, scoreclient, deployment, force_delete)

    elif 'info' == operation:
        _info_deployment(cmd_proc, scoreclient, deployment,
                         show_events=show_events)

    elif 'execute' == operation:
        _execute_workflow(cmd_proc, deployment, workflow, scoreclient)

    elif 'cancel' == operation:
        _cancel(cmd_proc, execution, force_cancel, scoreclient)


def _cancel(cmd_proc, execution, force_cancel, scoreclient):
    if not execution:
        utils.print_error("execution id is not specified")
        return
    try:
        e = scoreclient.executions.cancel(execution, force_cancel)
        print_execution(e, None) if e else utils.print_message(
            str(scoreclient.response.content), cmd_proc)
    except exceptions.ClientException as e:
        utils.print_error("Failed to cancel workflow. Reasons: {0}."
                          .format(str(e)), cmd_proc)


def _create_deployment(cmd_proc, blueprint, deployment, input_file,
                      scoreclient):
    try:
        inputs = None
        if input_file:
            inputs = yaml.load(input_file)
        scoreclient.deployments.create(
            blueprint, deployment,
            json.dumps(inputs, sort_keys=False,
                       indent=4, separators=(',', ': ')))
        utils.print_message("Successfully created deployment '%s'." %
                            deployment, cmd_proc)
    except exceptions.ClientException as e:
            utils.print_error("Failed to create deployment. Reason: %s" %
                              str(e), cmd_proc)


def _list_deployments(cmd_proc, scoreclient):
    try:
        deployments = scoreclient.deployments.list()
        print_deployments(deployments)
    except exceptions.ClientException as e:
        utils.print_message('No deployments found. Reason %s.' %
                            str(e), cmd_proc)


def _delete_deployment(cmd_proc, scoreclient,
                       deployment_to_delete, force_delete):
    try:
        scoreclient.deployments.delete(deployment_to_delete,
                                       force_delete=force_delete)
        utils.print_message("successfully deleted deployment '%s'" %
                            deployment_to_delete, cmd_proc)
    except exceptions.ClientException as e:
        utils.print_error("Failed to delete deployment. Reason: %s." %
                          str(e), cmd_proc)


def _info_deployment(cmd_proc, scoreclient, deployment_to_show,
                     show_events=False):
    try:
        d = scoreclient.deployments.get(deployment_to_show)
        e = scoreclient.executions.list(deployment_to_show)
        events = None
        if show_events and e is not None and len(e) > 0:
            events = scoreclient.events.get(e[-1].get('id'))
        print_deployment_info(d, e, events)
    except exceptions.ClientException as e:
        utils.print_error("Failed to get deployment info. Reason: %s." %
                          str(e), cmd_proc)


def _execute_workflow(cmd_proc, deployment_for_exection,
                      workflow, scoreclient):
    try:
        if not deployment_for_exection or not workflow:
            utils.print_error("Deployment ID or Workflow ID "
                              "was not specified.")
            return
        e = scoreclient.executions.start(
            deployment_for_exection, workflow)
        print_utils.print_dict(e) if e else utils.print_message(
            str(scoreclient.response.content), cmd_proc)
    except exceptions.ClientException as e:
            utils.print_error("Failed to execute workflow. Reasons: {0}."
                              .format(str(e)), cmd_proc)


@cli.command()
@click.pass_obj
@click.argument('operation', default=default_operation,
                metavar='[list]',
                type=click.Choice(['list']))
@click.option('-i', '--id', 'execution', metavar='<execution-id>',
              required=True, help='Execution Id')
@click.option('-f', '--from', 'from_event',
              default=0, metavar='<from_event>',
              help='From event')
@click.option('-s', '--size', 'batch_size',
              default=100, metavar='<batch_size>',
              help='Size batch of events')
@click.option('-l', '--show-logs', 'show_logs',
              is_flag=True, default=False,
              help='Show logs for event')
def event(cmd_proc, operation, execution, from_event, batch_size, show_logs):
    """Operations with Blueprint Events"""
    scoreclient = _authorize(cmd_proc)

    if 'list' == operation:
        try:
            events = scoreclient.events.get(execution, from_event=from_event,
                                            batch_size=batch_size,
                                            include_logs=show_logs)
            print_table("Status:", 'status', events[0].keys(),
                        [e.values() for e in events[:-1]], None)
            utils.print_message("Total events: {}".format(events[-1]),
                                cmd_proc)
        except exceptions.ClientException as e:
                utils.print_error("Can't find events for execution: {0}. "
                                  "Reason: {1}.".
                                  format(execution, str(e)),
                                  cmd_proc)
