
import threading

class MenuManager:
  """Menu manager for easy prototyping."""
  def __init__(self):
    self.commands = {}
    self.threads = []

  def add(self, option, text, callback, run_as_thread=False):
    if run_as_thread:
      self.commands.update({option: (text, self.run_as_thread_wrap(callback))})
    else:
      self.commands.update({option: (text, callback)})

  def activate(self):
    print('Menu:')
    for key in sorted(self.commands.keys()):
      print('  %s: %s' % (key, self.commands[key][0]))
    output = raw_input('Select option: ')
    print('')
    if self.commands.has_key(output):
      try:
        self.commands[output][1]()
      except KeyboardInterrupt:
        pass

  def run_as_thread_wrap(self, func):
    def to_run():
      thr = threading.Thread(name="", target=func)
      self.threads.append(thr)
      thr.start()
    return to_run

  def run_as_thread(self, func):
    thr = threading.Thread(name="", target=func)
    self.threads.append(thr)
    thr.start()
    return thr

  def stop(self):
    for thread in self.threads:
      thread.join()
