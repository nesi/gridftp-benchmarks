#!/usr/bin/python


import argparse
import os
import subprocess
import sys
from multiprocessing import Event
import time
import threading

__author__ = 'markus'


import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_source_file(size, working_directory, clean=False):

    """Create files with the specified size.

    Keyword arguments:
    size -- the size in mb
    working_directory -- the directory to create files in

    """

    filename = str(size)+'mb.file'
    file_path = working_directory+os.path.sep+filename

    if clean:
        try:
            os.remove(file_path)
        except OSError:
            pass

    logger.debug("Checking whether input file exists: %s", file_path)
    if not os.path.exists(file_path):
        logger.info("Creating file: %s", file_path)
        os.system("head -c "+str(size)+"M < /dev/urandom > "+file_path)

    return file_path

def timing(event, size, results_time, results_speed, run_name):
    ts = time.time()
    event.wait()
    te = time.time()
    elapsed_time = te - ts
    logger.debug("ADDING: "+run_name+" : "+str(elapsed_time))
    results_time[run_name] = elapsed_time
    speed = float(size) / elapsed_time
    results_speed[run_name] = speed
    # if we want megabit per second
    #results_speed[run_name] = speed * 8.389

def execution(event, transfer, parameters):

    transfer.transfer(parameters)

    event.set()

def do_the_transfer(source, target, filename, size, runname, parameters="", clean=False):

    logger.debug("starting transfer")

    if ("gsiftp" in source) or ("gsiftp" in target):
        transfer = Gridftp(source+filename, target+filename)
    else:
        transfer = Scp(source+filename, target+filename)

    file_temp = get_source_file(size, working_directory, clean)

    transfer.prepare(file_temp, clean)

    #logger.info("Starting transfer:\n\t"+str(gridftp))

    event = Event()
    e = threading.Thread(target=execution, args=(event, transfer, parameters))
    t = threading.Thread(target=timing, args=(event, size, results_time, results_speed, runname))
    t.start()
    e.start()
    while not event.is_set():
        time.sleep(1)


class Transfer(object):

    def __init__(self, source, target):
        self.source = source
        self.target = target


    def transfer(self, parameters):
        self.transfer_file(self.source, self.target, parameters)


class Gridftp(Transfer):

    """Gridftp transfers"""

    def __init__(self, source, target):
        super(Gridftp, self).__init__(source, target)


    def prepare(self, temp_file, clean=False):

        if temp_file == self.source:
            logger.info("Not uploading file, since temp file and source are the same")
            return

        if file:
            if not self.file_exists(self.source) or clean:
                logger.info('Uploading file to source destination')
                self.transfer_file(temp_file, self.source)


    def transfer_file(self, source_t, target_t, parameters):

        if not parameters:
            parameters = ""
        upload_command = 'globus-url-copy -vb ' + ' ' + parameters +  ' ' + source_t + ' ' + target_t
        logger.info('Transferring file:\n\t'+upload_command)
        upload_cmd = subprocess.Popen(upload_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        upload_cmd.wait()

        for line in upload_cmd.stderr:
            print >> sys.stderr, "Command error: "+line

        exists = self.file_exists(target_t)
        return exists


    def file_exists(self, file_url):
        last_slash = file_url.rindex("/")

        parent_url = file_url[:last_slash+1]
        filename = file_url[last_slash+1:]

        list_command = "globus-url-copy -list "+parent_url
        list_cmd = subprocess.Popen(list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        list_cmd.wait()

        contains = False
        for line in list_cmd.stdout:
            if line.strip() == filename:
                contains = True
                break

        return contains

class Scp(Transfer):

    def __init__(self, source, target):
        super(Scp, self).__init__(source, target)

    def prepare(self, temp_file, clean=False):
        # do nothing
        pass

    def transfer_file(self, source_t, target_t, parameters=""):
        if not parameters:
            parameters = ""
        upload_command = 'scp -r ' + parameters + ' ' + source_t + ' ' + target_t
        logger.info('Transferring file:\n\t'+upload_command)
        upload_cmd = subprocess.Popen(upload_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        upload_cmd.wait()

    def file_exists(self, file_url):

        host_separator = file_url.index(":")

        host = file_url[:host_separator]
        path = file_url[host_separator+1:]

        last_slash = path.rindex("/")
        filename = path[last_slash+1:]

        list_command = "ssh "+host+" ls "+path
        list_cmd = subprocess.Popen(list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        list_cmd.wait()

        contains = False
        for line in list_cmd.stdout:
            if line.strip() == filename:
                contains = True
                break

        return contains


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run transfer benchmarks in a parameterized way')
    parser.add_argument('--sizes', help='the size of the input file (in megabytes)', required=False)
    parser.add_argument('-d','--working-directory', help='the directoriy where the input files are, default: current dir', required=False, default=os.getcwd())
    parser.add_argument('-t','--target', help='the target host/directory', required=True)
    parser.add_argument('-s', '--source', help="the source host/directory. if not specified, files will be uploaded from working directory", )
    parser.add_argument('-p', '--parameters', help="extra parameters, if '-p' is specified as well, {x} gets replaced with those values for seperate runs")
    parser.add_argument('-x', help="comma separated list of parameters to use in the '-p' option")
    parser.add_argument('-c', '--clean', help="whether to clean up all generated input files and recreate them (to prevent caching affecting results)")
    args = parser.parse_args()

    working_directory = args.working_directory
    if not os.path.isdir(working_directory):
        try:
            os.makedirs(working_directory)
        except OSError:
            print >> sys.stderr, "Can't create directory "+working_directory
            sys.exit(1)
        if not os.path.isdir(working_directory):
            print >> sys.stderr, 'Directory does not exist or is not directory: '+working_directory
            sys.exit(1)

    working_directory = os.path.abspath(working_directory)

    source = args.source

    if not source:
        source = working_directory

    if not source.endswith("/"):
        source = source + "/"

    target = args.target
    if not target.endswith("/"):
        target = target + "/"

    sizes = args.sizes.split(',')

    results_time = {}
    results_speed = {}

    extra_parameters = args.parameters

    parameters = args.x

    if parameters and not extra_parameters:
        print "--parameters sepcified, but not --extra-parameters. that doesn't work"
        sys.exit(1)
    elif parameters and extra_parameters:
        if not '{x}' in extra_parameters:
            print "{x} not in extra parameters, doesn't make sense"
            sys.exit(1)

    if parameters:
        parameters = parameters.split(',')

    i = 1

    clean = args.clean

    if sizes:

        for size in sizes:

            filename = str(size)+'mb.file'

            size_string = "{0:05d}mb".format(int(size))

            if parameters:

                for p in parameters:
                    runname_prefix = "Run {0:03d}: ".format(i)

                    pars = extra_parameters.replace("{x}", p)
                    do_the_transfer(source, target, filename, size, runname_prefix + size_string + ' ['+pars+']', pars, clean)

                    i += 1
            else:
                runname_prefix = "Run {0:03d}: ".format(i)

                do_the_transfer(source, target, filename, size, runname_prefix + size_string, clean)

                i += 1

    else:

        print "not implmemented yet"
        sys.exit(1)

    for run in sorted(results_speed.iterkeys()):
        print("{0} : {1:.2f} MB/s ({2:.2f} sec)".format(run,results_speed[run],results_time[run]))






