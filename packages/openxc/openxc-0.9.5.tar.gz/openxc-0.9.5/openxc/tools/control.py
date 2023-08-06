"""
This module contains the methods for the ``openxc-control`` command line
program.

`main` is executed when ``openxc-control`` is run, and all other callables in
this module are internal only.
"""
from __future__ import absolute_import

import argparse
import sys
import time

from openxc.formats.json import JsonFormatter
from .common import device_options, configure_logging, select_device


def version(controller):
    print("Device is running version %s" % controller.version())


def reset(controller):
    print("Resetting device...")
    controller.reset()
    version(controller)


def write_file(controller, filename, raw=False):
    first_timestamp = None
    with open(filename, "r") as output_file:
        corrupt_entries = 0
        message_count = 0
        start_time = time.time()
        for line in output_file:
            try:
                parsed_message = JsonFormatter.deserialize(line.encode("utf-8"))
                if not isinstance(parsed_message, dict):
                    raise ValueError()
            except ValueError:
                corrupt_entries += 1
            else:
                # TODO at the moment it's taking longer to write all of
                # individual CAN messages than the time that actually
                # elapsed in receiving the trace - need to implement
                # batching to speed this up. right now this will never sleep
                # because it's always behind.
                timestamp = parsed_message.get('timestamp', None)
                # TODO this duplicates some code from sources/trace.py
                if timestamp is not None:
                    first_timestamp = first_timestamp or timestamp
                    target_time = start_time + (timestamp - first_timestamp)
                    time.sleep(max(.0002, target_time - time.time()))

                message_count += 1
                controller.write(raw=raw, **parsed_message)
        print("%d lines sent" % message_count)
        if corrupt_entries > 0:
            print("%d invalid lines in the data file were not sent" %
                    corrupt_entries)


def write(controller, name, value, event=None, raw=False):
    print("Sending command %s: %s %s" % (name, value, event))
    if raw:
        method = controller.write_raw
    else:
        method = controller.write
    method(name=name, value=value, event=event, raw=raw)
    print("Done.")


def parse_options():
    parser = argparse.ArgumentParser(description="Send control messages to an "
            "attached OpenXC CAN translator", parents=[device_options()])
    parser.add_argument("command", type=str,
            choices=['version', 'reset', 'write', 'writeraw'])
    write_group = parser.add_mutually_exclusive_group()
    write_group.add_argument("--name", action="store", dest="write_name",
            help="name for message write request")
    write_group.add_argument("--id", action="store", dest="write_id",
            help="ID for raw message write request")
    parser.add_argument("--value", action="store", dest="write_value",
            help="optional value for message write request")
    parser.add_argument("--event", action="store", dest="write_event",
            help="optional event for message write request")
    parser.add_argument("--data", action="store", dest="write_data",
            help="data for raw message write request")
    write_group.add_argument("-f", "--file", action="store",
            dest="write_input_file",
            help="path to a file with a list of message requests")

    return parser.parse_args()


def main():
    configure_logging()
    arguments = parse_options()

    controller_class, controller_kwargs = select_device(arguments)
    controller = controller_class(**controller_kwargs)

    if arguments.command == "version":
        version(controller)
    elif arguments.command == "reset":
        reset(controller)
    elif arguments.command.startswith("write"):
        name = value = None
        if arguments.command == "write":
            raw = False
            if arguments.write_name:
                name = arguments.write_name
                value = arguments.write_value
                event = arguments.write_event
        elif arguments.command == "writeraw":
            raw = True
            if arguments.write_id:
                if not arguments.write_data:
                    sys.exit("%s requires an id and data" % arguments.command)
                name = arguments.write_id
                value = arguments.write_data
                event = None

        if name:
            write(controller, name, value, event, raw)
        elif arguments.write_input_file:
            write_file(controller, arguments.write_input_file, raw=raw)
        else:
            sys.exit("%s requires a name or filename" % arguments.command)
    else:
        print("Unrecognized command \"%s\"" % arguments.command)
