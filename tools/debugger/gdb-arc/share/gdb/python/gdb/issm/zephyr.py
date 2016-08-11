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

import issm


TAB_NAME = "Name"
TAB_ADDR = "Addr"
T_CURRENT = " [CURRENT]"

# TCS THREADS DEFINES
TCS_INT_ACTIVE  = 0x002; TCS_INT_ACTIVEs = "INTERRUPT_HANDLER"   # 1 = executing context is interrupt handler
TCS_EXC_ACTIVE  = 0x004; TCS_EXC_ACTIVEs = "EXCEPTION_HANDLER"   # 1 = executing context is exception handler
TCS_ESSENTIAL   = 0x200; TCS_ESSENTIALs  = "ESSENTIAL_"          # 1 = system thread that must not abor

TAB_FLAGS   = "flags"
TAB_PRIO    = "prio"
TAB_CONTEXT = "context"
TAB_TASK    = "TASK"
TAB_FIBER   = "FIBER"


# TASKS DEFINES
TF_BREAK_MASK = 0xFFF
TF_STOP = 0x00000001; TF_STOPs = "NoStarted "  # Not started
TF_TERM = 0x00000002; TF_TERMs = "Terminated " # Terminated
TF_SUSP = 0x00000004; TF_SUSPs = "Suspended "  # Suspended
TF_BLCK = 0x00000008; TF_BLCKs = "Blocked "    # Blocked
TF_GDBS = 0x00000010; TF_GDBSs = "GDBstop "    # Stopped by GDB agent
TF_PRIO = 0x00000020; TF_PRIOs = "PrioChange " # Task priority is changing
TF_TIME = 0x00000800; TF_TIMEs = "Sleeping "   # Sleeping

TF_WAIT_MASK = 0x0FFFF000
TF_DRIV = 0x00001000; TF_DRIVs = "DRIVER "     # Waiting for arch specific driver
TF_RES0 = 0x00002000; TF_RES0s = "RESV0 "      # Reserved0
TF_EVNT = 0x00004000; TF_EVNTs = "EVENT "      # Waiting for an event
TF_ENQU = 0x00008000; TF_ENQUs = "PUT_FIFO "   # Waiting to put data on a FIFO
TF_DEQU = 0x00010000; TF_DEQUs = "GET_FIFO "   # Waiting to get data from a FIFO
TF_SEND = 0x00020000; TF_SENDs = "SEND_MB_P "  # Waiting to send via mailbox or pipe
TF_RECV = 0x00040000; TF_RECVs = "RECV_MB_P "  # Waiting to recv via mailbox or pipe
TF_SEMA = 0x00080000; TF_SEMAs = "SEMA "       # Waiting for a semaphore
TF_LIST = 0x00100000; TF_LISTs = "SEMA_GROUP " # Waiting for a group of semaphores
TF_LOCK = 0x00200000; TF_LOCKs = "MUTEX "      # Waiting for a mutex
TF_ALLO = 0x00400000; TF_ALLOs = "MEM_MAP "    # Waiting on a memory mapping
TF_GTBL = 0x00800000; TF_GTBLs = "MEM_POOL "   # Waiting on a memory pool
TF_RES1 = 0x01000000; TF_RES1s  = "RESV1 "     # Reserved1
TF_RES2 = 0x02000000; TF_RES2s = "RESV2 "      # Reserved2
TF_RECVDATA = 0x04000000; TF_RECVDATAs = "RECV_DATA " # Waiting to receive data
TF_SENDDATA = 0x08000000; TF_SENDDATAs = "SEND_DATA " # Waiting to send data

TAB_STATE  = "state"
TAB_BREAKF = "BreakF"
TAB_WAITF  = "WaitF"

