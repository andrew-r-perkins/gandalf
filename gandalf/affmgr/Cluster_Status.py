#!/usr/bin/python

# Copyright 2018 Synchronoss Technologies, Inc. | All Rights Reserved

###############################################################################
#
# Cluster_Status.py
#
# This is a template script to be used as a starting point for creating a
# new test case script. During automated testing, this script is called
# by the framework script (automated_testing.py) if the config tells
# the framework to run it.
#
# Detailed version history can be viewed on Bitbucket in the Gandalf Onering  
# repository at https://bitbucket.org/openwave/onering/commits/all
#
###############################################################################

#==============================================================================
# Imported python modules
#==============================================================================

# Allow import from parent directory
import os
import sys
import inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Insert local lib directory into path
libdir = currentdir + "/lib"
sys.path.insert(0, libdir)

# Import required modules
import argparse
import automated_testing_common

#==============================================================================
# description()
#
# Parameters:
#   None.
#
# Purpose:
#   Print out a one line test description. The string in the print line is
#   used in the Excel test report.
#==============================================================================
def description():
    #############################################################
    ###### UPDATE LINE BELOW WITH DESCRIPTION OF TEST CASE ######
    #############################################################
    print "Check Affinity Manager cluster status."

#==============================================================================
# main(commonConfig, scriptConfig, host)
#
# Parameters:
#   commonConfig - Python ordered dictionary containing common config data that
#                  is contained in common.yml.
#   scriptConfig - Python ordered dictionary containing script config data that
#                  is specific for this test. The config file that this script
#                  will use is defined in common.yml.
#   host         - Optional string parameter that contains argument contained in command
#                  line switch from --host.
#                  The framework (automated_testing.py) uses this to loop through
#                  a list of hosts so the framework can run the same test on multiple
#                  hosts.
#
# Purpose:
#   The main() is where the test case changes should be added for the
#    specifics of the test being added.
#==============================================================================
def main(commonConfig, scriptConfig, host):

    logger.debug("In main() subroutine for " + __file__)
    logger.debug("Site config:")
    logger.debug(str(commonConfig))
    logger.debug("Script config:")
    logger.debug(str(scriptConfig))
    logger.debug("Host:" + str(host))

    #############################################################
    ###### ADD UPDATES BELOW WITH TEST CASE SCRIPT         ######
    ###### If test fails, exit with a non-zero value       ######
    ###### Ie:                                             ######
    ######    If test passes, return()                     ######
    ######    If test fails, exit(x)                       ######
    ######      where x is a non-zero integer              ######
    ######      that will be reported as a error code.     ######
    #############################################################

    import pexpect

    # Set up local variables for hosts / ports needed. Info comes from config files.
    affmgrHost = host
    affmgrUsr = scriptConfig['affmgrUsr']
    affmgrPwd = scriptConfig['affmgrPwd']

    logger.info("------------")
    logger.info("Affinity Manager host:     " + affmgrHost)
    logger.info("------------")

    # Execute pcs status command
    logger.info("Execute pcs status command")
    cmd = "pcs status"
    try:
        output = automated_testing_common.runSshCmd(affmgrUsr, affmgrHost, cmd, affmgrPwd)
        logger.info( output )
    except Exception as e:
        exit(1)

#==============================================================================
# Main body
#==============================================================================

# Add details for command line arguments.
parser = argparse.ArgumentParser()
parser.add_argument("--description", help="Print a description of the test", action="store_true")
parser.add_argument("--config", help="Config file for this test")
parser.add_argument("--log", help="Log file that this test will write to")
parser.add_argument("--loglevel", default="INFO",
                    help="Log level ( ERROR | WARNING | INFO | DEBUG ). Default is INFO.")
parser.add_argument("--host", default="",
                    help="This is an optional switch that can be used to provide a host" +
                    " (IP or hostname) to be tested in this test.")
args = parser.parse_args()

# If command line has --description, excute description().
if args.description:
    description()
    exit(0)

# If command line has --config and --log switches,
# start logger, read config files and excute main().
if (__name__ == "__main__") and (args.config) and (args.log):

    # Start the logger for this script at the right log level.
    logger = automated_testing_common.createLogger(__file__, args.loglevel)
    # Log to file.
    automated_testing_common.addFileAndHostToLogger(args.log, args.host, logger)
    # Log to screen
    automated_testing_common.addConsoleToLogger(logger)

    # Log group and test being run.
    dir_path_list = __file__.split('/')
    logger.info("")
    logger.info("        --- TEST GROUP : " + dir_path_list[-2] +
                ", TEST CASE : " + dir_path_list[-1] + " " + args.host)
    logger.info("")

    # Load config data from the YAML config file into a python dictory 'config'
    # It is expected that the config file will be in the same dir path as this script.
    dir_path = os.path.dirname(os.path.realpath(__file__))
    configFullPath = dir_path + '/' + args.config
    scriptConfig = automated_testing_common.yamlLoader(logger, configFullPath)

    # Load common config file
    configFullPath = dir_path + '/../common.yml'
    commonConfig = automated_testing_common.yamlLoader(logger, configFullPath)

    # Run the test for this script
    main(commonConfig, scriptConfig, args.host)
