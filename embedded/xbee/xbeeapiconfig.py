
from embedded.helpers import get_hex, get_usb
from time import sleep
import datetime

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

  def __init__(self, xbee):
    self.xbee = xbee
    self._cur_channel = None

  def set_baudrate(self, value):
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

  def save_config(self):
    raise NotImplemented("Function not implemented!")

  def get_param(self, param):
    response = self._set_param(param)
    return response['parameter']

  def _set_param(self, param, value=None, wait=True):
    if value is not None:
      self.xbee.send('at', frame_id='A', command=param, parameter=value)
    else:
      self.xbee.send('at', frame_id='A', command=param)
    return self.read_timeout(timeout=0.1)
    #return self.xbee.wait_read_frame(timeout=0.1)

  def set_param(self, param, value=None, wait=True):
    try:
      response = self._set_param(param, value, wait)
      return True
      #return self._set_param(param, value, wait)['status'] == '\x00'
    except:
      return False

  def find_baudrate(self, set=False):
    original_baud = self.xbee.serial.getBaudrate()
    b = None
    l = list(reversed(baud_table))
    l.insert(0, original_baud)
    for baud in l:
      self.xbee.serial.setBaudrate(baud)
      sleep(0.01)
      self.xbee.send('at', frame_id='A', command='BD')
      sleep(0.01)
      #result = self.xbee.wait_read_frame(timeout=0.1)
      result = self.read_timeout(timeout=0.1)
      if result is not None:
        b = baud
        break
    if not set:
      self.xbee.serial.setBaudrate(original_baud)
    return b

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

def config():
  ser = serial.Serial(get_usb(), 57600)
  xbee = XBee(ser)
  conf = XBeeAPIConfig(xbee)
  baud = conf.find_baudrate(set=True)
  print 'XBee is running on %d baudrate.' % baud
  return conf

def display_config():
  conf = config()
  conf.print_conf()

def set_defaults():
  conf = config()
  conf.set_defaults(baudrate=9600)
  conf.print_conf()

if __name__ == '__main__':
  from xbee import XBee
  import serial
  
  #display_config()
  set_defaults()
