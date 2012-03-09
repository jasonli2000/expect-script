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
try:
  from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
except ImportError:
  import pexpect
  pass
import sys
from CreateConnection import createExpectConnection

def getRPCReferenceFromOptionFile(child, outputFile):
  try:
    child.logfile = open(outputFile,'wb')
    child.expect("[A-Za-z0-9]+>")
    child.send("S DUZ=1 D Q^DI\r")
    child.expect("Select OPTION:")
    # search file entry
    child.send("3\r" )
    child.expect("OUTPUT FROM WHAT FILE:")
    child.send("19\r")
    child.expect("-A- SEARCH FOR OPTION FIELD:")
    child.send("TYPE\r")
    child.expect("-A- CONDITION:")
    child.send("EQUALS\r")
    child.expect("-A- EQUALS:")
    child.send("B\r")
    child.expect("-B- SEARCH FOR OPTION FIELD:")
    child.send("\r")
    child.expect("IF:")
    child.send("\r")
    child.expect("STORE RESULTS OF SEARCH IN TEMPLATE:")
    child.send("\r")
    child.expect("SORT BY:")
    child.send("NAME\r")
    child.expect("START WITH NAME:")
    child.send("\r")
    child.expect("WITHIN NAME, SORT BY:")
    child.send("\r")
    child.expect("FIRST PRINT FIELD:")
    child.send("NAME\r")
    child.expect("THEN PRINT FIELD:")
    child.send("RPC\r")
    child.expect("THEN PRINT RPC SUB-FIELD:")
    child.send(".01\r")
    child.expect("THEN PRINT RPC SUB-FIELD:")
    child.send("\r")
    child.expect("THEN PRINT FIELD:")
    child.send("\r")
    child.expect("Heading \(S\/C\):")
    child.send("\r")
    child.expect("DEVICE:")
    child.send(";;9999\r")
    child.send("\r")
    child.expect("Select OPTION:")
    child.send("\r")
    child.expect("[A-Za-z0-9]+>")
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
    expectConn = createExpectConnection(system)
  if not expectConn:
    sys.exit(-1)
  getRPCReferenceFromOptionFile(expectConn, sys.argv[2])
