

class Transport():
  
  def send(self, data):
    raise NotImplementedError("Not implemented, abstract class!")
  
  def receive(self):
    raise NotImplementedError("Not implemented, abstract class!")

  def stop(self):
    raise NotImplementedError("Not implemented, abstract class!")

