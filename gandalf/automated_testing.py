#!/usr/bin/python2

# Copyright 2018 Synchronoss Technologies, Inc. | All Rights Reserved

###############################################################################
#
# automated_testing.py
#
# Python script to provide a framework for executing other python script that
# test functionality of a product (eg. Email Mx).
#
# Detailed version history can be viewed on Bitbucket in the Gandalf Onering  
# repository at https://bitbucket.org/openwave/onering/commits/all
#
###############################################################################

#==============================================================================
# Add local python lib to path
#==============================================================================
import os
import sys
import inspect
from shutil import copyfile

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

libdir = currentdir + "/lib"
sys.path.insert(0, libdir)

#==============================================================================
# Imported python modules
#==============================================================================
import subprocess
import os.path
import xlsxwriter
import argparse
import automated_testing_common
from collections import OrderedDict

#==============================================================================
# createExcelReport(config_for_looping,test_summary)
#
# Parameters:
#   config_for_looping - Python dictionary containing results of each test.
#   test_summary - Python dictionary containing summary of test results.
#
# Purpose:
#   Create report Excel file
#==============================================================================
def createExcelReport(config_for_looping, test_summary):

    test_groups_with_loop_tests = config_for_looping.get('testGroup')

    # Create an new Excel file and add a worksheet.
    workbookFile = './report/automated_testing_report_' + logTimestamp + '.xlsx'
    workbook = xlsxwriter.Workbook(workbookFile)

    # Add formats to use when writing cells (eg. bold, bold with blue background, etc).
    bold = workbook.add_format({'bold': True})
    boldAndBlue = workbook.add_format({'bold': True, 'bg_color': '#DAEEF3'})
    redBackground = workbook.add_format({'bg_color': '#FF0000'})
    orangeBackground = workbook.add_format({'bg_color': '#FFC000'})
    greenBackground = workbook.add_format({'bg_color': '#00FF00'})
    percent_fmt = workbook.add_format({'num_format': '0.00%'})

    # Create summary worksheet
    worksheet = workbook.add_worksheet('Summary')

    # Format columns
    worksheet.set_column('A:A', 20)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 20)
    worksheet.set_column('D:D', 20)
    worksheet.set_column('E:E', 20)
    worksheet.set_column('F:F', 20)

    # Write summary
    worksheet.write('A1', '', boldAndBlue)
    worksheet.write('B1', 'Total test cases', boldAndBlue)
    worksheet.write('C1', 'Test cases skipped', boldAndBlue)
    worksheet.write('D1', 'Test cases run', boldAndBlue)
    worksheet.write('E1', 'Test cases passed', boldAndBlue)
    worksheet.write('F1', 'Test cases failed', boldAndBlue)

    # test_summary[group_name] = {'numTest':0, 'numRun':0, 'numPass':0, 'numFail':0}
    rowCounter = 2
    for group_name, group_summary in test_summary.iteritems():

        numSkipped = group_summary['numTest'] - group_summary['numRun']

        worksheet.write('A' + str(rowCounter), group_name, bold)
        worksheet.write('B' + str(rowCounter), group_summary['numTest'])
        worksheet.write('C' + str(rowCounter), numSkipped)
        worksheet.write('D' + str(rowCounter), group_summary['numRun'])
        worksheet.write('E' + str(rowCounter), group_summary['numPass'])
        worksheet.write('F' + str(rowCounter), group_summary['numFail'])
        rowCounter += 1

    # Write a "Tolal" line.
    worksheet.write('A' + str(rowCounter), "Total", bold)
    worksheet.write('B' + str(rowCounter), "=SUM(B2:B" + str(rowCounter-1) + ")", bold)
    worksheet.write('C' + str(rowCounter), "=SUM(C2:C" + str(rowCounter-1) + ")", bold)
    worksheet.write('D' + str(rowCounter), "=SUM(D2:D" + str(rowCounter-1) + ")", bold)
    worksheet.write('E' + str(rowCounter), "=SUM(E2:E" + str(rowCounter-1) + ")", bold)
    worksheet.write('F' + str(rowCounter), "=SUM(F2:F" + str(rowCounter-1) + ")", bold)

    # Write a "Percentage" line.
    rowCounter += 2
    worksheet.write('A' + str(rowCounter), "Percentage Passed", boldAndBlue)
    worksheet.write('B' + str(rowCounter), "=(E" + str(rowCounter-2) + "/D" + str(rowCounter-2) + ")", percent_fmt)

    # Create worksheet for each group of tests.
    for group_name, group_tests in test_groups_with_loop_tests.iteritems():

        # Create test results worksheet for this group.
        worksheet = workbook.add_worksheet(group_name)

        # Write column headings and set widths
        worksheet.write('A1', 'Test Case Script', boldAndBlue)
        worksheet.set_column('A:A', 20)
        worksheet.write('B1', 'Host', boldAndBlue)
        worksheet.set_column('B:B', 20)
        worksheet.write('C1', 'Description', boldAndBlue)
        worksheet.set_column('C:C', 20)
        worksheet.write('D1', 'Execute Test? (y/n)', boldAndBlue)
        worksheet.set_column('D:D', 20)
        worksheet.write('E1', 'Test Status', boldAndBlue)
        worksheet.set_column('E:E', 20)
        worksheet.write('F1', 'Test Result', boldAndBlue)
        worksheet.set_column('F:F', 20)
        worksheet.write('G1', 'Timestamp', boldAndBlue)
        worksheet.set_column('G:G', 20)

        date_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss', 'align': 'left'})

        # Loop through tests and add results to Excel file
        rowCounter = 1
        for sub_script_name, sub_script_attr in group_tests.iteritems():

            # Write with row/column notation.
            script_name = sub_script_name.split()
            if len(script_name) > 1:
                worksheet.write(rowCounter, 0, script_name[0])
                worksheet.write(rowCounter, 1, script_name[1])
            else:
                worksheet.write(rowCounter, 0, script_name[0])
                worksheet.write(rowCounter, 1, 'N/A')
            worksheet.write(rowCounter, 2, sub_script_attr.get('description'))
            worksheet.write(rowCounter, 3, sub_script_attr.get('run'))
            worksheet.write(rowCounter, 4, sub_script_attr.get('status'))
            if ( sub_script_attr.get('result') == 'Pass'):
                worksheet.write(rowCounter, 5, sub_script_attr.get('result'), greenBackground)
            elif ( sub_script_attr.get('result') == 'N/A'):
                worksheet.write(rowCounter, 5, sub_script_attr.get('result'), orangeBackground)
            else:
                worksheet.write(rowCounter, 5, sub_script_attr.get('result'), redBackground)
            worksheet.write(rowCounter, 6, sub_script_attr.get('timestamp'))

            # Increament row counter
            rowCounter += 1

    # Close Excel file.
    workbook.close()

    # Write log event to inform user where to get Excel file from.
    print
    logger.info("Excel test report created: " + workbookFile)

    return

