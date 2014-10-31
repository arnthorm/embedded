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
TYPE_IDX = 2
DATA_IDX = 3
HEADER_LENGTH = 2

class SerialTransport(ThreadedTransport):
  """
  Message serial transport.

  Recieves messages on a seperate thread and makes 
  data frames available with self.receive()
  Sends data through self.send(data) and 
  wraps with a frame.
  """
  def __init__(self, port='/dev/ttyUSB0', baudrate=57600):
    if port is None:
      raise ValueError('No serial port supplied to transport!')
    self.serial = serial.Serial(port, baudrate)
    self.buffer = []
    super(SerialTransport, self).__init__()

  def _send(self, data):
    """
    Sends data over transport.
    
    Packs given data into a frame and sends over serial connection.
    """
    self._push(START_BYTE)
    self._push(chr(len(data)+1))
    print data
    self._push(data)
    self._push(END_BYTE)

  def _push(self, value):
    self.serial.write(value)

  def _receive(self):
    """
    Receive data sent over transport.

    A endless loop, that listens to data on the serial port.
    When a whole package has been received, it is put on a queue buffer
    and is accessible with the "receive" function.
    """
    if self._available > 0:
      self.buffer.append(self._pull())

      if len(self.buffer) > LENGTH_IDX:
        length = HEADER_LENGTH + ord(self.buffer[LENGTH_IDX])
      else:
        length = 0

      if len(self.buffer) > 0 and self.buffer[0] == START_BYTE:
        if len(self.buffer) == length and self.buffer[-1] == END_BYTE:
          self._process_buffer()
          self.buffer = []
        elif length != 0 and len(self.buffer) >= length:
          self.buffer = []
        else:
          pass
      else:
        if self.buffer[-1] == '\n':
          self._receive_queue.put({'data': ''.join(self.buffer), 'type': None})
          self.buffer = []
        elif self.buffer[-1] == START_BYTE and self.buffer[0] != START_BYTE:
          self.buffer = [START_BYTE, ]
        else:
          pass
    else:
      return None

  def _available(self):
    return self.serial.inWaiting()

  def _pull(self):
    return self.serial.read()

  def _process_buffer(self):
    type = self.buffer[TYPE_IDX]
    data = ''.join(self.buffer[TYPE_IDX:-1])
    self._receive_queue.put({'data': data, 'type': type})

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

