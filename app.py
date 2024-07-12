import os
import psycopg2
from psycopg2 import pool
from flask import Flask
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DATABASE_URL = os.getenv('DATABASE_URL')

connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)


@app.get("/")
def home():
  return "Hello World!"