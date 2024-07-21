class Room:
  def __init__(self, id, name, temperature=None): # constructor
    self.id = id 
    self.name = name
    self.temperature = temperature

  def dict_format(self):
    return {
      "id": self.id,
      "name": self.name,
      "temperature": self.temperature
    }