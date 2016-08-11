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
import os.path

import gdb

import issm


class GetLayout(gdb.Command):
    """
    Return JSON information about the selected model
    """

    def __init__(self):
        super(GetLayout, self).__init__(
            "issm_get_layout", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if args:
            print "Error: No argument expected"
            return
        else:
            if issm.jp_data is not None:
                print issm.ISSM_START + json.dumps(issm.jp_data) + issm.ISSM_END
            else:
                print "Error: No layout set"



class SetLayout(gdb.Command):
    """
    Select model, specifying JSON file descriptor
    """

    def __init__(self):
        super(SetLayout, self).__init__(
            "issm_set_layout", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if not args:
            print "Error: Missing arguments"
            return
        else:
            model_layout = args[0]

            # if full path provided
            if os.path.isfile(model_layout):
                return self.load_model(model_layout)

            # if only model name is provided
            model_path = os.path.join(gdb.PYTHONDIR, 'gdb', 'issm', 'models', model_layout + '.json')
            if os.path.isfile(model_path):
               return self.load_model(model_path)

            # if no model found
            print "Error: Invalid provided layout model"


    def load_model(self, model):
        issm.descriptor = model
        with open(issm.descriptor) as d:
            row_data = d.read()
            issm.jp_data = json.loads(row_data)

# Create instance of created commands
SetLayout()
GetLayout()
