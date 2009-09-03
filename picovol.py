#!/usr/bin/env python

import dbus
import gobject
import commands
import sys
import re

from dbus.mainloop.glib import DBusGMainLoop

class VolumeManager(object):

  GET = "amixer get Master"
  SET = "amixer set Master %s"

  def __init__(self, current=80, min=0, max=255, auto_detect=True):
    if auto_detect:
      status, output, (min, max, current, ismute) = self._getmixerinfo()
      if status != 0:
        sys.stderr.write(output)
        raise Exception("Could not get volume from amixer.")

    self.min = min
    self.max = max
    self.current = current
    self.ismute = ismute
    self._step = (max - min) / 12

  def toggle(self):
    status, output = commands.getstatusoutput(self.SET % 'toggle')
    if status == 0:
      self.ismute = not self.ismute
    return status, output

  def louder(self, step=None):
    return self._offset(step or self._step)

  def softer(self, step=None):
    return self._offset(step or -self._step)

  def _offset(self, offset):
    if offset < 0:
      set_to = max(self.min, self.current + offset)
    else:
      set_to = min(self.max, self.current + offset)
    status, output = self._set(set_to)
    if status == 0:
      self.current = set_to
    return status, output

  def _set(self, level):
    assert level >= self.min, "Failed: %d >= %d" % (level , self.min)
    assert level <= self.max, "Failed: %d <= %d" % (level , self.max)
    return commands.getstatusoutput(self.SET % level)

  def _getmixerinfo(self):
    status, output = commands.getstatusoutput(self.GET)
    range, current = re.findall("Playback (\d+(?: - \d+)?)", output)
    min, max = map(int, range.split(' - '))
    current = int(current)
    ismute = output.endswith('[off]')
    return status, output, (min, max, current, ismute)

  def _getvolume(self):
    _, _, (_, _, current) = self.getminmaxcurrent()
    return current

volume = VolumeManager()
actions = dict([
  ('mute', volume.toggle),
  ('volume-up', volume.louder),
  ('volume-down', volume.softer)
])

def handler(sender=None, destination=None):
  if sender == "ButtonPressed":
    status, output = actions.get(
        destination,
        lambda:(1, "Unknown: %s" % destination)
        )()

DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()
path = '/org/freedesktop/Hal/devices/'
dev = bus.get_object(
    'org.freedesktop.Hal',
    path + 'platform_i8042_i8042_KBD_port_logicaldev_input'
    )
iface = dbus.Interface(dev, 'org.freedesktop.Hal.Device')
iface.connect_to_signal('Condition', handler)

try:
  loop = gobject.MainLoop()
  loop.run()
finally:
  bus.close()
