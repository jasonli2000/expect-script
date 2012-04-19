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

class AddSystemManager:
  def __init__(self, system, connection, logFile, name, initial, accCode, veriCode):
    self._system = system
    self._logFile = logFile
    self._connection = connection
    self._name = name
    self._initial = initial
    self._accCode = accCode
    self._veriCode = veriCode
    self.__setupSystemDependentParameter__()
    self._duz = 0
  def __setupSystemDependentParameter__(self):
    pass
  def run(self):
    connection = self._connection
    try:
      connection.logfile = open(self._logFile, 'wb')
      self.__addSystemManager__()
      self.__findoutSystemManagerDuz__()
      self.__setupSystemManagerKeyOptions__()
      self.__exit__()
      connection.terminate()
    except TIMEOUT:
      print "TimeOut"
      print str(connection)
      connection.terminate()
    except ExceptionPexpect:
      connection.terminate()
    except EOF:
      connection.terminate()

  def __gotoEditNewPersonOption__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("1\r")
    connection.expect("INPUT TO WHAT FILE:")
    connection.send("200\r") # fileman file for new person

  def __exit__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("HALT\r")

  def __addSystemManager__(self):
    self.__gotoEditNewPersonOption__()
    connection = self._connection
    connection.expect("EDIT WHICH FIELD:")
    connection.send(".01\r") # name
    connection.expect("THEN EDIT FIELD:")
    connection.send("CPRS TAB\r") # name
    connection.expect("EDIT WHICH CPRS TAB SUB-FIELD:")
    connection.send(".01\r") # CPRS TAB
    connection.expect("THEN EDIT CPRS TAB SUB-FIELD:")
    connection.send("\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("PRIMARY MENU OPTION\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("SECONDARY MENU OPTIONS\r")
    connection.expect("EDIT WHICH SECONDARY MENU OPTIONS SUB-FIELD:")
    connection.send(".01\r") # Secondary menu options
    connection.expect("THEN EDIT SECONDARY MENU OPTIONS SUB-FIELD:")
    connection.send("\r") # Secondary menu options
    for item in ["DISUSER", "RESTRICT PATIENT SELECTION", "AUTHORIZED TO WRITE MED ORDERS"]:
      connection.expect("THEN EDIT FIELD:")
      connection.send(item + "\r") 
    connection.expect("THEN EDIT FIELD:")
    connection.send("PERSON CLASS\r") # Person Class
    connection.expect("EDIT WHICH PERSON CLASS SUB-FIELD:")
    connection.send(".01\r") # name
    connection.expect("THEN EDIT PERSON CLASS SUB-FIELD:")
    connection.send("\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("ACCESS CODE\r") # name
    connection.expect("THEN EDIT FIELD:")
    connection.send("VERIFY CODE\r")
    connection.expect("CHOOSE 1-2:")
    connection.send("1\r")
    connection.expect("THEN EDIT FIELD:")
    connection.send("\r")
    connection.expect("STORE THESE FIELDS IN TEMPLATE:")
    connection.send("\r")
    connection.expect("Select NEW PERSON NAME")
    connection.send(self._name + "\r")
    while True:
      index = connection.expect(["Are you adding \'%s\' as a new NEW PERSON" % self._name,
                                 "Do you still want to add this entry",
                                 "NEW PERSON INITIAL:",
                                 "NEW PERSON MAIL CODE:",
                                 "NAME: "])
      if index == 0:
        connection.send("YES\r")
        continue
      if index == 1:
        connection.send("YES\r")
        continue
      if index == 2:
        connection.send(self._initial + "\r")
        continue
      if index == 3:
        connection.send("\r")
        break
      if index == 4:
        connection.send("\r")
        break
    # handle CPRS TAB
    connection.expect("Select CPRS TAB:")
    connection.send("COR\r")
    while True:
      index = connection.expect(["Are you adding 'COR'",
                                 "...OK\?",
                                 "CPRS TAB:"])
      if index == 0:
        connection.send("YES\r")
        break
      elif index == 1:
        connection.send("YES\r")
        continue
      elif index == 2:
        connection.send("\r")
        break
    connection.expect("Select CPRS TAB:")
    connection.send("\r")
    # handle primary and secondary menu options
    connection.expect("PRIMARY MENU OPTION:")
    connection.send("EVE\r")
    connection.expect("CHOOSE 1-")
    connection.send("1\r")
    for item in ("OR CPRS GUI CHART", "MANAGE MAILMAN"):
      connection.expect("Select SECONDARY MENU OPTIONS:")
      connection.send(item + "\r")
      while True:
        index = connection.expect(["Are you adding",
                                   "...OK\?"])
        if index == 0:
          connection.send("YES\r")
          break
        if index == 1:
          connection.send("YES\r")
          connection.expect("SECONDARY MENU OPTIONS:")
          connection.send("\r")
          break
    connection.expect("Select SECONDARY MENU OPTIONS:")
    connection.send("\r")
    # handle DISUSER, RESTRICT PATIENT SELECTION, AUTHORIZED TO WRITE MED ORDERS
    for items in (("DISUSER","NO"),
                  ("RESTRICT PATIENT SELECTION","NO"),
                  ("AUTHORIZED TO WRITE MED ORDERS","YES")):
      connection.expect(items[0])
      connection.send(items[1] + "\r")
    # handle person class
    connection.expect("Select Person Class:")
    connection.send("PHYSICIAN\r")
    while True:
      index = connection.expect(["Are you adding",
                                 "CHOOSE 1-",
                                 "...OK\?",
                                 "Person Class:"])
      if index == 0:
        connection.send("YES\r")
        break
      elif index == 1:
        connection.send("1\r")
        continue
      elif index == 2:
        connection.send("YES\r")
        continue
      elif index == 3:
        connection.send("\r")
        break
    # handle access and verify code section    
    connection.expect("Want to edit ACCESS CODE")
    connection.send("YES\r")
    connection.expect("Enter a new ACCESS CODE")
    connection.send(self._accCode + "\r")
    isUsed = False
    while True:
      index = connection.expect(["Please re-type the new code",
                                 "This has been used previously",
                                 "Enter a new ACCESS CODE"])
      if index == 0:
        connection.send(self._accCode + "\r")
        break
      if index == 1:
        print ("Access code has been used before")
        continue
      if index == 2:
        connection.send("\r")
        break
    connection.expect("Want to edit VERIFY CODE")
    connection.send("YES\r")
    connection.expect("Enter a new VERIFY CODE")
    connection.send(self._veriCode + "\r")
    while True:
      index = connection.expect(["Please re-type the new code",
                                 "This has been used previously",
                                 "Enter a new VERIFY CODE"])
      if index == 0:
        connection.send(self._veriCode + "\r")
        break
      if index == 1:
        print ("Verify code has been used before")
        continue
      if index == 2:
        connection.send("\r")
        break
    connection.expect("Select NEW PERSON NAME:")
    connection.send("\r")
    connection.expect("Select OPTION:")
    connection.send("\r")

  def __setupSystemManagerKeyOptions__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=%s\r" % self._duz)
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S $P(^VA(200,%s,0),\"^\",4)=\"@\"\r" % self._duz)
    connection.expect("[A-Za-z0-9]+>")
    connection.send("D ^XUP\r")
    while True:
      index = connection.expect(["Select TERMINAL TYPE NAME:",
                                 "Terminal Type set to:"])
      if index == 0:
        connection.send("C-VT100\r")
        connection.expect("CHOOSE 1-")
        connection.send("1\r")
        continue
      else:
        break
    connection.expect("Select OPTION NAME:")
    connection.send("XUMAINT\r") # Menu Management
    connection.expect("Select Menu Management Option:")
    connection.send("KEY Management\r")
    connection.expect("Select Key Management Option:")
    connection.send("Allocation\r")
    connection.expect("Allocate key:")
    connection.send("XUPROG\r")
    connection.expect("CHOOSE 1-2:")
    connection.send("1\r")
    for item in ["XMMGR", "XUPROGMODE", "XUMGR", ""]:
      connection.expect("Another key:")
      connection.send(item + "\r")
    connection.expect("Holder of key:")
    connection.send(self._name + "\r")
    connection.expect("Another holder:")
    connection.send("\r")
    connection.expect("Do you wish to proceed\?")
    connection.send("YES\r")
    connection.expect("Select Key Management Option:")
    connection.send("\r")
    connection.expect("Select Menu Management Option:")
    connection.send("\r")
    connection.expect("Do you really want to halt\?")
    connection.send("YES\r")
    
  def __findoutSystemManagerDuz__(self):
    connection = self._connection
    connection.expect("[A-Za-z0-9]+>")
    connection.send("S DUZ=1 D P^DI\r")
    connection.expect("Select OPTION:")
    connection.send("5\r")
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("200\r")
    connection.expect("Select NEW PERSON NAME:")
    connection.send(self._name + "\r")
    connection.expect("ANOTHER ONE:")
    connection.send("\r")
    connection.expect("STANDARD CAPTIONED OUTPUT\?")
    connection.send("YES\r")
    connection.expect("Include COMPUTED fields:")
    connection.send("B\r")
    connection.expect("DISPLAY AUDIT TRAIL\?")
    connection.send("\r")
    connection.expect("NUMBER: \d+")
    self._duz = connection.after.strip()[8:]
    print ("[%s] - [%s]" % (connection.after, self._duz))
    while True:
      index = connection.expect(["Enter RETURN to continue or",
                                 "Select NEW PERSON NAME:"])
      if index == 0:
        connection.send("^\r")
        break
      if index == 1:
        connection.send("\r")
        break
    connection.expect("Select OPTION:")
    connection.send("\r")
def findoutSystemManagerDuz(connection, name):
  connection.expect("[A-Za-z0-9]+>")
  connection.send("S DUZ=1 D P^DI\r")
  connection.expect("Select OPTION:")
  connection.send("5\r")
  connection.expect("OUTPUT FROM WHAT FILE:")
  connection.send("200\r")
  connection.expect("Select NEW PERSON NAME:")
  connection.send(name + "\r")
  connection.expect("ANOTHER ONE:")
  connection.send("\r")
  connection.expect("STANDARD CAPTIONED OUTPUT\?")
  connection.send("YES\r")
  connection.expect("Include COMPUTED fields:")
  connection.send("B\r")
  connection.expect("DISPLAY AUDIT TRAIL\?")
  connection.send("\r")
  connection.expect("NUMBER: \d+")
  duz = connection.after.strip()[8:]
  print ("[%s] - [%s]" % (connection.after, duz))
  connection.expect("Enter RETURN to continue or")
  connection.send("^\r")
  connection.expect("Select OPTION:")
  connection.send("\r")
  connection.expect("[A-Za-z0-9]+>")
  connection.send("HALT\r")

def testFindoutSystemManagerDuz():
  expectConn = None
  expectConn = createExpectConnection(3)
  if not expectConn:
    sys.exit(-1)
  findoutSystemManagerDuz(expectConn, "TESTUSER,SIXTY")

if __name__ == '__main__':
  #testFindoutSystemManagerDuz()
  #sys.exit(0)
  parser = argparse.ArgumentParser(description='Setup System Manager')
  parser.add_argument('-N', dest='Name', required=True, help='Name')
  parser.add_argument('-I', dest='Initial', required=True, help='Initial')
  parser.add_argument('-A', dest='accCode', required=True, help='access code')
  parser.add_argument('-V', dest='veriCode', required=True, help='verification code')
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
  setupManager = AddSystemManager(system, expectConn, result['logFile'],
                          result['Name'],
                          result['Initial'],
                          result['accCode'],
                          result['veriCode'])
  setupManager.run()
