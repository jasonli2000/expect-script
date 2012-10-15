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
import glob
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from VistATestClient import VistATestClientFactory
from DefaultKIDSBuildInstallation import DefaultKIDSBuildInstallation
import logging
import sys
logger = logging.getLogger()

def initConsoleLogging(defaultLevel=logging.INFO,
                       formatStr = '%(asctime)s %(levelname)s %(message)s'):
    logger.setLevel(defaultLevel)
    consoleHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(formatStr)
    consoleHandler.setLevel(defaultLevel)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(consoleHandler)

def initFileLogging(outputFileName, defaultLevel=logging.INFO,
                    formatStr = '%(asctime)s %(levelname)s %(message)s'):
    logger.setLevel(defaultLevel)
    fileHandle = logging.FileHandler(outputFileName, 'w')
    formatter = logging.Formatter(formatStr)
    fileHandle.setLevel(defaultLevel)
    fileHandle.setFormatter(formatter)
    logger.addHandler(fileHandle)

""" Class to find and store patch history for each package
"""
class PackagePatchSequenceAnalyzer(object):
  DEFAULT_VISTA_LOG_FILENAME = "VISTA.log"
  DEFAULT_OUTPUT_FILE_LOG = "PatchAnalyzer.log"
  def __init__(self, testClient, logFileDir):
    self._testClient = testClient
    self._logFileName = os.path.join(logFileDir, self.DEFAULT_VISTA_LOG_FILENAME)
    self._packageMapping = dict()
    self._packagePatchHist = dict()
    self._outPatchList = []
    initConsoleLogging()
    initFileLogging(os.path.join(logFileDir, self.DEFAULT_OUTPUT_FILE_LOG))

  def generateKIDSPatchSequence(self, patchDir):
    kidsInfoParser = KIDSPatchInfoParser()
    (patchList, kidsDict) = kidsInfoParser.analyzeFOIAPatchDir(patchDir)
    outPatchList = []
    for patchInfo in patchList:
      packageName = patchInfo.package
      namespace = patchInfo.namespace
      self.getPackagePatchHistByNamespace(namespace)
      assert self._packageMapping[namespace] == packageName
      logger.info("Checking for patch info %s" % patchInfo)
      if self.isPatchReadyToInstall(patchInfo,
                                    self._packagePatchHist.get(packageName),
                                    kidsDict,
                                    patchList):
        outPatchList.append(patchInfo)
    logger.info("Total patches are %d" % len(outPatchList))
    for patchInfo in outPatchList:
      logger.info(patchInfo)
    self._outPatchList = outPatchList
  def applyKIDSPatchSequence(self):
    for patchInfo in self._outPatchList:
      """ need to corrent the patch install name for ver """
      logger.info("Applying KIDS Patch %s" % patchInfo)
      installName = patchInfo.installName
      (namespace,ver,patch) = installName.split("*")
      if ver.find(".") < 0:
        ver += ".0"
        installName = "%s*%s*%s" % (namespace, ver, patch)
      kidsInstaller = DefaultKIDSBuildInstallation(patchInfo.kidsFilePath,
                                                   installName, self._logFileName)
      result = kidsInstaller.runInstallation(self._testClient)
      if not result:
        logger.error("Failed to nstall patch %s: KIDS %s" %
                      (installName, patchInfo.kidsFilePath))
        break
  def hasPatchInstalled(self, namespace, version, patchNo):
    if namespace not in self._packageMapping:
      return False
    packageName = self._packageMapping[namespace]
    if packageName not in self._packagePatchHist:
      self.getPackagePatchHistByNamespace(namespace)
    patchHist = self._packagePatchHist[packageName]
    if patchHist.version:
      if float(patchHist.version) != float(version):
        logger.info("Diff ver %s, %s" % (patchHist.version, version))
        return False
    return patchHist.hasPatchNo(patchNo)
  def isPatchReadyToInstall(self, patchInfo, patchHist, kidsDict, patchList):
    if not patchHist or not patchHist.hasPatchHistory():
      logger.info("no patch hist for %s" % patchInfo.package)
      return True # if no such an package or hist info, just return True
    logger.debug("Checking %s, %s, %s" % (patchInfo.package, patchInfo.seqNo, patchInfo.installName))
    logger.debug("%s, %s" % (patchHist.getLastPatchInfo(), patchHist.getLatestSeqNo()))
    if patchHist.hasSeqNo(patchInfo.seqNo):
      logger.info("SeqNo %s is already installed" % patchInfo.seqNo)
      return False
    seqNo = patchHist.getLatestSeqNo()
    if patchInfo.seqNo < seqNo:
      logger.info("SeqNo %s less than latest one" % patchInfo.seqNo)
      return False
    # assume the patch no is the last part of the install name
    patchNo = patchInfo.installName.split("*")[-1]
    if patchHist.hasPatchNo(patchNo):
      logger.info("patchNo %s is already installed" % patchNo)
      return False
    # check all the dependencies
    for item in patchInfo.depKIDSPatch:
      if item in kidsDict: # we are going to install the dep patch
        """ make sure installation is in the right order """
        itemIndex = self.indexInPatchList(item, patchList)
        patchIndex = self.indexInPatchList(patchInfo.installName, patchList)
        if itemIndex >= patchIndex:
          logger.warn("%s is out of order with %s" % (item, patchInfo))
          return False
        else:
          continue
      (namespace, ver, patchNo) = item.split("*")
      if namespace == patchInfo.namespace:
        assert ver == patchInfo.version
        if not patchHist.hasPatchNo(patchNo):
          logger.warn("dep %s is not installed for %s %s" %
                      (item, patchInfo.installName, patchInfo.kidsFilePath))
          return False
      else:
        if not self.hasPatchInstalled(namespace, ver, patchNo):
          logger.warn("dep %s is not installed for %s %s" %
                      (item, patchInfo.installName, patchInfo.kidsFilePath))
          return False
    return True
  @staticmethod
  def indexInPatchList(installName, patchList):
    for index in range(0,len(patchList)):
      if patchList[index].installName == installName:
        return index
    return -1
  def getAllPackagesPatchHistory(self):
    self.createAllPackageMapping()
    for (namespace, package) in self._packageMapping.iteritems():
      logger.info("Parsing Package %s, namespace" % (package, namespace))
      #if not (package[0] == "PHARMACY" and package[1] == "PS"): continue
      result = self.getPackagePatchHistory(package, namespace)
      self._packagePatchHist[package] = result

  def getPackagePatchHistByName(self, packageName):
    if not self._packageMapping:
      self.createAllPackageMapping()
    for (namespace, package) in self._packageMapping.iteritems():
      if package == packageName and package not in self._packagePatchHist:
        result = self.getPackagePatchHistory(package, namespace)
        self._packagePatchHist[package] = result
        break
  def getPackagePatchHistByNamespace(self, namespace):
    if not self._packageMapping:
      self.createAllPackageMapping()
    if namespace in self._packageMapping:
      package = self._packageMapping[namespace]
      if package in self._packagePatchHist: return
      result = self.getPackagePatchHistory(package, namespace)
      self._packagePatchHist[package] = result
  def printPackagePatchHist(self, packageName):
    import pprint
    if packageName in self._packagePatchHist:
      print ("-----------------------------------------")
      print ("--- Package %s Patch History Info ---" % packageName)
      print ("-----------------------------------------")
      pprint.pprint(self._packagePatchHist[packageName].patchHistory)
  def printPackageLastPatch(self, packageName):
    import pprint
    if packageName in self._packagePatchHist:
      print ("-----------------------------------------")
      print ("--- Package %s Last Patch Info ---" % packageName)
      print ("-----------------------------------------")
      pprint.pprint(self._packagePatchHist[packageName].patchHistory[-1])

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
        self._packageMapping[packageNamespace] = packageName
        #print ("Name is [%s], Namespace is [%s]" % (packageName, packageNamespace))

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
  logger.debug("txt is [%s]" % choiceTxt)
  choiceLines = choiceTxt.split('\r\n')
  for line in choiceLines:
    if len(line.rstrip()) == 0:
      continue
    result = re.search('^ +(?P<number>[1-9])   %s +%s$' % (matchString, namespace), line)
    if result:
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
  def hasPatchHistory(self):
    return len(self.patchHistory) > 0
  def setVersion(self, version):
    self.version = version
  def hasSeqNo(self, seqNo):
    for patchInfo in self.patchHistory:
      if patchInfo.seqNo == int(seqNo):
        return True
    return False
  def hasPatchNo(self, patchNo):
    for patchInfo in self.patchHistory:
      if patchInfo.patchNo == int(patchNo):
        return True;
    return False
  def getLastPatchInfo(self):
    if len(self.patchHistory) == 0:
      return None
    return self.patchHistory[-1]
  def getLatestSeqNo(self):
    if not self.hasPatchHistory():
      return 0
    last = len(self.patchHistory)
    for index in range(last,0,-1):
      patchInfo = self.patchHistory[index-1]
      if patchInfo.seqNo:
        return patchInfo.seqNo
    return 0
  def __str__(self):
    return self.patchHistory.__str__()
  def __repr__(self):
    return self.patchHistory.__str__()