#==============================================================================
# writeSummary(test_summary)
#
# Parameters:
#   test_summary - Python dictionary containing summary of test results.
#
# Purpose:
#   Write summary of tests to logger.
#==============================================================================
def writeSummary(test_summary):

    # Define padding / truncation for data being displayed.
    strFormat = '{:<15.15}{:15}{:15}{:15}{:15}{:15}'

    # Format and print a header for the summary.
    print
    logger.info("Summary of test results...")
    header = strFormat.format('Test Group', '# Tests', '# Skipped', '# Tests Run', '# Passed', '# Failed')
    logger.info(header)

    # Loop through each group and print out a summary for that group.
    for group_name, group_summary in test_summary.iteritems():
        numSkipped = group_summary['numTest'] - group_summary['numRun']
        row = strFormat.format(
            str(group_name), str(group_summary['numTest']), str(numSkipped), str(group_summary['numRun']), str(group_summary['numPass']), str(group_summary['numFail']))
        logger.info(row)

#==============================================================================
# writeResults(config_for_looping,test_summary)
#
# Parameters:
#   config_for_looping - Python dictionary containing results of each test.
#   test_summary - Python dictionary containing summary of test results.
#
# Purpose:
#   Write results of tests to logger.
#==============================================================================
def writeResults(config_for_looping, test_summary):

    test_groups_with_loop_tests = config_for_looping.get('testGroup')

    # Define padding / truncation for data being displayed.
    strFormat = '{:<15.15}{:<30.30}{:<20.20}{:<20.20}{:<45.45}'

    # Print a header for the results.
    print
    logger.info("Detail of test results...")
    header = strFormat.format('Test Group', 'Test Case Script', 'Host', 'Test Result', 'Description')
    logger.info(header)

    # Loop through each group and print out a summary for that group.
    for group_name, group_tests in test_groups_with_loop_tests.iteritems():

        row = '{:<30.30}'.format(group_name)
        logger.info(row)

        for sub_script_name, sub_script_attr in group_tests.iteritems():
            res = sub_script_attr.get('result')
            desc = sub_script_attr.get('description').rstrip()
            script_name = sub_script_name.split()
            if len(script_name) > 1:
                row = strFormat.format('', script_name[0], script_name[1], res, desc)
            else:
                row = strFormat.format('', script_name[0], 'N/A', res, desc)
            logger.info(row)


