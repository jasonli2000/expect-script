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
from pexpect import TIMEOUT, EOF, ExceptionPexpect
from VistATestClient import VistATestClient, VistATestClientFactory
import argparse

def startTaskMan(testClient, logFile):
  connection = testClient.getConnection()
  connection.logfile = open(logFile, 'wb')
  testClient.waitForPrompt()
  connection.send("S DUZ=1 D ^XUP\r") # program menu
  connection.expect("Select OPTION NAME:")
  connection.send("EVE\r") # Systems Manager Menu
  connection.expect("CHOOSE 1-\d+:")
  connection.send("1\r") # Systems Manager Menu
  connection.expect("Select Systems Manager Menu Option:")
  connection.send("Taskman Management\r") 
  connection.expect("Select Taskman Management Option:")
  connection.send("Taskman Management Utilities\r") 
  connection.expect("Select Taskman Management Utilities Option:")
  connection.send("Restart Task Manager\r") 
  index = connection.expect(["ARE YOU SURE YOU WANT TO RESTART ANOTHER TASKMAN\?",
                             "ARE YOU SURE YOU WANT TO RESTART TASKMAN\?"])
  if index == 0:
    connection.send("NO\r")
  elif index == 1:
    connection.send("YES\r")
    connection.expect("Restarting...TaskMan restarted\!")
  connection.expect("Select Taskman Management Utilities Option:")
  connection.send("\r") 
  connection.expect("Select Taskman Management Option:")
  connection.send("\r") 
  connection.expect("Select Systems Manager Menu Option:")
  connection.send("\r") # Systems Manager Menu
  connection.expect("Do you really want to halt\?")
  connection.send("YES\r") # Systems Manager Menu
  testClient.waitForPrompt()
  connection.send("HALT\r")

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Start TaskMan')
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
  startTaskMan(expectConn, result['logFile'])
