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

def AppointmentCardXindex(child, logFileName):
  try:
    child.logfile = open(logFileName,'wb')
    child.expect("[A-Za-z0-9]+>")
    child.send("D ^XINDEX\r")
    child.expect("All Routines?")
    child.send("NO\r")
    child.expect("Routine:")
    child.send("R1*\r")
    child.expect("Routine:")
    child.send("\r")
    child.expect("Select BUILD NAME:")
    child.send("\r")
    child.expect("Select PACKAGE NAME:")
    child.send("\r")
    child.expect("Print more than compiled errors and warnings?")
    child.send("YES\r")
    child.expect("Print summary only?")
    child.send("NO\r")
    child.expect("Print routines?")
    child.send("YES\r")
    child.expect("Print ")
    child.send("R\r")
    child.expect("Print errors and warnings with each routine?")
    child.send("YES\r")
    child.expect("Index all called routines?")
    child.send("NO\r")
    child.expect("DEVICE:")
    child.send("HOME;132;99999\r")
    while True:
      index = child.expect(["VISTA>",
                            "Press return to continue:"] )
      if index == 0:
        break
      if index == 1:
        child.send("\r")
        continue
    child.terminate()
  except TIMEOUT:
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
  AppointmentCardXindex(expectConn, sys.argv[2])
                        
