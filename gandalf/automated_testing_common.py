#!/usr/bin/python2

# Copyright 2018 Synchronoss Technologies, Inc. | All Rights Reserved

###############################################################################
#
# automated_testing_common.py
#
# Module contains a set of common functions that can be used by other .py scripts
# for developing test script.
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
from random import randint

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

libdir = currentdir + "/lib"
sys.path.insert(0, libdir)

#==============================================================================
# Imported python modules
#==============================================================================
import os.path
import logging
import time
import datetime
import base64

# For Imap, Smtp and Pop classes
import imaplib
import smtplib
import poplib

# For handling email messages.
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

# ruamel.yaml is used so the order in the yaml files is kept.
from ruamel.yaml import YAML

# For Mxos class
import requests
import json

# For remote ssh commands (that use expect)
import pexpect

#==============================================================================
# runSshCmd()
#
# Parameters:
#   user       - The user to run remote command as.
#   host       - Host to run the command on.
#   cmd        - The command to be run.
#   pwd        - Password of user account.
#   
# Purpose:
#   To run a command on a remote host and return the output of the command.
#==============================================================================
def runSshCmd(user, host, cmd, pwd):

    import pexpect

    ssh_newkey = '(yes/no)\? '
    ssh_pwdprompt = 'Password:'

    p = pexpect.spawn('ssh -q ' + user + '@' + host + ' ' + cmd)

    r = p.expect([ssh_newkey, ssh_pwdprompt, pexpect.EOF])
    if r == 0:
        p.sendline('yes')
        r = p.expect([ssh_newkey, ssh_pwdprompt, pexpect.EOF])
    if r == 1:
        p.sendline(pwd)
        p.expect(pexpect.EOF)
    elif r == 2:
        pass

    # If password was entered, the return string has ' \r\n' that needs to be removed.
    if p.before.startswith(' \r\n'):
        output = p.before.replace(' \r\n','')
    else:
        output = p.before

    return output

#==============================================================================
# getTimestampFmt1()
#
# Parameters:
#   None
#
# Purpose:
#   Get timestamp with format: %Y-%m-%d %H:%M:%S. Eg. 2018-02-06 12:17:32
#==============================================================================
def getTimestampFmt1():
    timeNow = time.time()
    formattedTimeNow = datetime.datetime.fromtimestamp(timeNow).strftime('%Y-%m-%d %H:%M:%S')
    return formattedTimeNow

#==============================================================================
# getTimestampFmt2()
#
# Parameters:
#   None
#
# Purpose:
#   Get timestamp with format: %Y%m%d%H%M, Eg. 201802061217
#==============================================================================
def getTimestampFmt2():
    timeNow = time.time()
    formattedTimeNow = datetime.datetime.fromtimestamp(timeNow).strftime('%Y%m%d%H%M')
    return formattedTimeNow

#==============================================================================
# sleep(sleepInSec)
#
# Parameters:
#   sleepInSec - Amount of time to sleep.
#   logger     - Logger used to log events to.
#
# Purpose:
#   To pause the test script for 'sleepInSec' seconds.
#==============================================================================
def sleep(sleepInSec, logger):
    logger.info("Sleep : " + str(sleepInSec) + " sec")
    time.sleep(sleepInSec)

#==============================================================================
# yamlLoader(logger, filepath)
#
# Parameters:
#   logger - logger for logging log events.
#   filepath - file path of the yaml config file.
#
# Purpose:
#   Read yaml file and return data in a ordered dictionary
#==============================================================================
def yamlLoader(logger, filepath):
    yaml = YAML()
    if os.path.isfile(filepath):
        with open(filepath, "r") as stream:
            data = yaml.load(stream)
    else:
        logger.critical("Config file does not exist: " + filepath)
        exit(1)
    logger.debug("Config : \n" + str(data))
    return data

#==============================================================================
# createLogger(loggerName, logLevel)
#
# Parameters:
#   loggerName - Label for this logger.
#   logLevel - Log level, can be ERROR | WARNING | INFO | DEBUG
#
# Purpose:
#   Create logger for logging log events.
#==============================================================================
def createLogger(loggerName, logLevel):

    logger = logging.getLogger(loggerName)

    if logLevel == 'ERROR':
        logger.setLevel(logging.ERROR)
    elif logLevel == 'WARNING':
        logger.setLevel(logging.WARNING)
    elif logLevel == 'INFO':
        logger.setLevel(logging.INFO)
    elif logLevel == 'DEBUG':
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    return logger

