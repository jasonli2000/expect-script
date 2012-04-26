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

# this class will
# 1. create a new domain under domain file
# 2. update kernel site parameter and RPC parameter file
# 3. reindex the file
class CreateNewDomain:
  def __init__(self, system, connection, domainName, logFile):
    self._system = system
    self._logFile = logFile
    self._connection = connection
    self._domain = domainName
    self.__setupSystemDependentParameter__()
    self._isNewDomain = True
    self._newDomainNumber = 0
  def __setupSystemDependentParameter__(self):
    pass
  def run(self):
    connection = self._connection
    try:
      connection.logfile = open(self._logFile, 'wb')
      self.__setupNewDomainName__()
      self.__christenNewDomain__()
      self.__findOutDomainNumber__()
      self.__setupKernelRPCParameterFile__()
      self.__reindexKernelRPCParameterFile__()
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

  def __gotoEditDomainNameOption__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("DOMAIN\r") # DOMAIN FILE

  def __exit__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("HALT\r")

  def __setupNewDomainName__(self):
    self.__gotoEditDomainNameOption__()
    connection = self._connection
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select DOMAIN NAME:")
    connection.send(self._domain + "\r")
    while True:
      index = connection.expect(["Are you adding \'%s\' as a new DOMAIN" % self._domain,
                                 "NAME:"])
      if index == 0:
        connection.send("YES\r")
        break
      if index == 1:
        connection.send("\r")
        self._isNewDomain = False
        break
    connection.expect("FLAGS:")
    connection.send("^\r")
    connection.expect("Select DOMAIN NAME:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __christenNewDomain__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("DO CHRISTEN^XMUDCHR\r")
    connection.expect("Are you sure you want to change the name of this facility\?")
    connection.send("YES\r")
    connection.expect("Select DOMAIN NAME:")
    connection.send(self._domain + "\r")
    connection.expect("PARENT:")
    connection.send("FOIA.PLATINUM.VA.GOV\r") # VA as the parent domain
    connection.expect("TIME ZONE:")
    connection.send("EDT\r") # VA as the parent domain
  def __findOutDomainNumber__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("5\r") # inquire to file entries
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("DOMAIN\r") # DOMAIN FILE
    connection.expect("Select DOMAIN NAME:")
    connection.send(self._domain + "\r")
    connection.expect("ANOTHER ONE:")
    connection.send("\r")
    connection.expect("STANDARD CAPTIONED OUTPUT\?")
    connection.send("NO\r")
    connection.expect("FIRST PRINT FIELD:")
    connection.send("NUMBER\r")
    connection.expect("THEN PRINT FIELD:")
    connection.send("\r")
    connection.expect("Heading \(S\/C\):")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send("\r")
    connection.expect("DOMAIN LIST")
    connection.expect("NUMBER")
    connection.expect("-+")
    connection.expect("[1-9]+")
    self._newDomainNumber = connection.after
    print ("Domain Number is %s" % connection.after)
    connection.expect("Select OPTION:")
    connection.send("\r")
  def __setupKernelRPCParameterFile__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S $P(^XTV(8989.3,1,0),\"^\")=%s\r" % self._newDomainNumber.strip())
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S $P(^XWB(8994.1,1,0),\"^\")=%s\r" % self._newDomainNumber.strip())
  def __reindexFile__(self, fileNo):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("UTILITY FUNCTIONS\r")
    connection.expect("Select UTILITY OPTION:")
    connection.send("RE-INDEX FILE\r")
    connection.expect("MODIFY WHAT FILE:")
    connection.send(fileNo + "\r")
    connection.expect("DO YOU WISH TO RE-CROSS-REFERENCE ONE PARTICULAR INDEX\?")
    connection.send("NO\r")
    connection.expect("OK, ARE YOU SURE YOU WANT TO KILL OFF THE EXISTING")
    connection.send("YES\r")
    connection.expect("DO YOU THEN WANT TO \'RE-CROSS-REFERENCE\'\?")
    connection.send("YES\r")
    connection.expect("Select UTILITY OPTION:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __reindexKernelRPCParameterFile__(self):
    self.__reindexFile__("8989.3") # kernel system parameters
    self.__reindexFile__("8994.1") # RPC broker site parameters

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Setup Domain Name')
  parser.add_argument('-N', dest='DomainName',
                      help='Domain Name')
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
  domain = CreateNewDomain(system, expectConn, result['DomainName'], result['logFile'])
  domain.run()
