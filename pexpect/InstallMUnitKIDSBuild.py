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

import pexpect
import sys

def createExpectConnection():
  child = pexpect.spawn("gtm")
  assert child.isalive()
  return child
def createExpectConnectionCacheLinux():
  child = pexpect.spawn("ccontrol session cache")
  assert child
  child.logfile = sys.stdout
  child.expect("Username:")
  child.send("admin\r")
  child.expect("Password:")
  child.send("cache\r")
  return child

def installMUnitKIDSbuild(child, kidsFile, kidsPackageName):
  child.expect("[A-Za-z0-9]+>")
  child.sendline("S DUZ=1 D ^XUP")
  child.expect("Select OPTION NAME:")
  child.send("EVE\r")
  child.expect("CHOOSE 1-")
  child.send("1\r")
  child.expect("Select Systems Manager Menu Option: ")
  child.sendline("Programmer Options")
  child.expect("Select Programmer Options Option: ")
  child.sendline("KIDS")
  child.expect("Select Kernel Installation & Distribution System Option: ")
  child.sendline("Installation")
  child.expect("Select Installation Option: ")
  child.sendline("1")
  child.expect("Enter a Host File:")
  child.sendline(kidsFile)
  while True:
    index = child.expect(["OK to continue with Load",
                          "Want to Continue with Load?",
                          "Select Installation Option:"])
    if index == 0:
      child.sendline("YES")
      continue
    elif index == 1:
      child.sendline("YES")
      continue
    else:
      child.sendline("Install")
      break

  child.expect("Select INSTALL NAME:")
  child.sendline(kidsPackageName)
  child.expect("Want KIDS to Rebuild Menu Trees Upon Completion of Install?")
  child.sendline("NO")
  child.expect("Want KIDS to INHIBIT LOGONs during the install?")
  child.sendline("NO")
  child.expect("Want to DISABLE Scheduled Options, Menu Options, and Protocols?")
  child.sendline("NO")
  child.expect("DEVICE:")
  child.sendline("HOME;82;999")
  child.expect("Select Installation Option:")
  child.sendline()
  child.expect("Select Kernel Installation & Distribution System Option:")
  child.sendline()
  child.expect("Select Programmer Options Option:")
  child.sendline()
  child.expect("Select Systems Manager Menu Option:")
  child.sendline()
  index = child.expect(["[A-Za-z0-9]+>", "Do you really want to halt?"])
  if index == 0:
    child.sendline("HALT")
  elif index == 1:
    child.sendline("YES")

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
  installMUnitKIDSbuild(expectConn, sys.argv[2],
                        sys.argv[3])
