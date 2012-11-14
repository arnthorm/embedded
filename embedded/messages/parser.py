# -*- coding:utf-8 -*-
import struct
from collections import namedtuple

from embedded.helpers import hex_debug

COMMAND_TYPE = 'B'

__author__ = 'Arnþór Magnússon'

class MessageParser(object):
  """
  Message parser and serializer.

  Parses C-struct like messages according to message descriptions,
  as well serializes messages to C-struct like messages.
  """
  def __init__(self, endian='<'):
    self.endian = endian
    self.reset()

  def reset(self):
    """Remove all message descriptions."""
    self.types = {}

  def _msg_type(self, value):
    """Convert message type from str to int, if necessary."""
    if type(value) is str:
      return ord(value)
    else:
      return value

  def add(self, msg_type, description):
    """Add message description for a given message type."""
    self.types[self._msg_type(msg_type)] = description
  
  def add_collection(self, collection):
    """Add a collection of message descriptions."""
    for key in collection.keys():
      self.add(key, collection[key])

  def get_message_description(self, msg_type):
    """Return a message description of a given message type"""
    if self.types.has_key(msg_type):
      return self.types[msg_type]
    else:
      return None

  def parse(self, data):
    """Parse struct like message into a dictionary."""
    if len(data) > 0:
      msgType = ord(data[0])
      if self.types.has_key(msgType):
        t = self.types[msgType]
        types = ''.join(t['types'])
        if t.has_key('has_array') and t['has_array']:
          size = struct.calcsize(self.endian + COMMAND_TYPE + ''.join(t['types'][:-1]))
          types = types % (len(data)-size)#ord(data[size-1]) 
          #types = types % ord(data[size-1]) # the old way, byte with length
        Obj = namedtuple(t['name'], ('msg_type',) + t['fields'])
        data_format = self.endian + COMMAND_TYPE + types
        try:
          obj = Obj._make(
            struct.unpack(
              data_format,
              data
            )
          )
        except Exception as e:
          raise type(e)(e.message + 
            '.\nWhile processing message of type %d.\n' % msgType + 
            'Data length %d (%s).\n' % (len(data), hex_debug(data)) + 
            'Required length %d (%s).\n' % (struct.calcsize(data_format), data_format)
          )
        return obj
      else:
        return None

  def make(self, msg_type, data):
    """Make a struct like message from a dictionary."""
    msg_type = self._msg_type(msg_type)
    if (not self.types.has_key(msg_type)):
      raise Exception('Message type does not exists!')
    t = self.types[msg_type]
    types = ''.join(t['types'])
    if t.has_key('has_array') and t['has_array'] and 'length' in t['fields']:
      data['length'] = len(data[t['fields'][-1]])
      types = types % data['length']
    try:
      return struct.pack(
        self.endian + COMMAND_TYPE + types,
        *self._data_to_list(data, t['fields'], msg_type)
      )
    except Exception as e:
      raise type(e)(e.message +
        '\n While making message of type %d\n' % msg_type +
        'Data: %s.\n' % (str(data)) + 
        'Fields: %s\n' % (str(t['fields'])) + 
        'Types: %s.\n' % types
      )

  def _data_to_list(self, data, fields, id):
    """Convert dictionary data into ordered list, according to 
    message description."""
    l = [id]
    for field in fields:
      if type(data[field]) in (list, tuple):
        for value in data[field]:
          l.append(value)
      else:
        l.append(data[field])
    return l

