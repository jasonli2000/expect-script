import subprocess
from Queue import Queue, Empty
import threading
import thread
from threading import Thread

class IEvent:
  def __init__(self):
    pass
  def dispatch(self):
    pass
  def __expr__(self):
    pass
  def __str__(self):
    pass

class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, queue):
        Thread.__init__(self)
        self._stop= False
        self.queue = queue
        self.daemon = False
        self.start()
    def run(self):
        while not self._stop:
            try:
              event = self.queue.get(True, 2)
              print "%s : processing event %s" % (self.name, event)
              event.dispatch()
            except Empty: continue # do not call task_done if no event in the queue
            except Exception, e: print e
            self.queue.task_done()
    def stop(self):
      self._stop = True

class ThreadPool:
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, num_threads):
        self.queue = Queue()
        self._allthreads = []
        for _ in range(num_threads):
          self._allthreads.append(Worker(self.queue))

    def addEvent(self, IEvent):
        """Add a task to the queue"""
        self.queue.put(IEvent)

    def stop(self):
        """Wait for completion of all the tasks in the queue"""
        self.queue.join()
        print ("task queue is now empty")
        for thd in self._allthreads:
          print ("Joining thread %s" % thd.name)
          thd.stop()
          if thd.isAlive():
            thd.join(10)
          if thd.isAlive():
            print ("Joining thread %s failed" % thd.name)

class DummyEvent(IEvent):
  def __init__(self, seconds):
    self._seconds = seconds
  def dispatch(self):
    from time import sleep
    print threading.currentThread().name, ": sleep", self._seconds
    sleep(self._seconds)
  def __expr__(self):
    return "DummyEvent %d" % self._seconds
  def __str__(self):
    return self.__expr__()

class SubprocesEvent(IEvent):
  def dispatch(self):
    command = "ls -tl *.py"
    print threading.currentThread().name, "Running command %s" % command
    result = subprocess.call(command, shell=True)
    print result
  def __expr__(self):
    return "SubprocesEvent"
  def __str__(self):
    return self.__expr__()

def test1():
    from random import randrange
    delays = [randrange(1, 10) for i in range(10)]

    pool = ThreadPool(5)
    for i, d in enumerate(delays):
        pool.addEvent(DummyEvent(d))
    pool.stop()

def test2():
    from random import randrange
    delays = [randrange(1, 10) for i in range(10)]

    pool = ThreadPool(5)
    for i, d in enumerate(delays):
        pool.addEvent(SubprocesEvent())
    pool.stop()

def main():
  test2()

if __name__ == '__main__':
  main()
