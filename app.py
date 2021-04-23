import mariadb
import web3
import os
import configparser
from flask import Flask

# Configuration variables
config_file = 'config.ini'

# Start flask app (TODO: Does this need __name__ == '__main__'?
app = Flask(__name__)

# Read configuration file and set variables
def get_global_config():
    if not os.path.isfile(config_file):
        print(f"Error: needs configuration file '{config_file}'")
        exit()

    config = configparser.ConfigParser()
    config.read(config_file)
    
    conf = {'address': config['Ethereum']['Address']}
    conf['ipc'] = config['Ethereum']['IPCLocation']

    conf['user'] = config['ViewUser']['Username']
    conf['password'] = config['ViewUser']['Password']
    conf['host'] = config['Database']['Hostname']
    conf['port'] = int(config['Database']['Port'])
    conf['db'] = config['Database']['DB']
    print('Successfully read global config')
    return conf 

# Main page of app
@app.route('/')
def get_worker_statistics():
    conf = get_global_config()
    try:
        #print(f"Connecting with {conf['user']}/{conf['password']} to {conf['host']}:{conf['port']}")
        conn = mariadb.connect(
                user = conf['user'],
                password = conf['password'],
                host = conf['host'],
                port = conf['port'],
                db = conf['db']
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

    return str(arr)

