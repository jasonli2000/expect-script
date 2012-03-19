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
  import pexpect
  pass
from CreateConnection import createExpectConnection
from eventqueue import IEvent, ThreadPool
import FileManGlobalAttributes
from time import sleep

class GetFileManSchemaLogEvent(IEvent):
  def __init__(self, system, fileManFile, logDir):
    self._fileManFile = fileManFile
    self._system = system
    self._logDir = logDir
  def dispatch(self):
    expectConn = createExpectConnection(self._system)
    if not expectConn:
      return
    FileManGlobalAttributes.listFileManFileAttributes(expectConn, self._fileManFile,
                              os.path.join(self._logDir, self._fileManFile + ".log"))
  def __expr__(self):
    return "GetFileManSchemaLogEvent: %s" % self._fileManFile
  def __str__(self):
    return self.__expr__()

def main():
  allfilemanfile = open("/home/softhat/git/expect-script/VistA/allfilemanfiles", "rb")
  assert(allfilemanfile)
  pool = ThreadPool(10)
#  allfilemanfile = ["200","2100","9.4","165.5",".2", "2", "130","63","450",
#                    "55","6925", "509850.9", "45", "604", "9002313.02",
#                    "52","2260", "139.5", "115", ".11", ".31"]
  system = 3
  throttle = 100
  index = 0
  for item in allfilemanfile:
    item = item.strip()
    #print "Adding %s to the queue" % item
    pool.addEvent(GetFileManSchemaLogEvent(system, item, "/home/softhat/git/expect-script/VistA/output/logs/"))
    index = index + 1
    if (index % throttle) == 0:
      print ("total file %d processed, sleeping for 1 seconds......" % index)
      sleep(1)
  pool.stop()
if __name__ == '__main__':
  main()
