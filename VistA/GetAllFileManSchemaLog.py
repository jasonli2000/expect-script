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
    return "GetFileManSchemaLogEvent: %s" % fileManFile
  def __str__(self):
    return self.__expr__()

def main():
  pool = ThreadPool(2)
  fileManList = ["200","2100","9.4","165.5"]
  system = 3
  for item in fileManList:
    pool.addEvent(GetFileManSchemaLogEvent(system, item, "/home/softhat/git/expect-script/VistA/output/logs/"))
  pool.stop()
if __name__ == '__main__':
  main()
