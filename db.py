import psycopg2
from key import password

def get_connection():
    return psycopg2.connect(
        dbname="real_estate",
        user="postgres 17",
        password=password,
        host="localhost",
        port="5432"
    )