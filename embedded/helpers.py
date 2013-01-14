
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

def get_usb(vendor_id=None, product_id=None):
  """
    Get usb serial port by vendor and product id.

    For example for FTDI device:
      vendor_id = '403'
      product_id = '6001'
  """
  from serial.tools import list_ports

  if vendor_id is None and product_id is None:
    import operator
    for ports in sorted(list_ports.comports(), key=operator.itemgetter(1)):
      if 'USB' in ports[0] or 'ACM0' in ports[0] or 'COM' in ports[0]:
        return ports[0]
  elif vendor_id is not None and product_id is not None:
    for ports in list_ports.comports():
      if vendor_id in ports[2] and product_id in ports[2]:
        return ports[0]
  else:
    raise ValueError('Vendor id and product id must both be set or not.')
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

def get_attr(obj, attrs):
  """
  Returns the value of the attributes of obj given in attrs.
  
  Keyword arguments:
    obj   -- Object with attribute(s)
    attrs -- The attributes to fetch, can be in the form a/b or a.b,
             where a is attribute of obj and b is attribute of a
  """
  if '/' in attrs:
    attrs = attrs.split('/')
  elif '.' in attrs:
    attrs = attrs.split('.')
  elif type(attrs) not in (list, tuple):
    attrs = (attrs,)
  for attr in attrs:
    if attr:
      obj = getattr(obj, attr)
  return obj

def set_attr(obj, attrs, value):
  """
  Set attribute of a object.
 
  This function is different from built-in setattr, as the attribute name
  can be hierarchical, i.e. obj has a attribute 'a' which is a object that
  has a attribute 'b', which can therefore be set with 'a/b' 
  Keyword arguments:
    obj   -- Object with attribute(s)
    attrs -- The attributes to set, can be hierarchical, in the
             form 'a/b' or 'a.b', where 'a' is attribute of obj 
             and 'b' is attribute of the object 'a'.
    value -- Value to be set as.
  """

  if '/' in attrs:
    attrs = attrs.split('/')
  elif '.' in attrs:
    attrs = attrs.split('.')
  elif type(attrs) not in (list, tuple):
    attrs = (attrs,)
  for idx in xrange(0, len(attrs)):
    if attrs[idx]:
      if idx < (len(attrs)-1):
        obj = getattr(obj, attrs[idx])
      elif idx == (len(attrs)-1):
        setattr(obj, attrs[idx], value)

def attrs_to_dict(object, attrs, map={}):
  """
  Attributes to dictionary

  Keyword arguments:
    object -- Object that contains attributes
    attrs  -- List of attributes to extract
    map    -- Dictionary map from attributes to dictionary.
  """
  d = {}
  for attr in attrs:
    key = attr
    if map.has_key(attr):
      attr = map[attr]
    if hasattr(object, attr):
      d[key] = get_attr(object, attr)
    else:
      d[key] = None
  return d

def dict_to_attrs(object, attrs, key_values):
  """
  Set objects attributes values from a given dictionary.

  Where the keys in the dictionary represents the attributes.
  Only the attributes listed in attrs will be set.
  Keyword arguments:
    object -- Object with attributes.
    attrs  -- Attributes to change.
    key_values -- Attributes values.
  """
  for key in attrs:
    setattr(object, key, key_values[key])

def attrs_to_attrs(obj_to, attrs, obj_from):
  """
  Copy attributes listed in attrs, from one object to another.
  """
  for attr in attrs:
    if hasattr(obj_to, attr):
      setattr(obj_to, attr, getattr(obj_from, attr))
