
from embedded.helpers import get_hex, get_usb
from time import sleep
import datetime
import struct

now = datetime.datetime.now

CONF_PARAM = { 
  'ID': 'Id',
  'CH': 'Channel',
  'DH': 'Dest., high',
  'DL': 'Destt, low',
  'MY': '16 bit network address',
  'AP': 'API mode',
  'VR': 'Firmware version',
  'BD': 'Interface data rate',
  'SB': 'Stop bits',
}

baud_table = (
  1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200
)
channel_table = (
  '\x0B', '\x0C', '\x0D', '\x0E', '\x0F', '\x10', '\x11', '\x12', 
  '\x13', '\x14', '\x15', '\x16', '\x17', '\x18', '\x19', '\x1A', 
)

CONF_TO_READ = ('ID', 'CH', 'DH', 'DL', 'MY', 'AP', 'VR', 'BD')

class XBeeAPIConfig:

  def __init__(self, transport=None, xbee=None):
    if transport is not None:
      self.xbee = transport.xbee
      self.transport = transport
    elif xbee is not None:
      self.xbee = xbee
      self.transport = None
    else:
      raise ValueError("Transport was supplied! Supply XBeeTransport or XBee object!")
    self._cur_channel = None

  def send(self, data):
    if self.transport is not None:
      return self.transport.send_sync(data)
    else:
      self.xbee.send(**data)
      return self.read_timeout()

  def save_config(self):
    raise NotImplemented("Function not implemented!")

  def get_param(self, param):
    response = self._set_param(param)
    return response['parameter']

  def _set_param(self, param, value=None, wait=True):
    if value is not None:
      return self.send({'cmd': 'at', 'frame_id':'A', 'command':param, 'parameter':value})
    else:
      return self.send({'cmd': 'at', 'frame_id':'A', 'command':param})

  def set_param(self, param, value=None, wait=True):
    response = self._set_param(param, value, wait)
    return True

  def _read_raw(self, timeout=1):
    buffer = ''
    limit = now() + datetime.timedelta(0, timeout)
    escape = False
    length = 3
    while len(buffer) < length:
      if limit < now():
        return None
      if self.xbee.serial.inWaiting() > 0:
        b = self.xbee.serial.read()
        # Start byte
        if len(buffer) == 0 and ord(b) == 0x7E:
          buffer += b
        elif len(buffer) > 0:
          if b == 0x7D:
            escape = True
          elif escape:
            escape = False
            buffer += (b ^ 0x20)
          else:
            buffer += b
        if len(buffer) == 3:
          length = struct.unpack("> h", buffer[1:3])[0] + 4
    return buffer

  def set_baudrate(self, value):
    """Set XBee and computer baudrate."""
    if self.xbee.serial.getBaudrate() != value:
      try:
        success = set_param('BD', chr(baud_table.index(value)))
      except:
        success = False
      
      if success:
        self.xbee.serial.setBaudrate(value)
      return success
    else:
      return True

  def find_baudrate(self, set=False):
    """Find XBee's baudrate."""
    original_baud = self.xbee.serial.getBaudrate()
    b = None
    l = list(reversed(baud_table))
    l.insert(0, original_baud)
    for baud in l:
      self.xbee.serial.setBaudrate(baud)
      sleep(0.01)
      self.xbee.send(**{'cmd': 'at', 'frame_id':'A', 'command':'BD'})
      result = self._read_raw()
      if result is not None and ord(result[3]) == 0x88:
        b = baud
        break
    if not set:
      self.xbee.serial.setBaudrate(original_baud)
    return b

  def adjust_baudrate(self, baudrate=None):
    """Adjust/set XBee's baudrate to specified baudrate."""
    if baudrate is None:
      baudrate = self.xbee.serial.getBaudrate()
    # Set computer baudrate to match XBee's.
    self.find_baudrate(set=True)
    # Now, set both XBee and computers bautrate to specified.
    self.set_baudrate(baudrate)


  def print_conf(self):
    for param in CONF_TO_READ:
      value = self.get_param(param)
      print '%s: %s' % (CONF_PARAM.get(param, param), get_hex(value))

  def read_timeout(self, timeout=1):
    limit = now() + datetime.timedelta(0, timeout)
    while True:
      if self.xbee.serial.inWaiting() == 0:
        if limit < now():
          break
        sleep(0.001)
        continue
      return self.xbee.wait_read_frame()
    return None

  def set_channel(self, value):
    """Set XBee channel.

    Given channel can be on the form '\x0B' to '\x1A' or 0 to 15.
    """
    channel = None
    if type(value) is str:
      hex = None
      try:
        tmp_value = value
        if len(value) == 1:
          tmp_value = '0' + tmp_value
        hex = tmp_value.decode('hex')
        value = hex
      except:
        pass
      if 11 <= ord(value) and ord(value) <= 26:
        channel = value 
    if type(value) is int and 0 <= value and value <= 15:
      channel = chr(ord('\x0B')+value)

    if channel:
      if self.set_param('CH', channel):
        self._cur_channel = channel
        return True
    return False

  def get_channel(self, number=False):
    if self._cur_channel is None:
      self._cur_channel = self.get_param('CH')
    if number:
      return channel_table.index(self._cur_channel) 
    else:
      return self._cur_channel

  def set_defaults(self, baudrate=57600):
    sleep(0.01)
    self.set_baudrate(baudrate)
    print self.set_param('CH', '\x1B')
    sleep(0.1)
    print self.set_param('DH', '\x00')
    print self.set_param('DL', '\xFF\xFF')
    #print set_param('DL', '\x00\x01')
    print self.set_param('MY', '\xFF\xFF')
    #print set_param('MY', '\x00\x01')
    print self.set_param('AP', '\x02')

def transport_test():
  from embedded.messages.transports import XBeeTransport
  transport = XBeeTransport(get_usb(), 9600)
  transport.config.print_conf()
  transport.stop()

def config():
  ser = serial.Serial(get_usb(), 57600)
  xbee = XBee(ser)
  conf = XBeeAPIConfig(xbee=xbee)
  baud = conf.find_baudrate(set=True)
  print 'XBee is running on %d baudrate.' % baud
  return conf

def xbee_test():
  conf = config()
  conf.print_conf()

def set_defaults():
  conf = config()
  conf.set_defaults(baudrate=9600)
  conf.print_conf()

if __name__ == '__main__':
  from xbee import XBee
  import serial
  
  #xbee_test()
  transport_test()
  #config()
  #set_defaults()
