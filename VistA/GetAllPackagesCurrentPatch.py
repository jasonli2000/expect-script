#---------------------------------------------------------------------------
# Copyright 2011-2012 The Open Source Electronic Health Record Agent
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
import re
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
  from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect
except ImportError:
  import pexpect
  from pexpect import TIMEOUT, EOF, ExceptionPexpect
  pass
from VistATestClient import VistATestClientFactory

def getAllPackagesPatchHistory(testClient, outputFile):
  #allPackages = GetAllPackages(testClient, outputFile)
  GetPackagePatchHistory(testClient, outputFile, "TOOLKIT")
  testClient.getConnection().terminate()
"""Return a list of tuple of 2 (PackageName, Primary Namespace)vs
on Error, just return None
"""
def GetAllPackages(testClient, outputFile):
  connection = testClient.getConnection()
  result = None
  try:
    connection.logfile = open(outputFile,'wb')
    testClient.waitForPrompt()
    connection.send("S DUZ=1 D Q^DI\r")
    connection.expect("Select OPTION:")
    # print file entry
    connection.send("2\r" )
    connection.expect("OUTPUT FROM WHAT FILE:")
    connection.send("9.4\r") # Package file with fileman #9.4
    connection.expect("SORT BY:")
    connection.send("\r")
    connection.expect("START WITH")
    connection.send("\r")
    connection.expect("FIRST PRINT FIELD:")
    connection.send(".01\r") # fileman field# .01 is NAME
    connection.expect("THEN PRINT FIELD:")
    connection.send("1\r") # fileman field# 1 is the PREFIX
    connection.expect("THEN PRINT FIELD:")
    connection.send("\r")
    connection.expect("PACKAGE LIST//")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send(";132;99999\r")
    connection.expect("Select OPTION:")
    result = parseAllPackges(connection.before)
    connection.send("\r")
    close(outputFile)
  except TIMEOUT:
    print "TimeOut"
    print str(connection)
    connection.terminate()
  except ExceptionPexpect:
    connection.terminate()
  except EOF:
    connection.terminate()
  return result

def parseAllPackges(allPackageString):
  allLines = allPackageString.split('\r\n')
  packageStart = False
  result = None
  for line in allLines:
    line = line.strip()
    if len(line) == 0:
      continue
    if re.search("^-+$", line):
      packageStart = True
      continue
    if packageStart:
      if not result: result = []
      result.append((line[:32].strip(), line[32:].strip()))
      print ("Name is [%s], Namespace is [%s]" % (line[:32].strip(), line[32:].strip()))
  return result

def GetPackagePatchHistory(testClient, outputFile, packageName):
  connection = testClient.getConnection()
  result = None
  try:
    connection.logfile = open(outputFile,'ab')
    testClient.waitForPrompt()
    connection.send("S DUZ=1 D ^XUP\r")
    connection.expect("Select OPTION NAME:")
    connection.send("EVE\r" )
    connection.expect("CHOOSE 1-")
    connection.send("1\r") # Package file with fileman #9.4
    connection.expect("Select Systems Manager Menu Option:")
    connection.send("Programmer\r")
    connection.expect("Select Programmer Options Option:")
    connection.send("KIDS\r")
    connection.expect("Select Kernel Installation \& Distribution System Option:")
    connection.send("Utilities\r")
    connection.expect("Select Utilities Option:")
    connection.send("Display\r")
    connection.expect("Select PACKAGE NAME:")
    connection.send("%s\r" % packageName)
    connection.expect("Select VERSION:")
    connection.send("\r")
    connection.expect("Do you want to see the Descriptions\?")
    connection.send("\r")
    connection.expect("DEVICE:")
    connection.send(";132;99999\r")
    connection.expect("Select Utilities Option:")
    result = parseKIDSPatchHistory(connection.before)
    connection.send("\r")
    connection.expect("Select Kernel Installation \& Distribution System Option:")
    connection.send("\r")
    connection.expect("Select Programmer Options Option:")
    connection.send("\r")
    connection.expect("Select Systems Manager Menu Option:")
    connection.send("\r")
    connection.expect("Do you really want to halt?")
    connection.send("\r")
  except TIMEOUT:
    print "TimeOut"
    print str(connection)
    connection.terminate()
  except ExceptionPexpect:
    connection.terminate()
  except EOF:
    connection.terminate()
  return result

