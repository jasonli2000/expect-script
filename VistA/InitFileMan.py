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

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
  from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
except ImportError:
  from pexpect import TIMEOUT, EOF, ExceptionPexpect
  pass
from CreateConnection import createExpectConnection
import argparse

def inputMumpsSystem(connection, system):
  if system == 1 or system == 2: # this is the Cache
    connection.send("CACHE\r")
  elif system == 3: # this is GT.M(UNIX)
    connection.send("GT.M(UNIX)\r")
  else:
    pass
  return

def initFileMan(connection, logFile, siteName, siteNumber,
                system, zuSet=True):
  try:
    connection.logfile = open(logFile, 'wb')
    connection.expect("[A-Za-z0-9]+>")
    connection.send("D ^DINIT\r")
    connection.expect("Initialize VA FileMan now?")
    connection.send("YES\r")
    connection.expect("SITE NAME:")
    connection.send(siteName+"\r")
    connection.expect("SITE NUMBER")
    connection.send(str(siteNumber)+"\r")
    connection.expect("Do you want to change the MUMPS OPERATING SYSTEM File?")
    connection.send("NO\r")
    connection.expect("TYPE OF MUMPS SYSTEM YOU ARE USING:")
    inputMumpsSystem(connection, system)
    connection.expect("[A-Za-z0-9]+>")
    if not zuSet:
      return
    connection.send("D ^ZUSET\r")
    connection.expect("Rename")
    connection.send("YES\r")
    connection.expect("[A-Za-z0-9]+>")
  except TIMEOUT:
    print "TimeOut"
    print str(child)
    connection.terminate()
  except ExceptionPexpect:
    connection.terminate()
  except EOF:
    connection.terminate()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Initiate FileMan')
  parser.add_argument('-s', required=True, dest='siteName',
                      help='setup the site name')
  parser.add_argument('-n', required=True, dest="stationNumber", type=int,
                      help="setup the station number")
  parser.add_argument('-m', required=True, dest="mumpsSystem", choices='123',
                      help="1. Cache/Windows, 2. Cache/Linux 3. GTM/Linux")
  parser.add_argument('-l', required=True, dest="logFile",
                      help="where to store the log file")
  result = vars(parser.parse_args());
  print (result)
  expectConn = None
  system = int(result['mumpsSystem'])
  expectConn = createExpectConnection(system)
  if not expectConn:
    sys.exit(-1)
  initFileMan(expectConn, result['logFile'],
                          result['siteName'],
                          result['stationNumber'],
                          system)
