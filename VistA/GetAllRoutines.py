#---------------------------------------------------------------------------
# Copyright 2011-2012 The Open Source Electronic Health Record Agent
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

import pexpect
import sys

def createExpectConnection():
  child = pexpect.spawn("gtm")
  assert child.isalive()
  return child
def createExpectConnectionCacheLinux():
  child = pexpect.spawn("ccontrol session cache")
  assert child
  child.expect("Username:")
  child.send("admin\r")
  child.expect("Password:")
  child.send("cache\r")
  return child

def GetAllRoutines(child, outputFile):
  child.logfile = open(outputFile,'wb')
  child.expect("[A-Za-z0-9]+>")
  child.send("S DUZ=1 D Q^DI\r")
  child.expect("Select OPTION:")
  # print file entry
  child.send("2\r" )
  child.expect("OUTPUT FROM WHAT FILE:")
  child.send("ROUTINE\r") # fileman file #9.8
  child.expect("SORT BY:")
  child.send("NAME\r")
  child.expect("START WITH")
  child.send("\r")
  while True:
    index = child.expect(["FIRST PRINT FIELD:",
                          "WITHIN NAME, SORT BY:"])
    if index == 0:
      child.send("NAME\r")
      break
    if index == 1:
      child.send("\r")
      continue
  child.expect("THEN PRINT FIELD:")
  child.send("\r")
  child.expect("ROUTINE LIST//")
  child.send("\r")
  child.expect("DEVICE:")
  child.send(";132;99999\r")
  child.expect("Select OPTION:")
  child.send("\r")
  child.expect("[A-Za-z0-9]+>")
  child.send("HALT\r")
  child.terminate()

if __name__ == '__main__':
  print ("sys.argv is %s" % sys.argv)
  if len(sys.argv) <= 1:
    print ("Need at least two arguments")
    sys.exit()
  expectConn = None
  if len(sys.argv) > 2:
    system = int(sys.argv[1])
    if system == 1:
      expectConn = createExpectConnection()
    elif system == 2:
      expectConn = createExpectConnectionCacheLinux()
    elif system == 3:
      expectConn = createExpectConnection()
    else:
      sys.exit()
  GetAllRoutines(expectConn, sys.argv[2])
