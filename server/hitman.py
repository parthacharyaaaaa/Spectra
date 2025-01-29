### No witnesses ###
import os
import sqlite3
from time import sleep
from datetime import datetime
from dotenv import load_dotenv
CWD = os.path.dirname(__file__)


output = load_dotenv(dotenv_path=os.path.join(os.path.dirname(CWD), '.env'),
                verbose=True)

if not output:
    raise FileNotFoundError(f".env file at {os.path.join(os.path.dirname(CWD), '.env')} not found. Script execution aborted. Time: {datetime.now()}")

DB_PATH : os.PathLike = os.path.join(os.path.dirname(os.path.dirname(__file__)), os.environ["SQLALCHEMY_DB_URI"])

def bravo_6_going_dark(timeout : int = int(os.environ["CLEANER_TIMEOUT"])) -> None:
    sleep(timeout)

if __name__ == "__main__":
    print("Dispatched cleaner: ", os.getpid())
    MAX_ATTEMPTS = 3
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        db_cursor = conn.cursor()
    except:
        print("Failed to connect to database")
        exit(404)

    while(True):
        ### Base variables ###
        failed : bool = True
        attempt : int = 0

        ### Savepoint to valid transactional state for rollbacks ###
        db_cursor.execute("SAVEPOINT _sp")

        ### Begin job ###
        while attempt < MAX_ATTEMPTS:
            try:
                db_cursor.execute("DELETE FROM audio_entities WHERE in_hitlist = true;")
                conn.commit()
                print(f"[{attempt}] Hit(s) succesful")
                failed = False
                break
            except:
                db_cursor.execute("ROLLBACK TO _sp")
                print(f"[{attempt}] Hit(s) failed, trying again")
                attempt+=1
        if failed:
            print("Hit(s) failed, will try later in next iteration")

        ### Go dormant for some time ###
        bravo_6_going_dark()