"""
a class to parse and store KIDS patch history info
"""
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
      try:
        self.patchNo = int(patchPart.strip())
      except ValueError as ex:
        print ex
        logger.error("History Line is %s" % historyLine)
        self.patchNo = 0

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

"""
a class to store information related to a KIDS build
"""
class KIDSPatchInfo(object):
  def __init__(self):
    self.package = None
    self.namespace = None
    self.version = None
    self.seqNo = None
    self.installName = None
    self.kidsFilePath = None
    self.rundate = None
    self.status = None
    self.priority = None
    self.depKIDSPatch = []
  def __str__(self):
    return ("%s, %s, %s, %s, %s, %s, %s, %s, %s, \n%s" %
             (self.package, self.namespace, self.version,
              self.seqNo, self.installName, self.kidsFilePath,
              self.rundate, self.status, self.priority, self.depKIDSPatch) )
  def __repr__(self):
    return self.__str__()

"""
This class will read the KIDS installation guide and extract information and
create a KIDPatch Info object
"""
class KIDSPatchInfoParser(object):
  RUNDATE_DESIGNATION_REGEX = re.compile("^Run Date: (?P<date>[A-Z]{3,3} [0-9][0-9], [0-9]{4,4}) +Designation: (?P<design>.*)")
  RUNDATE_FORMAT_STRING = "%b %d, %Y"
  PACKAGE_PRIORITY_REGEX = re.compile("^Package : (?P<name>.*) Priority: (?P<pri>.*)")
  VERSION_STATUS_REGEX = re.compile("^Version : (?P<no>.*) Status: (?P<status>.*)")
  SUBJECT_PART_START_REGEX = re.compile("^Subject: ")
  ASSOCIATED_PATCH_START_REGEX = re.compile("^Associated patches: ")
  ASSOCIATED_PATCH_START_INDEX = 20
  ASSOCIATED_PATCH_SECION_REGEX = re.compile("^ {%d,%d}\(v\)" % (ASSOCIATED_PATCH_START_INDEX,
                                                                 ASSOCIATED_PATCH_START_INDEX))
  def __init__(self):
    pass
  def analyzeFOIAPatchDir(self, patchDir):
    assert os.path.exists(patchDir)
    patchList = []
    """find out all the kids files in the directory"""
    kidsFiles = glob.glob(os.path.join(patchDir, "*.KID"))
    kidsFiles.extend(glob.glob(os.path.join(patchDir, "*.KIDs")))
    kidsInstallNameDict = dict()
    for kidsFile in kidsFiles:
      logger.debug("%s" % kidsFile)
      installNameList = self.getKIDSBuildInstallName(kidsFile)
      for installName in installNameList:
        if installName in kidsInstallNameDict:
          logger.warn("%s is already in the dict" % installName)
        kidsInstallNameDict[installName] = os.path.normpath(kidsFile)
        """ this is to fix the install name inconsistence """
        logger.debug(installName)
        (namespace, ver, patchNo) = installName.split('*')
        newVer = ver.replace(".0","")
        if newVer != ver:
          newInstallName = "%s*%s*%s" % (namespace, newVer, patchNo)
          kidsInstallNameDict[newInstallName] = os.path.normpath(kidsFile)
    logger.info("%s" % sorted(kidsInstallNameDict.keys()))
    kidsInfoFiles = glob.glob(os.path.join(patchDir, "*.TXT"))
    for kidsInfoFile in kidsInfoFiles:
        patchInfo = self.parseKIDSInfoFile(kidsInfoFile)
        """ only add to list for info that is related to a KIDS patch"""
        if patchInfo.installName not in kidsInstallNameDict:
          logger.warn("no KIDS file related to %s" % patchInfo)
          continue
        patchInfo.kidsFilePath = kidsInstallNameDict[patchInfo.installName]
        patchList.append(patchInfo)
    patchList = topologicSort(patchList)
    logger.info("After topologic sort %d" % len(patchList))
    return (patchList, kidsInstallNameDict)
  """ one KIDS file can contains several kids build together """
  def getKIDSBuildInstallName(self, kidsFile):
    assert os.path.exists(kidsFile)
    kidsFileHandle = open(kidsFile, 'rb')
    for line in kidsFileHandle:
      line = line.rstrip(" \r\n")
      if len(line) == 0:
        continue
      ret = re.search('^\*\*KIDS\*\*:(?P<name>.*)\^$', line)
      if ret:
        kidNames = ret.group('name').strip().split('^')
        return kidNames
    kidsFileHandle.close()
    assert False
  def parseKIDSInfoFile(self, infoFile):
    kidsPatchInfo = KIDSPatchInfo()
    assert os.path.exists(infoFile)
    inputFile = open(infoFile, 'rb')
    for line in inputFile:
      line = line.rstrip(" \r\n")
      if len(line) == 0:
        continue
      """ subject part are treated as end of parser section for now"""
      if self.SUBJECT_PART_START_REGEX.search(line):
        break;
      ret = self.RUNDATE_DESIGNATION_REGEX.search(line)
      if ret:
        kidsPatchInfo.rundate = datetime.strptime(ret.group('date'), self.RUNDATE_FORMAT_STRING)
        kidsPatchInfo.installName = ret.group('design')
        continue
      ret = self.PACKAGE_PRIORITY_REGEX.search(line)
      if ret:
        package = ret.group('name').strip()
        (namespace, name) = package.split('-')
        kidsPatchInfo.namespace = namespace.strip()
        kidsPatchInfo.package = name.strip()
        kidsPatchInfo.priority = ret.group('pri').strip()
        continue
      ret = self.VERSION_STATUS_REGEX.search(line)
      if ret:
        versionInfo = ret.group('no').strip()
        pos = versionInfo.find('SEQ #')
        if pos >= 0:
          kidsPatchInfo.version = versionInfo[:pos].strip()
          kidsPatchInfo.seqNo = versionInfo[pos+5:].strip()
        else:
          kidsPatchInfo.version = versionInfo.strip()
        kidsPatchInfo.status = ret.group('status').strip()
      """ find out the dep patch info """
      ret = self.ASSOCIATED_PATCH_START_REGEX.search(line)
      if ret:
        self.parseAssociatedPart(line[self.ASSOCIATED_PATCH_START_INDEX:], kidsPatchInfo)
        continue
      ret = self.ASSOCIATED_PATCH_SECION_REGEX.search(line)
      if ret:
        self.parseAssociatedPart(line.strip(), kidsPatchInfo)
        continue
    return kidsPatchInfo

  def parseAssociatedPart(self, infoString, kidsPatchInfo):
    pos = infoString.find("<<=")
    assert pos >=0
    patchInfo = infoString[3:pos].strip()
    kidsPatchInfo.depKIDSPatch.append(patchInfo)

