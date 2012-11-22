# -*- coding:utf-8 -*-

import serial
import Queue
from time import sleep
import threading
from embedded.helpers import hex_debug
from embedded.messages.transports.transport import ThreadedTransport

__author__ = 'Arnþór Magnússon'


START_BYTE = '\x7e'
END_BYTE = '\n'
LENGTH_IDX = 1
DATA_IDX = 2

class SerialTransport(ThreadedTransport):
  """
  Message serial transport.

  Recieves messages on a seperate thread and makes 
  data frames available with self.receive()
  Sends data through self.send(data) and 
  wraps with a frame.
  """
  def __init__(self, port='/dev/ttyUSB0', baud=57600):
    self.serial = serial.Serial(port, baud)
    super(SerialTransport, self).__init__()

  def _send(self, data):
    """
    Sends data over transport.
    
    Packs given data into a frame and sends over serial connection.
    """
    self.serial.write(START_BYTE)
    self.serial.write(chr(len(data)))
    self.serial.write(data)
    self.serial.write(END_BYTE)

  def _receive(self):
    """
    Receive data sent over transport.

    A endless loop, that listens to data on the serial port.
    When a whole package has been received, it is put on a queue buffer
    and is accessible with the "receive" function.
    """
    if self.serial.inWaiting() > 0:
      value = self.serial.read()

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
      return None
  
  def stop(self):
    """Stop receiving data from the serial port by terminating the thread."""
    super(SerialTransport, self).stop()
    self.serial.close()

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

