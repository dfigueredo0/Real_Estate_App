import psycopg2
import logging
import os
from psycopg2 import DatabaseError 
from dotenv import load_dotenv

load_dotenv()

DB_NAME = os.environ.get("DB_NAME")
USER_NAME = os.environ.get("USER_NAME")
PASSWORD = os.environ.get("PASSWORD")
HOST = os.environ.get("HOST")
PORT = os.environ.get("PORT", "5432")

def get_connection():
    try:
        logging.info("Connecting to the database...")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=USER_NAME,
            password=PASSWORD,
            host=HOST,
            port=PORT
        )
        logging.info("Database connection established.")
        return conn
    except DatabaseError as e:
        logging.error(f"Database connection error: {e}")
        raise e