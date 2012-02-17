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

from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
import sys

def createExpectConnection():

  child = winspawn("C:/users/jason.li/Downloads/apps/plink.exe -telnet 127.0.0.1 -P 23")
  #child = winspawn("C:/InterSystems/TryCache/bin/cterm /console=cn_iptcp:127.0.0.1[23]")
  #child = pexpect.spawn("gtm")
  assert child.isalive()
  child.expect("[A-Za-z0-9]+>")
  child.send("znspace \"VISTA\"\r")
  return child
def installMUnitKIDSbuild(child, kidsFile, kidsPackageName):
  try:
    #child.logfile = open("c:/Temp/KidsInstallation.log", "wb")
    child.logfile = sys.stdout
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
  expectConn = createExpectConnection()
  installMUnitKIDSbuild(expectConn, "/home/softhat/temp/XT_7-3_81_TESTVER9.KID",
                        "XT*7.3*81")
