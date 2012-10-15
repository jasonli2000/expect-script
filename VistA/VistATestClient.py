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
from __future__ import with_statement
import pexpect
from pexpect import TIMEOUT, EOF, ExceptionPexpect
try:
  from winpexpect import winspawn
except ImportError:
  pass
import sys
import os # to get gtm environment variables

DEFAULT_TIME_OUT_VALUE = 30
CACHE_PROMPT_END = ">"

class VistATestClient(object):
  PLATFORM_NONE = 0
  CACHE_ON_WINDOWS = 1
  CACHE_ON_LINUX = 2
  GTM_ON_LINUX = 3
  PLATFORM_LAST = 4
  def __init__(self, platform, prompt = None, namespace = None):
    self._connection = None
    assert int(platform) > self.PLATFORM_NONE and int(platform) < self.PLATFORM_LAST
    self._platform = platform
    self._prompt = prompt
    self._namespace = namespace
  def createConnection(self, command, username = None, password = None):
    pass
  def waitForPrompt(self):
    self._connection.expect(self._prompt)
  def getConnection(self):
    return self._connection
  def getPrompt(self):
    return self._prompt
  def getNamespace(self):
    return self._namespace
class VistATestClientGTMLinux(VistATestClient):
  DEFAULT_GTM_PROMPT = "GTM>"
  DEFAULT_GTM_COMMAND = "mumps -direct"
  def __init__(self):
    gtm_prompt = os.getenv("gtm_prompt")
    if not gtm_prompt:
      gtm_prompt = self.DEFAULT_GTM_PROMPT
    VistATestClient.__init__(self, self.GTM_ON_LINUX, gtm_prompt, None)
  def createConnection(self, command, username = None, password = None):
    if not command:
      command = self.DEFAULT_GTM_COMMAND
    self._connection = pexpect.spawn(command, timeout = DEFAULT_TIME_OUT_VALUE)
    assert self._connection.isalive()
  def __del__(self):
    if self._connection:
      self._connection.close()
    
class VistATestClientCache(VistATestClient):
  def __init__(self, platform, prompt = None, namespace = None):
    VistATestClient.__init__(self, platform, prompt, namespace)
  def __changeNamesapce__(self):
    self._connection.send("znspace \"%s\"\r" % self.getNamespace())
  def __signIn__(self, username, password):
    child = self._connection
    child.expect("Username:")
    child.send("%s\r" % username)
    child.expect("Password:")
    child.send("%s\r" % password)
  def __del__(self):
    if self._connection:
      self._connection.close()
""" Make sure that plink is in you path
"""
class VistATestClientCacheWindows(VistATestClientCache):
  DEFAULT_WIN_TELNET_CMD =  "plink.exe -telnet 127.0.0.1 -P 23"
  def __init__(self, namespace):
    assert namespace, "Must provide a namespace"
    prompt = namespace + CACHE_PROMPT_END
    VistATestClientCache.__init__(self, self.CACHE_ON_WINDOWS, prompt, namespace)
  def createConnection(self, command, username = None, password = None):
    if not command:
      command = self.DEFAULT_WIN_TELNET_CMD
    self._connection = winspawn(command, timeout = DEFAULT_TIME_OUT_VALUE)
    assert self._connection.isalive()
    if username and password:
      self.__signIn__(username, password)
    self.__changeNamesapce__()
  def __del__(self):
    if self._connection:
      self._connection.close()

class VistATestClientCacheLinux(VistATestClientCache):
  DEFAULT_CACHE_CMD = "ccontrol session cache"
  def __init__(self, namespace):
    assert namespace, "Must provide a namespace"
    prompt = namespace + CACHE_PROMPT_END
    VistATestClientCache.__init__(self, self.CACHE_ON_LINUX, prompt, namespace)
  def createConnection(self, command, username = None, password = None):
    if not command:
        command = self.DEFAULT_CACHE_CMD
    self._connection = pexpect.spawn(command, timeout = DEFAULT_TIME_OUT_VALUE)
    assert self._connection.isalive()
    if username and password:
      self.__signIn__(username, password)
    self.__changeNamesapce__()
  def __del__(self):
    if self._connection:
      self._connection.close()

def isLinuxSystem():
  return sys.platform.startswith("linux")
def isWindowsSystem():
  return sys.platform.startswith("win")

class VistATestClientFactory(object):
  SYSTEM_NONE = 0
  SYSTEM_CACHE = 1
  SYSTEM_GTM = 2
  SYSTEM_LAST = 3
  @staticmethod
  def createVistATestClient(system, prompt = None, namespace = "VISTA", command = None, username = None, password = None):
    intSys = int(system)
    testClient = None
    assert intSys > VistATestClientFactory.SYSTEM_NONE and intSys < VistATestClientFactory.SYSTEM_LAST
    if VistATestClientFactory.SYSTEM_CACHE == intSys:
      if isLinuxSystem():
        testClient = VistATestClientCacheLinux(namespace)
      elif isWindowsSystem():
        testClient = VistATestClientCacheWindows(namespace)
    elif VistATestClientFactory.SYSTEM_GTM == intSys:
      if isLinuxSystem():
        testClient = VistATestClientGTMLinux()
    if not testClient:
      raise Exception ("Could not create VistA Test Client")
    testClient.createConnection(command, username, password)
    return testClient
