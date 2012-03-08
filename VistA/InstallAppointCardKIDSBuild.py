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

import sys
from CreateConnection import createExpectConnection
from DefaultKIDSBuildInstallation import DefaultKIDSBuildInstallation

class AppointCardKIDSBuild(DefaultKIDSBuildInstallation):
  def __init__(self, kidsFile, kidsPackageName, logFile = None):
    DefaultKIDSBuildInstallation.__init__(self,
                                          kidsFile,
                                          kidsPackageName,
                                          logFile)
  def handleKIDSBuildMenuOption(self, connection):
    connection.expect("Incoming Mail Groups:")
    connection.send("\r")
    connection.expect("Enter the Coordinator for Mail Group")
    connection.send("\r")

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
  logFile = None
  if len(sys.argv) > 4:
    logFile = sys.argv[4]
  appointCardKidsBuild = AppointCardKIDSBuild(sys.argv[2],
                                              sys.argv[3],
                                              logFile)
  appointCardKidsBuild.runInstallation(expectConn, False)