""" generate a sequence of patches that need to be applied by
    using topologic sort algorithm, also for the patch under the
    same namepsace, make sure it was applied in the right sequence
"""
def topologicSort(patchInfoList):
  """ first build a directory with installname as the key """
  patchDict = dict((x.installName, x) for x in patchInfoList)
  """ new generate the dependency graph"""
  depDict = dict()
  for patchInfo in patchInfoList:
    if patchInfo.depKIDSPatch:
      """ reduce the node by removing info not in the current patch """
      for item in patchInfo.depKIDSPatch:
        if item not in patchDict:
          continue
        if patchInfo.installName not in depDict:
          depDict[patchInfo.installName] = set()
        depDict[patchInfo.installName].add(item)
  """ new generate a set consist of patch info that does have dependencies"""
  startingSet = set()
  for patch in patchDict.iterkeys():
    found = False
    for depSet in depDict.itervalues():
      if patch in depSet:
        found = True
        break;
    if not found:
      startingSet.add(patch)
  startingList = [y.installName for y in sorted([patchDict[x] for x in startingSet], cmp=comparePatchInfo)]
  visitSet = set() # store all node that are already visited
  result = [] # store the final result
  for item in startingList:
    visitNode(item, depDict, visitSet, result)
  return [patchDict[x] for x in result]

