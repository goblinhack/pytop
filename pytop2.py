#!/usr/bin/env python
#
# yatop
#
# usage: yatop [-h] [-p PID] [-one] [-i IGNORE] [-d DELAY] [-a] [-c] [-H]
#
# optional arguments:
#   -h, --help            show this help message and exit
#   -p PID, --pid PID     filter to a given pid
#   -one, --one           one shot and then exit, like top -b
#   -i IGNORE, --ignore IGNORE
#                         filter idle processes after x seconds of inaction
#   -d DELAY, --delay DELAY
#                         delay between system sampes
#   -a, --all             include all processes, including idle ones
#   -c, --no-color        disable color output
#   -H, --no-histogram    disable histogram
#
# Python based top like tool with historical graphing for processes.
#
# Allows you to select individual processes and receive a histogram of the CPU usage for that process.
#
# Is a bit slow, but it's python based, so quite portable.
#
# Example output
# --------------
#
# CPU UsrTime   SysTime     Idle   IoWait     Ireq  SoftIrq
#   0    0.78%    0.00%   86.82%    0.00%    0.00%   12.40%
#   1    2.52%    0.00%   97.48%    0.00%    0.00%    0.00%
#   2   11.97%    4.27%   83.76%    0.00%    0.00%    0.00%
#   3    6.61%    0.83%   92.56%    0.00%    0.00%    0.00%
#   4  100.00%    0.00%    0.00%    0.00%    0.00%    0.00%
#   5    3.39%    0.00%   96.61%    0.00%    0.00%    0.00%
#   6    9.91%    1.80%   88.29%    0.00%    0.00%    0.00%
#   7    5.13%    0.85%   94.02%    0.00%    0.00%    0.00%
#   8    3.42%    0.85%   95.73%    0.00%    0.00%    0.00%
# PID  State     Process name       CPU     USER%  SYSTEM%      Cpu%   CpuMin%   CpuMax%  IOWait%   IoMin%   IoMax% CPUs
# 913      S /usr/bin/kvm -smbios   11    204.24%    0.00%   204.24%   195.97%   226.17%    4.82%    2.60%    4.84% CPU 5->6
# 58       S (ksoftirqd/10)         10      0.00%    0.00%     0.00%     0.00%     0.89%    0.00%    0.00%    0.00%
# 78       S (ksoftirqd/14)         14      0.00%    0.00%     0.00%     0.00%     0.86%    0.00%    0.00%    0.00%
# 118      S (ksoftirqd/22)         22      0.00%    0.00%     0.00%     0.00%     0.85%    0.00%    0.00%    0.00%
# 144      S (ksmd)                 2       0.00%    0.00%     0.00%     0.00%     2.56%    0.00%    0.00%    0.00% CPU 6->2
# 790      S rsyslogd -c5           10      0.00%    0.89%     0.89%     0.00%     0.90%    0.00%    0.00%    0.00%
# 3616     S bash -ls               5       0.00%    0.00%     0.00%     0.00%     0.88%    0.00%    0.00%    0.00% CPU 6->5
# 6888     S /usr/bin/ssh-agent     8       0.00%    0.00%     0.00%     0.00%     0.91%    0.00%    0.00%    0.00%
# 7154     S /usr/bin/kvm -smbios   3     134.19%   11.11%   145.30%   139.67%   160.87%    3.22%    1.62%    3.48% CPU 7->3
# \_ 7157  S (kvm)                  7       2.48%    0.83%     3.31%     0.00%     8.55%    0.16%    0.00%    0.24% tCPU 3->7
# \_ 7158  S (kvm)                  11      5.04%    0.00%     5.04%     0.82%    14.16%    0.24%    0.00%    0.28%
# vvv Maximum CPU seen for pid 913, 226.17%:
# 226.17 %__________________________________________#_____________________________________________________
# 225.01 %__________________________________________#_____________________________________________________
# 223.85 %__________________________________________#_____________________________________________________
# 222.68 %__________________________________________#_____________________________________________________
# 221.52 %__________________________________________#_____________________________________________________
# 220.36 %__________________________________________#_____________________________________________________
# 219.20 %__________________________________________#_____________________________________________________
# 218.04 %__________________________________________#_____________________________________________________
# 216.88 %__________________________________________#_____________________________________________________
# 215.71 %__________________________________________#_____________________________________________________
# 214.55 %__________________________________________#_____________________________________________________
# 213.39 %_________________#____________________#___#___________#_________________________________________
# 212.23 %_________________#_________________#__#___#___________#_________________________________________
# 211.07 %_________________#_________________#__#_#_#_________#_#____________________#____________________
# 209.91 %_________________#_________________#__#_#_#_#_______#_#_____________#______#____________________
# 208.74 %_#_______________#_____#___________#__#_#_#_#_______#_#______#______#______#__#_____#___________
# 207.58 %_#____#_______#_##_#___#___________#_##_#_#_#____#__###___#_##_____##______#__#_____#___________
# 206.42 %_##___#_______#_##_#___#__#___#____#_##_#_#_#____#__###___#_##_____##______#__#_____##__________
# 205.26 %_##___####____#_##_#__##_###__#_#__#_####_#_####_#_####___#_##_____####__#_#__#_____##__________
# 204.10 %###___####__#_####_#__######__#_#########_#_####_#######_#####__#######_####__#_____#####__#__##
# 202.94 %###___####__################__#_########################_######_############__#_##_######_##__##
# 201.78 %############################__#_########################_######_#############_#_##_######_###_##
# 200.61 %#############################################################################_#_#############_##
# 199.45 %#############################################################################_#_#############_##
# 198.29 %#############################################################################################_##
# 197.13 %#############################################################################################_##
#
# ```
import os
import argparse
import re
import time
import sys
import select
import tty
import termios

