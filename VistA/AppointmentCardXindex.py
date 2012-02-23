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

def createExpectConnectionGTMLinux():
  child = pexpect.spawn("gtm")
  assert child.isalive()
  return child
def createExpectConnection():

  child = winspawn("C:/users/jason.li/Downloads/apps/plink.exe -telnet 127.0.0.1 -P 23")
  assert child.isalive()
  child.expect("[A-Za-z0-9]+>")
  child.send("znspace \"VISTA\"\r")
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
    if system == 1:
      expectConn = createExpectConnection()
    elif system == 2:
      expectConn = createExpectConnectionCacheLinux()
    elif system == 3:
      expectConn = createExpectConnectionGTMLinux()
    else:
      sys.exit()
  AppointmentCardXindex(expectConn, sys.argv[2])
                        
