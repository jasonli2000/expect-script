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
try:
  from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
except ImportError:
  from pexpect import TIMEOUT, EOF, ExceptionPexpect
  pass
from CreateConnection import createExpectConnection
import argparse

class SetupVolumeSet:
  def __init__(self, system, connection, volName, boxName, domainName, logFile):
    self._system = system
    self._logFile = logFile
    self._connection = connection
    self._volName = volName
    self._boxName = boxName
    self._domainName = domainName
    self.__setupSystemDependentParameter__()
    self._origBoxVolSet = None
    self._origDomainName = None
  def __setupSystemDependentParameter__(self):
    pass
  def run(self):
    connection = self._connection
    try:
      connection.logfile = open(self._logFile, 'wb')
      self.__setupNewVolumeSet__()
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
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("14.5\r") # fileman file for volume Set

  def __exit__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("HALT\r")

  def __setupNewVolumeSet__(self):
    self.__gotoEditVolumeSetOption__()
    connection = self._connection
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select VOLUME SET:")
    connection.send(self._volName + "\r")
    while True:
      index = connection.expect(["Are you adding \'%s\' as a new VOLUME SET" % self._volName,
                                 "VOLUME SET:"])
      if index == 0:
        connection.send("YES\r")
        break
      if index == 1:
        connection.send("\r")
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

  def __editTaskManSiteParameter__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
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
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
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
    if self._domainName and len(self._domainName) > 1:
      connection.send("%s\r" % (self._domainName))
    else:
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
    connection.send("YES\r")
    connection.expect("Select RPC BROKER SITE PARAMETERS DOMAIN NAME:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")
  def __findoutTaskManBoxVolumePair__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
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
    connection.expect("TASKMAN SITE PARAMETERS LIST")
    connection.expect("BOX-VOLUME PAIR")
    connection.expect("-+")
    connection.expect("\S+:\S+") # \S match any non-whitespace chars
    self._origBoxVolSet = connection.after
    print ("[%s]"  % (connection.after))
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __findoutRPCDefaultDomainName__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
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
    connection.expect("RPC BROKER SITE PARAMETERS LIST")
    connection.expect("DOMAIN NAME")
    connection.expect("-+")
    connection.expect("\S+") # \S match any non-whitespace chars
    self._origDomainName = connection.after.strip()
    print ("[%s]"  % (connection.after.strip()))
    connection.expect("Select OPTION:")
    connection.send("\r")

def findoutTaskManBoxVolumePair(connection):
  connection.expect("[A-Za-z0-9]+>")
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
  connection.expect("TASKMAN SITE PARAMETERS LIST")
  connection.expect("BOX-VOLUME PAIR")
  connection.expect("-+")
  connection.expect("\S+:\S+") # \S match any non-whitespace chars
  print ("[%s]"  % (connection.after))
  connection.expect("Select OPTION:")
  connection.send("\r")
  connection.expect("[A-Za-z0-9]+>")
  connection.send("HALT\r")

def findoutRPCDomainName(connection):
  connection.expect("[A-Za-z0-9]+>")
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
  connection.expect("RPC BROKER SITE PARAMETERS LIST")
  connection.expect("DOMAIN NAME")
  connection.expect("-+")
  connection.expect("\S+") # \S match any non-whitespace chars
  print ("[%s]"  % (connection.after))
  connection.expect("Select OPTION:")
  connection.send("\r")
  connection.expect("[A-Za-z0-9]+>")
  connection.send("HALT\r")

def testFindoutTaskManBoxVolumePair():
  expectConn = None
  expectConn = createExpectConnection(3)
  if not expectConn:
    sys.exit(-1)
  #findoutTaskManBoxVolumePair(expectConn)
  findoutRPCDomainName(expectConn)

if __name__ == '__main__':
  #testFindoutTaskManBoxVolumePair()
  #sys.exit(0)
  parser = argparse.ArgumentParser(description='Setup Volume Set')
  parser.add_argument('-V', dest='VolumeSetName',
                      help='Volume set name')
  parser.add_argument('-B', dest='BoxName',
                      help='Box Name')
  parser.add_argument('-D', dest='DomainName',
                      help='PRC Domain Name')
  #parser.add_argument('-a', dest="Add", help="Add a new volume set")
  parser.add_argument('-m', required=True, dest="mumpsSystem", choices='123',
                      help="1. Cache/Windows, 2. Cache/Linux 3. GTM/Linux")
  parser.add_argument('-l', required=True, dest="logFile",
                      help="where to store the log file")
  result = vars(parser.parse_args());
  print (result)
  expectConn = None
  system = int(result['mumpsSystem'])
  expectConn = createExpectConnection(system)
  if not expectConn:
    sys.exit(-1)
  volSet = SetupVolumeSet(system, expectConn, 
                          result['VolumeSetName'],
                          result['BoxName'],
                          result['DomainName'],
                          result['logFile'])
  volSet.run()