class Main(object):

    #
    # display the difference between two snapshots in time for a pids threads
    #
    def display_thread_delta(self, last_stats, curr_stats, pid):

        process_last_stats = last_stats.pstats[pid]
        process_curr_stats = curr_stats.pstats[pid]

        for t in process_last_stats.threads:

            t = int(t)

            #
            # Check for transient processes
            #
            if not process_last_stats.tstats.has_key(t):
                continue
            if not process_curr_stats.tstats.has_key(t):
                continue

            thread_last_stats = process_last_stats.tstats[t]
            thread_curr_stats = process_curr_stats.tstats[t]

            if thread_last_stats.pid == process_last_stats.pid:
                if len(process_last_stats.threads) == 1:
                    continue

            #
            # Get the cpu time delta
            #
            utime = thread_curr_stats.utime - thread_last_stats.utime
            stime = thread_curr_stats.stime - thread_last_stats.stime

            clock0 = thread_last_stats.utime + thread_last_stats.stime
            clock1 = thread_curr_stats.utime + thread_curr_stats.stime
            delta = clock1 - clock0

            last_stats_clock = last_stats.cpuinfo[thread_last_stats.cpu].clock
            curr_stats_clock = curr_stats.cpuinfo[thread_last_stats.cpu].clock
            total_clock = float(curr_stats_clock - last_stats_clock)

            utime = (((float(utime)) / total_clock) * 100.0)
            stime = (((float(stime)) / total_clock) * 100.0)
            cpu_pct = (((float(delta)) / total_clock) * 100.0)

            #
            # Calculate the min and max CPU ranges we see
            #
            if thread_last_stats.cpu_min_pct == None:
                thread_last_stats.cpu_min_pct = cpu_pct
            if thread_last_stats.cpu_max_pct == None:
                thread_last_stats.cpu_max_pct = cpu_pct

            min_cpu_pct = thread_last_stats.cpu_min_pct
            max_cpu_pct = thread_last_stats.cpu_max_pct

            if cpu_pct < min_cpu_pct:
                min_cpu_pct = cpu_pct
            if cpu_pct > max_cpu_pct:
                max_cpu_pct = cpu_pct

            thread_curr_stats.cpu_min_pct = min_cpu_pct
            thread_curr_stats.cpu_max_pct = max_cpu_pct
            thread_curr_stats.cpu_pct = cpu_pct

            #
            # Get the iowait time delta
            #
            clock0 = thread_last_stats.blkio_ticks
            clock1 = thread_curr_stats.blkio_ticks
            delta = clock1 - clock0

            if delta != 0:
                iowait_pct = (float(delta) / float(self.ticks * self.opts.delay))

                if (iowait_pct < 0) or (iowait_pct > 100):
                    #
                    # Ubuntu 14.04 reports junk sometimes
                    #
                    iowait_pct = 0
                    thread_curr_stats.iowait_min_pct = 0
                    thread_curr_stats.iowait_max_pct = 0
                else:
                    #
                    # Calculate the min and max blk ranges we see
                    #
                    if thread_last_stats.iowait_min_pct == None:
                        thread_last_stats.iowait_min_pct = iowait_pct
                    if thread_last_stats.iowait_max_pct == None:
                        thread_last_stats.iowait_max_pct = iowait_pct

                    min_iowait_pct = thread_last_stats.iowait_min_pct
                    max_iowait_pct = thread_last_stats.iowait_max_pct

                    if iowait_pct < min_iowait_pct:
                        min_iowait_pct = iowait_pct
                    if iowait_pct > max_iowait_pct:
                        max_iowait_pct = iowait_pct

                    thread_curr_stats.iowait_min_pct = min_iowait_pct
                    thread_curr_stats.iowait_max_pct = max_iowait_pct
            else:
                iowait_pct = 0
                thread_curr_stats.iowait_min_pct = 0
                thread_curr_stats.iowait_max_pct = 0

            #
            # Skip idle threads
            #
            if self.opts.pid == thread_last_stats.pid:
                process_curr_stats.did_something = True
            else:
                thread_curr_stats.did_something = thread_last_stats.did_something
                if not self.opts.all:
                    if (cpu_pct == 0) and (iowait_pct == 0):
                        thread_curr_stats.did_something = thread_curr_stats.did_something - 1
                        if thread_curr_stats.did_something <= 0:
                            thread_curr_stats.did_something = 0
                            continue
                    else:
                        #
                        # If did nothing for 10 seconds, ignore
                        #
                        thread_curr_stats.did_something = self.opts.ignore

            #
            # Print the overal stats for this thread
            #
            print("\\_ %-5s " % (thread_last_stats.pid)),
            curr_stats.pids_and_tids.append(thread_last_stats.pid)

            if not self.opts.no_color:
                if thread_last_stats.state == "D":
                    sys.stdout.write("%s%s%s " % (colors.fg.red, thread_last_stats.state, colors.reset))
                else:
                    sys.stdout.write("%s%s%s " % (colors.fg.green, thread_last_stats.state, colors.reset))
            else:
                sys.stdout.write("%s " % (thread_last_stats.state))

            if not self.opts.no_color:
                if self.opts.pid == int(thread_last_stats.pid):
                    print("%s%-22s%s %-3d " % (colors.bg.purple, thread_last_stats.name, colors.reset, thread_curr_stats.cpu)),
                    self.found_user_selected_process = True
                else:
                    print("%-22s %-3d " % (thread_last_stats.name, thread_curr_stats.cpu)),
            else:
                if self.opts.pid == int(thread_last_stats.pid):
                    print("%s%-22s%s %-3d " % (colors.reverse, thread_last_stats.name, colors.reset, thread_curr_stats.cpu)),
                    self.found_user_selected_process = True
                else:
                    print("%-22s %-3d " % (thread_last_stats.name, thread_curr_stats.cpu)),

            if not self.opts.no_color:
                if utime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, utime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, utime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (utime))

            if not self.opts.no_color:
                if stime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, stime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, stime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (stime))

            if not self.opts.no_color:
                if cpu_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, cpu_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, cpu_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (cpu_pct))

            if not self.opts.no_color:
                if thread_curr_stats.cpu_min_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, thread_curr_stats.cpu_min_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, thread_curr_stats.cpu_min_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (thread_curr_stats.cpu_min_pct))

            if not self.opts.no_color:
                if thread_curr_stats.cpu_max_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, thread_curr_stats.cpu_max_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, thread_curr_stats.cpu_max_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (thread_curr_stats.cpu_max_pct))

            if not self.opts.no_color:
                if iowait_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, iowait_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, iowait_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (iowait_pct))

            if not self.opts.no_color:
                if thread_curr_stats.iowait_min_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, thread_curr_stats.iowait_min_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, thread_curr_stats.iowait_min_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (thread_curr_stats.iowait_min_pct))

            if not self.opts.no_color:
                if thread_curr_stats.iowait_max_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, thread_curr_stats.iowait_max_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, thread_curr_stats.iowait_max_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (thread_curr_stats.iowait_max_pct))

            if thread_last_stats.cpu != thread_curr_stats.cpu:
                if not self.opts.no_color:
                    sys.stdout.write(" %s" % (colors.fg.red))
                else:
                    sys.stdout.write(" ")

                print("CPU %d->%d" % (thread_last_stats.cpu, thread_curr_stats.cpu))
                sys.stdout.write("%s" % (colors.reset))

                thread_last_stats.cpu_switch = True
                thread_curr_stats.cpu_switch = True
            else:
                if not self.opts.no_color:
                    sys.stdout.write(" %s" % (colors.fg.green))
                else:
                    sys.stdout.write(" ")
                print("CPU %d" % thread_curr_stats.cpu)
                sys.stdout.write("%s" % (colors.reset))

            self.how_many_printed_lines += 1
            if self.how_many_printed_lines >= self.lines:
                return

    #
    # display the difference between two snapshots in time of system stats
    #
    def display_process_delta(self, last_stats, curr_stats):

        if not self.opts.no_color:
            sys.stdout.write("%s%s" % (colors.bg.blue, colors.fg.white))
        else:
            sys.stdout.write("%s" % (colors.reverse))

        print("PID  State     Process name       CPU     USER%  SYSTEM%      Cpu%   CpuMin%   CpuMax%  IOWait%   IoMin%   IoMax% CPUs")
        sys.stdout.write("%s" % (colors.reset))

        self.found_user_selected_process = False

        for pid in last_stats.pids:
            pid = int(pid)

            #
            # Check for transient processes
            #
            if not last_stats.pstats.has_key(pid):
                continue
            if not curr_stats.pstats.has_key(pid):
                continue

            process_last_stats = last_stats.pstats[pid]
            process_curr_stats = curr_stats.pstats[pid]

            #
            # Filter to a process?
            #
            if not self.all_pids:
                if self.opts.pid != None:
                    if self.opts.pid != pid:
                        ok = False
                        for tid in process_last_stats.threads:
                            if self.opts.pid == int(tid):
                                ok = True
                        if ok == False:
                            continue

            #
            # Get the cpu time delta
            #
            utime = process_curr_stats.utime - process_last_stats.utime
            stime = process_curr_stats.stime - process_last_stats.stime

            clock0 = process_last_stats.utime + process_last_stats.stime
            clock1 = process_curr_stats.utime + process_curr_stats.stime
            delta = clock1 - clock0

            last_stats_clock = last_stats.cpuinfo[process_last_stats.cpu].clock
            curr_stats_clock = curr_stats.cpuinfo[process_last_stats.cpu].clock
            total_clock = float(curr_stats_clock - last_stats_clock)

            if total_clock != 0:
                utime = (((float(utime)) / total_clock) * 100.0)
                stime = (((float(stime)) / total_clock) * 100.0)
                cpu_pct = (((float(delta)) / total_clock) * 100.0)

                #
                # Calculate the min and max CPU ranges we see
                #
                if process_last_stats.cpu_min_pct == None:
                    process_last_stats.cpu_min_pct = cpu_pct
                if process_last_stats.cpu_max_pct == None:
                    process_last_stats.cpu_max_pct = cpu_pct

                min_cpu_pct = process_last_stats.cpu_min_pct
                max_cpu_pct = process_last_stats.cpu_max_pct

                if cpu_pct < min_cpu_pct:
                    min_cpu_pct = cpu_pct
                if cpu_pct > max_cpu_pct:
                    max_cpu_pct = cpu_pct

                process_curr_stats.cpu_min_pct = min_cpu_pct
                process_curr_stats.cpu_max_pct = max_cpu_pct
            else:
                utime = 0
                stime = 0
                cpu_pct = 0
                process_curr_stats.cpu_min_pct = 0
                process_curr_stats.cpu_max_pct = 0

            process_curr_stats.cpu_pct = cpu_pct

            #
            # Get the iowait time delta
            #
            clock0 = process_last_stats.blkio_ticks
            clock1 = process_curr_stats.blkio_ticks
            delta = clock1 - clock0

            if delta != 0:
                iowait_pct = (float(delta) / float(self.ticks * self.opts.delay))

                if (iowait_pct < 0) or (iowait_pct > 100):
                    #
                    # Ubuntu 14.04 reports junk sometimes
                    #
                    iowait_pct = 0
                    process_curr_stats.iowait_min_pct = 0
                    process_curr_stats.iowait_max_pct = 0
                else:
                    #
                    # For iowait, what are the ranges?
                    #
                    if process_last_stats.iowait_min_pct == None:
                        process_last_stats.iowait_min_pct = iowait_pct
                    if process_last_stats.iowait_max_pct == None:
                        process_last_stats.iowait_max_pct = iowait_pct

                    min_iowait_pct = process_last_stats.iowait_min_pct
                    max_iowait_pct = process_last_stats.iowait_max_pct

                    if iowait_pct < min_iowait_pct:
                        min_iowait_pct = iowait_pct
                    if iowait_pct > max_iowait_pct:
                        max_iowait_pct = iowait_pct

                    process_curr_stats.iowait_min_pct = min_iowait_pct
                    process_curr_stats.iowait_max_pct = max_iowait_pct
            else:
                iowait_pct = 0
                process_curr_stats.iowait_min_pct = 0
                process_curr_stats.iowait_max_pct = 0

            #
            # Skip idle processes
            #
            if self.opts.pid == pid:
                process_curr_stats.did_something = True
            else:
                process_curr_stats.did_something = process_last_stats.did_something
                if not self.opts.all:
                    if (cpu_pct == 0) and (iowait_pct == 0):
                        process_curr_stats.did_something = process_curr_stats.did_something - 1
                        if process_curr_stats.did_something <= 0:
                            process_curr_stats.did_something = 0
                            continue
                    else:
                        # If did nothing for 10 seconds, ignore
                        process_curr_stats.did_something = self.opts.ignore

            #
            # Print the overal stats for this process
            #
            if not self.opts.no_color:
                sys.stdout.write("%s" % (colors.fg.blue))

            print("%-5s    " % (process_last_stats.pid)),
            curr_stats.pids_and_tids.append(process_last_stats.pid)

            #
            # If showing all pids then highlight the first pid to start with
            #
            if self.all_pids:
                if self.opts.pid == None:
                    self.opts.pid = pid

            if not self.opts.no_color:
                if process_last_stats.state == "D":
                    sys.stdout.write("%s%s%s " % (colors.fg.red, process_last_stats.state, colors.reset))
                else:
                    sys.stdout.write("%s%s%s " % (colors.fg.green, process_last_stats.state, colors.reset))
            else:
                sys.stdout.write("%s " % (process_last_stats.state))

            name = last_stats.get_process_name(process_last_stats.pid)
            if name == None or name == "":
                name = process_last_stats.name
                if name == None or name == "":
                    continue

            name = name[:21]

            if not self.opts.no_color:
                if self.opts.pid == pid:
                    sys.stdout.write("%s%-22s%s %-3d " % (colors.bg.purple, name, colors.reset, process_curr_stats.cpu))
                    self.found_user_selected_process = True
                else:
                    print("%-22s %-3d " % (name, process_curr_stats.cpu)),
            else:
                if self.opts.pid == pid:
                    sys.stdout.write("%s%-22s%s %-3d " % (colors.reverse, name, colors.reset, process_curr_stats.cpu))
                    self.found_user_selected_process = True
                else:
                    print("%-22s %-3d " % (name, process_curr_stats.cpu)),

            if not self.opts.no_color:
                if utime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, utime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, utime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (utime))

            if not self.opts.no_color:
                if stime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, stime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, stime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (stime))

            if not self.opts.no_color:
                if cpu_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, cpu_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, cpu_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (cpu_pct))

            if not self.opts.no_color:
                if process_curr_stats.cpu_min_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, process_curr_stats.cpu_min_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, process_curr_stats.cpu_min_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (process_curr_stats.cpu_min_pct))

            if not self.opts.no_color:
                if process_curr_stats.cpu_max_pct > 90:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.red, process_curr_stats.cpu_max_pct, colors.reset))
                else:
                    sys.stdout.write("%s%9.02f%%%s" % (colors.fg.green, process_curr_stats.cpu_max_pct, colors.reset))
            else:
                sys.stdout.write("%9.02f%%" % (process_curr_stats.cpu_max_pct))

            if not self.opts.no_color:
                if iowait_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, iowait_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, iowait_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (iowait_pct))

            if not self.opts.no_color:
                if process_curr_stats.iowait_min_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, process_curr_stats.iowait_min_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, process_curr_stats.iowait_min_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (process_curr_stats.iowait_min_pct))

            if not self.opts.no_color:
                if process_curr_stats.iowait_max_pct > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, process_curr_stats.iowait_max_pct, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, process_curr_stats.iowait_max_pct, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (process_curr_stats.iowait_max_pct))

            if process_last_stats.cpu != process_curr_stats.cpu:
                if not self.opts.no_color:
                    sys.stdout.write(" %s" % (colors.fg.red))
                else:
                    sys.stdout.write(" ")

                print("CPU %d->%d " % (process_last_stats.cpu, process_curr_stats.cpu))
                sys.stdout.write("%s" % (colors.reset))

                process_last_stats.cpu_switch = True
                process_curr_stats.cpu_switch = True
            else:
                if not self.opts.no_color:
                    sys.stdout.write(" %s" % (colors.fg.green))
                else:
                    sys.stdout.write(" ")

                print("CPU %d" % process_curr_stats.cpu)
                sys.stdout.write("%s" % (colors.reset))

            if not self.opts.no_color:
                sys.stdout.write("%s" % (colors.reset))

            self.how_many_printed_lines += 1
            if self.how_many_printed_lines >= self.lines:
                return

            self.display_thread_delta(last_stats, curr_stats, pid)

        #
        # If we did not print a pid, get a new focus
        #
        if not self.found_user_selected_process:
            if self.all_pids:
                self.opts.pid = None

    #
    # display the difference between two snapshots in time of system stats
    #
    def display_cpu_delta(self, last_stats, curr_stats):

        self.how_many_printed_lines = 0

        if not self.opts.no_color:
            sys.stdout.write("%s%s" % (colors.bg.blue, colors.fg.white))
        else:
            sys.stdout.write("%s" % (colors.reverse))

        print("CPU UsrTime   SysTime     Idle   IoWait     Ireq  SoftIrq")

        sys.stdout.write("%s" % (colors.reset))

        self.how_many_printed_lines += 1
        if self.how_many_printed_lines >= self.lines:
            return

        for cpu in range(0, last_stats.cpus):

            c0 = last_stats.cpuinfo[cpu]
            c1 = curr_stats.cpuinfo[cpu]

            #
            # How must CPU time has been used?
            #
            total_clock = float(c1.clock - c0.clock)

            utime = ((float(c1.utime - c0.utime)) / total_clock) * 100.0
            stime = ((float(c1.stime - c0.stime)) / total_clock) * 100.0
            idle = ((float(c1.idle - c0.idle)) / total_clock) * 100.0
            iowait = ((float(c1.iowait - c0.iowait)) / total_clock) * 100.0
            ireq = ((float(c1.ireq - c0.ireq)) / total_clock) * 100.0
            softirq = ((float(c1.softirq - c0.softirq)) / total_clock) * 100.0

            #
            # Filter idle CPUs
            #
            c1.did_something = c0.did_something
            if not self.opts.all:
                if (total_clock == 0):
                    c1.did_something = c1.did_something - 1
                    if c1.did_something <= 0:
                        c1.did_something = 0
                        continue
                else:
                    # If did nothing for 10 seconds, ignore
                    c1.did_something = self.opts.ignore

            #
            # Print the overal stats for this cpu
            #
            sys.stdout.write("%3d" % (cpu))

            if not self.opts.no_color:
                if utime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, utime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, utime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (utime))

            if not self.opts.no_color:
                if stime > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, stime, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, stime, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (stime))

            if not self.opts.no_color:
                if idle > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, idle, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, idle, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (idle))

            if not self.opts.no_color:
                if iowait > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, iowait, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, iowait, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (iowait))

            if not self.opts.no_color:
                if ireq > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, ireq, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, ireq, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (ireq))

            if not self.opts.no_color:
                if softirq > 90:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.red, softirq, colors.reset))
                else:
                    sys.stdout.write("%s%8.02f%%%s" % (colors.fg.green, softirq, colors.reset))
            else:
                sys.stdout.write("%8.02f%%" % (softirq))

            print

            self.how_many_printed_lines += 1
            if self.how_many_printed_lines >= self.lines:
                return

    def append_to_history(self, last_stats):
        for pid in last_stats.pids:
            pid = int(pid)

            if not self.cpu_history.has_key(pid):
                self.cpu_history[pid] = []
                self.cpu_switch_history[pid] = []
                self.cpu_hist_min[pid] = []
                self.cpu_hist_max[pid] = []

            if not last_stats.pstats.has_key(pid):
                return

            process_last_stats = last_stats.pstats[pid]
            self.cpu_history[pid].append(process_last_stats.cpu_pct)
            self.cpu_switch_history[pid].append(process_last_stats.cpu_switch)
            self.cpu_hist_min[pid] = process_last_stats.cpu_min_pct
            self.cpu_hist_max[pid] = process_last_stats.cpu_max_pct

            for tid in process_last_stats.threads:
                tid = int(tid)

                if pid == tid:
                    continue

                if not self.cpu_history.has_key(tid):
                    self.cpu_history[tid] = []
                    self.cpu_switch_history[tid] = []
                    self.cpu_hist_min[tid] = []
                    self.cpu_hist_max[tid] = []

                if not process_last_stats.tstats.has_key(tid):
                    continue

                thread_last_stats = process_last_stats.tstats[tid]
                self.cpu_history[tid].append(thread_last_stats.cpu_pct)
                self.cpu_switch_history[tid].append(thread_last_stats.cpu_switch)
                self.cpu_hist_min[tid] = thread_last_stats.cpu_min_pct
                self.cpu_hist_max[tid] = thread_last_stats.cpu_max_pct

    def display_histogram(self, pid):

        histogram_lines = self.lines - self.how_many_printed_lines
        if histogram_lines <= 2:
            return

        histogram_lines -= 1

        if not self.cpu_hist_max.has_key(pid):
            return

        if not self.cpu_history.has_key(pid):
            return

        if not self.opts.no_color:
            sys.stdout.write("%s%s" % (colors.bg.blue, colors.fg.white))
        else:
            sys.stdout.write("%s" % (colors.reverse))

        print "vvv Maximum CPU seen for pid %d, %.2f%%" % (pid, float(self.cpu_hist_max[pid])),

        sys.stdout.write("%s:" % (colors.reset))
        print

        hist_len = len(self.cpu_history[pid])

        for row in range(0, histogram_lines):
            s = ""

            start = hist_len - (self.columns - 10)
            if start < 0:
                start = 0
            end = hist_len

            max_cpu_percent_seen = float(self.cpu_hist_max[pid])
            low_cpu_percent_seen = float(self.cpu_hist_min[pid])
            r = max_cpu_percent_seen - low_cpu_percent_seen

            for x in range(start, end):
                if r <= 0:
                    s += '?'
                    continue

                if self.cpu_history[pid][x] == None:
                    s += '?'
                    continue

                v = (float(self.cpu_history[pid][x]) - low_cpu_percent_seen) / r
                v *= float(histogram_lines)
                v = histogram_lines - v

                if v > row:
                    if not self.opts.no_color:
                        s += "%s%s%s" % (colors.fg.white, "_", colors.reset)
                    else:
                        s += "%s%s%s" % (colors.reset, "_", colors.reset)
                else:
                    if not self.opts.no_color:
                        s += "%s%s%s" % (colors.bg.green, "#", colors.reset)
                    else:
                        s += "%s%s%s" % (colors.reverse, "#", colors.reset)

            percent_axis = "%03.02f%%" % (low_cpu_percent_seen + float(histogram_lines - row) * (r / histogram_lines))

            print("%7s %s" % (percent_axis, s))

        if not self.opts.no_color:
            sys.stdout.write("%s%s" % (colors.bg.blue, colors.fg.white))
        else:
            sys.stdout.write("%s" % (colors.reverse))

        print "^^^ Minimum CPU seen for pid %d, %.2f%%" % (pid, float(self.cpu_hist_min[pid])),

        sys.stdout.write("%s" % (colors.reset))

        print(" yatop, yet another top: use j,k,up/down to select processes, q to quit")

    #
    # Handle user input
    #
    def handle_user_input(self, last_stats):
        s = curses_get_ch(self.opts.delay)

        if s == "up":
            last = None

            for pid in last_stats.pids_and_tids:
                pid = int(pid)

                if self.opts.pid == pid:
                    if last != None:
                        self.opts.pid = last
                    return

                last = pid

        if s == "down":
            use_next = False

            for pid in last_stats.pids_and_tids:
                pid = int(pid)

                if use_next:
                    self.opts.pid = pid
                    return

                if self.opts.pid == pid:
                    use_next = True

        if s == "quit":
            exit(0)

    def main(self):
        #
        # Initialize the parser
        #
        arger = argparse.ArgumentParser()

        #
        # Arguments
        #
        arger.add_argument("-p", "--pid", type=int,
                help="filter to a given pid")

        arger.add_argument("-one", "--one", action="count", default=0,
                help="one shot and then exit, like top -b")

        arger.add_argument("-i", "--ignore", type=int, default=3,
                help="filter idle processes after x seconds of inaction")

        arger.add_argument("-d", "--delay", type=float, default=0.5,
                help="delay between system sampes")

        arger.add_argument("-a", "--all", action="count", default=0,
                help="include all processes, including idle ones")

        arger.add_argument("-c", "--no-color", action="count", default=0,
                help="disable color output")

        arger.add_argument("-H", "--no-histogram", action="count", default=0,
                help="disable histogram")

        #
        # Parse
        #
        self.opts = arger.parse_args()

        #
        # Screen size
        #
        self.lines, self.columns = os.popen('stty size', 'r').read().split()
        self.lines = int(self.lines) - 3
        self.columns = int(self.columns)
        if self.lines == None:
            self.lines = -1

        #
        # Linux clock tick; 100 usually
        #
        self.ticks = os.sysconf((os.sysconf_names['SC_CLK_TCK']))

        self.cpu_history = {}
        self.cpu_switch_history = {}
        self.cpu_hist_min = {}
        self.cpu_hist_max = {}

        #
        # One pid or all?
        #
        self.all_pids = False
        if not self.opts.pid:
            self.all_pids = True

        #
        # One snapshot like top -b?
        #
        if self.opts.one:
            last_stats = SystemSnapshot(self.opts.pid)
            time.sleep(self.opts.delay)
            curr_stats = SystemSnapshot(self.opts.pid)

            self.display_cpu_delta(last_stats, curr_stats)
            self.display_process_delta(last_stats, curr_stats)
            return

        #
        # Snapshots every x seconds
        #
        last_stats = SystemSnapshot(self.opts.pid)

        while True:
            time.sleep(self.opts.delay)
            curr_stats = SystemSnapshot(self.opts.pid)
            os.system('clear')

            self.display_cpu_delta(last_stats, curr_stats)
            self.display_process_delta(last_stats, curr_stats)
            self.append_to_history(curr_stats)

            #
            # Include bar chart?
            #
            if not self.opts.no_histogram:
                self.display_histogram(self.opts.pid)

            last_stats = curr_stats
            self.handle_user_input(last_stats)

