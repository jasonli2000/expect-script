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
import ConfigParser
import InitFileMan
from CreateNewDomain import CreateNewDomain
from SetupVolumeSet import SetupVolumeSet
import StartTaskMan
from SetupDevice import SetupDevice
from CreateSystemManager import AddSystemManager

class InitSystemSetup:
  def __init__(self, configFile):
    self._configFile = configFile
    self._configParser = ConfigParser.RawConfigParser(allow_no_value=True)
    self._logDir = None
    self._system = None
    self._domainName = None
    self._volumeSet = None
    self._boxValue = None
  def __parseConfigFile__(self):
    self._configParser.readfp(open(self._configFile,'rb'))
    config = self._configParser
    # get the system and logdir variable
    if not config.has_section("MAIN"):
      raise ConfigParser.NoSectionError("MAIN")
    # this will raise an exception if option system or logdir does not exit
    self._system = config.get("MAIN","system")
    print ("system is %s" % self._system)
    self._logDir = config.get("MAIN","logdir")
    print ("logDir is %s" % self._logDir)
    self.__convertSystemToNumber__()
    # found out the domain name and also the volume set box value
    if not config.has_section("SITE INFO"):
      raise ConfigParser.NoSectionError("SITE INFO")
    if not config.has_option("SITE INFO", "volume_set"):
      raise ConfigParser.NoOptionError("SITE INFO", "volume_set")
    self._volumeSet = config.get("SITE INFO", "volume_set")
    if self._volumeSet == None or len(self._volumeSet) == 0:
      raise ConfigParser.NoOptionError("SITE INFO", "volume_set")
    if not config.has_option("SITE INFO", "box_value"):
      raise ConfigParser.NoOptionError("SITE INFO", "box_value")
    self._boxValue = config.get("SITE INFO", "box_value")
    if self._boxValue == None or len(self._boxValue) == 0:
      raise ConfigParser.NoOptionError("SITE INFO", "box_value")
    if config.has_option("SITE INFO", "domain_name"):
      self._domainName = config.get("SITE INFO", "domain_name")

  def __convertSystemToNumber__(self):
    if self._system == "GTM":
      self._system = 2
    elif self._system == "Cache":
      self._system = 1
    else:
      raise Exception("unsupported System %s" % self._system)
  def __createTestClient__(self):
    return VistATestClientFactory.createVistATestClient(self._system)
  def run(self):
    self.__parseConfigFile__()
    self.__initFileMan__()
    self.__createNewDomain__()
    self.__setupVolumeSet__()
    self.__startTaskMan__()
    self.__setupDevice__()
    self.__createSystemManager__()
  def __initFileMan__(self):
    config = self._configParser
    siteName = ""
    siteNumber = 0
    if config.has_section("SITE INFO"):
      if config.has_option("SITE INFO", "site_name"):
        tempName = config.get("SITE INFO", "site_name")
        if tempName:
          siteName = tempName
      if config.has_option("SITE INFO", "site_number"):
        try:
          tempNumber = config.getint("SITE INFO", "site_number")
          if tempNumber > 0:
            siteNumber = tempNumber
        except:
          pass
    # create connection
    connection = self.__createTestClient__()
    InitFileMan.initFileMan(connection,
                            os.path.join(self._logDir,"InitFileMan.log"),
                            siteName,
                            siteNumber,
                            self._system)
  def __createNewDomain__(self):
    if self._domainName == None or len (self._domainName) == 0:
      return
    connection = self.__createTestClient__()
    createNewDomain = CreateNewDomain(self._system,
                                      connection,
                                      self._domainName,
                                      os.path.join(self._logDir, "CreateNewDomain.log"))

    print ("Creating new domain %s" % (self._domainName))
    createNewDomain.run()
  def __setupVolumeSet__(self):
    connection = self.__createTestClient__()
    setupVolumeSet = SetupVolumeSet(self._system,
                                    connection,
                                    self._volumeSet,
                                    self._boxValue,
                                    self._domainName,
                                    os.path.join(self._logDir, "SetupVolumeSet.log"))
    print ("Setting up volume set %s:%s" % (self._volumeSet, self._boxValue))
    setupVolumeSet.run()
  def __setupDevice__(self):
    config = self._configParser
    hfsDev = None
    nullDev = None
    if not config.has_section("DEVICE"):
      return
    if config.has_option("DEVICE", "hfs"):
      hfsDev = config.get("DEVICE", "hfs")
    if config.has_option("DEVICE", "null"):
      nullDev = config.get("DEVICE", "null")
    connection = self.__createTestClient__()
    setupDevice = SetupDevice(self._system,
                              os.path.join(self._logDir, "SetupDevice.log"),
                              connection)
    if hfsDev and len(hfsDev) > 0:
      setupDevice.setupHostFileSystem(hfsDev)
    if nullDev and len(nullDev) > 0:
      setupDevice.setupNullDevice(nullDev)
    print ("Setting Device")
    setupDevice.run()
  def __startTaskMan__(self):
    connection = self.__createTestClient__()
    print ("Starting taskman")
    StartTaskMan.startTaskMan(connection,
                              os.path.join(self._logDir, "StartTaskMan.log"))
    pass
  def __createSystemManager__(self):
    config = self._configParser
    if not config.has_section("SYSTEM MANAGER"):
      return
    name = config.get("SYSTEM MANAGER","name")
    initial = config.get("SYSTEM MANAGER","initial")
    accCode = config.get("SYSTEM MANAGER","access_code")
    veriCode = config.get("SYSTEM MANAGER","verify_code")
    connection = self.__createTestClient__()
    systemManager = AddSystemManager(self._system,
                                     connection,
                                     os.path.join(self._logDir, "CreateSystemManager.log"),
                                     name,
                                     initial,
                                     accCode,
                                     veriCode)
    print ("Creating System Manager")
    systemManager.run()

def main(inputFile):
  print ("inputFile is %s" % inputFile)
  setup = InitSystemSetup(inputFile)
  setup.run()

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Setup Init VistA-FOIA System')
  parser.add_argument('-i', required=True, dest='inputFile',
                      help='input configuration file contains all information related to the initial setup of the VistA-FOIA System')
  result = vars(parser.parse_args());
  print (result)
  main(result['inputFile'])
