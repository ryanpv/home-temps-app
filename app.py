import os
import psycopg2
from datetime import datetime, timezone
from pprint import pprint
from psycopg2 import pool
from psycopg2.extras import DictCursor
from flask import Flask, request, jsonify, Blueprint
from dotenv import load_dotenv

from services import RoomService

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

# Update room temperature
@room_bp.route("/api/temperature", methods=["PUT"])
def update_temp():
  data = request.get_json()
  temperature = data["temperature"]
  room_id = data["room_id"]

  updated_room_temp = room_service.update_room_temp(temperature, room_id)
  return jsonify(updated_room_temp)



@app.get('/api/average')
def get_global_average():
  average = room_service.get_average()
  if average:
    return average
  return None


@app.get("/")
def home():
  try:

      # env_vars = {key: value for key, value in os.environ.items()}
      # return '<br>'.join([f'{key}: {value}' for key, value in env_vars.items()])
    query = ("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)

    with connection:
      with connection.cursor() as cursor:
        cursor.execute(query)
        table_list = cursor.fetchall()
        print("TABLE LIST: ", len(table_list))
    return "Tables have been fetched"
  except Exception as e: 
    print("No data found", e)
    return "No table data found"


app.register_blueprint(room_bp)