class Thread(object):
    def __init__(self, pid, thread, stat):

        self.parent = pid
        self.thread = thread

        #
        # Get rid of spaces in process names
        #
        while True:
            new = re.sub(r'\((.*) (.*)\)', r'(\1_\2)', stat)
            if new == stat:
                break;
            stat = new

        sp = stat.split(' ')
        self.pid = sp[0]
        self.name = sp[1]
        self.state = sp[2]
        self.ppid = int(sp[3])
        self.pgid = int(sp[4])
        self.sid = int(sp[5])
        self.tty_nr = int(sp[6])
        self.tty_pgrp = int(sp[7])
        self.flags = int(sp[8])
        self.min_flt = int(sp[9])
        self.cmin_flt = int(sp[10])
        self.maj_flt = int(sp[11])
        self.cmaj_flt = int(sp[12])
        self.utime = int(sp[13])
        self.stime = int(sp[14])
        self.cutime = int(sp[15])
        self.cstime = int(sp[16])
        self.priority = int(sp[17])
        self.nice = int(sp[18])
        self.num_threads = int(sp[19])
        self.it_real_value = int(sp[20])
        self.start_time = int(sp[21])
        self.vsize = int(sp[22])
        self.rss = int(sp[23])
        self.rsslim = int(sp[24])
        self.start_code = int(sp[25])
        self.end_code = int(sp[26])
        self.start_stack = int(sp[27])
        self.esp = int(sp[28])
        self.eip = int(sp[29])
        self.pending = int(sp[30])
        self.blocked = int(sp[31])
        self.sigign = int(sp[32])
        self.sigcatch = int(sp[33])
        self.wchan = int(sp[34])
        self.zero1 = int(sp[35])
        self.zero2 = int(sp[36])
        self.exit_signal = int(sp[37])
        self.cpu = int(sp[38])
        self.rt_priority = int(sp[39])
        self.policy = int(sp[40])

        if (len(sp) > 42):
            self.blkio_ticks = int(sp[42])
        else:
            self.blkio_ticks = -1

        self.cpu_pct = None
        self.cpu_switch = None
        self.cpu_min_pct = None
        self.cpu_max_pct = None
        self.iowait_pct = None
        self.iowait_min_pct = None
        self.iowait_max_pct = None

        self.did_something = 0

