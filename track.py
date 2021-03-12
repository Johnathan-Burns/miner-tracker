'''
Miner-Tracker: Track individual worker statistics in Pooled ETH Mining
Copyright (C) 2021 John Burns

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import mariadb
import requests
import configparser
import os.path

# Configuration variables
config_file = 'config.ini'

# Read configuration file and set variables
def get_global_config():
    if not os.path.isfile(config_file):
        print(f"Error: needs configuration file '{config_file}'")
        exit()

    config = configparser.ConfigParser()
    config.read(config_file)

    conf = {'address': config['Ethereum']['Address']}

    conf['user'] = config['TrackUser']['Username']
    conf['password'] = config['TrackUser']['Password']
    conf['host'] = config['Database']['Hostname']
    conf['port'] = int(config['Database']['Port'])
    conf['db'] = config['Database']['DB']

    return conf

def get_worker_names(conn):
    cur = conn.cursor()
    names = []

    cur.execute("SELECT WorkerName, WorkerID FROM workers;",)

    for name in cur:
        names.append(name)

    cur.close()
    return names

# Gets 12 hour historical stats for all workers
def get_worker_stats(conn, name, conf):
    cur = conn.cursor()
    shares = 0

    req = requests.get(f"https://api.ethermine.org/miner/:{conf['address']}/worker/{name[0]}/history")
    data = req.json()["data"]

    for x in data:
        # Only record data from the top of the hour to avoid overcounting shares
        time = x['time']
        if (time % 3600 == 0):
            cur.execute(f"SELECT Timestamp FROM history WHERE WorkerID={name[1]} AND Timestamp={time};",)

            if (cur.rowcount == 0):
                s = x['validShares']
                shares = shares + s
                cur.execute(f"INSERT INTO history(WorkerID, Timestamp, Shares) VALUES({name[1]}, {time}, {s});",)
                conn.commit()

    cur.close()
    return shares

# Updates the totals of a worker to include the newly inserted total
def update_totals(conn, worker_id, total):
    cur = conn.cursor()
    cur.execute(f"UPDATE workers SET TotalShares = TotalShares+{total} WHERE WorkerID = {worker_id}",)
    conn.commit()
    cur.close()

# Main function creates connection to database and executes functions as needed
if __name__ == '__main__':
    conf = get_global_config()
    try:
        conn = mariadb.connect(
                user = conf['user'],
                password = conf['password'],
                host = conf['hostname'],
                port = conf['port'],
                database = conf['db']
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB instance: {e}")
        exit()

    worker_names = get_worker_names(conn)
    for worker in worker_names:
        total = get_worker_stats(conn, worker, conf)
        print(f"Total for worker {worker[0]} - {total}")
        update_totals(conn, worker[1], total)

    # End session
    conn.close()
