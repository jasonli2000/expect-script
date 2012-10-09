#---------------------------------------------------------------------------
# Copyright 2011 The Open Source Electronic Health Record Agent
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#---------------------------------------------------------------------------

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pexpect import TIMEOUT, EOF, ExceptionPexpect
from VistATestClient import VistATestClient, VistATestClientFactory
import argparse

class SetupVolumeSet:
  def __init__(self, system, testClient, volName, boxName, domainName, logFile):
    self._system = system
    self._logFile = logFile
    self._testClient = testClient
    self._volName = volName
    self._boxName = boxName
    self._domainName = domainName
    self.__setupSystemDependentParameter__()
    self._defaultVolSet = None
    self._origBoxVolSet = None
    self._origDomainName = None
  def __setupSystemDependentParameter__(self):
    pass
  def run(self):
    connection = self._testClient.getConnection()
    try:
      connection.logfile = open(self._logFile, 'wb')
      self.__findoutDefaultVolumeSet__()
      if True: #self._defaultVolSet != self._volName:
        self.__setupVolumeSet()
        # this is to make sure the vol set is the same as the one in
        # kernel system parameters file 8989.3
        self.__setKernelSystemParametersVolumeSet__()
        self.__findoutTaskManBoxVolumePair__()
        self.__editTaskManSiteParameter__()
        self.__findoutRPCDefaultDomainName__()
        self.__editRCPBrokerSiteParameter__()
      self.__exit__()
      connection.terminate()
    except TIMEOUT:
      print "TimeOut"
      print str(connection)
      connection.terminate()
    except ExceptionPexpect:
      connection.terminate()
    except EOF:
      connection.terminate()

  def __gotoEditVolumeSetOption__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("14.5\r") # fileman file for volume Set

  def __exit__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("HALT\r")

  def __setupVolumeSet(self):
    self.__gotoEditVolumeSetOption__()
    connection = self._testClient.getConnection()
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select VOLUME SET:")
    connection.send(self._defaultVolSet + "\r")
    while True:
      index = connection.expect(["Are you adding \'%s\' as a new VOLUME SET" % self._volName,
                                 "VOLUME SET:"])
      if index == 0:
        connection.send("NO\r")
        break
      if index == 1:
        connection.send(self._volName + "\r")
        break
    connection.expect("TYPE: ")
    connection.send("GENERAL PURPOSE VOLUME SET\r")
    connection.expect("INHIBIT LOGONS\?:")
    connection.send("NO\r")
    connection.expect("LINK ACCESS\?:")
    connection.send("YES\r")
    connection.expect("OUT OF SERVICE\?:")
    connection.send("NO\r")
    connection.expect("REQUIRED VOLUME SET\?:")
    connection.send("NO\r")
    connection.expect("TASKMAN FILES UCI:")
    connection.send(self._volName + "\r")
    connection.expect("TASKMAN FILES VOLUME SET:")
    connection.send(self._volName + "\r")
    connection.expect("REPLACEMENT VOLUME SET:")
    connection.send("\r")
    connection.expect("DAYS TO KEEP OLD TASKS:")
    connection.send("4\r")
    connection.expect("SIGNON\/PRODUCTION VOLUME SET:")
    connection.send("YES\r")
    connection.expect("RE-QUEUES BEFORE UN-SCHEDULE:")
    connection.send("\r")
    connection.expect("Select VOLUME SET:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __setKernelSystemParametersVolumeSet__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("8989.3\r") # KERNEL SYSTEM PARAMETERS
    connection.expect("EDIT WHICH FIELD:")
    connection.send("VOLUME SET\r")
    connection.expect("EDIT WHICH VOLUME SET SUB-FIELD:")
    connection.send("VOLUME SET\r")
    connection.expect("THEN EDIT VOLUME SET SUB-FIELD:")
    connection.send("MAX SIGNON ALLOWED\r")
    connection.expect("THEN EDIT VOLUME SET SUB-FIELD:")
    connection.send("\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("\r")
    connection.expect("Select KERNEL SYSTEM PARAMETERS DOMAIN NAME:")
    connection.send(self._domainName + "\r")
    connection.expect("...OK\?")
    connection.send("YES\r")
    connection.expect("Select VOLUME SET:")
    connection.send("\r")
    connection.expect("VOLUME SET:")
    connection.send(self._volName + "\r")
    connection.expect("MAX SIGNON ALLOWED:")
    connection.send("\r")
    connection.expect("Select VOLUME SET:")
    connection.send("\r")
    connection.expect("Select KERNEL SYSTEM PARAMETERS DOMAIN NAME:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __editTaskManSiteParameter__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("14.7\r") # fileman file for taskman site parameter
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select TASKMAN SITE PARAMETERS BOX-VOLUME PAIR:")
    connection.send(self._origBoxVolSet + "\r")
    while True:
      index = connection.expect(["Are you adding '%s:%s' as" % (self._volName, self._boxName),
                                 "BOX-VOLUME PAIR:"])
      if index == 0:
        connection.send("NO\r")
        continue
      if index == 1:
        connection.send("%s:%s\r" % (self._volName, self._boxName))
        break
    connection.expect("RESERVED:")
    connection.send("^\r")
    connection.expect("Select TASKMAN SITE PARAMETERS BOX-VOLUME PAIR:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")
  def __editRCPBrokerSiteParameter__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("8994.1\r") # fileman file for taskman site parameter
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select RPC BROKER SITE PARAMETERS DOMAIN NAME:")
    connection.send("%s\r" % (self._origDomainName))
    connection.expect("...OK\?")
    connection.send("YES\r")
    connection.expect("DOMAIN NAME:")
    connection.send("\r")
    connection.expect("MAIL GROUP FOR ALERTS:")
    connection.send("\r")
    connection.expect("Select BOX-VOLUME PAIR:")
    connection.send("%s:%s\r" % (self._volName, self._boxName))
    while True:
      index = connection.expect(["Are you adding '%s:%s' as a new LISTENER" % (self._volName, self._boxName),
                                 "...OK\?",
                                 "BOX-VOLUME PAIR:"])
      if index == 0:
        connection.send("NO\r")
        continue
      if index == 1:
        connection.send("YES\r")
        continue
      if index == 2:
        connection.send("%s:%s\r" % (self._volName, self._boxName))
        break
    connection.expect("Select PORT:")
    connection.send("9210\r")
    while True:
      index = connection.expect(["Are you adding '9210' as a new PORT",
                                 "PORT:"])
      if index == 0:
        connection.send("YES\r")
        break
      if index == 1:
        connection.send("\r")
        break
    connection.expect("TYPE OF LISTENER:")
    connection.send("New Style\r")
    connection.expect("STATUS:")
    connection.send("\r")
    connection.expect("CONTROLLED BY LISTENER STARTER:")
    connection.send("No\r")
    connection.expect("Select RPC BROKER SITE PARAMETERS DOMAIN NAME:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __findoutSystemBoxVolumeSet__(self):
# this is to find the VistA system-wise box-volume pair after initialization
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("D GETENV^%ZOSV W Y\r")
    connection.expect("(?P<volSet>[^\^:]+):(?P<boxValue>[^\^:]+)")
    print (connection.match)
    self._testClient.waitForPrompt()

  def __findoutDefaultVolumeSet__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("2\r")
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("VOLUME SET\r")
    connection.expect("SORT BY:")
    connection.send("\r")
    connection.expect("START WITH VOLUME SET:")
    connection.send("\r")
    connection.expect("FIRST PRINT FIELD:")
    connection.send("VOLUME SET\r")
    connection.expect("THEN PRINT FIELD:")
    connection.send("\r")
    connection.expect("Heading \(S\/C\):")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send("\r")
    while True:
      index = connection.expect(["Right Margin:","VOLUME SET LIST"])
      if index == 0:
        connection.send("\r")
      else:
        break
    connection.expect("VOLUME SET")
    connection.expect("-+")
    connection.expect("\S+") # \S match any non-whitespace chars
    print ("before expect: [%s]"  % (connection.before))
    self._defaultVolSet = connection.after
    print ("after expect match [%s]"  % (connection.after))
    connection.expect("Select OPTION:")
    connection.send("\r")
  def __findoutTaskManBoxVolumePair__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("2\r")
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("14.7\r")
    connection.expect("SORT BY: BOX-VOLUME PAIR\/\/")
    connection.send("\r")
    connection.expect("START WITH BOX-VOLUME PAIR:")
    connection.send("\r")
    connection.expect("FIRST PRINT FIELD:")
    connection.send("BOX-VOLUME PAIR\r")
    connection.expect("THEN PRINT FIELD:")
    connection.send("\r")
    connection.expect("Heading \(S\/C\):")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send("\r")
    while True:
      index = connection.expect(["Right Margin:","TASKMAN SITE PARAMETERS LIST"])
      if index == 0:
        connection.send("\r")
      else:
        break
    connection.expect("BOX-VOLUME PAIR")
    connection.expect("-+")
    connection.expect("\S+:\S+") # \S match any non-whitespace chars
    self._origBoxVolSet = connection.after
    print ("default box_vloume pair is [%s]"  % (connection.after))
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __findoutRPCDefaultDomainName__(self):
    connection = self._testClient.getConnection()
    self._testClient.waitForPrompt()
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("2\r")
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("8994.1\r")
    connection.expect("SORT BY:")
    connection.send("DOMAIN NAME\r")
    connection.expect("START WITH DOMAIN NAME:")
    connection.send("\r")
    connection.expect("WITHIN DOMAIN NAME, SORT BY:")
    connection.send("\r")
    connection.expect("FIRST PRINT FIELD:")
    connection.send("DOMAIN NAME\r")
    connection.expect("THEN PRINT FIELD:")
    connection.send("\r")
    connection.expect("Heading \(S\/C\):")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send("\r")
    while True:
      index = connection.expect(["Right Margin:","RPC BROKER SITE PARAMETERS LIST"])
      if index == 0:
        connection.send("\r")
      else:
        break
    connection.expect("DOMAIN NAME")
    connection.expect("-+")
    connection.expect("\S+") # \S match any non-whitespace chars
    self._origDomainName = connection.after.strip()
    print ("[%s]"  % (connection.after.strip()))
    connection.expect("Select OPTION:")
    connection.send("\r")

def findoutTaskManBoxVolumePair(testClient):
  connection = testClient.getConnection()
  testClient.waitForPrompt()
  connection.send("S DUZ=1 D P^DI\r")
  connection.expect("Select OPTION:")
  connection.send("2\r")
  connection.expect("OUTPUT FROM WHAT FILE:")
  connection.send("14.7\r")
  connection.expect("SORT BY: BOX-VOLUME PAIR\/\/")
  connection.send("\r")
  connection.expect("START WITH BOX-VOLUME PAIR:")
  connection.send("\r")
  connection.expect("FIRST PRINT FIELD:")
  connection.send("BOX-VOLUME PAIR\r")
  connection.expect("THEN PRINT FIELD:")
  connection.send("\r")
  connection.expect("Heading \(S\/C\):")
  connection.send("\r")
  connection.expect("DEVICE:")
  connection.send("\r")
  while True:
    index = connection.expect(["Right Margin:","TASKMAN SITE PARAMETERS LIST"])
    if index == 0:
      connection.send("\r")
    else:
      break
  connection.expect("BOX-VOLUME PAIR")
  connection.expect("-+")
  connection.expect("\S+:\S+") # \S match any non-whitespace chars
  print ("default box-volume pair is [%s]"  % (connection.after))
  connection.expect("Select OPTION:")
  connection.send("\r")
def findoutRPCDomainName(testClient):
  connection = testClient.getConnection()
  testClient.waitForPrompt()
  connection.send("S DUZ=1 D P^DI\r")
  connection.expect("Select OPTION:")
  connection.send("2\r")
  connection.expect("OUTPUT FROM WHAT FILE:")
  connection.send("8994.1\r")
  connection.expect("SORT BY:")
  connection.send("DOMAIN NAME\r")
  connection.expect("START WITH DOMAIN NAME:")
  connection.send("\r")
  connection.expect("WITHIN DOMAIN NAME, SORT BY:")
  connection.send("\r")
  connection.expect("FIRST PRINT FIELD:")
  connection.send("DOMAIN NAME\r")
  connection.expect("THEN PRINT FIELD:")
  connection.send("\r")
  connection.expect("Heading \(S\/C\):")
  connection.send("\r")
  connection.expect("DEVICE:")
  connection.send("\r")
  while True:
    index = connection.expect(["Right Margin:","RPC BROKER SITE PARAMETERS LIST"])
    if index == 0:
      connection.send("\r")
    else:
      break
  connection.expect("DOMAIN NAME")
  connection.expect("-+")
  connection.expect("\S+") # \S match any non-whitespace chars
  print ("[%s]"  % (connection.after))
  connection.expect("Select OPTION:")
  connection.send("\r")
def findoutDefaultVolumeSet(testClient):
  connection = testClient.getConnection()
  testClient.waitForPrompt()
  connection.send("S DUZ=1 D P^DI\r")
  connection.expect("Select OPTION:")
  connection.send("2\r")
  connection.expect("OUTPUT FROM WHAT FILE:")
  connection.send("VOLUME SET\r")
  connection.expect("SORT BY:")
  connection.send("\r")
  connection.expect("START WITH VOLUME SET:")
  connection.send("\r")
  connection.expect("FIRST PRINT FIELD:")
  connection.send("VOLUME SET\r")
  connection.expect("THEN PRINT FIELD:")
  connection.send("\r")
  connection.expect("Heading \(S\/C\):")
  connection.send("\r")
  connection.expect("DEVICE:")
  connection.send("\r")
  while True:
    index = connection.expect(["Right Margin:","VOLUME SET LIST"])
    if index == 0:
      connection.send("\r")
    else:
      break
  connection.expect("VOLUME SET")
  connection.expect("-+")
  connection.expect("\S+") # \S match any non-whitespace chars
  print ("before expect: [%s]"  % (connection.before))
  print ("after expect match [%s]"  % (connection.after))
  connection.expect("Select OPTION:")
  connection.send("\r")
def testFindoutTaskManBoxVolumePair(system):
  expectConn = None
  expectConn = VistATestClientFactory.createVistATestClient(system)
  if not expectConn:
    sys.exit(-1)
  #findoutTaskManBoxVolumePair(expectConn)
  findoutRPCDomainName(expectConn)
def testFindoutDefaultVolumeSet(system):
  expectConn = None
  expectConn = VistATestClientFactory.createVistATestClient(system)
  if not expectConn:
    sys.exit(-1)
  findoutTaskManBoxVolumePair(expectConn)
  findoutDefaultVolumeSet(expectConn)
  findoutSystemBoxVolumeSet(expectConn)
  expectConn.waitForPrompt()
  expectConn.getConnection().terminate()
def findoutSystemBoxVolumeSet(expectConn):
# this is to find the VistA system-wise box-volume pair after initialization
  connection = expectConn.getConnection()
  expectConn.waitForPrompt()
  connection.send("D GETENV^%ZOSV W Y\r")
  connection.expect("(?P<UCI>[^\^\r\n]+)\^(?P<VOL>[^\^]+)\^(?P<Node>[^\^]+)\^(?P<volSet>[^\^:]+):(?P<boxValue>[^\^:\r\n]+)")
  result = connection.match
  if result:
    print (result.groups())
    print (result.group('UCI'))
    print (result.group('VOL'))
    print (result.group('Node'))
    print (result.group('volSet'))
    print (result.group('boxValue'))
def test():
  #testFindoutTaskManBoxVolumePair(1)
  testFindoutDefaultVolumeSet(1)
  sys.exit(0)
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Setup Volume Set')
  parser.add_argument('-V', dest='VolumeSetName',
                      help='Volume set name')
  parser.add_argument('-B', dest='BoxName',
                      help='Box Name')
  parser.add_argument('-D', dest='DomainName',
                      help='PRC Domain Name')
  #parser.add_argument('-a', dest="Add", help="Add a new volume set")
  parser.add_argument('-m', required=True, dest="mumpsSystem", choices='12',
                      help="1. Cache, 2. GTM")
  parser.add_argument('-l', required=True, dest="logFile",
                      help="where to store the log file")
  result = vars(parser.parse_args());
  print (result)
  expectConn = None
  system = int(result['mumpsSystem'])
  expectConn = VistATestClientFactory.createVistATestClient(system)
  if not expectConn:
    sys.exit(-1)
  volSet = SetupVolumeSet(system, expectConn,
                          result['VolumeSetName'],
                          result['BoxName'],
                          result['DomainName'],
                          result['logFile'])
  volSet.run()
