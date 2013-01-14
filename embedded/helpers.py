
import time

def time_delta_to_str(start=None, end=None, delta=None):
  """
    Returns a string with the delta time.
  """
  if start is not None and end is not None:
    delta = end - start  
  if delta is None:
    raise ValueError('Wrong usage, start and end required or delta!')
  return time.strftime('%H:%M:%S', time.gmtime(delta.seconds))

def enum(*sequential, **named):
  """
    enum_type = enum('a', 'b', 'c')
    enum_type = enum(a=0, b=1, c=2)
  """
  enums = dict(zip(sequential, range(len(sequential))), **named)
  return type('Enum', (), enums)

def get_usb(vendor_id, product_id):
  """
    Get the serial port for any device:
      vendor_id = '403'
      product_id = '6001'
  """
  from serial.tools import list_ports

  try:
    for ports in list_ports.comports():
      if vendor_id in ports[2] and product_id in ports[2]:
        return ports[0]
    else:
      return None

  except:
    return None

def get_hex(arr):
  r_value = []
  for value in arr:
    r_value.append(hex(ord(value)))
  return ' '.join(r_value)

def hex_debug(arr):
  """
  Converts a byte array to readable hex, dec and ascii string.
  """
  r_value = []
  for value in arr:
    r_value.append('%s/%d/%s' % (hex(ord(value)), ord(value), value))
  return ' '.join(r_value)

def print_hex(arr, new_line=True):
  """
    Takes an string and prints out the hex values.
  """
  for value in arr:
    h = hex(ord(value))#.replace('0x', '') 
    print '%s (%s)' % (h, ord(value)),
  if new_line:
    print ''
