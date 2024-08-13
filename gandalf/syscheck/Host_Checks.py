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
    print "Check uptime, load average, memory, disk space, network & swapping."

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
    loadAverageThreshold = float( scriptConfig['loadAverageThreshold'] )
    hostUpTimeHourThreshold = float( scriptConfig['hostUpTimeHourThreshold'] )
    diskUsageThreshold = float( scriptConfig['diskUsageThreshold'] )
    memoryUsageThreshold = float( scriptConfig['memoryUsageThreshold'] )
    swapUsageThreshold = float( scriptConfig['swapUsageThreshold'] )
    timeWaitThreshold = float( scriptConfig['timeWaitThreshold'] )
    closeWaitThreshold = float( scriptConfig['closeWaitThreshold'] )
    swapSiThreshold = int( scriptConfig['swapSiThreshold'] )
    swapSoThreshold = int( scriptConfig['swapSoThreshold'] )

    logger.info("------------")
    logger.info("Server: " + host)
    logger.info("Load Average Threshold: " + str(loadAverageThreshold))
    logger.info("Up Time Threshold (Hours): " + str(hostUpTimeHourThreshold))
    logger.info("Disk Usage % Threshold: " + str(diskUsageThreshold))
    logger.info("Memory Usage % Threshold: " + str(memoryUsageThreshold))
    logger.info("Swap Usage % Threshold: " + str(swapUsageThreshold))
    logger.info("# TIME_WAIT Threshold: " + str(timeWaitThreshold))
    logger.info("# CLOSE_WAIT Threshold: " + str(closeWaitThreshold))
    logger.info("# Swap in / sec Threshold: " + str(swapSiThreshold))
    logger.info("# Swap out / sec Threshold: " + str(swapSoThreshold))
    logger.info("------------")

    checkPassed = True

    try:
        #
        # Check up time of the server (using first number in /proc/uptime file)
        #
        cmd = "cat /proc/uptime"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
        # Get load average info and do threshold check
        upTimeSec = float(cmdOutput.split(" ")[0])
        upTimeHour = upTimeSec / 3600.0

        strFormat = '{:<30.30}{:28}{:15}'
        str2Format = '{:<30.30}{:<28.2f}{:15}'
        alarmStr = ''
        if (upTimeHour < hostUpTimeHourThreshold):
            alarmStr = '***THRESHOLD REACHED***'
            checkPassed = False

        if alarmStr is '':
            logger.info( str2Format.format("Uptime (hrs):", upTimeHour, alarmStr) )
        else:
            logger.warning( str2Format.format("Uptime (hrs):", upTimeHour, alarmStr) )

        #
        # Check load average (using 'uptime' cmd)
        #
        cmd = "uptime"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)

        # Get load average info and do threshold check
        loadAverage = float(cmdOutput.split("load average: ")[1].split(",")[0])

        strFormat = '{:<30.30}{:28}{:15}'
        if (loadAverage >= loadAverageThreshold):
            logger.warning( strFormat.format("Load average:", str(loadAverage), '***THRESHOLD REACHED***') )
            checkPassed = False
        else:
            logger.info( strFormat.format("Load average:", str(loadAverage), '') )

        # Get load average info and do threshold check
        loadAverage = float(cmdOutput.split("load average: ")[1].split(",")[0])

        #
        # Memory & swap usage
        #
        cmd = "free --mega"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)

        cmdOutputLines = cmdOutput.split("\r\n")
        memoryInfo = cmdOutputLines[1]
        swapInfo   = cmdOutputLines[2]

        memoryTotal = int( memoryInfo.split()[1] )
        memoryUsed  = int( memoryInfo.split()[2] )
        memoryUsedPercentage = (float(memoryUsed) / float(memoryTotal)) * 100

        if (memoryUsedPercentage > memoryUsageThreshold):
            memoryStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            memoryStr = ''

        swapTotal = int( swapInfo.split()[1] )
        swapUsed  = int( swapInfo.split()[2] )
        if (swapUsed == 0):
            swapUsedPercentage = 0.0
        else:
            swapUsedPercentage = (float(swapUsed) / float(swapTotal)) * 100

        if (swapUsedPercentage > swapUsageThreshold):
            swapStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            swapStr = ''

        strFormat = '{:<30.30}{:14}{:14}{:15}'
        logger.info('')
        logger.info('Memory Usage:')
        if memoryStr is '':
            logger.info( strFormat.format('  RAM (MB)', 'Total:' + str(memoryTotal), 'Used:' + str(memoryUsed), memoryStr ) )
        else:
            logger.warning( strFormat.format('  RAM (MB)', 'Total:' + str(memoryTotal), 'Used:' + str(memoryUsed), memoryStr ) )
        if swapStr is '':
            logger.info( strFormat.format('  Swap (MB)', 'Total:' + str(swapTotal), 'Used:' + str(swapUsed), swapStr ) )
        else:
            logger.warning( strFormat.format('  Swap (MB)', 'Total:' + str(swapTotal), 'Used:' + str(swapUsed), swapStr ) )

        #
        # Check disk space
        #
        cmd = "df -h | grep -v '/instance'"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
        cmdOutputLines = cmdOutput.split("\r\n")

        firstLine = True
        strFormat = '{:<17.17}{:41}{:15}'
        for line in cmdOutputLines:

            # If line is empty, skip it. 
            if not line:
                continue

            if firstLine:
                logger.info('')
                logger.info('Disk Usage:')
                header = strFormat.format('  Use%', 'Mounted', '')
                logger.info(header)
                firstLine = False
            else:
                elements = line.split()
                user = float(elements[4].translate(None,'%'))
                mount = elements[5]
                
                if (user >= diskUsageThreshold):
                    logger.warning( strFormat.format( '  ' + str(user), mount, '***THRESHOLD REACHED***') )
                    checkPassed = False
                else:
                    logger.info( strFormat.format( '  ' + str(user), mount, '') )

        #
        # Check network states (TIME_WAIT, CLOSE_WAIT & ESTABLISHED)
        #
        cmd = "netstat -ntu"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
        cmdOutputLines = cmdOutput.split("\r\n")

        numEstablished = 0
        numTimeWait = 0
        numCloseWait = 0

        for line in cmdOutputLines:
            if 'ESTABLISHED' in line:
                numEstablished += 1
            if 'TIME_WAIT' in line:
                numTimeWait += 1
            if 'CLOSE_WAIT' in line:
                numCloseWait += 1

        if (numTimeWait >= timeWaitThreshold):
            timeWaitStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            timeWaitStr = ''

        if (numCloseWait >= closeWaitThreshold):
            closeWaitStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            closeWaitStr = ''

        logger.info('')
        logger.info('Network (# connection in each state):')
        strFormat = '{:<30.30}{:<28}{:15}'
        logger.info( strFormat.format( '  ESTABLISHED', numEstablished, '') )
        if timeWaitStr is '':
            logger.info( strFormat.format( '  TIME_WAIT', numTimeWait, timeWaitStr) )
        else:
            logger.warning( strFormat.format( '  TIME_WAIT', numTimeWait, timeWaitStr) )
        if closeWaitStr is '':
            logger.info( strFormat.format( '  CLOSE_WAIT', numCloseWait, closeWaitStr) )
        else:
            logger.warning( strFormat.format( '  CLOSE_WAIT', numCloseWait, closeWaitStr) )


        #
        # Check number of page swaps
        #
        cmd = "vmstat"

        # Run the command on remote host.
        cmdOutput = automated_testing_common.runSshCmd(sysCheckUsr, host, cmd, sysCheckPwd)
        cmdOutputLines = cmdOutput.split("\r\n")[2]
        swapSi = int( cmdOutputLines.split()[6] )
        swapSo = int( cmdOutputLines.split()[7] )

        if (swapSi >= swapSiThreshold):
            swapSiStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            swapSiStr = ''

        if (swapSo >= swapSoThreshold):
            swapSoStr = '***THRESHOLD REACHED***'
            checkPassed = False
        else:
            swapSoStr = ''

        logger.info('')
        logger.info('Swapping:')
        strFormat = '{:<30.30}{:<28}{:15}'
        if swapSiStr is '':
            logger.info( strFormat.format( '  swapped in / sec', swapSi, swapSiStr) )
        else:
            logger.warning( strFormat.format( '  swapped in / sec', swapSi, swapSiStr) )
        if swapSoStr is '':
            logger.info( strFormat.format( '  swapped out / sec', swapSo, swapSoStr) )
        else:
            logger.warning( strFormat.format( '  swapped out / sec', swapSo, swapSoStr) )

    except Exception as e:
        logger.error( str(e) )
        exit(1)

    if not checkPassed:
        exit(1)

    return

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
