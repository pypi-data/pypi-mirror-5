from .wiggle import Entity
from .package import Package
from .dataset import Dataset

from fifo.helper import *
from fifo.api.package import *
from fifo.api.dataset import *

from datetime import datetime
import sys
import json

def vm_action(args):
    if args.action == 'start':
        args.endpoint.start(args.uuid)

    elif args.action == 'stop':
        if args.f:
            args.endpoint.force_stop(args.uuid)
        else:
            args.endpoint.stop(args.uuid)
    elif args.action == 'reboot':
        if args.f:
            args.endpoint.force_reboot(args.uuid)
        else:
            args.endpoint.reboot(args.uuid)

def snapshot_create(args):
    res = args.endpoint.make_snapsot(args.vmuuid, args.comment)
    if res:
        print "Snapshot successfully created!"
    else:
        print "Snapshot creation failed!"

# Helper functions to format the different getters for VM's
def vm_map_fn(vm):
    return(vm['config'])

def vm_info_map_fn(vm):
    return(vm['info'])

def vm_metadata_map_fn(vm):
    return(vm['metadata'])

# Returns the ip of a vm (first ip in the networks)
def vm_ip(e):
    n = d(e, ['config', 'networks'], [])
    if len(n) > 0:
        return n[0]['ip']
    else:
        return "-"

vm_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'alias':
    {'title': 'alias', 'len': 10, 'fmt': "%-10s", 'get': lambda e: d(e, ['config', 'alias'])},
    'ip':
    {'title': 'IP', 'len': 15, 'fmt': "%15s", 'get': vm_ip},
    'state':
    {'title': 'state', 'len': 15, 'fmt': "%-15s", 'get': lambda e: d(e, ['state'])},
    'hypervisor':
    {'title': 'hypervisor', 'len': 20, 'fmt': "%-20s", 'get': lambda e: d(e, ['hypervisor'])},
}

snapshot_fmt = {
    'uuid':
    {'title': 'UUID', 'len': 36, 'fmt': "%36s", 'get': lambda e: d(e, ['uuid'])},
    'timestamp':
    {'title': 'Timestamp', 'len': 20, 'fmt': "%-20s",
     'get': lambda e: datetime.fromtimestamp(d(e, ['timestamp'])/1000000).isoformat()},
    'comment':
    {'title': 'Comment', 'len': 30, 'fmt': "%-30s", 'get': lambda e: d(e, ['comment'])},

}

def vm_delete(args):
    args.endpoint.delete(args.uuid)

def vm_create(args):
    if args.file:
        f = open(args.file, 'r')
        config = json.loads(f.read())
        f.close()
    else:
        config = json.loads(sys.stdin.read())

    wiggle = args.endpoint._wiggle

    package = Package(wiggle).uuid_by_name(args.package)
    if not package:
        print "Could not find package: " + args.package + "."
        exit(1)

    dataset = Dataset(wiggle).uuid_by_name(args.dataset)
    if not dataset:
        print "Could not find dataset: " + args.dataset + "."
        exit(1)

    reply = args.endpoint.create(package, dataset, config)
    if reply:
        print "VM " + reply["uuid"] + " created successfully."
    else:
        print "Faied to create VM."

# Shows the data when list was selected.
def snapshots_list(args):
    l = args.endpoint.list_snapsots(args.vmuuid)
    if args.H:
        header(args)
        fmt = mk_fmt_str(args)
        for e in l:
            if not e:
                print("error!")
                exit(1)
            l = mk_fmt_line(args, e)
            if args.p:
                print(":".join(l))
            else:
                print(fmt%tuple(l))

def snapshot_get(args):
    e = args.endpoint.get_snapsot(args.vmuuid, args.snapuuid)
    if not e:
        print("error!")
        exit(1)
    if 'map_fn' in args:
        e = args.map_fn(e)
        print(json.dumps(e, sort_keys=True, indent=2, separators=(',', ': ')))

def snapshot_delete(args):
    e = args.endpoint.delete_snapsot(args.vmuuid, args.snapuuid)
    if not e:
        print("error!")
        exit(1)
        print "Snapshot deleted successfully."

def snapshot_rollback(args):
    e = args.endpoint.rollback_snapsot(args.vmuuid, args.snapuuid)
    if not e:
        print("error!")
        exit(1)
        print "Snapshot deleted successfully."

