import os

TOKEN = os.getenv("TOKEN")

ip = os.getenv("ip")
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DATABASE = os.getenv("DATABASE")

PG_URI = f"postreSQL://{PG_USER}:{PG_PASSWORD}@{ip}/{PG_DATABASE}"

ADMINS = os.getenv("ADMINS").split()