

from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)


class Machine:
    def __init__(self, id, machine_name, machine_serial_no, time):
        self.id = id
        self.machine_name = machine_name
        self.machine_serial_no = machine_serial_no
        self.time = time


class ProductionLog:
    def __init__(self, id, cycle_no, unique_id, material_name, machine_id, start_time, end_time, duration):
        self.id = id
        self.cycle_no = cycle_no
        self.unique_id = unique_id
        self.material_name = material_name
        self.machine_id = machine_id
        self.start_time = start_time
        self.end_time = end_time
        self.duration = duration


def connect_db():
    conn = sqlite3.connect('example.db')
    return conn


def create_tables():
    conn = connect_db()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS machine (
            id INTEGER PRIMARY KEY,
            machine_name TEXT,
            machine_serial_no TEXT,
            time TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS product_log (
            id INTEGER PRIMARY KEY,
            cycle_no TEXT,
            unique_id TEXT UNIQUE,
            material_name TEXT,
            machine_id INTEGER,
            start_time TEXT,
            end_time TEXT,
            duration FLOAT
        )
    """)
    conn.commit()
    conn.close()


def calculate_availability(total_shift_time, total_products, available_operating_time):
    unplanned_downtime = total_shift_time - available_operating_time
    if available_operating_time == 0:
        return 0
    return ((total_shift_time - unplanned_downtime) / total_shift_time) * 100


def calculate_performance(total_products, available_operating_time):
    if available_operating_time == 0:
        return 0
    return ((5 / 60) * total_products / available_operating_time) * 100


def calculate_quality(total_products, good_products):
    if total_products == 0:
        return 0
    return (good_products / total_products) * 100


def calculate_oee(production_logs):
    if not production_logs:
        return {
            'availability': 0,
            'performance': 0,
            'quality': 0,
            'oee': 0
        }

    total_products = len(production_logs)
    good_products = sum(1 for log in production_logs if log.duration == 5.0)  

    total_shift_time = 24 * 3  
    available_operating_time = total_products * 5  

    availability = calculate_availability(total_shift_time, total_products, available_operating_time)
    performance = calculate_performance(total_products, available_operating_time)
    quality = calculate_quality(total_products, good_products)

    oee = (availability * performance * quality) / 10000

    return {
        'availability': availability,
        'performance': performance,
        'quality': quality,
        'oee': oee
    }


@app.route('/oee', methods=['GET'])
def get_oee():
    machine_id = request.args.get('machine_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    conn = connect_db()
    c = conn.cursor()
    c.execute("SELECT * FROM product_log WHERE machine_id = ? AND start_time >= ? AND end_time <= ?", 
              (machine_id, start_time, end_time))
    rows = c.fetchall()
    product_logs = [ProductionLog(*row) for row in rows]
    conn.close()

    oee_values = calculate_oee(product_logs)

    return jsonify(oee_values)


if __name__ == '__main__':
    create_tables()
    app.run(debug=True, port=2002)














