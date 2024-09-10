from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable CORS for all routes

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dbserial'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class aquamans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    oxygen = db.Column(db.Float)
    phlevel = db.Column(db.Float)
    turbidity = db.Column(db.Float)

@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            temperature = latest_record.temperature
            if isinstance(temperature, (int, float)): 
                return jsonify({'temperature': temperature})
            else:
                return jsonify({'temperature': 'Invalid data type'})
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
            oxygen = latest_record.oxygen
            if isinstance(oxygen, (int, float)):  # Ensure it's a number
                return jsonify({'oxygen': oxygen})
            else:
                return jsonify({'oxygen': 'Invalid data type'})
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
            phlevel = latest_record.phlevel
            if isinstance(phlevel, (int, float)):  # Ensure it's a number
                return jsonify({'phlevel': phlevel})
            else:
                return jsonify({'phlevel': 'Invalid data type'})
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
            turbidity = latest_record.turbidity
            if isinstance(turbidity, (int, float)):  # Ensure it's a number
                return jsonify({'turbidity': turbidity})
            else:
                return jsonify({'turbidity': 'Invalid data type'})
        else:
            return jsonify({'turbidity': 'N/A'})
    except Exception as e:
        print(f"Error fetching turbidity: {e}")
        return jsonify({'error': str(e)})




@app.route('/data', methods=['GET'])
def get_data():
    try:
        # Open a connection to the database
        with db.engine.connect() as connection:
            # Execute the raw SQL query
            result = connection.execute(text("SELECT * FROM aquamans"))

            # Get column names from the result metadata
            columns = result.keys()
            
            # Convert each row to a dictionary using the column names
            records = [dict(zip(columns, row)) for row in result]

            print(f"Total records fetched: {len(records)}")  # Debugging: Check the number of records fetched
            print(f"Fetched data: {records}")  # Debugging: Print the data fetched

            # No need for further conversion since records is already a list of dictionaries
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)})

    
@app.route('/temperature-data', methods=['GET'])
def get_temperature_data():
    try:
        # Open a connection to the database
        with db.engine.connect() as connection:
            # Execute the raw SQL query to fetch temperature and timeData columns
            result = connection.execute(text("SELECT id, temperature, timeData AS date FROM aquamans"))

            # Get column names from the result metadata
            columns = result.keys()

            # Convert each row to a dictionary using the column names
            records = [dict(zip(columns, row)) for row in result]

            print(f"Fetched temperature data: {records}")  # Debugging: Print the temperature data fetched

            return jsonify(records)
    except Exception as e:
        print(f"Error fetching temperature data: {e}")
        return jsonify({'error': str(e)})

@app.route('/weekly-temperature-data', methods=['GET'])
def get_weekly_temperature_data():
    try:
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Open a connection to the database
        with db.engine.connect() as connection:
            # Execute the raw SQL query to fetch temperature and date columns for the current week
            query = text("""
                SELECT temperature, timeData
                FROM aquamans
                WHERE timeData >= :start_date AND timeData <= :end_date
            """)
            result = connection.execute(query, {'start_date': start_of_week, 'end_date': end_of_week})

            # Get column names from the result metadata
            columns = result.keys()

            # Convert each row to a dictionary using the column names
            records = [dict(zip(columns, row)) for row in result]

            print(f"Fetched weekly temperature data: {records}")  # Debugging: Print the temperature data fetched

            return jsonify(records)
    except Exception as e:
        print(f"Error fetching weekly temperature data: {e}")
        return jsonify({'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
