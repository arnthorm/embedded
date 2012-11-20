# -*- coding:utf-8 -*-
from embedded.messages.transports.transport import Transport
from embedded.xbee.xbeeapiconfig import XBeeAPIConfig
import serial
from xbee import XBee
from time import sleep
import Queue
import threading

__author__ = 'Arnþór Magnússon'

DEFAULT_XBEE_SETTINGS = {
  'DH': '\x00',
  'DL': '\xFF\xFF',
  'MY': '\xFF\xFF',
  'AP': '\x02',
}

class XBeeTransport(Transport):
  
  def __init__(self, port='/dev/ttyUSB0', baudrate=9600, channel='\x0C'):
    self.serial = serial.Serial(port, baudrate)
    self.xbee = XBee(self.serial, escaped=True)
    self._stop = False
    self._queue = Queue.Queue()
    self._send_queue = Queue.Queue()
    self._receive_thread = None
    self.channel = channel
    self.config = XBeeAPIConfig(self)
    self._receive_thread = threading.Thread(name="", target=self._receive)
    self._receive_thread.start()
    self.default_xbee(self.serial.getBaudrate(), self.channel)

  def default_xbee(self, baudrate, channel):
    """Set default XBee settings for the tiles"""
    #self.config.find_baudrate(set=True)
    sleep(0.01)
    self.config.set_baudrate(baudrate)
    self.config.set_channel(channel)
    for key in DEFAULT_XBEE_SETTINGS:
      if not self.config.set_param(key, DEFAULT_XBEE_SETTINGS[key]):
        raise Exception("Failed to set XBee settings for key %s!" % key)
      sleep(0.01)

  def send(self, data):
    self._send_queue.put(data)
    #self.xbee.send("tx_long_addr", data=data, dest_addr=dest)
 
  def _send(self, data, dest='\x00\x00\x00\x00\x00\x00\xFF\xFF'):
    if type(data) is dict:
      self.xbee.send(**data)
    else:
      self.xbee.send("tx_long_addr", data=data, dest_addr=dest)

  def _receive(self):
    while True:
      if self._stop:
        break

      if not self._send_queue.empty():
        self._send(self._send_queue.get())
      sleep(0.001)
      if self.serial.inWaiting() > 0:
        self._queue.put(self.xbee.wait_read_frame())

  def receive(self):
    if self._queue.empty():
      return None
    data = self._queue.get()
    if data.has_key('rf_data'):
      return data['rf_data']
    else:
      return None

  def stop(self):
    self._stop = True
    self._receive_thread.join()
    self.serial.close()

if __name__ == '__main__':
  transport = XBeeTransport()
  print 'Starting ...'
  while True:
    try:
      response = transport.receive()
      if response is not None:
        print 'Data received:' + str(response)
    except KeyboardInterrupt:
      transport.stop()
      break


