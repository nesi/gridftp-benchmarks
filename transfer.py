#!/usr/bin/python

import os
import sys
import subprocess
import argparse

from multiprocessing import Event
import threading
import time
import subprocess

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def timing(event, size, parameter, results_time, results_speed):
    ts = time.time()
    event.wait()
    te = time.time()
    elapsed_time = te - ts
    logger.debug("ADDING: "+parameter+" : "+str(elapsed_time))
    results_time[parameter] = elapsed_time
    speed = float(size) / elapsed_time
    # we want megabit per second
    results_speed[parameter] = speed * 8.389

def execution(event, command): 

    cmd = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    cmd.wait()
    event.set()
    for line in cmd.stderr:
        print >> sys.stderr, "Command error: "+line

def get_source_file(size, working_directory):
    
    filename = str(size)+'mb.file'
    file_path = working_directory+os.path.sep+filename

    logger.debug("Checking whether input file exists: %s", file_path)
    if not os.path.exists(file_path):
        logger.info("Creating file: %s", file_path)
        os.system("head -c "+str(size)+"M < /dev/urandom > "+file_path)
    
    return file_path

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Run gridftp benchmarks in a parameterized way')
    parser.add_argument('--sizes', help='the size of the input file (in megabytes)', required=True)
    parser.add_argument('-d','--working_directory', help='the directoriy where the input files are, default: current dir', required=False, default=os.getcwd())
    parser.add_argument('-t','--target', help='the target host/directory', required=True)
    parser.add_argument('-p','--parallel', help='level of parallelization', required=False)
    parser.add_argument('-s', '--source', help="the source host/directory, impies 3rd party transfer. if not specified, files will be uploaded from working directory", )
    args = parser.parse_args()
    
    source = args.source
    if source and not source.endswith("/"):
        source = source + "/"

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
    
    sizes = args.sizes.split(',')

    results_time = {}
    results_speed = {}

    
    for size in sizes:

        filename = str(size)+'mb.file'
        
        if source:
            list_command = "globus-url-copy -list "+source
            list_cmd = subprocess.Popen(list_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            list_cmd.wait()
            source_path = source + filename
            contains = False
            for line in list_cmd.stdout:
                if line.strip() == filename:
                    contains = True
            if not contains:
                file_path = 'file://'+get_source_file(size, working_directory)
                upload_command = 'globus-url-copy -vb ' + '-p 16 ' + file_path + ' ' + source_path
                logger.info('Uploading source file for 3rd party transfer:\n\t'+upload_command)
                upload_cmd = subprocess.Popen(upload_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                upload_cmd.wait()

        else:
            source_path = "file://"+get_source_file(size, working_directory)

        parallels = args.parallel.split(',')

        for parallel in parallels:

            target = args.target
            if not target.endswith("/"):
                target = target + "/"

            logger.debug("starting transfer")

            command = 'globus-url-copy -vb ' + '-p ' + str(parallel) + ' '+source_path+' ' + target + filename

            logger.info("Starting transfer:\n\t"+command)

            parameter = str(size)+'mb_par_'+str(parallel)

            event = Event()
            e = threading.Thread(target=execution, args=(event, command))
            t = threading.Thread(target=timing, args=(event, size, parameter, results_time, results_speed))
            t.start()  
            e.start() 
            while not event.is_set():
                time.sleep(1)
                

    for run in sorted(results_speed.iterkeys()):
        print("{0} : {1:.2f} mbps ({2:.2f} sec)".format(run,results_speed[run],results_time[run]))