#
# Parse /proc/stat output for 1 CPU
#
class CpuSnapshot(object):
    def __init__(self, pid, stat):

        self.utime = int(stat.split(' ')[1])
        self.nice = int(stat.split(' ')[2])
        self.stime = int(stat.split(' ')[3])
        self.idle = int(stat.split(' ')[4])
        self.iowait = int(stat.split(' ')[5])
        self.ireq = int(stat.split(' ')[6])
        self.softirq = int(stat.split(' ')[7])

        self.clock = self.utime + self.nice + self.stime + \
            self.idle + self.iowait + self.ireq + self.softirq
        self.did_something = 0


class GetPidShapshot(object):
    def __init__(self, pid, stat):

        #
        # Get rid of pesky space in process names
        #
        self.debug = stat
        while True:
            new = re.sub(r'\((.*) (.*)\)', r'(\1_\2)', stat)
            if new == stat:
                break;
            stat = new

        sp = stat.split(' ')
        self.pid = sp[0]
        self.name = sp[1]
        self.state = sp[2]
        self.ppid = int(sp[3])
        self.pgid = int(sp[4])
        self.sid = int(sp[5])
        self.tty_nr = int(sp[6])
        self.tty_pgrp = int(sp[7])
        self.flags = int(sp[8])
        self.min_flt = int(sp[9])
        self.cmin_flt = int(sp[10])
        self.maj_flt = int(sp[11])
        self.cmaj_flt = int(sp[12])
        self.utime = int(sp[13])
        self.stime = int(sp[14])
        self.cutime = int(sp[15])
        self.cstime = int(sp[16])
        self.priority = int(sp[17])
        self.nice = int(sp[18])
        self.num_threads = int(sp[19])
        self.it_real_value = int(sp[20])
        self.start_time = int(sp[21])
        self.vsize = int(sp[22])
        self.rss = int(sp[23])
        self.rsslim = int(sp[24])
        self.start_code = int(sp[25])
        self.end_code = int(sp[26])
        self.start_stack = int(sp[27])
        self.esp = int(sp[28])
        self.eip = int(sp[29])
        self.pending = int(sp[30])
        self.blocked = int(sp[31])
        self.sigign = int(sp[32])
        self.sigcatch = int(sp[33])
        self.wchan = int(sp[34])
        self.zero1 = int(sp[35])
        self.zero2 = int(sp[36])
        self.exit_signal = int(sp[37])
        self.cpu = int(sp[38])
        self.rt_priority = int(sp[39])
        self.policy = int(sp[40])

        if (len(sp) > 42):
            self.blkio_ticks = int(sp[42])
        else:
            self.blkio_ticks = -1

        self.cpu_pct = None
        self.cpu_switch = None
        self.cpu_min_pct = None
        self.cpu_max_pct = None
        self.iowait_pct = None
        self.iowait_min_pct = None
        self.iowait_max_pct = None

        self.did_something = 0

        self.threads = []

        try:
            self.threads = \
                [thread for thread in
                    os.listdir(
                        os.path.join('/proc/', pid, 'task')) \
                            if thread.isdigit()]

            self.tstats = {}
            for thread in self.threads:
                with open( \
                    os.path.join('/proc/', pid, 'task', thread, 'stat' )) \
                        as pidfile:

                    self.tstats[int(thread)] = \
                        Thread(pid, thread, pidfile.readline())

        except Exception:
            pass
            return


