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
from __future__ import with_statement
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pexpect import TIMEOUT, EOF, ExceptionPexpect
from VistATestClient import VistATestClient, VistATestClientFactory
from eventqueue import IEvent, ThreadPool
import FileManGlobalAttributes
from time import sleep

class GetFileManSchemaLogEvent(IEvent):
  def __init__(self, system, fileManFile, logDir, namespace):
    self._fileManFile = fileManFile
    self._system = system
    self._logDir = logDir
    self._namespace = namespace
  def dispatch(self):
#    expectConn = VistATestClientFactory.createVistATestClient(self._system, namespace=self._namespace)
#    if not expectConn:
#      return
#    FileManGlobalAttributes.listFileManFileAttributes(expectConn, self._fileManFile, 3,
#                              os.path.join(self._logDir, self._fileManFile + ".custom"),
#                              os.path.join(self._logDir, self._fileManFile + ".customlog"))
    expectConn = VistATestClientFactory.createVistATestClient(self._system, namespace=self._namespace)
    if not expectConn:
      return
    FileManGlobalAttributes.listFileManFileAttributes(expectConn, self._fileManFile, 1,
                              os.path.join(self._logDir, self._fileManFile + ".schema"),
                              os.path.join(self._logDir, self._fileManFile + ".log"))
  def __expr__(self):
    return "GetFileManSchemaLogEvent: %s" % self._fileManFile
  def __str__(self):
    return self.__expr__()


TEST_FILEMAN_FILE_LIST = ["200","2100","9.4","165.5",".2", "2", "130","63","450",
                          "55","6925", "509850.9", "45", "604", "9002313.02",
                          "52","2260", "139.5", "115", ".11", ".31"]

DEFAULT_NUM_THREADS = 10
DEFAULT_THROTTLE_NUMBER = 20
DEFAULT_SLEEP_SECONDS = 1

def runTaskInThreadPool(numTheads, fileManList, system, logDir, namespace):
  threadPool = ThreadPool(numTheads)
  index = 0
  for item in fileManList:
    item = item.strip()
    print ("Adding %s to the queue" % item)
    threadPool.addEvent(GetFileManSchemaLogEvent(system, item, logDir, namespace))
    index = index + 1
    if (index % DEFAULT_THROTTLE_NUMBER) == 0:
      print ("total file %d processed, sleeping for %d seconds......" % (index, DEFAULT_SLEEP_SECONDS))
      sleep(DEFAULT_SLEEP_SECONDS)
  threadPool.stop()

def main(inputFile, system, numberThreads, logDir, namespace):
  print ("inputFile is %s" % inputFile)
  allfilemanfile = open(inputFile, "rb")
  assert(allfilemanfile)
  runTaskInThreadPool(numberThreads, allfilemanfile, system, logDir, namespace)

def testMain(system, numberThreads, logDir, namespace):
  runTaskInThreadPool(numberThreads, TEST_FILEMAN_FILE_LIST, system, logDir, namespace)

if __name__ == '__main__':
  try:
    import argparse
    parser = argparse.ArgumentParser(description='Get All FileMan File Schema')
    parser.add_argument('-i', required=True, dest='inputFile',
                        help='input file contains all fileman file# to retrieve the schema log')
    parser.add_argument('-s', required=True, dest='system', choices='12',
                        help='1: Cache, 2: GTM')
    parser.add_argument('-o', required=True, dest='outputDir',
                        help='Output dirctory to store all the data dictionary file schema')
    parser.add_argument('--namespace', required=False, dest='namespace',
                        default="VISTA")
    parser.add_argument('-n', required=False, dest="numOfThreads", type=int,
                        default=DEFAULT_NUM_THREADS,
                        help="number of threads to run in parallel")
    parser.add_argument('-test', required=False, dest='isTest', default=False, action='store_true',
                        help='is this the test run')
    result = vars(parser.parse_args());
    print (result)
    system = int(result['system'])
    numOfThreads = DEFAULT_NUM_THREADS
    if result['numOfThreads']:
      numOfThreads = result['numOfThreads']
    if result['isTest'] == True:
      testMain(system, numOfThreads, result['outputDir'], result['namespace'])
    else:
      main(result['inputFile'], system, numOfThreads, result['outputDir'], result['namespace'])
  except ImportError:
    print ("sys.argv is %s" % sys.argv)
    numOfThreads = DEFAULT_NUM_THREADS
    if len(sys.argv) <= 1:
      print ("Need at least two arguments")
      sys.exit()
    # manual parsing for now
    index, system, outputDir, inputFile = 0, None, None, None
    try:
      index = sys.argv.index("-s")
      system = sys.argv[index+1]
    except ValueError:
      sys.exit()
    try:
      index = sys.argv.index("-o")
      outputDir = sys.argv[index+1]
    except ValueError:
      sys.exit()
    try:
      index = sys.argv.index("-i")
      inputFile = sys.argv[index+1]
    except ValueError:
      sys.exit()
    if "-test" in sys.argv:
      testMain(system, numOfThreads, outputDir)
    else:
      main(inputFile, system, numOfThreads, outputDir)
