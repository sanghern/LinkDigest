import sys
import os

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.db.db_init import init_db

if __name__ == "__main__":
    init_db() 