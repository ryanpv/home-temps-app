import psycopg2
from models import Room

GET_ALL_TEMPS = """SELECT temperatures.temperature, rooms.*
                    FROM temperatures 
                    JOIN rooms 
                    ON temperatures.room_id=rooms.id;"""

class RoomService:
  def __init__(self, db_config):
    self.connection = psycopg2.connect(db_config)
    # self.create_table()

  def get_all_rooms(self):
    with self.connection.cursor() as cursor:
      cursor.execute(GET_ALL_TEMPS)
      rows = cursor.fetchall()
      print('rows', rows)

    return [Room(*row) for row in rows]
  