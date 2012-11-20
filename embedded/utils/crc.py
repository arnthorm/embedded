# -*- coding: utf-8 -*-

import struct

__author__ = 'Arnþór Magnússon' # Created Sept. 2012

def crc16_update(crc, data):
  for i in range(8):
    j = (data^crc) & 0x0001
    crc >>= 1
    if j:
      crc ^= 0xa001
    data >>= 1
  return crc

def crc_pack(crc, endian='<'):
  return struct.pack(endian + 'H', crc)

def crc16(string):
  crc = 0
  for data in string:
    crc = crc16_update(crc, ord(data))
  return crc_pack(crc)


if __name__ == '__main__':
  data = 'this is just a test'
  print crc16(data)
