import os
import psycopg2
from psycopg2 import pool
from flask import Flask
from dotenv import load_dotenv

CREATE_ROOMS_TABLE = (
  "CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);"
)
CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL,
                        date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
INSERT_TEMP = (
  "INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);"
)

# Get amount of different dates
GLOBAL_NUMBER_OF_DAYS = (
  """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;"""
)
GLOBAL_AVG = """SELECT AVG(temperature) as average FROM temperatures;"""

load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)


@app.get("/")
def home():
  return "Hello World!"