class PatchInfo(object):
  PATCH_HISTORY_LINE_REGEX = re.compile("^   [0-9]")
  PATCH_VERSION_START_INDEX = 3
  PATCH_APPLIED_DATETIME_INDEX = 20
  PATCH_APPLIED_USERNAME_INDEX = 50
  
  DATETIME_FORMAT_STRING = "%b %d, %Y@%H:%M:%S"
  DATE_FORMAT_STRING = "%b %d, %Y"
  DATE_TIME_SEPERATOR = "@"
  def __init__(self, historyLine):
    self.patchNo = None
    self.seqNo = None
    self.datetime = None
    self.userName = None
    self.__parseHistoryLine__(historyLine)
  def __parseHistoryLine__(self, historyLine):
    totalLen = len(historyLine)
    if totalLen < self.PATCH_VERSION_START_INDEX:
      return
    if totalLen > self.PATCH_APPLIED_USERNAME_INDEX:
      self.userName = historyLine[self.PATCH_APPLIED_USERNAME_INDEX:].strip()
    if totalLen > self.PATCH_APPLIED_DATETIME_INDEX:
      datetimePart = historyLine[self.PATCH_APPLIED_DATETIME_INDEX:self.PATCH_APPLIED_USERNAME_INDEX].strip()
      pos = datetimePart.find(self.DATE_TIME_SEPERATOR)
      if pos >=0:
        if len(datetimePart) - pos == 3:
          datetimePart += ":00:00"
        if len(datetimePart) - pos == 6:
          datetimePart +=":00"
        self.datetime = datetime.strptime(datetimePart, self.DATETIME_FORMAT_STRING)
      else:
        self.datetime = datetime.strptime(datetimePart, self.DATE_FORMAT_STRING)
    patchPart = historyLine[self.PATCH_VERSION_START_INDEX:self.PATCH_APPLIED_DATETIME_INDEX]
    seqIndex = patchPart.find("SEQ #")
    if seqIndex >= 0:
      self.patchNo = int(patchPart[:seqIndex].strip())
      self.seqNo = int(patchPart[seqIndex+5:].strip())
    else:
      self.patchNo = int(patchPart.strip())
    
  @staticmethod
  def isValidHistoryLine(historyLine):
    return PatchInfo.PATCH_HISTORY_LINE_REGEX.search(historyLine) != None
  
  def __str__(self):
    retString = ""
    if self.patchNo:
      retString += "%d" % self.patchNo
    if self.seqNo:
      retString += " SEQ #%d" % self.seqNo
    if self.datetime:
      retString += ", %s" % self.datetime.strftime(self.DATETIME_FORMAT_STRING)
    if self.userName:
      retString += ", %s" % self.userName
    return retString
  def __repr__(self):
    return self.__str__()

def parseKIDSPatchHistory(historyString):
  allLines = historyString.split('\r\n')
  patchHistoryStart = False
  result = None
  for line in allLines:
    line = line.rstrip()
    if len(line) == 0:
      continue
    if re.search("^-+$", line):
      patchHistoryStart = True
      continue
    if patchHistoryStart:
      if not PatchInfo.isValidHistoryLine(line):
        continue
      if not result: result = []
      patchInfo = PatchInfo(line)
      result.append((patchInfo))
  if result:
    import pprint
    pprint.pprint(result)
  return result

if __name__ == '__main__':
  print ("sys.argv is %s" % sys.argv)
  if len(sys.argv) <= 1:
    print ("Need at least two arguments")
    sys.exit()
  testClient = None
  if len(sys.argv) > 2:
    system = int(sys.argv[1])
    testClient = VistATestClientFactory.createVistATestClient(system)
  if not testClient:
    sys.exit(-1)
  getAllPackagesPatchHistory(testClient, sys.argv[2])