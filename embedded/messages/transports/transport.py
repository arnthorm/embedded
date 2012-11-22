

import Queue
import threading
import datetime 
from time import sleep

class Transport(object):

  def send_sync(self, data):
    pass

  def send(self, data):
    raise NotImplementedError("Not implemented, abstract class!")
  
  def receive(self):
    raise NotImplementedError("Not implemented, abstract class!")

  def stop(self):
    raise NotImplementedError("Not implemented, abstract class!")


class ThreadedTransport(Transport):
  
  def __init__(self):
    self._receive_queue = Queue.Queue()
    self._send_queue = Queue.Queue()
    self._receive_sync_queue = Queue.Queue()
    self._send_sync_queue = Queue.Queue()
    self._stop = False
    self._process_thread = None
    self._process_thread = threading.Thread(name="transport_process", target=self._process)
    self._process_thread.start()

  def send_sync(self, data, timeout=0.6):
    self._send_sync_queue.put(data)
    timeout = datetime.datetime.now() + datetime.timedelta(0, timeout)
    while True:
      if not self._receive_sync_queue.empty():
        return self._receive_sync_queue.get()
      elif timeout < datetime.datetime.now():
        return None
      sleep(0.001)

  def send(self, data):
    self._send_queue.put(data)

  def receive(self):
    if self._receive_queue.empty():
      return None
    return self._receive_queue.get()

  def _send(self):
    raise NotImplementedError("Not implemented, abstract function!")

  def _receive(self):
    raise NotImplementedError("Not implemented, abstract function!")

  def _process(self):
    while True:
      if self._stop:
        break

      # Try synchronous communication
      if not self._send_sync_queue.empty():
        while self.serial.inWaiting() > 0:
          self._receive_sync_queue.put(self._receive())
        self._send(self._send_sync_queue.get())
        timeout = datetime.datetime.now() + datetime.timedelta(0, 0.5)
        while True:
          response = self._receive()
          if response is not None:
            self._receive_sync_queue.put(response)
            break
          elif timeout < datetime.datetime.now():
            break
          sleep(0.001)

      response = self._receive()
      if response is not None:
        self._receive_queue.put(response)
      if not self._send_queue.empty():
        self._send(self._send_queue.get())
      sleep(0.001)
  
  def stop(self):
    self._stop = True
    self._process_thread.join()
