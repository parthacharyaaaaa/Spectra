import os
from dotenv import load_dotenv
from datetime import timedelta

CWD = os.path.dirname(__file__)


output = load_dotenv(dotenv_path=os.path.join(os.path.dirname(CWD), '.env'),
                verbose=True,
                override=True)

if not output:
    print(f"ERROR: Failed to parse .env file at: {os.path.join(os.path.dirname(CWD), '.env')}. Make sure path is entered correctly, and that a file actually exists there.")
    raise FileNotFoundError()

class AppConfig:
    '''### Class to encapsulate all Flask-related configurations into a single entity.

    Any failure to load configurations that are deemed mandatory will cause a crash, hence ensuring that the server never runs with improper or missing configurations. 
    
    Configurations which are not that crucial, or can be safely set to a default value in case of any issues, are looked up using the dict.get(key) method instead of dict[key]
    
    #### Note: This class does NOT encapsulate all environment variables in one place. See the .env file to get a full picture of the configurations used.'''
    try:
        SECRET_KEY = os.environ["APP_SECRET_KEY"]
        SESSION_PERMANENT = False

        PORT = int(os.environ["APP_PORT"])
        HOST = os.environ["APP_HOST"]

        SQLALCHEMY_DATABASE_URI = "sqlite:///{DB_URI}".format(DB_URI=os.environ["SQLALCHEMY_DB_URI"])
        SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get("DB_TRACK_MODIFICATIONS", False)

        SUPPORTED_VIDEO_FORMATS = os.environ["SUPPORTED_VIDEO_FORMATS"].split(",")
        MAX_VIDEO_SIZE = int(os.environ["MAX_VIDEO_SIZE"])

        REQUIRE_REDIS = bool(int(os.environ["REQUIRE_REDIS"]))
        REDIS_HOST = os.environ.get("REDIS_HOST")
        REDIS_PORT = int(os.environ.get("REDIS_PORT"))

        if REQUIRE_REDIS and not (REDIS_HOST and REDIS_PORT):
            raise ValueError("REQUIRE_REDIS set to True, but mandatory args not found")


        GENERIC_HTTP_MESSAGES : dict = {2 : "Success",
                                        3 : "Redirection",
                                        4 : "Client-Side Error",
                                        5 : "There seems to be an issue at our server. Please try again later"}

    except KeyError as e:
        print(f"ERROR: Missing configuration in {os.path.dirname(CWD), '.env'}, check .env file, Original Error: {e}")
        raise e
    except ValueError as e:
        print(f"ERROR: Invalid configuration in {os.path.dirname(CWD), '.env'}. Original Error: {e}")
        raise e
  
configObj = AppConfig()