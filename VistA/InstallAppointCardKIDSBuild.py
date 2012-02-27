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

def installAppointCardKIDSBuild(child, kidsFile, kidsPackageName, logFile):
  try:
    child.logfile = open(logFile, "wb")
    child.expect("[A-Za-z0-9]+>")
    child.send("S DUZ=1 D ^XUP\r")
    child.expect("Select OPTION NAME: ")
    child.send("EVE\r")
    child.expect("CHOOSE 1-")
    child.send("1\r")
    child.expect("Select Systems Manager Menu Option: ")
    child.send("Programmer Options\r")
    child.expect("Select Programmer Options Option: ")
    child.send("KIDS\r")
    child.expect("Select Kernel Installation & Distribution System Option: ")
    child.send("Installation\r")
    child.expect("Select Installation Option: ")
    child.send("1\r")
    child.expect("Enter a Host File:")
    child.send(kidsFile+"\r")
    while True:
      index = child.expect(["OK to continue with Load",
                            "Want to Continue with Load?",
                            "Select Installation Option:"])
      if index == 0:
        child.send("YES\r")
        continue
      elif index == 1:
        child.send("YES\r")
        continue
      else:
        child.send("Install\r")
        break
    child.expect("Select INSTALL NAME:")
    child.send(kidsPackageName+"\r")
    child.expect("Want KIDS to Rebuild Menu Trees Upon Completion of Install?")
    child.send("NO\r")
    child.expect("Want KIDS to INHIBIT LOGONs during the install?")
    child.send("NO\r")
    child.expect("Want to DISABLE Scheduled Options, Menu Options, and Protocols?")
    child.send("NO\r")
    child.expect("DEVICE:")
    child.send("HOME;82;999\r")
    child.expect("Select Installation Option:")
    child.send("\r")
    child.expect("Select Kernel Installation & Distribution System Option:")
    child.send("\r")
    child.expect("Select Programmer Options Option:")
    child.send("\r")
    child.expect("Select Systems Manager Menu Option:")
    child.send("\r")
    index = child.expect(["[A-Za-z0-9]+>", "Do you really want to halt?"])
    if index == 0:
      child.send("HALT\r")
    elif index == 1:
      child.send("YES\r")
    if not child.isalive():
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
  installAppointCardKIDSBuild(expectConn, sys.argv[2],
                              sys.argv[3], sys.argv[4])
