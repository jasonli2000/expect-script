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

class SetupDevice:
  def __init__(self, system, logFile, connection):
    self._HFS = None
    self._Term =None
    self._NullDevice = None
    self._system = system
    self._logFile = logFile
    self._connection = connection
    self.__setupSystemDependentParameter__()
  def __setupSystemDependentParameter__(self):
    pass
  def setupHostFileSystem(self, HFSPath):
    self._HFS = HFSPath
  def setupTerminalDevice(self, Term):
    self._Term = Term
  def setupNullDevice(self, NullPath):
    self._NullDevice = NullPath
  def run(self):
    connection = self._connection
    try:
      connection.logfile = open(self._logFile, 'wb')
      if (self._HFS):
        self.__initHFSDevice__()
      if (self._Term):
        self.__initTerminalDevice_()
      if (self._NullDevice):
        self.__initNullDevice__()
      connection.terminate()
    except TIMEOUT:
      print "TimeOut"
      print str(connection)
      connection.terminate()
    except ExceptionPexpect:
      connection.terminate()
    except EOF:
      connection.terminate()

  def __gotoEditDeviceOption__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("DEVICE\r")

  def __initNullDevice__(self):
    self.__gotoEditDeviceOption__()
    connection = self._connection
    connection.expect("EDIT WHICH FIELD:")
    connection.send("$I\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("SIGN-ON/SYSTEM DEVICE\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("LOCATION OF TERMINAL\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("\r")
    connection.expect("Select DEVICE NAME:")
    connection.send("NULL\r")
    connection.expect("CHOOSE 1-[2-9]:")
    connection.send("1\r")
    connection.expect("\$I:")
    connection.send(self._NullDevice + "\r")
    connection.expect("SIGN-ON\/SYSTEM DEVICE")
    connection.send("NO\r")
    connection.expect("LOCATION OF TERMINAL:")
    connection.send("Bit Bucket (GT.M-Unix)\r")
    connection.expect("Select DEVICE NAME:")
    connection.send("^\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __initTerminalDevice__(self):
    pass

  def __initHFSDevice__(self):
    self.__gotoEditDeviceOption__()
    connection = self._connection
    connection.expect("EDIT WHICH FIELD:")
    connection.send("ALL\r")
    connection.expect("Select DEVICE NAME:")
    connection.send("HFS\r")
    connection.expect("NAME: HFS\/\/")
    connection.send("\r")
    connection.expect("LOCATION OF TERMINAL:")
    connection.send("\r")
    connection.expect("Select MNEMONIC:")
    connection.send("\r")
    connection.expect("LOCAL SYNONYM:")
    connection.send("\r")
    connection.expect("\$I:")
    connection.send(self._HFS + "\r")
    connection.expect("VOLUME SET\(CPU\)")
    connection.send("\r")
    connection.expect("SIGN-ON\/SYSTEM DEVICE")
    connection.send("NO\r")
    connection.expect("TYPE:")
    connection.send("\r")
    connection.expect("SUBTYPE:")
    connection.send("\r")
    connection.expect("ASK DEVICE:")
    connection.send("YES\r")
    connection.expect("ASK PARAMETERS:")
    connection.send("YES\r")
    connection.expect("ASK HOST FILE:")
    connection.send("YES\r")
    connection.expect("ASK HFS I\/O OPERATION:")
    connection.send("YES\r")
    connection.expect("QUEUING:")
    connection.send("\r")
    connection.expect("OUT-OF-SERVICE DATE:")
    connection.send("\r")
    connection.expect("NEAREST PHONE:")
    connection.send("\r")
    connection.expect("KEY OPERATOR:")
    connection.send("\r")
    connection.expect("MARGIN WIDTH:")
    connection.send("132\r")
    connection.expect("PAGE LENGTH:")
    connection.send("65534\r")
    connection.expect("SUPPRESS FORM FEED AT CLOSE:")
    connection.send("\r")
    connection.expect("SECURITY:")
    connection.send("\r")
    connection.expect("CLOSEST PRINTER:")
    connection.send("\r")
    connection.expect("FORM CURRENTLY MOUNTED:")
    connection.send("\r")
    connection.expect("OPEN PARAMETERS:")
    connection.send("(newversion)\r")
    connection.expect("CLOSE PARAMETERS:")
    connection.send("^\r")
    connection.expect("Select DEVICE NAME:")
    connection.send("^\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Setup Device')
  parser.add_argument('-H', dest='HFS',
                      help='Host File System path')
  parser.add_argument('-N', dest="NULLDevice",
                      help="Set up NULL Device")
  parser.add_argument('-T', dest="Terminal",
                      help="Set up Terminal Device")
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
  device = SetupDevice(system, result['logFile'], expectConn)
  if result['HFS']:
    device.setupHostFileSystem(result['HFS'])
  if result['NULLDevice']:
    device.setupNullDevice(result['NULLDevice'])
  if result['Terminal']:
    device.setupTerminalDevice(result['Terminal'])
  device.run()
