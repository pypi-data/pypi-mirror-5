#!/usr/bin/env python

"""
A runnable script for managing a FireWorks database (a command-line interface to launchpad.py)
"""

from argparse import ArgumentParser
import os
from pymongo import DESCENDING, ASCENDING
from fireworks.core.fw_config import FWConfig
from fireworks.core.launchpad import LaunchPad
from fireworks.core.firework import Workflow
import ast
import json
from fireworks import __version__ as FW_VERSION
from fireworks.utilities.fw_serializers import DATETIME_HANDLER

__author__ = 'Anubhav Jain'
__copyright__ = 'Copyright 2013, The Materials Project'
__version__ = '0.1'
__maintainer__ = 'Anubhav Jain'
__email__ = 'ajain@lbl.gov'
__date__ = 'Feb 7, 2013'


def lpad():
    m_description = 'This script is used for creating and managing a FireWorks database (LaunchPad). For a list of ' \
                    'available commands, type "lpad -h". For more help on a specific command, ' \
                    'type "lpad <command> -h".'

    parser = ArgumentParser(description=m_description)
    subparsers = parser.add_subparsers(help='command', dest='command')

    reset_parser = subparsers.add_parser('reset', help='reset and re-initialize the FireWorks database')
    reset_parser.add_argument('password', help="Today's date, e.g. 2012-02-25. Required to prevent \
    against accidental initializations.")

    addwf_parser = subparsers.add_parser('add', help='insert a Workflow from file')
    addwf_parser.add_argument('wf_file', help="path to a FireWork or Workflow file")

    adddir_parser = subparsers.add_parser('add_dir', help='insert all FWs/Workflows in a directory')
    adddir_parser.add_argument('wf_dir', help="path to a directory containing only FireWorks or Workflow files")

    get_fw_parser = subparsers.add_parser('get_fws', help='get information about FireWorks')
    get_fw_parser.add_argument('-i', '--fw_id', help='get FW with this fw_id', default=None, type=int)
    get_fw_parser.add_argument('-n', '--name', help='get FWs with this name', default=None)
    get_fw_parser.add_argument('-s', '--state', help='get FWs with this state', default=None)
    get_fw_parser.add_argument('-q', '--query', help='get FWs matching this query (as pymongo string, enclose in single-quotes)', default=None)
    get_fw_parser.add_argument('-d', '--display_format', help='display_format ("all","more", "less","ids", "count")', default=None)
    get_fw_parser.add_argument('-m', '--max', help='limit results', default=0, type=int)
    get_fw_parser.add_argument('--sort', help='sort results ("created_on")', default=None)
    get_fw_parser.add_argument('--rsort', help='reverse sort results ("created_on")', default=None)


    get_wf_parser = subparsers.add_parser('get_wfs', help='get information about Workflows')
    get_wf_parser.add_argument('-i', '--fw_id', help='get WF with this fw_id', default=None, type=int)
    get_wf_parser.add_argument('-n', '--name', help='get WFs with this name', default=None)
    get_wf_parser.add_argument('-s', '--state', help='get WFs with this state', default=None)
    get_wf_parser.add_argument('-q', '--query', help='get WFs matching this query (as pymongo string, enclose in single-quotes)', default=None)
    get_wf_parser.add_argument('-d', '--display_format', help='display_format ("all","more", "less","ids", "count")', default=None)
    get_wf_parser.add_argument('-m', '--max', help='limit results', default=0, type=int)
    get_wf_parser.add_argument('--sort', help='sort results ("created_on", "updated_on")', default=None)
    get_wf_parser.add_argument('--rsort', help='reverse sort results ("created_on", "updated_on")', default=None)

    rerun_fw = subparsers.add_parser('rerun_fw', help='re-run a FireWork (reset its previous launches)')
    rerun_fw.add_argument('fw_id', help='FireWork id', type=int)

    reservation_parser = subparsers.add_parser('detect_unreserved', help='Find launches with stale reservations')
    reservation_parser.add_argument('--time', help='expiration time (seconds)',
                                    default=FWConfig().RESERVATION_EXPIRATION_SECS, type=int)
    reservation_parser.add_argument('--fix', help='cancel bad reservations', action='store_true')

    fizzled_parser = subparsers.add_parser('detect_fizzled', help='Find launches that have FIZZLED')
    fizzled_parser.add_argument('--time', help='expiration time (seconds)', default=FWConfig().RUN_EXPIRATION_SECS,
                                type=int)
    fizzled_parser.add_argument('--fix', help='mark fizzled', action='store_true')

    defuse_parser = subparsers.add_parser('defuse', help='cancel (de-fuse) an entire Workflow')
    defuse_parser.add_argument('fw_id', help='Any FireWork id in the workflow to defuse', type=int)

    reignite_parser = subparsers.add_parser('reignite', help='reignite (un-cancel) an entire Workflow')
    reignite_parser.add_argument('fw_id', help='Any FireWork id in the workflow to reignite', type=int)

    defuse_fw_parser = subparsers.add_parser('defuse_fw', help='cancel (de-fuse) a single FireWork')
    defuse_fw_parser.add_argument('fw_id', help='FireWork id to defuse', type=int)

    reignite_fw_parser = subparsers.add_parser('reignite_fw', help='reignite (un-cancel) a single FireWork')
    reignite_fw_parser.add_argument('fw_id', help='FireWork id to reignite', type=int)

    maintain_parser = subparsers.add_parser('maintain', help='Run database maintenance')
    maintain_parser.add_argument('--infinite', help='loop infinitely', action='store_true')
    maintain_parser.add_argument('--maintain_interval', help='sleep time between maintenance loops (infinite mode)',
                                 default=FWConfig().MAINTAIN_INTERVAL, type=int)

    tuneup_parser = subparsers.add_parser('tuneup',
                                          help='Tune-up the database (should be performed during scheduled downtime)')

    subparsers.add_parser('version', help='Print the version of FireWorks installed')

    parser.add_argument('-l', '--launchpad_file', help='path to LaunchPad file containing central DB connection info',
                        default=FWConfig().LAUNCHPAD_LOC)
    parser.add_argument('-c', '--config_dir',
                        help='path to a directory containing the LaunchPad file (used if -l unspecified)',
                        default=FWConfig().CONFIG_FILE_DIR)
    parser.add_argument('--logdir', help='path to a directory for logging', default=None)
    parser.add_argument('--loglvl', help='level to print log messages', default='INFO')
    parser.add_argument('-s', '--silencer', help='shortcut to mute log messages', action='store_true')

    args = parser.parse_args()

    if args.command == 'version':
        print FW_VERSION

    else:
        if not args.launchpad_file and os.path.exists(os.path.join(args.config_dir, 'my_launchpad.yaml')):
            args.launchpad_file = os.path.join(args.config_dir, 'my_launchpad.yaml')

        if args.launchpad_file:
            lp = LaunchPad.from_file(args.launchpad_file)
        else:
            args.loglvl = 'CRITICAL' if args.silencer else args.loglvl
            lp = LaunchPad(logdir=args.logdir, strm_lvl=args.loglvl)

        if args.command == 'reset':
            lp.reset(args.password)

        elif args.command == 'detect_fizzled':
            print lp.detect_fizzled(args.time, args.fix)

        elif args.command == 'detect_unreserved':
            print lp.detect_unreserved(args.time, args.fix)

        elif args.command == 'add':
            fwf = Workflow.from_file(args.wf_file)
            lp.add_wf(fwf)

        elif args.command == 'add_dir':
            for filename in os.listdir(args.wf_dir):
                fwf = Workflow.from_file(filename)
                lp.add_wf(fwf)

        elif args.command == 'maintain':
            lp.maintain(args.infinite, args.maintain_interval)

        elif args.command == 'tuneup':
            lp.tuneup()

        elif args.command == 'get_wfs':
            if sum([bool(x) for x in [args.fw_id, args.name, args.state, args.query]]) > 1:
                raise ValueError('Please specify exactly one of (fw_id, name, state, query)')
            if sum([bool(x) for x in [args.fw_id, args.name, args.state, args.query]]) == 0:
                args.query = '{}'
                args.display_format = args.display_format if args.display_format else 'ids'
            else:
                args.display_format = args.display_format if args.display_format else 'more'

            if args.fw_id:
                query = {'nodes': args.fw_id}
            elif args.name:
                query = {'name': args.name}
            elif args.state:
                query = {'state': args.state}
            else:
                query = ast.literal_eval(args.query)

            if args.sort:
                sort = [(args.sort, ASCENDING)]
            elif args.rsort:
                sort = [(args.rsort, DESCENDING)]
            else:
                sort = None

            ids = lp.get_wf_ids(query, sort, args.max)
            wfs = []
            if args.display_format == 'ids':
                wfs = ids
            elif args.display_format == 'count':
                wfs = [len(ids)]
            else:
                for id in ids:
                    wf = lp.get_wf_by_fw_id(id)
                    d = wf.to_display_dict()
                    if args.display_format == 'more' or args.display_format == 'less':
                        del d['name']
                        del d['parent_links']
                        del d['nodes']
                        del d['links']
                        del d['metadata']
                    if args.display_format == 'less':
                        del d['states']
                        del d['launch_dirs']
                        del d['updated_on']
                    if args.display_format == 'more' or args.display_format == 'all':
                        del d['states_list']
                    wfs.append(d)
            if len(wfs) == 1:
                wfs = wfs[0]

            print json.dumps(wfs, default=DATETIME_HANDLER, indent=4)

        elif args.command == 'get_fws':
            if sum([bool(x) for x in [args.fw_id, args.name, args.state, args.query]]) > 1:
                raise ValueError('Pleases specify exactly one of (fw_id, name, state, query)')
            if sum([bool(x) for x in [args.fw_id, args.name, args.state, args.query]]) == 0:
                args.query = '{}'
                args.display_format = args.display_format if args.display_format else 'ids'
            else:
                args.display_format = args.display_format if args.display_format else 'more'

            if args.fw_id:
                query = {'fw_id': args.fw_id}
            elif args.name:
                query = {'name': args.name}
            elif args.state:
                query = {'state': args.state}
            else:
                query = ast.literal_eval(args.query)

            if args.sort:
                sort = [(args.sort, ASCENDING)]
            elif args.rsort:
                sort = [(args.rsort, DESCENDING)]
            else:
                sort = None

            ids = lp.get_fw_ids(query, sort, args.max)
            fws = []
            if args.display_format == 'ids':
                fws = ids
            elif args.display_format == 'count':
                fws = [len(ids)]
            else:
                for id in ids:
                    fw = lp.get_fw_by_id(id)
                    d = fw.to_dict()
                    if args.display_format == 'more' or args.display_format == 'less':
                        if 'archived_launches' in d:
                            del d['archived_launches']
                        del d['spec']
                    if args.display_format == 'less':
                        if 'launches' in d:
                            del d['launches']


                    fws.append(d)
            if len(fws) == 1:
                fws = fws[0]

            print json.dumps(fws, default=DATETIME_HANDLER, indent=4)


        elif args.command == 'defuse':
            lp.defuse_wf(args.fw_id)

        elif args.command == 'reignite':
            lp.reignite_wf(args.fw_id)

        elif args.command == 'defuse_fw':
            lp.defuse_fw(args.fw_id)

        elif args.command == 'reignite_fw':
            lp.reignite_fw(args.fw_id)

        elif args.command == 'rerun_fw':
            lp.rerun_fw(args.fw_id)


if __name__ == '__main__':
    lpad()