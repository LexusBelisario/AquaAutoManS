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



if __name__ == '__main__':
    app.run(debug=True)
