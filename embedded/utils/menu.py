
import threading

class MenuManager:
  """Menu manager for easy prototyping.
  """
  def __init__(self):
    self.commands = {}

  def add(self, option, text, callback, run_as_thread=False):
    if run_as_thread:
      self.commands.update({option: (text, callback)})
    else:
      self.commands.update({option: (text, self.run_as_thread(callback))})

  def activate(self):
    print('Menu:')
    for key in sorted(self.commands.keys()):
      print('  %s: %s' % (key, self.commands[key][0]))
    output = raw_input('Select option: ')
    if self.commands.has_key(output):
      self.commands[output][1]()

  def run_as_thread(self, func):
    def to_run():
      thr = threading.Thread(name="", target=func)
      thr.start()
    return to_run