def comparePatchInfo(one, two):
  assert isinstance(one, KIDSPatchInfo)
  assert isinstance(two, KIDSPatchInfo)
  if one.package == two.package and one.version == two.version:
    return cmp(int(one.seqNo), int(two.seqNo))
  return cmp(one.rundate, two.rundate)

def visitNode(nodeName, depDict, visitSet, result):
  if nodeName in visitSet: # already visited, just return
    return
  visitSet.add(nodeName)
  for item in depDict.get(nodeName,[]):
    visitNode(item, depDict, visitSet, result)
  result.append(nodeName)

def testMain():
  print ("sys.argv is %s" % sys.argv)
  if len(sys.argv) <= 1:
    print ("Need at least two arguments")
    sys.exit()
  testClient = None
  if len(sys.argv) > 3:
    system = int(sys.argv[1])
    testClient = VistATestClientFactory.createVistATestClient(system)
  if not testClient:
    sys.exit(-1)
  try:
    packagePatchHist = PackagePatchSequenceAnalyzer(testClient, sys.argv[2])
    packagePatchHist.generateKIDSPatchSequence(sys.argv[3])
    packagePatchHist.applyKIDSPatchSequence()
    #packagePatchHist.getAllPackagesPatchHistory()
#  packagePatchHist.getPackagePatchHistByName("TOOLKIT")
#  packagePatchHist.printPackageLastPatch("TOOLKIT")
#  packagePatchHist.getPackagePatchHistByName("IMAGING")
#  packagePatchHist.printPackageLastPatch("IMAGING")
#  packagePatchHist.getPackagePatchHistByNamespace("VPR")
#  packagePatchHist.printPackagePatchHist("VIRTUAL PATIENT RECORD")
#  packagePatchHist.printPackageLastPatch("VIRTUAL PATIENT RECORD")
  finally:
    testClient.getConnection().terminate()