#==============================================================================
# getHostInLoop(hostLoopStr,hostsInConfig)
#
# Parameters:
#   hostLoopStr   - Loop hosts string from the common.yml for this test.
#                   This string can be in the format of:
#                     hostType(1,3)   - Loop through 1st and 3rd host of that type.
#                     hostType(all)   - Loop through all hosts of that type.
#   hostsInConfig - Python dictionary containing hosts from common.yml
#
# Returns:
#   List of host IPs and/or hostnames needed for test loop.
#
# Purpose:
#   From the loop hosts string get a list of hostnames / IPs for host looping.
#==============================================================================
def getHostInLoop(hostLoopStr, hostsInConfig):

    # Save orig string for log events, if needed.
    hostLoopStrOrig = hostLoopStr

    # Remove all whitespace from the string.
    hostLoopStr = ''.join(hostLoopStr.split())

    # Remove '(' and ')' from string (replace '(' with space).
    # This will change string from something like 'hostType(1,3)' to 'hostType 1,3'
    hostLoopStr = hostLoopStr.replace('(', ' ')
    hostLoopStr = hostLoopStr.replace(')', '')

    # Now split string on space to get the host type and the host type list.
    hostLoopElements = hostLoopStr.split()

    # hostLoopElements should have 2 element
    if len(hostLoopElements) != 2:
        logger.warn("Mal-formatted loop config data: " + hostLoopStrOrig)
        return

    hostType = hostLoopElements[0]
    hostList = hostLoopElements[1].split(',')

    # hostList should only contain the word 'all' or a list a integers.
    if hostList[0] == 'all' and len(hostList) != 1:
        logger.critical("Mal-formatted loop config data: " + hostLoopStrOrig)
        exit(1)

    # If hostList[0] is not 'all', item in the list should be a whole number as a string .
    # Map number in string form to int form.
    if hostList[0] != 'all':
        try:
            hostList = map(int, hostList)
        except:
            logger.critical("Mal-formatted loop config data: " + hostLoopStrOrig)
            exit(1)

    # If the host in hostType does not appear in hostsInConfig, exit, as there
    # is a misconfiguration.
    if hostType not in hostsInConfig:
        logger.critical("Mal-formatted loop config data or missing host type in config. Loop string is: " + hostLoopStrOrig)
        exit(1)
    else:
        try:
            listOfHostIPs = hostsInConfig[hostType].split()
        except:
            logger.critical("Missing IPs or hostname in the 'hosts' section for '" + hostType + "' needed for loop. Loop string is: " + hostLoopStrOrig)
            exit(1)

    # Build list of only IPs or hostnames required.
    subListOfHostIPs = []
    if hostList[0] == 'all':
        # Set subListOfHostIPs to have all IPs or hostnames.
        subListOfHostIPs = listOfHostIPs
    else:
        for element in hostList:

            # Check the element is in range for listOfHostIPs before adding it to the subListOfHostIPs.
            if len(listOfHostIPs) >= element and element > 0:
                subListOfHostIPs.append(listOfHostIPs[element-1])
            else:
                logger.critical("List out of range. May not be enough IPs or hostname in the 'hosts' section for '" +
                    hostType + "' needed for loop. Loop string is: " + hostLoopStrOrig)
                exit(1)

    logger.debug("For loop config string, " + hostLoopStrOrig + ", here is the list of IPs or hostname: " + str(subListOfHostIPs))
    return subListOfHostIPs

