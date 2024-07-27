import psycopg2
from models import Room
from datetime import datetime, timezone

GET_ALL_TEMPS = """SELECT temperatures.temperature, rooms.*
                    FROM temperatures 
                    JOIN rooms 
                    ON temperatures.room_id=rooms.id;"""

GET_ROOM_TEMP = """SELECT temperatures.temperature, rooms.*
                  FROM temperatures
                  JOIN rooms
                  ON temperatures.room_id=rooms.id
                  WHERE rooms.id = (%s);"""

GLOBAL_AVG = "SELECT AVG(temperature) as average FROM temperatures;"
GLOBAL_NUMBER_OF_DAYS = "SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"

CREATE_ROOMS_TABLE = "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL,
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_TEMP = "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"

UPDATE_TEMPERATURE = """UPDATE temperatures 
                        SET temperature = (%s)
                        WHERE temperatures.room_id = (%s)
                        RETURNING room_id;                       
                        """


class RoomService:
  def __init__(self, db_config):
    self.connection = psycopg2.connect(db_config)
    # self.create_table()

  # list of rooms with their temps
  def get_all_rooms(self):
    try:
      with self.connection.cursor() as cursor:
        cursor.execute(GET_ALL_TEMPS)
        rows = cursor.fetchall()
        print('rows', rows)

      return [Room(*row) for row in rows]
    except Exception as e:
      print("ERROR FETCHIGN ROOMS /api/temperature", e)
      return "ERROR FETCHING /api/temperature"
  
  # single room
  def get_room(self, room_id):
    with self.connection.cursor() as cursor:
      cursor.execute(GET_ROOM_TEMP, (room_id,))
      result = cursor.fetchone()
      print('result: ', result)
    if result:
      return Room(*result)
    return None
  
  # temp average of all rooms
  def get_average(self):
    with self.connection.cursor() as cursor:
      cursor.execute(GLOBAL_AVG)
      average = cursor.fetchone()[0]
      cursor.execute(GLOBAL_NUMBER_OF_DAYS)
      days = cursor.fetchone()[0]
    return { "average": round(average, 2), "days": days }
  
  # add new room
  def add_room(self, name, temperature=None):
    try:
      with self.connection.cursor() as cursor:
        cursor.execute(CREATE_ROOMS_TABLE)
        cursor.execute(INSERT_ROOM_RETURN_ID, (name,))
        room_id = cursor.fetchone()[0]
      self.connection.commit()
      return Room(room_id, name, temperature)
    except Exception as e:
      print("EXCEPTION: ", e)
      return "error exeception"
    
  # add temperatures to room
  def add_temp(self, room_id, temperature, date):
    with self.connection.cursor() as cursor:
      cursor.execute(INSERT_TEMP, (room_id, temperature, date))
    self.connection.commit()
    return { "message": f"Temperature added for room: { room_id }" }
  
  # update room temperature
  def update_room_temp(self, temperature, room_id):
    with self.connection.cursor() as cursor:
      cursor.execute(UPDATE_TEMPERATURE, (temperature, room_id))
      updated_room = cursor.fetchone()[0]
    self.connection.commit()
    return { "message": f"Updated temperature for room: { updated_room }" }