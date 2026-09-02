import os
import sys

# Ensure backend directory is in path to import correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine
from models import User

def recreate_users_table():
    print("Dropping old users table...")
    User.__table__.drop(engine, checkfirst=True)
    print("Creating new users table...")
    User.__table__.create(engine)
    print("Done!")

if __name__ == "__main__":
    recreate_users_table()
