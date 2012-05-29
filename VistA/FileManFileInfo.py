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
from __future__ import with_statement
from pexpect import TIMEOUT, EOF, ExceptionPexpect
import sys
from VistATestClient import VistATestClient, VistATestClientFactory

def getFileManAllFileInfo(testClient, outputFile, logFile):
  child = testClient.getConnection()
  try:
    child.logfile = open(logFile,'wb')
    testClient.waitForPrompt()
    child.send("S DUZ=1 D Q^DI\r")
    child.expect("Select OPTION:")
    # print file entry
    child.send("2\r" )
    child.expect("OUTPUT FROM WHAT FILE:")
    child.send("1\r")
    child.expect("SORT BY:")
    child.send("@NUMBER\r")
    child.expect("START WITH NUMBER:")
    child.send("\r")
    child.expect("WITHIN NUMBER, SORT BY:")
    child.send("\r")
    child.expect("FIRST PRINT ATTRIBUTE:")
    child.send("NUMBER\r")
    child.expect("THEN PRINT ATTRIBUTE:")
    child.send("NAME\r")
    child.expect("THEN PRINT ATTRIBUTE:")
    child.send("GLOBAL NAME\r")
    #child.expect("THEN PRINT ATTRIBUTE:")
    #child.send("DESCRIPTION\r")
    child.expect("THEN PRINT ATTRIBUTE:")
    child.send("\r")
    while True:
      index = child.expect(["Heading \(S\/C\):",
                            "STORE PRINT LOGIC IN TEMPLATE:",
                            "DEVICE:",
                            "HOST FILE NAME:",
                            "ADDRESS\/PARAMETERS:"])
      if index == 0 or index == 1 or index == 4:
        child.send("\r")
        if index == 4:
          break
        else:
          continue
      elif index == 2:
        child.send("HFS;999;9999\r")
        continue
      elif index == 3:
        child.send("%s\r" % outputFile)
        continue
    child.send("\r")
    child.expect("Select OPTION:")
    child.send("\r")
    testClient.waitForPrompt()
    child.send("HALT\r")
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
  if len(sys.argv) <= 1:
    print ("Need at least two arguments")
    sys.exit()
  expectConn = None
  if len(sys.argv) > 2:
    system = int(sys.argv[1])
    expectConn = VistATestClientFactory.createVistATestClient(system)
  if not expectConn:
    sys.exit(-1)
  getFileManAllFileInfo(expectConn, sys.argv[2], sys.argv[3])