class VM(Entity):
    def __init__(self, wiggle):
        self._wiggle = wiggle
        self._resource = "vms"

    def name_of(self, obj):
        return d(obj, ["config", "alias"])

    def create(self, package, dataset, config):
        return self._post({"package": package,
                           "dataset": dataset,
                           "config": config})

    def start(self, uuid):
        return self._put(uuid, {"action": "start"})

    def stop(self, uuid):
        return self._put(uuid, {"action": "stop"})

    def reboot(self, uuid):
        return self._put(uuid, {"action": "reboot"})

    def force_stop(self, uuid):
        return self._put(uuid, {"action": "stop", "force": True})

    def force_reboot(self, uuid):
        return self._put(uuid, {"action": "reboot", "force": True})

    def list_snapsots(self, uuid):
        return self._wiggle.get_attr(self._resource, uuid, "snapshots")

    def make_snapsot(self, uuid, comment):
        return self._post_attr(uuid, "snapshots", {"comment": comment})

    def get_snapsot(self, uuid, snapid):
        return self._get_attr(uuid, "snapshots/" + snapid)

    def delete_snapsot(self, uuid, snapid):
        return self._delete_attr(uuid, "snapshots/" + snapid)

    def rollback_snapsot(self, uuid, snapid):
        return self._put_attr(uuid, "snapshots/" + snapid, {"action":"rollback"})

    def make_parser(self, subparsers):
        parser_vms = subparsers.add_parser('vms', help='vm related commands')
        parser_vms.set_defaults(endpoint=self)
        subparsers_vms = parser_vms.add_subparsers(help='vm commands')
        parser_vms_list = subparsers_vms.add_parser('list', help='lists a vm')
        parser_vms_list.add_argument("--fmt",
                                     action=ListAction, default=['uuid', 'hypervisor', 'alias', 'state'],
                                     help="Rows to show, valid options are: uuid, alias, ip, state, hypervisor")
        parser_vms_list.add_argument("-H", action='store_false',
                                     help="Supress the header.")
        parser_vms_list.add_argument("-p", action='store_true',
                                     help="show in parsable format, rows sepperated by colon.")
        parser_vms_list.set_defaults(func=show_list,
                                     fmt_def=vm_fmt)
        parser_vms_get = subparsers_vms.add_parser('get', help='gets a VM')
        parser_vms_get.add_argument("uuid",
                                    help="uuid of VM to show")
        parser_vms_get.set_defaults(func=show_get,
                                    map_fn=vm_map_fn)

        parser_vms_delete = subparsers_vms.add_parser('delete', help='deletes a VM')
        parser_vms_delete.add_argument("uuid",
                                       help="uuid of VM to show")
        parser_vms_delete.set_defaults(func=vm_delete)

        parser_vms_create = subparsers_vms.add_parser('create', help='creates a new VM')
        parser_vms_create.add_argument("--package", "-p",
                                       help="UUID of the package to use.")
        parser_vms_create.add_argument("--dataset", "-d",
                                       help="UUID of the dataset to use")
        parser_vms_create.add_argument("--file", "-f",
                                       help="Filename of config.json, not not present will be read from STDIN.")
        parser_vms_create.set_defaults(func=vm_create)

        parser_vms_get = subparsers_vms.add_parser('metadata', help='gets a vms metadata')
        parser_vms_get.add_argument("uuid",
                                    help="uuid of VM to show")
        parser_vms_get.set_defaults(func=show_get,
                                    map_fn=vm_metadata_map_fn)
        parser_vms_info = subparsers_vms.add_parser('info', help='gets a vm info')
        parser_vms_info.add_argument("uuid",
                                     help="uuid of VM to show")
        parser_vms_info.set_defaults(func=show_get,
                                     map_fn=vm_info_map_fn)
        parser_vms_start = subparsers_vms.add_parser('start', help='starts a vm')
        parser_vms_start.add_argument("uuid",
                                      help="uuid of VM to start")
        parser_vms_start.set_defaults(func=vm_action,
                                      action='start')
        parser_vms_stop = subparsers_vms.add_parser('stop', help='stops a vm')
        parser_vms_stop.add_argument("uuid",
                                     help="uuid of VM to stop")
        parser_vms_stop.add_argument("-f", action='store_true')
        parser_vms_stop.set_defaults(func=vm_action,
                                     action='stop')
        parser_vms_reboot = subparsers_vms.add_parser('reboot', help='reboot a vm')
        parser_vms_reboot.add_argument("uuid",
                                       help="uuid of VM to reboot")
        parser_vms_reboot.add_argument("-f", action='store_true')
        parser_vms_reboot.set_defaults(func=vm_action,
                                       action='reboot')
        parser_snapshots = subparsers_vms.add_parser('snapshots', help='snapshot related commands')
        parser_snapshots.add_argument("vmuuid",
                                      help="UUID of the VM to work with.")
        subparsers_snapshots = parser_snapshots.add_subparsers(help='snapshot commands')
        parser_snapshots_list = subparsers_snapshots.add_parser('list', help='lists snapshots')
        parser_snapshots_list.add_argument("--fmt", action=ListAction,
                                           default=['uuid', 'timestamp', 'comment'],
                                           help="Fields to show in the list, valid chances are: uuid, timestamp, comment")
        parser_snapshots_list.add_argument("-H", action='store_false',
                                           help="Supress the header.")
        parser_snapshots_list.add_argument("-p", action='store_true',
                                           help="show in parsable format, rows sepperated by colon.")
        parser_snapshots_list.set_defaults(func=snapshots_list,
                                           fmt_def=snapshot_fmt)
        parser_snapshots_get = subparsers_snapshots.add_parser('get', help='gets snapshots')
        parser_snapshots_get.add_argument("snapuuid",
                                          help="UUID if the snapshot")
        parser_snapshots_get.set_defaults(func=snapshot_get)
        parser_snapshots_delete = subparsers_snapshots.add_parser('delete', help='deletes snapshots')
        parser_snapshots_delete.add_argument("snapuuid",
                                             help="UUID if the snapshot")
        parser_snapshots_delete.set_defaults(func=snapshot_delete)
        parser_snapshots_rollback = subparsers_snapshots.add_parser('rollback', help='rolls back a snapshot')
        parser_snapshots_rollback.add_argument("snapuuid",
                                               help="UUID if the snapshot")
        parser_snapshots_rollback.set_defaults(func=snapshot_rollback)
        parser_snapshots_create = subparsers_snapshots.add_parser('create', help='gets snapshots')
        parser_snapshots_create.add_argument("comment",
                                             help="Comment for the snapshot.")
        parser_snapshots_create.set_defaults(func=snapshot_create)