class SystemSnapshot(object):
    def __init__(self, pid=""):
        self.get_cpus_snapshot()
        self.get_processes_snapshot(pid)

    #
    # Get /proc/<cpu>/stat information for a single cpu
    #
    def get_cpus_snapshot(self):
        try:
            self.cpuinfo = {}
            cpu = 0

            with open(os.path.join('/proc/stat'), 'r') as cpufile:
                for line in cpufile.readlines():
                    if not line.startswith("cpu"):
                        continue

                    if line.startswith("cpu "):
                        continue

                    self.cpuinfo[int(cpu)] = CpuSnapshot(cpu, line)
                    cpu += 1

            self.cpus = cpu

        except Exception:
            pass
            return

    #
    # Process names have some garbage at the end; remove it.
    #
    def process_name_filter(self, str):
        ret=""
        for c in str:
            if ord(c) > 31 or ord(c) == 9:
                ret += c
            else:
                ret += " "
        return ret

    #
    # Parse /proc/<cpu>/cmdline
    #
    def get_process_name(self, pid):
        try:
            with open(os.path.join('/proc/', pid, 'cmdline'), 'r') as pidfile:
                return self.process_name_filter(pidfile.readline())

        except Exception:
            pass
            return

    #
    # Get /proc/<pid>/stat information for a single pid
    #
    def get_process_info(self, pid):
        try:
            with open(os.path.join('/proc/', pid, 'stat'), 'r') as pidfile:
                self.pstats[int(pid)] = GetPidShapshot(pid, pidfile.readline())

        except Exception:
            pass
            return

    #
    # Filter to a given pid or all pids.
    #
    def get_processes_snapshot(self, pid=None):
        self.pids = [pid for pid in os.listdir('/proc') if pid.isdigit()]

        self.pids_and_tids = []
        self.pstats = {}
        for pid in self.pids:
            self.get_process_info(pid)

