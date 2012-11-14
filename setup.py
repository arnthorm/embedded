# -*- coding:utf8 -*-
from distutils.core import setup
packages = [
  'embedded',
  'embedded.messages',
  'embedded.messages.transports',
  'embedded.xbee'
]

requires = [
  'XBee',
  'pyserial'
]

setup(
  name='embedded',
  version='12.11',
  author='Arnþór Magnússon',
  packages=packages,
  requires=requires
)
