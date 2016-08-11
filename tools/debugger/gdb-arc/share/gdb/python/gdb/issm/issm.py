#
# Copyright (C) 2016 Free Software Foundation, Inc.
#
# Contributed by Intel Corporation, <jessica.gomez.hernandez@intel.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#

import json

import gdb

descriptor = None
jp_data = None

ISSM_START = "ISSM_START"
ISSM_END = "ISSM_END"


def is_container(gdb_value):
    type_code = gdb_value.type.code
    return type_code in(gdb.TYPE_CODE_STRUCT, gdb.TYPE_CODE_UNION)


def is_pointer(gdb_value):
    return gdb_value.type.code == gdb.TYPE_CODE_PTR


def is_pointer_init(gdb_value):
    return gdb_value.address != 0


def follow_link_list(linked_list, follow_key, print_keys, fill_list):
    """
    Utility function that walks through a linked list and collect specific fields of the data structures

    :param linked_list: Object of gdb.Value represening a structure
    :param follow_key: Name of the field that points to the next element in the linked list
    :param print_keys: List of strings of the fields that want to be collected
    :param fill_list: List to fill with the found elements and its fields
    :return:void
    """

    if is_pointer_init(linked_list):

        addr = str(linked_list.address).split()[0]
        name = str(linked_list.address).split()[-1]
        element_dict = {'Addr': addr, 'Name': name}

        link_list_iterator = linked_list
        lastkey = ""
        for key in print_keys:
            subkeys = key.split(".")
            highest_index = len(subkeys) -1
            for i, lastkey in enumerate(subkeys):
                if i < highest_index:
                    link_list_iterator = link_list_iterator[lastkey]
            else:
                # Avoid conflicts with JSON parsers
                element_dict[key] = str(link_list_iterator[lastkey]).replace("\"", "\'")
                link_list_iterator = linked_list

        fill_list.append(element_dict)
        gdb_value = linked_list[follow_key]

        try:
            new_gdb_value = gdb_value.dereference()
            new_gdb_value.fetch_lazy()
            # Avoid self recursive pointers
            if linked_list.address != new_gdb_value.address:
                follow_link_list(new_gdb_value, follow_key, print_keys, fill_list)
        except gdb.error:
            print "Error: Exception"


def json_printer(json_list):
    """
    Prints the JSON information in a table-type human readable way

    :param json_list: JSON list to print
    :return: void
    """

    for json_element in json_list:
        if isinstance(json_element, dict):
            for value in json_element.itervalues():
                print value + "\t",
            else:
                print ""


class ListWalkCmd(gdb.Command):
    """
    Command that walks through a linked list and collect specific fields of the data structures

    Arguments:
        [0] : Name of the linked list
        [1] : Name of the field that points to the next element in the linked list
        [*] : Name to the fields that want to be supervised

    Usage example:
        print-plist *_trace_list_nano_timer __next user_data timeout_data.delta_ticks_from_prev
    """

    def __init__(self):
        super(ListWalkCmd, self).__init__(
            "print-plist", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if not args:
            print "Error: Missing arguments"
            print help(self)
            return

        expr = args[0]
        follow_key = args[1]
        print_keys = args[2::]

        # initialize list of elements in linked list
        elements_container = []
        gdb_value_llist = gdb.parse_and_eval(expr)

        # walk linked list
        if is_pointer_init(gdb_value_llist):
            follow_link_list(gdb_value_llist, follow_key, print_keys, elements_container)

            if from_tty:
                print elements_container
            else:
                print ISSM_START + json.dumps(elements_container) + ISSM_END

        else:
            error = "Error: No initialized pointer"
            if from_tty:
                print error
            else:
                print ISSM_START + json.dumps([error]) + ISSM_END


# Create instance of created commands
ListWalkCmd()
