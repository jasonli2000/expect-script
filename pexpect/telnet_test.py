import os
import sys
from winpexpect import winspawn, TIMEOUT, EOF, ExceptionPexpect

def test_telnet():
  child = winspawn("C:/users/jason.li/Downloads/apps/plink.exe -telnet 127.0.0.1 -P 23")
  assert child.isalive()
  child.logfile = sys.stdout
# wait until the prompt
  index = child.expect(["[A-Z]+>", TIMEOUT, EOF], timeout = 10)
  if index != 0:
    child.terminate()
    exit()
  print "The return index is %d" % index
  print "child process is alive ?", child.isalive()
  child.sendline("znspace \"VISTA\"\r\n")
  index = child.expect(["VISTA>", TIMEOUT, EOF], timeout = 10)
  if index != 0:
    child.terminate()
    exit()
  child.sendline("D ^XINDEX")
  child.expect("All Routines?")
  child.sendline("NO")
  child.expect("Routine:")
  child.sendline()
  child.expect("Select BUILD NAME")
  child.sendline()
  child.expect("Select PACKAGE NAME")
  child.sendline()
  index = child.expect(["VISTA", TIMEOUT, EOF], timeout=10)
  print index
  child.sendline("HALT")
  child.terminate()

def test_python():
  logFile = StringIO.StringIO()
  child = winspawn("c:\Python27\python.exe", logfile=logFile)
  index = child.expect([">>>", TIMEOUT, EOF])
  print index
  print logFile.getvalue()
  child.terminate()

def test_dircommand():
  logFile = StringIO.StringIO()
  child = winspawn("dir", logfile=logFile)
  index = child.expect([">>>", TIMEOUT, EOF])
  print index
  print logFile.getvalue()
  child.terminate()

if __name__ == '__main__':
  test_telnet()
  #test_dircommand()
  #test_python()