#==============================================================================
# replaceEnterInOrdererDict(orderded_dict,newTestDict,keyToReplace)
#
# Parameters:
#   orderded_dict - Ordered dict where an entry needs replacing.
#   newTestDict - Dict structure to replace part of the original orderded_dict.
#   keyToReplace - Key of the orderded_dict to be replaced.
#
# Return:
#   There is no return parameter, but orderded_dict is updated with new structure.
#
# Purpose:
#   To replace put of an OrdererDict with another data strucure.
#==============================================================================

def replaceEnterInOrdererDict(orderded_dict, newTestDict, keyToReplace):

    new_orderded_dict=orderded_dict.__class__()

    for key, value in orderded_dict.items():
        if key==keyToReplace:

            for newKey, newValue in newTestDict.items():
                new_orderded_dict[newKey]=newValue

        else:
            new_orderded_dict[key]=value

    orderded_dict.clear()
    orderded_dict.update(new_orderded_dict)

#==============================================================================
# buildDictForLoop(rootKey,rootValue,loopList)
#
# Parameters:
#   rootKey - String to but used as a root for the new key.
#   rootValue - Data structure to be used as a root for the new value.
#   loopList - List of loop info.
#
# Return:
#   Dictionary structure containing a key/value pair for each item in the loopList.
#   Each key/value pair as based on the rootKey/rootValue.
#
# Purpose:
#   To build a dictionary, using rootKey/rootValue as a template key/value pair
#   and modifying it based on loopList. There will be one dictionary key/value pair
#   for each item in the loopList.
#==============================================================================

def buildDictForLoop(rootKey, rootValue, loopList):

    logger.debug("rootKey: " + str(rootKey))
    logger.debug("rootValue: " + str(rootValue))
    logger.debug("loopList: " + str(loopList))

    builtDict = OrderedDict()

    for thisLoopInfo in loopList:
        newKey = str(rootKey) + " " + str(thisLoopInfo)

        copyRootValue = {}
        copyRootValue['run'] = rootValue['run']
        copyRootValue['config'] = rootValue['config']
        copyRootValue['host'] = thisLoopInfo

        builtDict[newKey] = copyRootValue

    return builtDict

#==============================================================================
# expandForLoops(config_for_looping,config)
#
# Parameters:
#   config_for_looping - Python dict that will be expanded to contain loop and un-loop test cases.
#   config             - Python dict containing original config.
#
# Return:
#   No return value, but 'config_for_looping' is updated with the additional tests for loops.
#
# Purpose:
#   To expand Python dict, 'config_for_looping', to hold all test cases (loop and un-loop).
#==============================================================================

