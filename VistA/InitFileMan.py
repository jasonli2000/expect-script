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
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pexpect import TIMEOUT, EOF, ExceptionPexpect
from VistATestClient import VistATestClient, VistATestClientFactory
import argparse

def inputMumpsSystem(connection, system):
  if system == 1: # this is the Cache
    connection.send("CACHE\r")
  elif system == 2: # this is GT.M(UNIX)
    connection.send("GT.M(UNIX)\r")
  else:
    pass
  return

def initFileMan(testClient, logFile, siteName, siteNumber,
                system, zuSet=True):
  connection = testClient.getConnection()
  try:
    connection.logfile = open(logFile, 'wb')
    testClient.waitForPrompt()
    connection.send("D ^DINIT\r")
    connection.expect("Initialize VA FileMan now?")
    connection.send("YES\r")
    connection.expect("SITE NAME:")
    if siteName and len(siteName) > 0:
      connection.send(siteName+"\r")
    else:
      connection.send("\r") # just use the default
    connection.expect("SITE NUMBER")
    if siteNumber and siteNumber != 0:
      connection.send(str(siteNumber)+"\r")
    else:
      connection.send("\r")
    connection.expect("Do you want to change the MUMPS OPERATING SYSTEM File?")
    connection.send("YES\r") # we want to change MUMPS OPERATING SYSTEM File
    connection.expect("TYPE OF MUMPS SYSTEM YOU ARE USING:")
    inputMumpsSystem(connection, system)
    testClient.waitForPrompt()
    if zuSet:
      connection.send("D ^ZUSET\r")
      connection.expect("Rename")
      connection.send("YES\r")
      testClient.waitForPrompt()
    connection.send("HALT\r")
    connection.terminate()    
  except TIMEOUT:
    print "TimeOut"
    print str(connection)
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
  parser.add_argument('-m', required=True, dest="mumpsSystem", choices='12',
                      help="1. Cache, 2. GTM")
  parser.add_argument('-l', required=True, dest="logFile",
                      help="where to store the log file")
  result = vars(parser.parse_args());
  print (result)
  expectConn = None
  system = int(result['mumpsSystem'])
  expectConn = VistATestClientFactory.createVistATestClient(system)
  if not expectConn:
    sys.exit(-1)
  initFileMan(expectConn, result['logFile'],
                          result['siteName'],
                          result['stationNumber'],
                          system)
