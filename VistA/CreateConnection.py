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
def createExpectConnectionWindows():
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

def createExpectConnection(option):
  expectConn = None
  if option == 1:
    expectConn = createExpectConnectionWindows()
  elif option == 2:
    expectConn = createExpectConnectionCacheLinux()
  elif option == 3:
    expectConn = createExpectConnectionGTMLinux()
  return expectConn
