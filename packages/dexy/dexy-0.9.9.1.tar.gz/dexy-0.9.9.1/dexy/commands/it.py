from dexy.commands.utils import init_wrapper
from dexy.utils import defaults
import dexy.exceptions
import os
import subprocess
import sys
import time

def log_and_print_exception(wrapper, e):
    if hasattr(wrapper, 'log'):
        wrapper.log.error("An error has occurred.")
        wrapper.log.error(e)
        wrapper.log.error(e.message)
    import traceback
    traceback.print_exc()

def handle_user_feedback_exception(wrapper, e):
    if hasattr(wrapper, 'log'):
        wrapper.log.error("A problem has occurred with one of your documents:")
        wrapper.log.error(e.message)
    sys.stderr.write("Oops, there's a problem processing one of your documents. Here is the error message:" + os.linesep)
    sys.stderr.write(e.message)
    if not e.message.endswith(os.linesep) or e.message.endswith("\n"):
        sys.stderr.write(os.linesep)

def handle_keyboard_interrupt():
    sys.stderr.write("""
    ok, stopping your dexy run
    you might want to 'dexy reset' before running again\n""")
    sys.exit(1)

def run_dexy_in_profiler(wrapper, profile):
    if isinstance(profile, bool):
        profile_filename = 'dexy.prof'
    else:
        profile_filename = profile

    import cProfile
    print "running dexy with cProfile, writing profile data to %s" % profile_filename
    cProfile.runctx("wrapper.run_from_new()", None, locals(), profile_filename)
    import pstats
    stat = pstats.Stats(profile_filename)
    stat.sort_stats("cumulative")
    stat.print_stats(25)

def run_dexy_in_strace(wrapper, strace):
    if isinstance(strace, bool):
        strace_filename = 'dexy.strace'
    else:
        strace_filename = strace

    def run_command(command):
        proc = subprocess.Popen(
                   command,
                   shell=True,
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE
                   )
        stdout, stderr = proc.communicate()
        print stdout

    commands = ( 
            "strace dexy --reports \"\" 2> %s" % strace_filename, # TODO pass command line args except for --strace option
            "echo \"calls to stat:\" ; grep \"^stat(\" %s | wc -l" % strace_filename,
            "echo \"calls to read:\" ; grep \"^read(\" %s | wc -l" % strace_filename,
            "echo \"calls to write:\" ; grep \"^write(\" %s | wc -l" % strace_filename,
            "grep \"^stat(\" %s | sort | uniq -c | sort -r -n > strace-stats.txt" % strace_filename,
            "grep \"^read(\" %s | sort | uniq -c | sort -r -n > strace-reads.txt" % strace_filename,
            "grep \"^write(\" %s | sort | uniq -c | sort -r -n > strace-writes.txt" % strace_filename,
        )

    for command in commands:
        run_command(command)

def dexy_command(
        __cli_options=False,
        artifactsdir=defaults['artifacts_dir'], # location of directory in which to store artifacts
        conf=defaults['config_file'], # name to use for configuration file
        configs=defaults['configs'], # list of doc config files to parse
        debug=defaults['debug'], # Prints stack traces, other debug stuff.
        dryrun=defaults['dry_run'], # if True, just parse config and print batch info, don't run dexy
        encoding=defaults['encoding'], # Default encoding. Set to 'chardet' to use chardet auto detection.
        exclude=defaults['exclude'], # comma-separated list of directory names to exclude from dexy processing
        excludealso=defaults['exclude_also'], # comma-separated list of directory names to exclude from dexy processing
        full=defaults['full'], # Whether to do a full run including tasks marked default: False
        globals=defaults['globals'], # global values to make available within dexy documents, should be KEY=VALUE pairs separated by spaces
        help=False, #nodoc
        h=False, #nodoc
        hashfunction=defaults['hashfunction'], # What hash function to use, set to crc32 or adler32 for more speed but less reliability
        logdir=defaults['log_dir'], # location of directory in which to store logs
        logfile=defaults['log_file'], # name of log file
        logformat=defaults['log_format'], # format of log entries
        loglevel=defaults['log_level'], # log level, valid options are DEBUG, INFO, WARN
        nocache=defaults['dont_use_cache'], # whether to force dexy not to use files from the cache
        noreports=False, # if true, don't run any reports
        pickle=defaults['pickle'], # library to use for persisting info to disk, may be 'c', 'py', 'json'
        plugins=defaults['plugins'], # additional python packages containing dexy plugins
        profile=defaults['profile'], # whether to run with cProfile. Arg can be a boolean, in which case profile saved to 'dexy.prof', or a filename to save to.
        r=False, # whether to clear cache before running dexy
        recurse=defaults['recurse'], # whether to include doc config files in subdirectories
        reports=defaults['reports'], # reports to be run after dexy runs, enclose in quotes and separate with spaces
        reset=False, # whether to clear cache before running dexy
        silent=defaults['silent'], # Whether to not print any output when running dexy
        strace=defaults['strace'], # Run dexy using strace (VERY slow)
        uselocals=defaults['uselocals'], # use cached local copies of remote URLs, faster but might not be up to date, 304 from server will override this setting
        target=defaults['target'], # Which target to run. By default all targets are run, this allows you to run only 1 bundle (and its dependencies).
        version=False # For people who type -version out of habit
    ):
    """
    Runs Dexy.
    """
    if h or help:
        return dexy.commands.help_command()

    if version:
        return dexy.commands.version_command()

    if r or reset:
        dexy.commands.dirs.reset_command(artifactsdir=artifactsdir, logdir=logdir)

    # Don't trap errors yet because error handling uses wrapper instance.
    wrapper = init_wrapper(locals())

    # TODO make this error nicer..
    wrapper.assert_dexy_dirs_exist()

    run_reports = (not noreports)

    try:
        if profile:
            run_dexy_in_profiler(wrapper, profile)
        elif strace:
            run_dexy_in_strace(wrapper, strace)
            run_reports = False
        else:
            start = time.time()
            wrapper.run_from_new()
            elapsed = time.time() - start
            print "dexy run finished in %0.3f" % elapsed

    except dexy.exceptions.UserFeedback as e:
        handle_user_feedback_exception(wrapper, e)
    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        log_and_print_exception(wrapper, e)
        raise

    if run_reports and hasattr(wrapper, 'batch'):
        start_time = time.time()
        wrapper.report()
        print "dexy reports finished in %0.3f" % (time.time() - start_time)

def it_command(**kwargs):
    # so you can type 'dexy it' if you want to
    dexy_command(kwargs)
