import mariadb
from flask import Flask

# Configuration variables
config_file = 'config.ini'
address = ''
username = ''
password = ''
hostname = ''
port = ''
db = ''

# Start flask app (TODO: Does this need __name__ == '__main__'?
app = Flask(__name__)

# Read configuration file and set variables
def get_global_config():
    if not os.path.isfile(config_file):
        print(f"Error: needs configuration file '{config_file}'")
        exit()

    config = configparser.ConfigParser()
    config.read(config_file)
    
    address = config['Mining']['Address']

    username = config['ViewUser']['Username']
    password = config['ViewUser']['Password']
    hostname = config['Database']['Hostname']
    port = int(config['Database']['Port'])
    db = config['Database']['DB']

# Main page of app
@app.route('/')
def get_worker_statistics():
    get_global_config()
    try:
        conn = mariadb.connect(
                user=username,
                password=password,
                host=hostname,
                port=port,
                database=db
        )
    except mariadb.Error as e:
        print(f"Error connecting to database instance: {e}")
        exit()

    cur = conn.cursor()

    cur.execute(f"SELECT * FROM workers;",)

    arr = []
    for res in cur:
        arr.append(res)
    
    cur.close()
    conn.close()

    return arr

