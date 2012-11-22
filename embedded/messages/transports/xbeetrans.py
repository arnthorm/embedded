# -*- coding:utf-8 -*-
from embedded.messages.transports.transport import ThreadedTransport
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

class XBeeTransport(ThreadedTransport):
  
  def __init__(self, port='/dev/ttyUSB0', baudrate=9600, channel='\x0C'):
    self.serial = serial.Serial(port, baudrate)
    self.xbee = XBee(self.serial, escaped=True)
    self.channel = channel

    self.config = XBeeAPIConfig(xbee=self.xbee)
    self.default_xbee(self.channel)
    self.config.transport = self

    super(XBeeTransport, self).__init__()

  def default_xbee(self, channel):
    """Set default XBee settings for the tiles"""
    self.config.adjust_baudrate()
    self.config.set_channel(channel)
    for key in DEFAULT_XBEE_SETTINGS:
      if not self.config.set_param(key, DEFAULT_XBEE_SETTINGS[key]):
        raise Exception("Failed to set XBee settings for key %s!" % key)
      sleep(0.01)

  def _send(self, data):
    if type(data) is dict:
      self.xbee.send(**data)
    else:
      self.xbee.send("tx_long_addr", data=data, dest_addr='\x00\x00\x00\x00\x00\x00\xFF\xFF')

  def _receive(self):
    if self.serial.inWaiting() > 0:
      data = self.xbee.wait_read_frame()
      if type(data) is dict and data.has_key('rf_data'):
        data['data'] = data['rf_data']
      return data
    else:
      return None

  def stop(self):
    super(XBeeTransport, self).stop()
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