def expandForLoops(config_for_looping, config):

    test_groups_with_loop_tests = config_for_looping.get('testGroup')
    test_groups                 = config.get('testGroup')

    ############################################
    # Interate through all the test groups (eg. pop, imap)
    ############################################

    for group_name, group_tests in test_groups.iteritems():

        ############################################
        # Interate through all test scripts in a test groups
        ############################################

        for script_name, script_attr in group_tests.iteritems():

            ############################################
            # Check if this test script has a non-empty 'hosts' config entry
            # (ie. check if it to be run against multiple hosts).
            ############################################

            if 'hosts' in script_attr and script_attr['hosts'] and script_attr['hosts'] != '':

                ############################################
                # Convert test script hosts string ( eg. 'pop(all)') into
                # an actual list of hostnames / IPs (eg. 10.123.22.01, 10.123.22.02, 10.123.22.03)
                ############################################

                # Get hosts string for this test script. The string
                # may be something like 'pop(all)'.
                script_hosts = script_attr.get('hosts')

                # Get all hosts types and hostnames / IP from config.
                hostsInConfig = config.get('hosts')

                # Convert test script hosts string into actual list of hostnames / IPs.
                listOfHostIPs = getHostInLoop(script_hosts, hostsInConfig)

                ############################################
                # Create a new Python dict containing template data
                # for creating each iteration of the looping test script.
                ############################################

                newRootValue = OrderedDict()
                newRootValue['run'] = script_attr['run']
                newRootValue['config'] = script_attr['config']

                ############################################
                # For this test script which has looping, build an
                # expended Python dict with enteries for each host to be looped through.
                ############################################

                newTestDict = buildDictForLoop(script_name, newRootValue, listOfHostIPs)

                ############################################
                # Replace the newly build Python dict (containing with enteries for
                # each host to be looped through) with the orig Python dict.
                ############################################

                group_tests_with_loop_tests = test_groups_with_loop_tests[group_name]
                replaceEnterInOrdererDict(group_tests_with_loop_tests, newTestDict, script_name)

#==============================================================================
# addKeysForTestResults(config_for_looping,test_summary)
#
# Parameters:
#   config_for_looping - Python dict that will be expanded to contain place holder keys for test results.
#   test_summary - Python dict for test summary data.
#
# Return:
#   No return value, but 'config_for_looping' is updated with place holder keys for test results and
#   'test_summary' is initialized.
#
# Purpose:
#   Add place holder keys to Python dict for test results info and initialized test summary.
#==============================================================================
def addKeysForTestResults(config_for_looping, test_summary):

    test_groups = config_for_looping.get('testGroup')

    ############################################
    # Interate through all the test groups (eg. pop, imap)
    ############################################

    for group_name, group_tests in test_groups.iteritems():

        ############################################
        # Initialize test summary counters
        ############################################

        test_summary[group_name] = {'numTest':0, 'numRun':0, 'numPass':0, 'numFail':0}

        ############################################
        # Interate through all test scripts in a test groups
        ############################################

        for script_name, script_attr in group_tests.iteritems():

            ############################################
            # Add new key / value pairs for each test script
            # that will be used to track the status of that test.
            ############################################

            script_attr['status'] = 'Not run'
            script_attr['result'] = 'N/A'
            script_attr['timestamp'] = 'N/A'

            # Normally the script_name would be something like 'test.py', but if this is a loop
            # test this will be something like 'test.py 111.222.333.444'. So need to split on whitespace
            # and use first part for the actual script in all cases.
            script_name = script_name.split()
            try:
                process = subprocess.Popen(["./" + group_name + "/" + script_name[0], "--description"], stdout=subprocess.PIPE, stderr=None)
                stdout, stderr = process.communicate()
                script_attr['description'] = stdout
            except OSError:
                logger.critical("Test script in common.yml does not exist or is not executable: " + script_name[0])
                exit(1)

