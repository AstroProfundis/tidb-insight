# -*- coding: utf-8 -*-
# Trace direct reclaim latency.

import os
import logging

from utils import util
from utils import fileopt


class DirectReclaimTracer():
    # options about tracer
    ftrace_options = {}

    # output dir
    data_dir = "mem"

    # tracefs mount point
    tracefs = "/sys/kernel/debug/tracing"
    direct_reclaim_begin = "events/vmscan/mm_vmscan_direct_reclaim_begin/enable"
    direct_reclaim_end = "events/vmscan/mm_vmscan_direct_reclaim_end/enable"

    def __init__(self, options={}):
        self.ftrace_options = options

    def save_trace(self, cwd, outputdir=None):
        _, stderr = util.run_cmd(["cd", self.tracefs])
        if stderr:
            logging.fatal("""ERROR: accessing tracing. Root user? Kernel has FTRACE?
            debugfs mounted? (mount -t debugfs debugfs /sys/kernel/debug)""")
            return

        if not outputdir:
            logging.fatal("ERROR: please give a dir to save trace data")
            return

        dr_outputdir = ileopt.build_full_output_dir(
            basedir=outputdir, subdir=self.data_dir)

        if not dr_outputdir:
            return

        util.chdir(self.tracefs)

        # setup trace, set opt
        _, stderr = util.run_cmd(["echo nop > current_tracer"], shell=True)
        if stderr:
            logging.fatal("ERROR: reset current_tracer failed")
            os.chdir(cwd)
            return

        bufsize_kb = self.ftrace_options["bufsize"] if "bufsize" in \
            self.ftrace_options and self.ftrace_options["bufsize"] else "4096"
        _, stderr = util.run_cmd(
            ["echo %s > buffer_size_kb" % bufsize_kb], shell=True)
        if stderr:
            logging.fatal("ERROR: set bufsize_kb failed")
            os.chdir(cwd)
            return

        # begin tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo 1 > %s" % event], shell=True)
            if stderr:
                logging.fatal("ERROR: enable %s tracepoint failed" % event)
                os.chdir(cwd)
                return

        # collect trace
        time = self.ftrace_options["time"] if "time" in \
            self.ftrace_options and self.ftrace_options["time"] else 60
        util.run_cmd_for_a_while(
            ["cat trace_pipe > %s/drtrace" % dr_outputdir], time, shell=True)

        # End tracing
        for event in [self.direct_reclaim_begin, self.direct_reclaim_end]:
            _, stderr = util.run_cmd(["echo 0 > %s" % event], shell=True)
            if stderr:
                logging.fatal("ERROR: disable %s tracepoint failed" % event)
                os.chdir(cwd)
                return

        os.chdir(cwd)