#==============================================================================
# addFileToLogger(logFilePath, logger)
# addFileAndHostToLogger(logFilePath, host, logger)
#
# Parameters:
#   logFilePath - Add log handler to this log file.
#   logger - Logger that log handler will be added to.
#   host - Hostname or IP string that will be written into the log event.
#
# Purpose:
#   Add log handler for log file to the logger and to log the hostname on each log event.
#==============================================================================
def addFileToLogger(logFilePath, logger):
    addFileAndHostToLogger(logFilePath, 'N/A', logger)

def addFileAndHostToLogger(logFilePath, host, logger):
    hdlr = logging.FileHandler(logFilePath)
    formatedHost = host.ljust(12)
    formatter = logging.Formatter('%(asctime)s %(levelname).4s ' + formatedHost + ' :\t%(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

#==============================================================================
# addConsoleToLogger(logger)
#
# Parameters:
#   logger - Logger that log handler for logging to the screen.
#
# Purpose:
#   Add log handler for logging to screen.
#==============================================================================
def addConsoleToLogger(logger):
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname).4s :\t%(message)s')
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

#==============================================================================
# addConsoleWithFormatToLogger(logger, format)
#
# Parameters:
#   logger - Logger that log handler for logging to the screen.
#   format - Formating string
#
# Purpose:
#   Add log handler for logging to screen with a given format.
#==============================================================================
def addConsoleWithFormatToLogger(logger, format):
    consoleHandler = logging.StreamHandler()
    formatter = logging.Formatter(format)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

#==============================================================================
# CLASS: Account
#==============================================================================

class Account():

    def __init__(self, **kwargs):
        # Build account attribute from keyword pairs passed in (whick are orig from 
        # the attr in the 'testAccounts' section of common.yml file).
        # Then update username to randomize it.
        self.__dict__.update(kwargs)
        self.username = self.username + '-' + str(randint(0, 99999999))

    def getFullQualifiedName(self):
        return self.username + '@' + self.domain

    def getPassword(self):
        return self.password

    # Method to build dir of attributes that can be used in mOS account creation.
    def getAttrForCreationMxAccount(self):
        attrDict = {}
        for attr in dir(self):

            # Getting rid of dunder methods
            if not attr.startswith("__"):
                value = getattr(self, attr)

                # Getting rid of methods, username & domain attribute.
                if 'method' not in str(value) and 'username' != attr.lower() and 'domain' != attr.lower():
                    attrDict[attr] = value
        return attrDict

#==============================================================================
# CLASS: Message
#==============================================================================
# Message class in inherited from MIMEMultipart.
class Message(MIMEMultipart):

    def __init__(self, From, To, subject, bodyText):
        MIMEMultipart.__init__(self)
        self['From'] = From
        if type(To) is list:
            self['To'] = ', '.join(To)
        elif type(To) is str:
            self['To'] = To
        self['Subject'] = subject
        self.attach(MIMEText(bodyText, 'plain'))

    def addCc(self, Cc):
        if type(Cc) is list:
            self['Cc'] = ', '.join(Cc)
        elif type(Cc) is str:
            self['Cc'] = Cc

    def addBcc(self, Bcc):
        if type(Bcc) is list:
            self['Bcc'] = ', '.join(Bcc)
        elif type(Bcc) is str:
            self['Bcc'] = Bcc

    def addAttachment(self, filePath):
        part = MIMEBase('application', "octet-stream")
        part.set_payload(open(filePath, "rb").read())
        Encoders.encode_base64(part)
        if os.path.exists(filePath):
            part.add_header('Content-Disposition', 'attachment; filename=' + filePath)
            self.attach(part)
        else:
            raise Exception("Failed attaching file to message. File doesn't exist: " + filePath)

#==============================================================================
# CLASS: Smtp
#==============================================================================