def testKIDSInfoParser():
  print ("sys.argv is %s" % sys.argv)
  if len(sys.argv) <= 1:
    print ("Need at least two arguments")
    sys.exit()
  kidsInfoParser = KIDSPatchInfoParser()
  kidsInfoParser.analyzeFOIAPatchDir(sys.argv[1])
""" main
"""
def main():
  import argparse
  parser = argparse.ArgumentParser(description='FOIA Patch Sequence Analyzer')
  parser.add_argument('-i', required=True, dest='patchFileDir',
                      help='input file path to the folder that contains all the FOIA patches')
  parser.add_argument('-s', required=True, dest='system', choices='12',
                      help='1: Cache, 2: GTM')
  parser.add_argument('-o', required=True, dest='outputLogDir',
                      help='Output dirctory to store all log file information')
  parser.add_argument('--namespace', required=False, dest='namespace',
                      default="VISTA")
  parser.add_argument('--username', required=False, dest='username',
                      default=None)
  parser.add_argument('--password', required=False, dest='password',
                      default=None)
  parser.add_argument('--installKIDSPatch', required=False, dest='installKIDS',
                      default=False)
  result = vars(parser.parse_args());
  print (result)
  system = int(result['system'])
  inputPatchDir = result['patchFileDir']
  assert os.path.exists(inputPatchDir)
  outputDir = result['outputLogDir']
  assert os.path.exists(outputDir)
  """ create the VistATestClient"""
  testClient = None
  testClient = VistATestClientFactory.createVistATestClient(system,
                  namespace = result['namespace'],
                  username = result['username'],
                  password = result['password'])
  assert testClient
  try:
    packagePatchHist = PackagePatchSequenceAnalyzer(testClient,
                                              outputDir)
    packagePatchHist.generateKIDSPatchSequence(inputPatchDir)
    if result['installKIDS']:
      packagePatchHist.applyKIDSPatchSequence()
  finally:
    testClient.getConnection().terminate()
if __name__ == '__main__':
  main()
