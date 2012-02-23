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

def createExpectConnectionGTMLinux():
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
def createExpectConnection():
  child = winspawn("C:/users/jason.li/Downloads/apps/plink.exe -telnet 127.0.0.1 -P 23")
  assert child.isalive()
  child.expect("[A-Za-z0-9]+>")
  child.send("znspace \"VISTA\"\r")
  return child

def listFileManFileAttributes(child, FileManNo, outputFile):
  child.logfile = open(outputFile,'wb')
  child.expect("[A-Za-z0-9]+>")
  child.send("S DUZ=1 D Q^DI\r")
  child.expect("Select OPTION:")
  # data dictionary utilities
  child.send("8\r" )
  child.expect("Select DATA DICTIONARY UTILITY OPTION:")
  child.send("1\r")
  child.expect("START WITH WHAT FILE:")
  child.send(FileManNo + "\r")
  child.expect("GO TO WHAT FILE:")
  child.send(FileManNo + "\r")
  while True:
    index = child.expect(["Select SUB-FILE:",
                          "Select LISTING FORMAT:"])
    if index == 0:
      child.send("\r")
      continue
    else: 
      # brief format 2, condensed 7, standard 1
      child.send("1\r")
      break
  while True:
    index = child.expect(["ALPHABETICALLY BY LABEL?",
                          "Start with field:",
                          "DEVICE:"])
    if index == 0:
      child.send("No\r")
      continue
    elif index == 1:
      # using default
      child.send("\r")
      continue
    else:
      child.send("HOME;132;999\r")
      break
  child.send("\r")
  child.expect("Select DATA DICTIONARY UTILITY OPTION:")
  child.send("\r")
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
      expectConn = createExpectConnectionGTMLinux()
    else:
      sys.exit()
  listFileManFileAttributes(expectConn, sys.argv[2],
                            sys.argv[3])
