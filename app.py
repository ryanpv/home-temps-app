import os
import psycopg2
from datetime import datetime, timezone
from pprint import pprint
from psycopg2 import pool
from psycopg2.extras import DictCursor
from flask import Flask, request, jsonify, Blueprint
from dotenv import load_dotenv

from services import RoomService

CREATE_ROOMS_TABLE = "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL,
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_TEMP = "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"

# Get amount of different dates
GLOBAL_NUMBER_OF_DAYS = "SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"

GLOBAL_AVG = "SELECT AVG(temperature) as average FROM temperatures;"

GET_ALL_TEMPS = """SELECT temperatures.*, rooms.name 
                    FROM temperatures 
                    JOIN rooms 
                    ON temperatures.room_id=rooms.id;"""

GET_ROOM_TEMP = """SELECT temperatures.*, rooms.name
                  FROM temperatures
                  JOIN rooms
                  ON temperatures.room_id=rooms.id
                  WHERE rooms.id = (%s);"""

load_dotenv()
app = Flask(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')
# connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)
connection = psycopg2.connect(DATABASE_URL)
room_service = RoomService(DATABASE_URL)
room_bp = Blueprint('room', __name__)


@room_bp.route("/api/room/<room_id>", methods=["GET"])
def get_room(room_id):
  room = room_service.get_room(room_id)
  if room:
    return jsonify(room.dict_format())
  return jsonify({ 'error': 'Room does not exist' }), 404

@app.post("/api/room")
def create_room():
  data = request.get_json()
  print('POSTMAN DATA: ', data["name"])
  new_room = room_service.add_room(data["name"])
  return jsonify(new_room.dict_format())

  
# Get all room temperatures

@room_bp.route("/api/temperature", methods=['GET'])
def get_all_temps():
  rooms = room_service.get_all_rooms()
  return jsonify([room.dict_format() for room in rooms])

  
# Add temperatures of rooms
@app.post("/api/temperature")
def add_temp():
  data = request.get_json()
  temperature = data["temperature"]
  room_id = data["room"]
  try:
    date = datetime.strptime(data["data"], "%m-%d-%Y %H:%M:%S")
  except KeyError:
    date = datetime.now(timezone.utc)

  temp_added = room_service.add_temp(room_id, temperature, date)
  return jsonify(temp_added)


@app.get('/api/average')
def get_global_average():
  average = room_service.get_average()
  if average:
    return average
  return None
# def global_avg():
#   with connection: # 'with' to automatically close connection
#     with connection.cursor() as cursor: # best practice to also close cursor to ensure freeing unused resources
#       cursor.execute(GLOBAL_AVG)
#       average = cursor.fetchone()[0]
#       cursor.execute(GLOBAL_NUMBER_OF_DAYS)
#       days = cursor.fetchone()[0]
#   return {"average": round(average, 2), "days": days}


@app.get("/")
def home():
  return "Hello World!"

app.register_blueprint(room_bp)