class Smtp():

    def __init__(self, logger, host, port, useSsl, verifyCert=False):
        self.logger = logger
        self.host = host
        self.port = port
        self.useSsl = useSsl
        self.verifyCert = verifyCert
        self.smtpObj = ''

    def __str__(self):
        return ("host : " + self.host + ", port : " + str(self.port) +
                ", useSsl : " + str(self.useSsl) +
                ", verifyCert : " + str(self.verifyCert))

    def sendMessage(self, message, account):

        # Connect to SMTP server.
        self.logger.info("- Connect to MTA")
        #self.logger.info("self.host=" + self.host)
        #self.logger.info("self.port=" + self.port)
        try:
            #self.smtpObj = smtplib.SMTP(self.host, self.port)
            #self.smtpObj = smtplib.SMTP_SSL('nsdu2fep02t')

            if self.useSsl:
                self.logger.info("- Make encrypted connection to SMTP server")
                self.smtpObj = smtplib.SMTP_SSL(self.host, self.port)
                #self.smtpObj.set_debuglevel(1)
                #self.smtpObj.starttls()
                #self.smtpObj.login(account.getFullQualifiedName(),account.getPassword())
            else:
                self.logger.info("- Make unencrypted connection to SMTP server")
                self.smtpObj = smtplib.SMTP(self.host, self.port)

        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to make SMTP connection.')

        # Send message.
        self.logger.info("- Send message : TO " + message['To'] + 
                         ", FROM " + message['From'] + 
                         ", SUBJ " + message['Subject'])
        try:
            self.smtpObj.sendmail(message['From'], message['To'], message.as_string())
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            self.smtpObj.quit()
            raise Exception('Failed to send message.')
        else:
            self.logger.info("  Result -> PASS")
            self.smtpObj.quit()

    def sendMultipleMessage(self, messageTemplate, account, numToSend):

        origSubject = messageTemplate['Subject']
        for i in range(numToSend):

            # Replace subject line in message.
            messageTemplate.replace_header('Subject', origSubject + ' ' + str(i+1) + ' of ' + str(numToSend))

            # send newly build message
            self.sendMessage(messageTemplate, account)

#==============================================================================
# CLASS: Mxos
#==============================================================================

