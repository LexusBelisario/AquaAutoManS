from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime, timedelta
import threading
import logging
import time


logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://admin:password@localhost/dbserial'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class aquamans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    oxygen = db.Column(db.Float)
    phlevel = db.Column(db.Float)
    turbidity = db.Column(db.Float)
    catfish = db.Column(db.Float, default=0)
    dead_catfish = db.Column(db.Float, default=0)
    timeData = db.Column(db.DateTime, default=datetime.utcnow)



@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'temperature': latest_record.temperature})
        else:
            return jsonify({'temperature': 'N/A'})
    except Exception as e:
        print(f"Error fetching temperature: {e}")
        return jsonify({'error': str(e)})

@app.route('/oxygen', methods=['GET'])
def get_oxygen():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'oxygen': latest_record.oxygen})
        else:
            return jsonify({'oxygen': 'N/A'})
    except Exception as e:
        print(f"Error fetching oxygen: {e}")
        return jsonify({'error': str(e)})

@app.route('/phlevel', methods=['GET'])
def get_phlevel():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'phlevel': latest_record.phlevel})
        else:
            return jsonify({'phlevel': 'N/A'})
    except Exception as e:
        print(f"Error fetching phlevel: {e}")
        return jsonify({'error': str(e)})

@app.route('/turbidity', methods=['GET'])
def get_turbidity():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            return jsonify({'turbidity': latest_record.turbidity})
        else:
            return jsonify({'turbidity': 'N/A'})
    except Exception as e:
        print(f"Error fetching turbidity: {e}")
        return jsonify({'error': str(e)})

@app.route('/data', methods=['GET'])
def get_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)})

@app.route('/temperature-data', methods=['GET'])
def get_temperature_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT id, temperature, timeData AS date FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
        return jsonify({'error': str(e)})

@app.route('/weekly-temperature-data', methods=['GET'])
def get_weekly_temperature_data():
    try:
        filter_type = request.args.get('filter', 'weekly')
        
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT temperature, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0: 
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly temperature data: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/weekly-oxygen-data', methods=['GET'])
def get_weekly_oxygen_data():
    try:
        filter_type = request.args.get('filter', 'weekly')

        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT oxygen, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0: 
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly oxygen data: {e}")
        return jsonify({'error': str(e)})


@app.route('/weekly-ph-data', methods=['GET'])
def get_weekly_phlevel_data():
    try:
        filter_type = request.args.get('filter', 'weekly')

        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        with db.engine.connect() as connection:
            query = text("""
                SELECT phlevel, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == '3hours':
                filtered_records = []
                for record in records:
                    time_data = record['timeData']
                    hour = time_data.hour
                    if hour % 3 == 0:  
                        filtered_records.append(record)
                return jsonify(filtered_records)
            else:
                return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly oxygen data: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    global sensor_data
    data = request.json
    sensor_data = {
        'temperature': data.get('temperature'),
        'oxygen': data.get('oxygen'),
        'phlevel': data.get('phlevel'),
        'turbidity': data.get('turbidity')
    }
    logging.debug(f"Updated sensor data: {sensor_data}")
    return jsonify({'status': 'success'})

@app.route('/update_detection', methods=['POST'])
def update_detection():
    try:
        data = request.json
        catfish_count = data.get('catfish', 1)
        dead_catfish_count = data.get('dead_catfish', 0)

        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            latest_record.catfish = catfish_count
            latest_record.dead_catfish = dead_catfish_count
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Detection data updated'})
        else:
            return jsonify({'status': 'failure', 'message': 'No record to update'})
    except Exception as e:
        print(f"Error updating detection data: {e}")
        return jsonify({'status': 'error', 'message': str(e)})
if __name__ == '__main__':
    app.run(debug=True)