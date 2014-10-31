# -*- coding:utf8 -*-
import os
import sys

from embedded.helpers import get_usb
from embedded.messages.manager import MessageManager
from embedded.messages.transports import SerialTransport
from embedded.utils.menu import MenuManager

from messages import msgs, message_collection

from serial.serialutil import SerialException

from time import sleep
import datetime
import threading

__author__ = 'Arnþór Magnússon'

class ChannelsUI(object):
  
  def __init__(self, port='/dev/ttyUSB0'):
    self._stop = False
    self.menu = MenuManager()

    # Register menu functions
    self.menu.add('1', 'Echo', self.menu_echo)
    self.menu.add('q', 'Quit', self.menu_quit)

    self.manager = MessageManager(SerialTransport(port, baudrate=57600))
    try:
      # Subscribe to messages
      self.manager.register_messages(message_collection)
      self.manager.subscribe(msgs.echo, self.msg_echo_cb)
      
      self.menu.run_as_thread(self.process)

      while not self._stop:
        print('')
        print('-'*80)
        print('')
        self.menu.activate()
    except KeyboardInterrupt:
      self.stop()
    except Exception:
      self.stop()
      raise

  def process(self):
    while not self._stop:
      try:
        self.manager.act()
        sleep(0.001)
      except:
        raise

  def stop(self):
    self._stop = True
    self.menu.stop()
    self.manager.stop()

  def msg_echo_cb(self, message):
    print message

  def menu_echo(self):
    input = raw_input("Enter text to echo: ")
    if input:
      self.manager.send(0, text=input)

  def menu_quit(self):
    self.stop()
    raise KeyboardInterrupt 


def run_console():
  node = None
  try:
    node = ChannelsUI(port=get_usb('2341', '0010'))
  except SerialException:
    if node is not None:
      node.stop()
    print('')
    print('Please specify correct port of XBee in %s (COM1, COM2 ...)' % PORT_FILE)
    print('')
    raw_input("Press enter to continue...")

if __name__ == '__main__':
  run_console()