#
# Taken from
#
# http://stackoverflow.com/users/4157799/gi-jack
#
class colors:
    reset='\033[0m'
    bold='\033[01m'
    disable='\033[02m'
    underline='\033[04m'
    reverse='\033[07m'
    strikethrough='\033[09m'
    invisible='\033[08m'
    class fg:
        black='\033[30m'
        red='\033[31m'
        green='\033[32m'
        orange='\033[33m'
        blue='\033[34m'
        purple='\033[35m'
        cyan='\033[36m'
        white='\033[37m'
        darkgrey='\033[90m'
        lightred='\033[91m'
        lightgreen='\033[92m'
        yellow='\033[93m'
        lightblue='\033[94m'
        pink='\033[95m'
        lightcyan='\033[96m'
    class bg:
        black='\033[40m'
        red='\033[41m'
        green='\033[42m'
        orange='\033[43m'
        blue='\033[44m'
        purple='\033[45m'
        cyan='\033[46m'
        white='\033[47m'

#
# Read raw data from the console, so we can understand cursor keys.
#
def curses_read_raw(delay):
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)

    ch = None
    try:
        tty.setraw(sys.stdin.fileno())

        i, o, e = select.select( [sys.stdin], [], [], delay)

        if (i):
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch

#
# Map keyboard strings to an event.
#
def curses_get_ch(delay):
    inkey = curses_read_raw(delay)
    if inkey == None:
        return

    if inkey == 'q':
        return "quit"
    elif inkey == 'j':
        return "down"
    elif inkey == 'k':
        return "up"
    elif inkey == '\x1b[A':
        return "up"
    elif inkey == '\x1b[B':
        return "down"
    elif inkey == '\x1b[C':
        return "right"
    elif inkey == '\x1b[D':
        return "left"
    else:
        return


if __name__ == '__main__':
    Main().main()

exit(0)