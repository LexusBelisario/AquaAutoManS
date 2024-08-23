from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the database URI
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
            if isinstance(temperature, (int, float)):  # Ensure it's a number
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





if __name__ == '__main__':
    app.run(debug=True)
