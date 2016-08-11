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

import os.path
import ast, json, pprint

import gdb

import issm


class PrintDataJson(gdb.Command):
    """
      Executes the command found in the json layout
      Sends the gdb query with enabled "from_tty" argument
      Inferior commands should use this argument to return data in JSON format

      Arguments:
          [0] : Name of the tab

      Usage example:
        issm_pData Threads
    """

    def __init__(self):
        super(PrintDataJson, self).__init__(
            "issm_pData", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if not args:
            print "Error: Missing arguments"
            print help(self)
            return

        # check for valid layout data
        if issm.jp_data is not None:
            tab_name = args[0]
            tabs = issm.jp_data['Tabs']
            for tab in tabs:
                if tab['name'] == tab_name:
                    if 'command' in tab:
                        json_string = gdb.execute(tab['command'], False, True)
                        print json_string
                        return
                    else:
                        print "Error: No 'command' tag found for tab '" + tab_name + "'"
                        return
            else:
                print "Error: Tab not found"
        else:
            print "Error: Invalid layout file"

class PrintDataTable(gdb.Command):
    """
      Executes the command found in the json layout
      Sends the gdb query with disabled "from_tty" argument
      Prints the JSON information in a table-type human readable way

      Arguments:
          [0] : Name of the tab

      Usage example:
        issm_pData Threads
    """

    def __init__(self):
        super(PrintDataTable, self).__init__(
            "issm_data", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if not args:
            print "Error: Missing arguments"
            return
        else:

            if issm.jp_data is not None:
                tab_name = args[0]
                tabs = issm.jp_data['Tabs']
                for tab in tabs:
                    if tab['name'] == tab_name:
                        if 'command' in tab:
                            json_string = gdb.execute(tab['command'], True, True)
                            # TODO: get nice way to display data to user in CMD
                            json_list = ast.literal_eval(json_string)
                            issm.json_printer(json_list)
                            # print json.dumps(json_list, sort_keys=False, indent=4, separators=(',',': '))
                            return
                        else:
                            print "Error: No 'command' tag found for tab '" + tab_name + "'"
                            return
                else:
                    print "Error: Tab not found"
            else:
                print "Error: Invalid layout file"

# Create instance of created commands
PrintDataTable()
PrintDataJson()