#==============================================================================
# executeTests(config_for_looping,test_summary)
#
# Parameters:
#   config_for_looping - Python dict that contains details about all tests to be run
#   test_summary - Python dict for test summary data.
#
# Return:
#   No return value, but 'config_for_looping' and 'test_summary' will be updated with
#   info about if each test case was run successfully.
#
# Purpose:
#   To execute test cases and record if each test was successfully.
#==============================================================================
def executeTests(config_for_looping, test_summary):

    ############################################
    # Interate through all the test groups (eg. pop, imap)
    ############################################

    test_groups_with_loop_tests = config_for_looping.get('testGroup')
    for group_name, group_tests in test_groups_with_loop_tests.iteritems():

        ############################################
        # Interate through all test scripts in a test groups
        ############################################

        for script_name, script_attr in group_tests.iteritems():

            script_run = script_attr.get('run')
            test_summary[group_name]['numTest'] = test_summary[group_name]['numTest'] + 1

            ############################################
            # If the config file says to run the test, (script_run == "y"), and
            # the command line groups matches this group, ( (args.group == "all") or (group_name in args.group)),
            # then run this test script.
            ############################################

            if (script_run == "y") and ( (args.group == "all") or (group_name in args.group)):

                # Only log this line to wrapper log file, as the test case scripts already log a similar line to screen.
                loggerFileOnly.info("--- TEST GROUP : " + group_name + ", TEST CASE : " + script_name)

                # Increament number of tests were run in this group.
                test_summary[group_name]['numRun'] = test_summary[group_name]['numRun'] + 1

                # Get timestamp for what time was run.
                script_attr['timestamp'] = automated_testing_common.getTimestampFmt1()

                # Build path for test scripts log file. One log file is used for all test scripts in a test group.
                logFile = "./log/" + group_name + "_" + logTimestamp + ".log"

                ############################################
                # Execute the test script, this can be done with or without the --host switch.
                #
                # 'script_name' will be used be determine if --host switch is needed.
                # At this point, 'script_name' could be something like:
                #   'popTest.py'               - For test script that IS NOT looping through hosts.
                #   'popTest.py 10.55.123.2'   - For test script that IS looping through hosts.
                ############################################

                script_name_list = script_name.split()

                if len(script_name_list) > 1:
                    # Execute test script with --host switch
                    res = subprocess.call(["./" + group_name + "/" + script_name_list[0],
                        "--config", script_attr.get('config'), "--log", logFile,
                        "--loglevel", args.loglevel, "--host", script_name_list[1] ])
                else:
                    # Execute test script without --host switch
                    res = subprocess.call(["./" + group_name + "/" + script_name_list[0],
                        "--config", script_attr.get('config'), "--log", logFile,
                        "--loglevel", args.loglevel ])

                ############################################
                # Check test result and update status.
                ############################################

                if res != 0:
                    if res < 0:
                        script_attr['status'] = 'Run'
                        script_attr['result'] = 'Killed by signal : ' + str(res)
                        test_summary[group_name]['numFail'] = test_summary[group_name]['numFail'] + 1
                    else:
                        script_attr['status'] = 'Run'
                        script_attr['result'] = 'Error code : ' + str(res)
                        test_summary[group_name]['numFail'] = test_summary[group_name]['numFail'] + 1

                else:
                    script_attr['status'] = 'Run'
                    script_attr['result'] = 'Pass'
                    test_summary[group_name]['numPass'] = test_summary[group_name]['numPass'] + 1

            ############################################
            # If test script is not to be run, just log a SKIPPED log event.
            ############################################

            else:
                logger.info("--- TEST GROUP : " + group_name + ", TEST CASE : " + script_name + " - SKIPPED")


#==============================================================================
# createDir(dir)
#
# Parameters:
#   dir - Directory to be created, if it doesn't exist
#
# Return:
#   None
#
# Purpose:
#   To create a directory, if it does not already exist. If it can't create the
#   directory, the script will exit.
#==============================================================================
def createDir(dir):

    if not os.path.exists(dir):
        try:
            os.makedirs(dir)
        except:
            print("Failed to create " + dir)
            exit(0)
    elif not os.path.isdir(dir):
        print("The script logs under the " + dir + " directory and needs to exist.")
        print("Currently, there is a file, " + dir + ", that is provently the directory from being created.")
        exit(0)

#==============================================================================
# removeGroups(config)
#
# Parameters:
#   config - Ordered dict of config containing 'testGroup'
#
# Purpose:
#   Take 'config' and make a copy but exclude any test groups that were
#   not specified to run.
#==============================================================================
def removeGroups(config):

    new_config = config.__class__()

    # Loop through key / value pairs in config.
    for key, value in config.iteritems():

        # If this key if 'testGroup' only copy if all groups
        # are to be run OR the group was specified to run.
        if key == 'testGroup':

            test_groups = value
            new_test_groups = config.__class__()

            for group_name, group_tests in test_groups.iteritems():

                if (args.group == "all") or (group_name in args.group):
                    new_test_groups[group_name] = group_tests

            new_config[key] = new_test_groups 

        # For all other key copy the key/value pair.
        else:

            new_config[key] = value

    return(new_config)

