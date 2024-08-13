#!/usr/bin/python

# Copyright 2018 Synchronoss Technologies, Inc. | All Rights Reserved

###############################################################################
#
# golden.py
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
    print "Check MX imservping, process uptime & stats."

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

    # Set up local variables for hosts / ports needed. Info comes from config files.
    sysCheckUsr = scriptConfig['sysCheckUsr']
    sysCheckPwd = scriptConfig['sysCheckPwd']
    fileChecks = scriptConfig['fileChecks']
    mxProcessUpTimeHourThreshold = int( scriptConfig['mxProcessUpTimeHourThreshold'] )
    mxQueueRootDir = scriptConfig['mxQueueRootDir']
    mxQueueThreshold = int( scriptConfig['mxQueueThreshold'] )

    logger.info("------------")
    logger.info("Server: " + host)
    logger.info("------------")

    checkPassed = True

    try:
        #
        # Check imservping & process uptime
        #
        imservpingPath = '~imail/bin/imservping'
        cmd = 'source ~imail/.profile; ' + imservpingPath

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
        cmdOutputLines = cmdOutput.split("\r\n")

        if 'No such file or directory' in cmdOutput:
            raise ValueError('imservping was not found at ' + host + ':' + imservpingPath)

        imservpingResults = {}
        for line in cmdOutputLines:
            if 'imservping: (Info)' in line and 'responded' in line:
                mxServerType = line.split()[7]
                imservpingResults[mxServerType] = 'responded'
            elif 'imservping: (Alarm) server' in line:
                mxServerType = line.split()[8]
                imservpingResults[mxServerType] = 'not-responding'
                checkPassed = False

        logger.info('imservping results:')
        strFormat = '{:<30.30}{:<15}{:<13}{:<15}'
        str2Format = '{:<30.30}{:<15}{:<13.2f}{:<15}'
        logger.info( strFormat.format( '  MX PROCESS', 'STATUS', 'UP TIME(HRS)', '') )
        for key in imservpingResults:
            alarmStr = ''
            if 'not-responding' in imservpingResults[key]:
                alarmStr = '***SERVER DOWN***'
                checkPassed = False
                mxProcessUptime = 0.0
            else:
                # For Mx servers that are responding, find out how long they have been up.
                mxProcessUptime = float ( mxServerUptime(host, sysCheckUsr, sysCheckPwd, key) ) / 3600.0
                if (mxProcessUptime < mxProcessUpTimeHourThreshold):
                    alarmStr = '***SERVER RESTARTED***'
                    checkPassed = False
            if alarmStr is '':
                logger.info( str2Format.format( '  ' + key, imservpingResults[key], mxProcessUptime, alarmStr) )
            else:
                logger.warning( str2Format.format( '  ' + key, imservpingResults[key], mxProcessUptime, alarmStr) )

        #
        # Check the queue size of Mx queueserv.
        #
        if 'imqueueserv' in imservpingResults:
            # queueserv process is meant to be running, so check queue size.

            cmd = 'find ' + mxQueueRootDir + ' -name \"*-Control\" | wc -l'

            # Run the command on remote host.
            cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
            cmdOutputLines = int(cmdOutput.split("\r\n")[0])

            alarmStr = ''
            if cmdOutputLines >= mxQueueThreshold:
                alarmStr = '***QUEUE THRESHOLD***'
                checkPassed = False

            strFormat = '{:<30.30}{:<28}{:<15}'
            logger.info('')
            if alarmStr is '':
                logger.info( strFormat.format( 'queue count:', str(cmdOutputLines), alarmStr) )
            else:
                logger.warning( strFormat.format( 'queue count:', str(cmdOutputLines), alarmStr) )

        else:
            # No queueserv running on host, so skip.
            pass

        #
        # Check the stats of Mx server running.
        #

        # Loop through each stats file in the 'fileChecks' config.

        for statFileLocaction, statToCheck in fileChecks.iteritems():

            statFile = statFileLocaction.split('/')[-1]

            # If Mx server found by imservping (above) doesn't appear in the statFile, skip it.
            found = False
            for key in imservpingResults:

                if key in statFile:
                    found = True

                # Format of mss entry is different ('mss/mss.1') and needs this...
                if 'mss/' in key:
                    if 'mss' in statFile:
                        found = True

            if not found:
                continue

            logger.info('')
            logger.info( statFile )

            #  Loop through each stat check

            for statName, statChecks in statToCheck.iteritems():

                elementPosition = statChecks.get('elementPosition')
                elementThreshold = int( statChecks.get('elementThreshold') )
                alarmOnOverOrUnderThreshold = statChecks.get('alarmOnOverOrUnderThreshold')

                # Grep stat file ('statFileLocaction') for the stat to be checked ('statName')

                cmd = 'grep ' + statName + ' ' + statFileLocaction + ' | tail -1'

                # Run the command on remote host.
                cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
                statEvent = cmdOutput.split("\r\n")[0]

                # Define output format, so output looks nice.
                strFormat = '{:<30.30}{:<28}{:15}'

                if 'No such file' in cmdOutput:
                    logger.info('   File not found.')
                    checkPassed = False
                    break

                if statName not in statEvent:
                    logger.info( strFormat.format( '  ' + statName, '', '***STAT NOT FOUND***') )
                    checkPassed = False
                    break

                elementToCheck = int( statEvent.split()[elementPosition] )
                if alarmOnOverOrUnderThreshold == 'over':
                    if (elementToCheck >= elementThreshold):
                        alarmStr = '***THRESHOLD REACHED***'
                        checkPassed = False
                    else:
                        alarmStr = ''
                else:
                    if (elementToCheck <= elementThreshold):
                        alarmStr = '***THRESHOLD REACHED***'
                        checkPassed = False
                    else:
                        alarmStr = ''

                if alarmStr is '':
                    logger.info( strFormat.format( '  ' + statName, elementToCheck, alarmStr) )
                else:
                    logger.warning( strFormat.format( '  ' + statName, elementToCheck, alarmStr) )

    except Exception as e:
        logger.error( str(e) )
        exit(1)

    if not checkPassed:
        exit(1)

    return

#==============================================================================
# mxServerUptime()
#
# Get the time a process has been running for (in Sec)
#==============================================================================
def mxServerUptime(host, sysCheckUsr, sysCheckPwd, mxServerName):

    if 'mss/' in mxServerName:
        mxServerName = mxServerName.replace("mss/","")

    cmd = 'ps -ef | grep ' + mxServerName + ' | grep -v grep | grep -v perl'
    cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
    pid = cmdOutput.split()[1]
    cmd = 'ps -p ' + str(pid) + ' -o etimes | tail -1'
    cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd).split('\r\n')[0].strip()
    return cmdOutput

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

