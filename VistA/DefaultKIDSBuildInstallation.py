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

class DefaultKIDSBuildInstallation:
  def __init__(self, kidsFile, kidsPackageName, logFile = None):
    self._kidsFile = kidsFile
    self._kidsPackageName = kidsPackageName
    self._logFile = logFile

  def __setupLogFile__(self, connection):
    if self._logFile:
      connection.logfile = open(self._logFile, "wb")
    else:
      connection.logfile = sys.stdout
  
  def __gotoKIDSInstallationMenu__(self, connection):
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D ^XUP\r")
    connection.expect("Select OPTION NAME: ")
    connection.send("EVE\r")
    connection.expect("CHOOSE 1-")
    connection.send("1\r")
    connection.expect("Select Systems Manager Menu Option: ")
    connection.send("Programmer Options\r")
    connection.expect("Select Programmer Options Option: ")
    connection.send("KIDS\r")

  def __preLoadKIDSFile__(self, connection):
    connection.expect("Select Kernel Installation & Distribution System Option: ")
    connection.send("Installation\r")
    connection.expect("Select Installation Option: ")
    connection.send("1\r")
    connection.expect("Enter a Host File:")
    connection.send(self._kidsFile+"\r")
  
  def __installKIDSPackage__(self, connection):
    connection.expect("Select INSTALL NAME:")
    connection.send(self._kidsPackageName+"\r")
    self.handleKIDSBuildMenuOption(connection)
    connection.expect("Want KIDS to Rebuild Menu Trees Upon Completion of Install?")
    connection.send("NO\r")
    connection.expect("Want KIDS to INHIBIT LOGONs during the install?")
    connection.send("NO\r")
    connection.expect("Want to DISABLE Scheduled Options, Menu Options, and Protocols?")
    connection.send("NO\r")
 
  def __handleKIDSLoadOptions__(self, connection, reinst):
    while True:
      index = connection.expect(["OK to continue with Load",
                            "Want to Continue with Load?",
                            "Select Installation Option:",
                            self._kidsPackageName + "   Install Completed"])
      if index == 0:
        connection.send("YES\r")
        continue
      elif index == 1:
        connection.send("YES\r")
        continue
      elif index == 2:
        connection.send("Install\r")
        break
      else:
        if not reinst:
          return False
    return True

  def __setupDevice__(self, connection):
    connection.expect("DEVICE:")
    connection.send("HOME;82;999\r")
  
  def __postKIDSBuildInstallation__(self, connection):
      connection.expect("Select Installation Option:")
      connection.send("\r")
      connection.expect("Select Kernel Installation & Distribution System Option:")
      connection.send("\r")
      connection.expect("Select Programmer Options Option:")
      connection.send("\r")
      connection.expect("Select Systems Manager Menu Option:")
      connection.send("\r")
      index = connection.expect(["[A-Za-z0-9]+>", "Do you really want to halt?"])
      if index == 0:
        connection.send("HALT\r")
      elif index == 1:
        connection.send("YES\r")
  def handleKIDSBuildMenuOption(self, connection):
    pass
  def runInstallation(self, connection, reinst=True):
    try:
      self.__setupLogFile__(connection)
      self.__gotoKIDSInstallationMenu__(connection)
      self.__preLoadKIDSFile__(connection)
      result = self.__handleKIDSLoadOptions__(connection, reinst)
      if result:
        self.__installKIDSPackage__(connection)
        self.__setupDevice__(connection)
        self.__postKIDSBuildInstallation__(connection)
      connection.terminate()
    except TIMEOUT:
      print "TimeOut"
      print str(connection)
      connection.terminate()
    except ExceptionPexpect:
      connection.terminate()
    except EOF:
      connection.terminate()