#==============================================================================
# Main
#==============================================================================

############################################
# Set up command line switches for script
############################################

parser = argparse.ArgumentParser(description="Wrapper script to automate running and reporting of functional tests. The script will run" +
    " tests detailed in the config file, common.yml.")
parser.add_argument("group", nargs='*', default="all", help="List of one or more test groups to run. If omitted, all groups will be run.")
parser.add_argument("--loglevel", default="INFO", help="Log level ( ERROR | WARNING | INFO | DEBUG). Default is INFO.")
args = parser.parse_args()

# Do if script was executed (and not just imported)

if __name__ == "__main__":

    # Create ./log and ./report directories if they doesn't exist.

    createDir("./log")
    createDir("./report")

    ############################################
    # Create loggers for this script.
    # More of the time, we want to log to file and screen, for this 'logger' will be set up.
    # For only logging to file, 'loggerFileOnly' will be set up.
    ############################################

    logger = automated_testing_common.createLogger('main', args.loglevel)
    loggerFileOnly = automated_testing_common.createLogger('mainFileOnly', args.loglevel)

    # Add file log handler to logger.

    logTimestamp = automated_testing_common.getTimestampFmt2()
    name = "automated_testing"
    logFile = "./log/" + name + "_" + logTimestamp + ".log"
    automated_testing_common.addFileToLogger(logFile, logger)
    automated_testing_common.addFileToLogger(logFile, loggerFileOnly)

    # Add screen log handler to logger with format for this wrapping script.
    format = 'WRAPPER %(levelname).4s :\t%(message)s'
    automated_testing_common.addConsoleWithFormatToLogger(logger, format)

    # For nicely readable output.
    print

    ############################################
    # Make a working copy of config file
    ############################################

    config_file_path = "common.yml"
    working_copy_config_file_path = ".common.yml." + str(os.getpid())
    copyfile(config_file_path, working_copy_config_file_path)

    ############################################
    # Read main config file
    #
    # Take two copies of the config.
    # 'config' will be the exact config (and should never be modified).
    # 'config_for_looping' will be a working version of the config, that is expanded for loops.
    ############################################

    config             = automated_testing_common.yamlLoader(logger, config_file_path)
    config_for_looping = automated_testing_common.yamlLoader(logger, config_file_path)

    ############################################
    # Remove any groups not run.
    ############################################

    config             = removeGroups(config)
    config_for_looping = removeGroups(config_for_looping)

    ############################################
    # Take 'config_for_looping' (so far unmodified) and expand it to have
    # one entry for each interation of a loop.
    #
    # Eg. In common.yml we may have something like:
    #
    # testGroup:
    #    pop:
    #        popTest.py:
    #            run: y
    #            config: pop.yml
    #            hosts: pop(all)
    #
    # So for the test, popTest.py, we need to run against all POP hosts ( hosts: pop(all)).
    # Currently, 'config_for_looping' has one entry for test, popTest.py.
    # Now expand 'config_for_looping' to have one entry for host definded by pop(all).
    ############################################

    # Expend 'config_for_looping' for all loops.
    expandForLoops(config_for_looping, config)

    ############################################
    # Create an ordered dictionary to hold a summary of test data.
    ############################################

    # Create an ordered dictionary to hold a summary of test data.
    test_summary = OrderedDict()

    ############################################
    # Add place holder keys to 'config_for_looping' for test results info
    # and initialize 'test_summary' data structure.
    ############################################

    addKeysForTestResults(config_for_looping, test_summary)

    ############################################
    # Execute the tests in the main config file
    ############################################

    logger.info("Start running test cases")
    executeTests(config_for_looping, test_summary)
    logger.info("Finish running test cases")

    ############################################
    # Write test summary to screen and create report
    ############################################

    # Log summary of tests.
    writeResults(config_for_looping, test_summary)

    # Log summary of tests.
    writeSummary(test_summary)

    # Output report to Excel file
    createExcelReport(config_for_looping, test_summary)

    # For nicely readable output.
    print

    # Delete working copy of config file
    os.remove(working_copy_config_file_path)

