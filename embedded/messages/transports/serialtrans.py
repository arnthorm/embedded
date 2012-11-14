# -*- coding:utf-8 -*-

import serial
import Queue
from time import sleep
import threading
from embedded.helpers import hex_debug
from embedded.messages.transports.transport import Transport

__author__ = 'Arnþór Magnússon'


START_BYTE = '\x7e'
END_BYTE = '\n'
LENGTH_IDX = 1
DATA_IDX = 2

class SerialTransport(Transport):
  """
  Message serial transport.

  Recieves messages on a seperate thread and makes 
  data frames available with self.receive()
  Sends data through self.send(data) and 
  wraps with a frame.
  """
  def __init__(self, port='/dev/ttyUSB0', baud=57600):
    self.ser = serial.Serial(port, baud)
    self._stop = False
    self._queue = Queue.Queue()
    self._receive_thread = threading.Thread(name="", target=self._receive)
    self._receive_thread.start()

  def send(self, data):
    """
    Sends data over transport.
    
    Packs given data into a frame and sends over serial connection.
    """
    self.ser.write(START_BYTE)
    self.ser.write(chr(len(data)))
    self.ser.write(data)
    self.ser.write(END_BYTE)

  def receive(self):
    """Returns received frames over serial."""
    if self._queue.empty():
      return None
    return self._queue.get()

  def _receive(self):
    """
    Receive data sent over transport.

    A endless loop, that listens to data on the serial port.
    When a whole package has been received, it is put on a queue buffer
    and is accessible with the "receive" function.
    """
    buffer = ''
    while True:
      if self._stop:
        break
      if self.ser.inWaiting() > 0:
        value = self.ser.read()

        if len(buffer) > 0 and buffer[0] == START_BYTE:
          if len(buffer) > 1 and \
             len(buffer) == DATA_IDX+ord(buffer[LENGTH_IDX]) and \
             value == END_BYTE:
            self._queue.put(buffer[DATA_IDX:
                                  DATA_IDX+ord(buffer[LENGTH_IDX])])
            #print hex_debug(buffer)
            buffer = ''
          elif len(buffer) > 1 and \
              len(buffer) > DATA_IDX+ord(buffer[LENGTH_IDX]):
            buffer = ''
          else:
            buffer += value
        else:
          if '\n' == value:
            self._queue.put(buffer)
            buffer = ''
          else:
            buffer += value
      else:
        sleep(0.0001)
  
  def stop(self):
    """
    Stop receiving data from the serial port by terminating the thread.
    """
    self._stop = True
    self._receive_thread.join()
    self.ser.close()

if __name__ == '__main__':
  transport = SerialTransport()
  while True:
    try:
      response = transport.receive()
      if response is not None:
        print 'Data ' + response
    except KeyboardInterrupt:
      transport.stop()
      break