class Mxos():

    def __init__(self, logger, host, port, useSsl, verifyCert=False):
        self.logger = logger
        self.host = host
        self.port = port
        self.useSsl = useSsl
        self.verifyCert = verifyCert
        self.response = ''

    def __str__(self):
        return ("host : " + self.host + ", port : " + str(self.port) +
                ", useSsl : " + str(self.useSsl) +
                ", verifyCert : " + str(self.verifyCert))

    def wasRequestSuccessful(self):
        return self.response.status_code == requests.codes.ok

    def getResponseCode(self):
        return self.response.status_code

    def getResponseText(self):
        return str(self.response.text)

    def getAccountStatus(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- MxOS Get account status : " + fullQualifiedName)

        if self.useSsl:
            self.response = requests.get("https://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/base",
                                         verify=self.verifyCert)
        else:
            self.response = requests.get("http://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/base")

        # Try to load the response as a JSON string
        try:
            info = json.loads(str(self.response.text))

            if 'status' in info: 
                self.logger.info("  Account status : " + info['status'])
            elif 'shortMessage' in info:
                self.logger.info("  Account status : " + info['shortMessage'])

        # If response is not in JSON format.
        except:
             self.logger.info("  Account status : An unexpected error occurred.")

    def getAccountBase(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        if self.useSsl:
            self.response = requests.get("https://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/base",
                                         verify=self.verifyCert)
        else:
            self.response = requests.get("http://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/base")

        self.displayResponse()

    def getAccountCredentials(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        if self.useSsl:
            self.response = requests.get("https://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/credentials",
                                         verify=self.verifyCert)
        else:
            self.response = requests.get("http://" + self.host + ":" + self.port +
                                         "/mxos/mailbox/v2/" + fullQualifiedName + "/credentials")

        self.displayResponse()

    def isAccountProvisioned(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        # Try to get base info for account.
        try:
            if self.useSsl:
                response = requests.get("https://" + self.host + ":" + self.port +
                                        "/mxos/mailbox/v2/" + fullQualifiedName + "/credentials",
                                        verify=self.verifyCert)
            else:
                response = requests.get("http://" + self.host + ":" + self.port +
                                        "/mxos/mailbox/v2/" + fullQualifiedName + "/credentials")

        # If there is an exception, return False.
        except:
            return False

        # If no exception, return True or False based on the status_code.
        return response.status_code == requests.codes.ok

    def createAccount(self, account):

        fullQualifiedName = account.getFullQualifiedName()
        data = account.getAttrForCreationMxAccount()

        self.logger.info("- MxOS Create account : " + fullQualifiedName)
        if not self.isAccountProvisioned(account):

            # Try to create the account
            try:
                if self.useSsl:
                    self.response = requests.put("https://" + self.host + ":" + self.port +
                                                 "/mxos/mailbox/v2/" + fullQualifiedName,
                                                 data,
                                                 verify=self.verifyCert)
                else:
                    self.response = requests.put("http://" + self.host + ":" + self.port +
                                                 "/mxos/mailbox/v2/" + fullQualifiedName,
                                                 data)

            # If unexpected exception, catch it and fail gratefully.
            # This could happen if MxOS dies.
            except Exception as e:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR: " + str(e))
                self.logger.info('  MxOS ERROR: Failed to connect to MxOS (' + self.host + ')')
                raise Exception('Failed to connect to MxOS')

            if self.response.status_code == requests.codes.ok:
                self.logger.info("  Result -> PASS")
            else:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
                self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
                self.logger.info('  MxOS ERROR: Failed to create account (' + fullQualifiedName + ') via MxOS (' + self.host + ')')
                raise Exception('Failed to create account')

        else:
            self.logger.info("  Result -> SKIP")

    def deleteAccount(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        pabcal = {}

        self.logger.info("- MxOS Delete account : " + fullQualifiedName)
        if self.isAccountProvisioned(account):

            if self.useSsl:
                self.response = requests.delete("https://" + self.host + ":" + self.port +
                                                "/mxos/mailbox/v2/" + fullQualifiedName,
                                                verify=self.verifyCert)
            else:
                self.response = requests.delete("http://" + self.host + ":" + self.port +
                                                "/mxos/mailbox/v2/" + fullQualifiedName)

            if self.response.status_code == requests.codes.ok:
                self.logger.info("  Result -> PASS")
            else:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
                self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
                raise Exception('Failed to delete account via MxOS.')

        else:
            self.logger.info("  Result -> SKIP")

    def foldersList(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- MxOS Get folder list info : " + fullQualifiedName)
        if self.isAccountProvisioned(account):

            if self.useSsl:
                self.response = requests.get("https://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/list",
                                             verify=self.verifyCert)
            else:
                self.response = requests.get("http://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/list")

            if self.response.status_code == requests.codes.ok:
                # Define padding / truncation for data being displayed.
                strFormat = '{:<30.30}{:>12}{:>12}{:>12}{:>25}'

                # Format and print a header for the summary.
                header = strFormat.format('    Folder', '# Msg', '# Read', '# Unread', 'Folder Size (Bytes)')
                self.logger.info(header)

                for folder in json.loads(str(self.response.text)):
                    line = strFormat.format('    ' + folder['folderName'], folder['numMessages'],
                                            folder['numReadMessages'], folder['numUnreadMessages'], 
                                            folder['folderSizeBytes'])
                    self.logger.info(line)

                self.logger.info("  Result -> PASS")

            else:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
                self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
                self.logger.info("  MxOS REQUEST    : " + str(self.response.request))
                raise Exception('Failed to get folder list.')

        else:
            self.logger.info("  Result -> ACCOUNT NOT PROVISIONED")
            raise Exception('Account is not provisioned.')

    def verifyNumMsgsInFolder(self, account, folderToVerify, expectedNumMsgs):

        foldersToCheck = {folderToVerify : expectedNumMsgs}
        self.verifyNumMsgsInFolders(account, foldersToCheck)

    def verifyNumMsgsInFolders(self, account, foldersToCheck):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- MxOS verify number of messages in folder.")
        self.logger.info("    Account          : " + fullQualifiedName)
        self.logger.info("    Folders to check : " + str(foldersToCheck))

        # Build dict to actual num messages in folders AND for results of the check.
        foldersToCheckResults = {}
        actualNumMsgsInFolder = {}
        for folder, numMsgs in foldersToCheck.items():
            foldersToCheckResults[folder] = 'NOT FOUND'
            actualNumMsgsInFolder[folder] = 'NOT FOUND'

        if self.isAccountProvisioned(account):

            if self.useSsl:
                self.response = requests.get("https://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/list",
                                             verify=self.verifyCert)
            else:
                self.response = requests.get("http://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/list")

            if self.response.status_code == requests.codes.ok:

                for folder in json.loads(str(self.response.text)):

                    thisFolderName = str(folder['folderName'])
                    thisFolderNumMessages = folder['numMessages']
                    actualNumMsgsInFolder[thisFolderName] = thisFolderNumMessages

                    if thisFolderName in foldersToCheck:

                        if foldersToCheck[thisFolderName] == thisFolderNumMessages:
                            foldersToCheckResults[thisFolderName] = 'PASS'
                        else:
                            foldersToCheckResults[thisFolderName] = 'FAIL'
                    else:
                        continue

               # Define padding / truncation for data being displayed.
                strFormat = '{:<30.30}{:<12}{:>20}{:>20}'

                # Format and print a header for the summary.
                header = strFormat.format('    Folder', 'Result', 'Expected # msgs', 'Actual # msgs')
                self.logger.info(header)

                allFoldersOk = True
                for folder, result in foldersToCheckResults.items():

                    line = strFormat.format('    ' + folder, result, foldersToCheck[folder], actualNumMsgsInFolder[folder])
                    self.logger.info(line)
                    if result == 'FAIL' or foldersToCheckResults[folder] == 'NOT FOUND':
                        allFoldersOk = False

                if allFoldersOk:
                    self.logger.info("  Result -> PASS")
                else:
                    self.logger.info("  Result -> FAIL")
                    raise Exception('Not all folders were successfully verified.')

            else:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
                self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
                self.logger.info("  MxOS REQUEST    : " + str(self.response.request))
                raise Exception('Failed to get folder list.')

        else:
            self.logger.info("  Result -> ACCOUNT NOT PROVISIONED")
            raise Exception('Account is not provisioned.')

    def messageList(self, account, folder):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- MxOS Get messages in folder : " + fullQualifiedName + " " + folder)
        if self.isAccountProvisioned(account):

            if self.useSsl:
                self.response = requests.get("https://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/" +
                                             folder + "/messages/metadata/list",
                                             verify=self.verifyCert)
            else:
                self.response = requests.get("http://" + self.host + ":" + self.port +
                                             "/mxos/mailbox/v2/" + fullQualifiedName + "/folders/" +
                                             folder + "/messages/metadata/list")

            if self.response.status_code == requests.codes.ok:

                messages = json.loads(json.dumps(json.loads(str(self.response.text))))

                if len(messages.keys()) == 0:

                    self.logger.info("  THERE ARE NO MESSAGES IN THIS FOLDER")

                else:

                    strFormat1 = '{:<10.10}{:<}'
                    strFormat2 = '{:<20}{:<20}{:<20}{:<20}{:<20}'
                    strFormat3 = '{:<33}{:<33}{:<33}'

                    messageSeparater = '-' * 100
                    self.logger.info(messageSeparater)

                    for msgId in messages:

                        msg = messages[msgId]

                        line = strFormat1.format('From:', msg['from'])
                        self.logger.info(line)

                        line = strFormat1.format('To:', ','.join(msg['to']))
                        self.logger.info(line)

                        line = strFormat1.format('Cc:', ','.join(msg['cc']))
                        self.logger.info(line)

                        line = strFormat1.format('Bcc:', ','.join(msg['bcc']))
                        self.logger.info(line)

                        subjInBase64 = msg['subject']
                        subj = base64.b64decode(subjInBase64).decode('utf-8')
                        line = strFormat1.format('Subject:', subj)
                        self.logger.info(line)

                        uidStr = 'uid:' + str(msg['uid'])
                        sizeStr = 'size:' + str(msg['size'])
                        priorityStr = 'priority:' + msg['priority']
                        flagRecentStr = 'flagRecent:' + str(msg['flagRecent'])
                        flagSeenStr = 'flagSeen:' + str(msg['flagSeen'])
                        line = strFormat2.format(uidStr, sizeStr, priorityStr, flagRecentStr ,flagSeenStr)
                        self.logger.info(line)

                        flagUnreadStr = 'flagUnread:' + str(msg['flagUnread'])
                        flagAnsStr = 'flagAns:' + str(msg['flagAns'])
                        flagFlaggedStr = 'flagFlagged:' + str(msg['flagFlagged'])
                        flagDelStr = 'flagDel:' + str(msg['flagDel'])
                        flagBounceStr = 'flagBounce:' + str(msg['flagBounce'])
                        line = strFormat2.format(flagUnreadStr, flagAnsStr, flagFlaggedStr, flagDelStr, flagBounceStr)
                        self.logger.info(line)

                        flagPrivStr = 'flagPriv:' + str(msg['flagPriv'])
                        flagRichMailStr = 'flagRichMail:' + str(msg['flagRichMail'])
                        flagDraftStr = 'flagDraft:' + str(msg['flagDraft'])
                        popDeletedFlagStr = 'popDelFlag:' + str(msg['popDeletedFlag'])
                        hasAttachmentsStr = 'hasAttach:' + str(msg['hasAttachments'])
                        line = strFormat2.format(flagPrivStr, flagRichMailStr, flagDraftStr, popDeletedFlagStr, hasAttachmentsStr)
                        self.logger.info(line)

                        sentDateStr = 'sent:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg['sentDate']))
                        arrivalTimeStr = 'arrive:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg['arrivalTime']))
                        if msg['lastAccessedTime'] == 0:
                            lastAccessedTimeStr = 'lastAccess: N/A'
                        else:
                            lastAccessedTimeStr = 'lastAccess:' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg['lastAccessedTime']))
                        line = strFormat3.format(sentDateStr, arrivalTimeStr, lastAccessedTimeStr)
                        self.logger.info(line)

                        self.logger.info(messageSeparater)

                    
                self.logger.info("  Result -> PASS")

            elif self.response.status_code == 404:

                self.logger.warning("REQUESTED FOLDER NOT AVAILABLE")
                if (folder[0] == '/') or (folder[0] == '\\'):
                    self.logger.warning("'" + folder[0] + "' CHAR MAY NOT BE NEEDED IN METHOD CALL.")

            else:
                self.logger.info("  Result -> FAIL")
                self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
                self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
                self.logger.info("  MxOS REQUEST    : " + str(self.response.request))
                raise Exception('Failed to get folder list.')

        else:
            self.logger.info("  Result -> ACCOUNT NOT PROVISIONED")
            raise Exception('Account is not provisioned.')

    def updateAccountStatus(self, account, status):

        fullQualifiedName = account.getFullQualifiedName()

        data = {}
        data['status'] = status

        self.logger.info("- MxOS update account status : " + fullQualifiedName + " " + status)

        # Try to update account status
        try:
            if self.useSsl:
                self.response = requests.post("https://" + self.host + ":" + self.port +
                                              "/mxos/mailbox/v2/" + fullQualifiedName + "/base/",
                                              data,
                                              verify=self.verifyCert)
            else:
                self.response = requests.post("http://" + self.host + ":" + self.port +
                                              "/mxos/mailbox/v2/" + fullQualifiedName + "/base/",
                                              data)

        # If unexpected exception, catch it and fail gratefully.
        # This could happen if MxOS dies.
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  MxOS ERROR: " + str(e))
            self.logger.info('  MxOS ERROR: Failed to connect to MxOS (' + self.host + ')')
            raise Exception('Failed to connect to MxOS')

        if self.response.status_code == requests.codes.ok:
            self.logger.info("  Result -> PASS")
        else:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  MxOS REQUEST URL : " + str(self.response.request.url))
            self.logger.info("  MxOS ERROR CODE : " + str(self.response.status_code))
            self.logger.info("  MxOS ERROR TEXT : " + str(self.response.text))
            self.logger.info('  MxOS ERROR: Failed to create account (' + fullQualifiedName + ') via MxOS (' + self.host + ')')
            raise Exception('Failed to update account status')

    def displayResponse(self):

        self.logger.info("- MxOS Last response ")

        if not self.response:

            self.logger.info("  An MxOS call has not been performed yet.")

        elif self.response.status_code == requests.codes.ok:

            # Try to load the response as a JSON string and if it is
            # in JSON format, display key / value pairs.

            try:
                info = json.loads(str(self.response.text))
                strFormat = '{:<40.40}{:<40}'
                for key in info:
                    line = strFormat.format('    ' + key, info[key])
                    self.logger.info(line)

            # If response is not in JSON format, output as string.
            except:
                 self.logger.info("  " + str(self.response.text) )

        else:
            self.logger.info("  " + str(self.response.text))

#==============================================================================
# CLASS: Pop
#==============================================================================

class Pop():

    def __init__(self, logger, host, port, useSsl, verifyCert=False):
        self.logger = logger
        self.host = host
        self.port = port
        self.useSsl = useSsl
        self.verifyCert = verifyCert
        self.popSession = ''
        self.loggedIn = False
        self.numMessages = 0
        self.totalMessageSize = 0
        self.msgList = []
        self.msgUidl = []
        self.message = []

    def __str__(self):
        return ("host : " + self.host + ", port : " + str(self.port) +
                ", useSsl : " + str(self.useSsl) + ", verifyCert : " + str(self.verifyCert) +
                ", loggedIn : " + str(self.loggedIn))

    def login(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- Connect to POP server")
        try:
            if self.useSsl:
                self.logger.info("- Make encrypted connection to POP server")
                self.popSession = poplib.POP3_SSL(self.host, self.port)
            else:
                self.logger.info("- Make unencrypted connection to POP server")
                self.popSession = poplib.POP3(self.host, self.port)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to create poplib.POP3 object.')
        else:
            self.logger.info("  Result -> PASS")

        self.logger.info("- Login to POP server")
        try:
            self.popSession.user(fullQualifiedName)
            self.popSession.pass_(account.password)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Login failed')
        else:
            self.loggedIn = True
            self.logger.info("  Result -> PASS")

    def getWelcome(self):
        self.logger.info("- Server welcome message :")
        try:
            welcomeMsg = self.popSession.getwelcome()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to get POP welcome message.')
        else:
            self.logger.info("  " + str(welcomeMsg))

    def getStat(self):
        self.logger.info("- Inbox statistics :")

        try:
            (self.numMessages, self.totalMessageSize) = self.popSession.stat()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to get POP stats.')
        else:
            self.logger.info("  Number of messages    : " + str(self.numMessages))
            self.logger.info("  Total size of messages: " + str(self.totalMessageSize))

    def getList(self):
        self.logger.info("- Inbox list :")

        try:
            (response, self.msgList, octets) = self.popSession.list()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to get POP list.')
        else:
            self.logger.info("  " + str(self.msgList))

    def getUidl(self):
        self.logger.info("- Inbox uidl :")

        try:
            (response, self.msgUidl, octets) = self.popSession.uidl()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to get POP uidl.')
        else:
            for thisUid in self.msgUidl:
                self.logger.info("  " + thisUid)

    def retrMessage(self,messageIndex):
        self.logger.info("- Retrieve message (index:" + str(messageIndex) + ") :")

        try:
            (response, self.message, octets)  = self.popSession.retr(messageIndex)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to retrieve message.')
        else:
            self.logger.info("")
            for line in self.message:
                self.logger.info("  " + line)
            self.logger.info("")

    def deleMessage(self,messageIndex):
        self.logger.info("- Delete message (index:" + str(messageIndex) + ") :")

        try:
            (response, self.message, octets)  = self.popSession.dele(messageIndex)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to delete message.')
        else:
            self.logger.info("  Result -> PASS")

    def quit(self):
        self.logger.info("- Quit POP server")
        try:
            self.popSession.quit()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR: " + str(e))
            raise Exception('Failed to do POP QUIT.')
        else:
            self.loggedIn = False
            self.logger.info("  Result -> PASS")

#==============================================================================
# CLASS: Imap
#==============================================================================

class Imap():

    def __init__(self, logger, host, port, useSsl, verifyCert=False):
        self.logger = logger
        self.host = host
        self.port = port
        self.useSsl = useSsl
        self.verifyCert = verifyCert
        self.imapSession = ''
        self.loggedIn = False
        #self.numMessages = 0
        #self.totalMessageSize = 0
        #self.msgList = []

    def __str__(self):
        return ("host : " + self.host + ", port : " + str(self.port) +
                ", useSsl : " + str(self.useSsl) + ", verifyCert : " + str(self.verifyCert) +
                ", loggedIn : " + str(self.loggedIn))

    def login(self, account):

        fullQualifiedName = account.getFullQualifiedName()

        self.logger.info("- Connect to IMAP server")
        try:
            #self.imapSession = imaplib.IMAP4(self.host, self.port)
            if self.useSsl:
                self.logger.info("- Make encrypted connection to POP server")
                self.imapSession = imaplib.IMAP4_SSL(self.host, self.port)
            else:
                self.logger.info("- Make unencrypted connection to POP server")
                self.imapSession = imaplib.IMAP4(self.host, self.port)

        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to create imaplib.IMAP4 object.')
        else:
            self.logger.info("  Result -> PASS")

        self.logger.info("- Login to IMAP server")
        try:
            self.imapSession.login(fullQualifiedName, account.password)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Login failed')
        else:
            self.loggedIn = True
            self.logger.info("  Result -> PASS")

    def select(self, folder):
        self.logger.info("- Select folder : " + folder)
        try:
            self.imapSession.select(folder)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to select folder.')
        else:
            self.logger.info("  Result -> PASS")

    def list(self):
        self.logger.info("- List folder content")
        try:
            result = self.imapSession.list()
            for folder in result[1]:
                self.logger.info("  " + folder.replace('() "/" ', ''))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to list folder.')
        else:
            self.logger.info("  Result -> PASS")

    def create(self,newFolder):
        self.logger.info("- Create new folder : '" + newFolder + "'")
        try:
            result = self.imapSession.create(newFolder)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to create folder.')
        else:
            self.logger.info("  Result -> PASS")

    def rename(self,oldFolder,newFolder):
        self.logger.info("- Rename folder from '" + oldFolder + "' to '" + newFolder + "'")
        try:
            result = self.imapSession.rename(oldFolder,newFolder)
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to rename folder.')
        else:
            self.logger.info("  Result -> PASS")

    def quotaroot(self):
        self.logger.info("- Quota")
        try:
            result = self.imapSession.getquotaroot("INBOX")
            self.logger.info("  " + str(result[1]))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to get quota info.')
        else:
            self.logger.info("  Result -> PASS")

    def append(self, message):
        self.logger.info("- Append message : TO " + message['To'] +
                         ", FROM " + message['From'] +
                         ", SUBJ " + message['Subject'])
        try:
            result = self.imapSession.append("INBOX", None, None, message.as_string())
            self.logger.info("  " + str(result[1]))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to append message.')
        else:
            self.logger.info("  Result -> PASS")

    def fetch(self, message_set, message_parts):
        self.logger.info("- Fetch message(s) part : " + message_parts)
        try:
            result = self.imapSession.fetch(message_set, message_parts)
            for line in result[1]:
                self.logger.info("  " + str(line))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to fetch message.')
        else:
            self.logger.info("  Result -> PASS")

    def copy(self, message_set, folder):
        self.logger.info("- Copy messages to folder : " + folder)
        try:
            result = self.imapSession.copy(message_set, folder)
            for line in result[1]:
                self.logger.info("  " + str(line))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to copy message.')
        else:
            self.logger.info("  Result -> PASS")

    def search(self, charset, criterion, *args):
        if len(args) == 0:
            self.logger.info("- Search for messages with criteria : " + str(criterion))
        else:
            self.logger.info("- Search for messages with criteria : " + str(criterion) + " : " + str(args))
        try:
            typ, msgnums = self.imapSession.search(charset, criterion, *args)
            numMsgFound = len(msgnums[0].split())
            if numMsgFound == 0:
                self.logger.info("  NO MESSAGES FOUND THAT MATCH CRITERIA")
            else:
                self.logger.info("  " + str(numMsgFound) + " MESSAGES MATCH CRITERIA.")
                self.logger.info("  MESSAGE NUMBERS : " + msgnums[0])
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Search failed.')
        else:
            self.logger.info("  Result -> PASS")

    def delete(self, message_set):
        self.logger.info("- Delete messages in folder : " + message_set)
        try:
            result = self.imapSession.store(message_set, '+FLAGS', '\DELETED')
            for line in result[1]:
                self.logger.info("  " + str(line))
            self.logger.info("- Expunge messages.")
            result = self.imapSession.expunge()
            for line in result[1]:
                self.logger.info("  " + str(line))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to delete message(s).')
        else:
            self.logger.info("  Result -> PASS")

    def markRead(self, message_set):
        self.logger.info("- Mark messages as read : " + message_set)
        try:
            result = self.imapSession.store(message_set, '+FLAGS', '\SEEN')
            for line in result[1]:
                self.logger.info("  " + str(line))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to delete message(s).')
        else:
            self.logger.info("  Result -> PASS")

    def markUnread(self, message_set):
        self.logger.info("- Mark messages as unread : " + message_set)
        try:
            result = self.imapSession.store(message_set, '-FLAGS', '\SEEN')
            for line in result[1]:
                self.logger.info("  " + str(line))
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to delete message(s).')
        else:
            self.logger.info("  Result -> PASS")

    def logout(self):
        self.logger.info("- Logout of IMAP server")
        try:
            self.imapSession.logout()
        except Exception as e:
            self.logger.info("  Result -> FAIL")
            self.logger.info("  ERROR : " + str(e))
            raise Exception('Failed to do IMAP LOGOUT.')
        else:
            self.loggedIn = False
            self.logger.info("  Result -> PASS")
