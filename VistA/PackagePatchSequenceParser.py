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

""" Class to find and store patch history for each package
"""
class PackagePatchSequenceParser(object):
  def __init__(self, testClient, logFileName):
    self._testClient = testClient
    self._logFileName = logFileName
    self._packageMapping = dict()
    self._packagePatchHist = dict()

  def getAllPackagesPatchHistory(self):
    self.createAllPackageMapping()
    for (package, namespace) in self._packageMapping.iteritems():
      print ("Parsing Package %s" % package)
      #if not (package[0] == "PHARMACY" and package[1] == "PS"): continue
      result = self.getPackagePatchHistory(package, namespace)
      self._packagePatchHist[package] = result
  
  def printPackagePatchHist(self, packageName):
    import pprint
    if packageName in self._packagePatchHist:
      pprint.pprint(self._packagePatchHist[packageName].patchHistory)

  def createAllPackageMapping(self):
    connection = self._testClient.getConnection()
    result = None
    connection.logfile = open(self._logFileName,'wb')
    self._testClient.waitForPrompt()
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
    self.__parseAllPackges__(connection.before)
    connection.send("\r")
    connection.logfile.close()

  def __parseAllPackges__(self, allPackageString):
    allLines = allPackageString.split('\r\n')
    packageStart = False
    for line in allLines:
      line = line.strip()
      if len(line) == 0:
        continue
      if re.search("^-+$", line):
        packageStart = True
        continue
      if packageStart:
        packageName = line[:32].strip()
        packageNamespace = line[32:].strip()
        self._packageMapping[packageName] = packageNamespace
        print ("Name is [%s], Namespace is [%s]" % (packageName, packageNamespace))

  def getPackagePatchHistory(self, packageName, namespace):
    connection = self._testClient.getConnection()
    result = None
    connection.logfile = open(self._logFileName,'ab')
    self._testClient.waitForPrompt()
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
    while True:
      index  = connection.expect(["Select VERSION: [0-9.]+\/\/",
                                  "Select VERSION: ",
                                  "Select Utilities Option:",
                                  "CHOOSE 1-"])
      if index == 3:
        outchoice = findChoiceNumber(connection.before, packageName, namespace)
        if outchoice:
          connection.send("%s\r" % outchoice)
        continue
      if index == 0 or index == 1:
        if index == 0:
          connection.send("\r")
        else:
          connection.send("1.0\r")
        connection.expect("Do you want to see the Descriptions\?")
        connection.send("\r")
        connection.expect("DEVICE:")
        connection.send(";132;99999\r")
        connection.expect("Select Utilities Option:")
        result = parseKIDSPatchHistory(connection.before, packageName, namespace)
        break
      else:
        break
    connection.send("\r")
    connection.expect("Select Kernel Installation \& Distribution System Option:")
    connection.send("\r")
    connection.expect("Select Programmer Options Option:")
    connection.send("\r")
    connection.expect("Select Systems Manager Menu Option:")
    connection.send("\r")
    connection.expect("Do you really want to halt?")
    connection.send("\r")
    connection.logfile.close()
    return result

  def __del__(self):
    if self._testClient:
      self._testClient.getConnection().terminate()

def findChoiceNumber(choiceTxt, matchString, namespace):
  print ("txt is [%s]" % choiceTxt)
  choiceLines = choiceTxt.split('\r\n')
  for line in choiceLines:
    if len(line.rstrip()) == 0:
      continue
    result = re.search('^ +(?P<number>[1-9])   %s +%s$' % (matchString, namespace), line)
    if result:
      print (line)
      return result.group('number')
    else:
      continue
  return None

class AllPackagePatchInfo(object):
  def __init__(self):
    pass
"""Store the Patch History related to a Package
"""
class PackagePatchHistory(object):
  def __init__(self, packageName, namespace):
    self.packageName = packageName
    self.namespace = namespace
    self.patchHistory = []
    self.version = None
  def addPatchInfo(self, PatchInfo):
    self.patchHistory.append(PatchInfo)
  def setVersion(self, version):
    self.version = version
  def __str__(self):
    return self.patchHistory.__str__()
  def __repr__(self):
    return self.patchHistory.__str__()

class PatchInfo(object):
  PATCH_HISTORY_LINE_REGEX = re.compile("^   [0-9]")
  PATCH_VERSION_LINE_REGEX = re.compile("^VERSION: [0-9.]+ ")
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
    self.version = None
    self.__parseHistoryLine__(historyLine)
  def __parseHistoryLine__(self, historyLine):
    totalLen = len(historyLine)
    if totalLen < self.PATCH_VERSION_START_INDEX:
      return
    if historyLine.find(";Created on") >=0: # ignore the Created on format
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
    if self.isVersionLine(historyLine):
      self.__parseVersionInfo__(historyLine[:self.PATCH_APPLIED_DATETIME_INDEX].strip())
      return
    patchPart = historyLine[self.PATCH_VERSION_START_INDEX:self.PATCH_APPLIED_DATETIME_INDEX]
    seqIndex = patchPart.find("SEQ #")
    if seqIndex >= 0:
      self.patchNo = int(patchPart[:seqIndex].strip())
      self.seqNo = int(patchPart[seqIndex+5:].strip())
    else:
      self.patchNo = int(patchPart.strip())
  
  def hasVersion(self):
    return self.version != None
  def __parseVersionInfo__(self, historyLine):
    self.seqNo = None
    self.patchNo = None
    self.version = historyLine[historyLine.find("VERSION: ")+9:]
  @staticmethod
  def isValidHistoryLine(historyLine):
    return PatchInfo.isPatchLine(historyLine) or PatchInfo.isVersionLine(historyLine) 
  @staticmethod
  def isPatchLine(patchLine):
    return PatchInfo.PATCH_HISTORY_LINE_REGEX.search(patchLine) != None
  @staticmethod
  def isVersionLine(versionLine):
    return PatchInfo.PATCH_VERSION_LINE_REGEX.search(versionLine) != None
  
  def __str__(self):
    retString = ""
    if self.version:
      retString += "Ver: %s " % self.version
    if self.patchNo:
      retString += "%d" % self.patchNo
    if self.seqNo:
      retString += " SEQ #%d" % self.seqNo
    if self.datetime:
      retString += " %s " % self.datetime.strftime(self.DATETIME_FORMAT_STRING)
    if self.userName:
      retString += " %s" % self.userName
    return retString
  def __repr__(self):
    return self.__str__()

def parseKIDSPatchHistory(historyString, packageName, namespace):
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
      if not result: result = PackagePatchHistory(packageName, namespace)
      patchInfo = PatchInfo(line)
      result.addPatchInfo(patchInfo)
      if patchInfo.hasVersion():
        result.setVersion(patchInfo.version)
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
  packagePatchHist = PackagePatchSequenceParser(testClient, sys.argv[2])
  packagePatchHist.getAllPackagesPatchHistory()
  packagePatchHist.printPackagePatchHist("TOOLKIT")
  testClient.getConnection().terminate()