class ZephyrTCS(gdb.Command):
    """
    Prints a list of the kernel thread contexts, walking a list of TCSs.
    Uses the flags and the defines in nano_private.h to represent thread context type.

    Arguments:
         [0] : Structure pointing to current thread
         [1] : Linked list that keeps track of threads
         [2] : Name of the field that points to the next element in the linked list
         [*] : Name to the fields that want to be supervised

    Usage example:
        z_tcs *_nanokernel.current *_nanokernel.threads next_thread prio flags coopReg preempReg
    """

    def __init__(self):
        super(ZephyrTCS, self).__init__(
            "z_tcs", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if len(args) < 3:
            print "Error: Missing arguments"
            print help(self)
            return

        current = gdb.parse_and_eval(args[0])
        current_addr = str(current.address).split()[0]

        expr = args[1]
        follow_key = args[2]
        print_keys = args[3::]

        # initialize list of threads
        thread_list = []
        gdb_value_thread_list = gdb.parse_and_eval(expr)

        # walk linked list
        if issm.is_pointer_init(gdb_value_thread_list):
            issm.follow_link_list(gdb_value_thread_list, follow_key, print_keys, thread_list)

            for thread in thread_list:
                if TAB_PRIO in thread and TAB_ADDR in thread:
                    if thread[TAB_PRIO] == "-1":
                        thread[TAB_CONTEXT] = TAB_TASK
                    else:
                        thread[TAB_CONTEXT] = TAB_FIBER

                    if thread[TAB_ADDR] == current_addr:
                        thread[TAB_CONTEXT] += T_CURRENT

                if "coopReg.esp" in thread:
                    thread["coopReg.esp"] = hex(int(thread["coopReg.esp"]))

                if TAB_FLAGS in thread:
                    tcs_flags = int(thread[TAB_FLAGS])
                    thread[TAB_FLAGS] = hex(tcs_flags)

                    if tcs_flags & TCS_EXC_ACTIVE:
                        thread[TAB_CONTEXT] = TCS_EXC_ACTIVEs
                    if tcs_flags & TCS_INT_ACTIVE:
                        thread[TAB_CONTEXT] = TCS_INT_ACTIVEs
                    if tcs_flags & TCS_ESSENTIAL:
                        thread[TAB_CONTEXT] = TCS_ESSENTIALs + thread[TAB_CONTEXT]

            if from_tty:
                print thread_list
            else:
                print issm.ISSM_START + json.dumps(thread_list) + issm.ISSM_END

        else:
            error = "Error: No initialized pointer"
            if from_tty:
                print error
            else:
                print issm.ISSM_START + json.dumps([error]) + issm.ISSM_END


class ZephyrTask(gdb.Command):
    """
    Prints a list of the kernel tasks contexts, walking a list of K_TASKs
    Uses the flags and the defines in micro_private.h to represent tasks state.

    Arguments:
         [0] : Structure pointing to current task
         [1] : Linked list that keeps track of the tasks
         [2] : Name of the field that points to the next element in the linked list
         [*] : Name to the fields that want to be supervised

    Usage example:
        z_task *_k_current_task *_trace_list_micro_task __next id priority group workspace state
    """

    def __init__(self):
        super(ZephyrTask, self).__init__(
            "z_task", gdb.COMMAND_DATA, gdb.COMPLETE_SYMBOL)

    def invoke(self, argument, from_tty):
        # parse arguments
        args = gdb.string_to_argv(argument)
        if len(args) < 3:
            print "Error: Missing arguments"
            print help(self)
            return

        current = gdb.parse_and_eval(args[0])
        current_addr = str(current.address).split()[0]

        expr = args[1]
        follow_key = args[2]
        print_keys = args[3::]

        # initialize list of tasks
        task_list = []
        gdb_value_task_list = gdb.parse_and_eval(expr)

        # walk linked list
        if issm.is_pointer_init(gdb_value_task_list):
            issm.follow_link_list(gdb_value_task_list, follow_key, print_keys, task_list)

            for task in task_list:
                if TAB_NAME in task and TAB_ADDR in task:
                    if task[TAB_ADDR] == current_addr:
                        task[TAB_NAME] += T_CURRENT

                if TAB_STATE in task:
                    state_flags = int(task[TAB_STATE])
                    task[TAB_STATE] = hex(state_flags)

                    break_flags = state_flags & TF_BREAK_MASK
                    break_string = ""
                    if not break_flags:
                        break_string += hex(break_flags)
                    else:
                        if break_flags & TF_STOP:
                            break_string += TF_STOPs
                        if break_flags & TF_TERM:
                            break_string += TF_TERMs
                        if break_flags & TF_SUSP:
                            break_string += TF_SUSPs
                        if break_flags & TF_BLCK:
                            break_string += TF_BLCKs
                        if break_flags & TF_GDBS:
                            break_string += TF_GDBSs
                        if break_flags & TF_PRIO:
                            break_string += TF_PRIOs
                        if break_flags & TF_TIME:
                            break_string += TF_TIMEs

                    wait_flags = state_flags & TF_WAIT_MASK
                    wait_string = ""
                    if not wait_flags:
                        wait_string += hex(wait_flags)
                    else:
                        if wait_flags & TF_DRIV:
                            wait_string += TF_DRIVs
                        if wait_flags & TF_RES0:
                            wait_string += TF_RES0s
                        if wait_flags & TF_EVNT:
                            wait_string += TF_EVNTs
                        if wait_flags & TF_ENQU:
                            wait_string += TF_ENQUs
                        if wait_flags & TF_DEQU:
                            wait_string += TF_DEQUs
                        if wait_flags & TF_SEND:
                            wait_string += TF_SENDs
                        if wait_flags & TF_RECV:
                            wait_string += TF_RECVs
                        if wait_flags & TF_SEMA:
                            wait_string += TF_SEMAs
                        if wait_flags & TF_LIST:
                            wait_string += TF_LISTs
                        if wait_flags & TF_LOCK:
                            wait_string += TF_LOCKs
                        if wait_flags & TF_ALLO:
                            wait_string += TF_ALLOs
                        if wait_flags & TF_GTBL:
                            wait_string += TF_GTBLs
                        if wait_flags & TF_RES1:
                            wait_string += TF_RES1s
                        if wait_flags & TF_RES2:
                            wait_string += TF_RES2s
                        if wait_flags & TF_RECVDATA:
                            wait_string += TF_RECVDATAs
                        if wait_flags & TF_SENDDATA:
                            wait_string += TF_SENDDATAs

                    task[TAB_BREAKF] = break_string
                    task[TAB_WAITF] = wait_string

            if from_tty:
                print task_list
            else:
                print issm.ISSM_START + json.dumps(task_list) + issm.ISSM_END

        else:
            error = "Error: No initialized pointer"
            if from_tty:
                print error
            else:
                print issm.ISSM_START + json.dumps([error]) + issm.ISSM_END

# Create instance of created commands
ZephyrTask()
ZephyrTCS()
