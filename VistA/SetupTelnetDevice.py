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
try:
  from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
except ImportError:
  import pexpect
  pass
import sys
from CreateConnection import createExpectConnection

def SetupTelnetDevice(child, telnetOption, logFileName):
  try:
    child.logfile = open(logFileName,'wb')
    child.expect("[A-Za-z0-9]+>")
    child.send("S DUZ=1 D Q^DI\r")
    child.expect("Select OPTION:")
    child.send("1\r")
    child.expect("INPUT TO WHAT FILE:")
    child.send("DEVICE\r")
    child.expect("EDIT WHICH FIELD:")
    child.send("$I\r")
    child.expect("THEN EDIT FIELD:")
    child.send("\r")
    child.expect("Select DEVICE NAME:")
    child.send("TELNET\r")
    child.expect("CHOOSE 1-2:")
    child.send("1\r")
    child.expect("\$I: .*//")
    child.send(telnetOption+"\r")
    child.expect("Select DEVICE NAME:")
    child.send("\r")
    child.expect("Select OPTION:")
    child.send("\r")
    child.expect("VISTA")
    child.terminate()
  except TIMEOUT:
    print "TimeOut"
    print str(child)
    child.terminate()
  except ExceptionPexpect:
    child.terminate()
  except EOF:
    child.terminate()

if __name__ == '__main__':
  print ("sys.argv is %s" % sys.argv)
  if len(sys.argv) <= 2:
    print ("Need at least two arguments")
    sys.exit()
  expectConn = None
  if len(sys.argv) > 3:
    system = int(sys.argv[1])
    expectConn = createExpectConnection(system)
  if not expectConn:
    sys.exit(-1)
  SetupTelnetDevice(expectConn, sys.argv[2], sys.argv[3])
                        
