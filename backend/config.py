from flask import Flask, Response, jsonify, request, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime, timedelta
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
import base64
import logging
import threading
import time
from PIL import Image

active = True 

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/dbserial'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class aquamans(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Float)
    tempResult = db.Column(db.String(255))
    oxygen = db.Column(db.Float)
    oxygenResult = db.Column(db.String(255))
    phlevel = db.Column(db.Float)
    phResult = db.Column(db.String(255))
    turbidity = db.Column(db.Float)
    turbidityResult = db.Column(db.String(255))
    catfish = db.Column(db.Float, default=0)
    dead_catfish = db.Column(db.Float, default=0)
    timeData = db.Column(db.DateTime, default=datetime.utcnow)
    dead_catfish_image = db.Column(db.LargeBinary, nullable=True)
    
def periodic_sleep():
    """
    """
    global active
    while True:
        logging.info("System active.")
        time.sleep(3600 - 300)
        logging.info("System will sleep for 5 minutes to prevent overheating.")
        active = False
        time.sleep(300)
        active = True
        logging.info("System resumed.")

def some_background_task():
    while True:
        if not active:
            logging.info("Task paused due to system rest period.")
            time.sleep(300) 
            continue
        
        logging.info("Task executed.")
        time.sleep(60)

sleep_thread = threading.Thread(target=periodic_sleep, daemon=True)
sleep_thread.start()    

@app.route('/some-sensitive-task', methods=['GET'])
def sensitive_task():
    if not active:
        return jsonify({'status': 'inactive', 'message': 'System is in rest mode. Try again later.'}), 503
    return jsonify({'status': 'success', 'message': 'Task executed successfully.'})

@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            logging.debug(f"Latest temperature record: {latest_record.temperature}")
            return jsonify({'temperature': latest_record.temperature})
        else:
            return jsonify({'temperature': 'N/A'})
    except Exception as e:
        logging.error(f"Error fetching temperature: {e}")
        return jsonify({'error': str(e)})


@app.route('/oxygen', methods=['GET'])
def get_oxygen():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            logging.debug(f"Latest oxygen record: {latest_record.oxygen}")
            return jsonify({'oxygen': latest_record.oxygen})
        else:
            return jsonify({'oxygen': 'N/A'})
    except Exception as e:
        logging.error(f"Error fetching oxygen: {e}")
        return jsonify({'error': str(e)})

    
@app.route('/phlevel', methods=['GET'])
def get_phlevel():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            logging.debug(f"Latest pH level record: {latest_record.phlevel}")
            return jsonify({'phlevel': latest_record.phlevel})
        else:
            return jsonify({'phlevel': 'N/A'})
    except Exception as e:
        logging.error(f"Error fetching pH level: {e}")
        return jsonify({'error': str(e)})


@app.route('/turbidity', methods=['GET'])
def get_turbidity():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
        if latest_record:
            logging.debug(f"Latest turbidity record: {latest_record.turbidity}")
            return jsonify({'turbidity': latest_record.turbidity})
        else:
            return jsonify({'turbidity': 'N/A'})
    except Exception as e:
        logging.error(f"Error fetching turbidity: {e}")
        return jsonify({'error': str(e)})

@app.route('/data', methods=['GET'])
def get_data():
    try:
        date_filter = request.args.get('date', None)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
            except ValueError:
                return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
        else:
            filter_date = None

        with db.engine.connect() as connection:
            if filter_date:
                query = """
                    SELECT * FROM aquamans
                    WHERE DATE(timeData) = :filter_date
                """
                result = connection.execute(text(query), {'filter_date': filter_date})
            else:
                query = "SELECT * FROM aquamans"
                result = connection.execute(text(query))

            records = []
            for row in result:
                record = dict(zip(result.keys(), row))
                
                for key, value in record.items():
                    if isinstance(value, bytes):
                        record[key] = base64.b64encode(value).decode('utf-8')

                records.append(record)

            if not records:
                return jsonify({"message": "No data found for the selected date."}), 404

            return jsonify(records)

    except Exception as e:
        print(f"Error fetching data: {e}")
        return jsonify({'error': str(e)}), 500

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

@app.route('/filtered-temperature-data', methods=['GET'])
def get_filtered_temperature_data():
    try:
        filter_type = request.args.get('filter', 'date')
        selected_date = request.args.get('selected_date')
        selected_week_start = request.args.get('week_start')
        
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        
        if selected_week_start:
            selected_week_start = datetime.strptime(selected_week_start, '%Y-%m-%d')
            end_of_week = selected_week_start + timedelta(days=6) 

        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT temperature, timeData FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == 'date' and selected_date:
                filtered_records = [
                    record for record in records if record['timeData'].date() == selected_date.date()
                ]
                return jsonify(filtered_records)

            elif filter_type == 'week' and selected_week_start:
                filtered_records = [
                    record for record in records if selected_week_start <= record['timeData'] <= end_of_week
                ]
                return jsonify(filtered_records)

            return jsonify(records)

    except Exception as e:
        print(f"Error fetching filtered temperature data: {e}")
        return jsonify({'error': str(e)})

@app.route('/oxygen-data', methods=['GET'])
def get_oxygen_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT id, oxygen, timeData AS date FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching oxygen data: {e}")
        return jsonify({'error': str(e)})

@app.route('/filtered-oxygen-data', methods=['GET'])
def get_filtered_oxygen_data():
    try:
        filter_type = request.args.get('filter', 'date')
        selected_date = request.args.get('selected_date')
        selected_week_start = request.args.get('week_start')
        
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        
        if selected_week_start:
            selected_week_start = datetime.strptime(selected_week_start, '%Y-%m-%d')
            end_of_week = selected_week_start + timedelta(days=6)

        with db.engine.connect() as connection:
            
            result = connection.execute(text("SELECT oxygen, timeData FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

           
            if filter_type == 'date' and selected_date:
                filtered_records = [
                    record for record in records if record['timeData'].date() == selected_date.date()
                ]
                return jsonify(filtered_records)

            elif filter_type == 'week' and selected_week_start:
                filtered_records = [
                    record for record in records if selected_week_start <= record['timeData'] <= end_of_week
                ]
                return jsonify(filtered_records)

            return jsonify(records)

    except Exception as e:
        print(f"Error fetching filtered oxygen data: {e}")
        return jsonify({'error': str(e)})

@app.route('/phlevel-data', methods=['GET'])
def get_phlevel_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT id, phlevel, timeData AS date FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching pH level data: {e}")
        return jsonify({'error': str(e)})

@app.route('/filtered-phlevel-data', methods=['GET'])
def get_filtered_phlevel_data():
    try:
        filter_type = request.args.get('filter', 'date')
        selected_date = request.args.get('selected_date')
        selected_week_start = request.args.get('week_start')
        
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        
        if selected_week_start:
            selected_week_start = datetime.strptime(selected_week_start, '%Y-%m-%d')
            end_of_week = selected_week_start + timedelta(days=6) 

        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT phlevel, timeData FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == 'date' and selected_date:
                filtered_records = [
                    record for record in records if record['timeData'].date() == selected_date.date()
                ]
                return jsonify(filtered_records)

            elif filter_type == 'week' and selected_week_start:
                filtered_records = [
                    record for record in records if selected_week_start <= record['timeData'] <= end_of_week
                ]
                return jsonify(filtered_records)

            return jsonify(records)

    except Exception as e:
        print(f"Error fetching filtered pH level data: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/turbidity-data', methods=['GET'])
def get_turbidity_data():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT id, turbidity, timeData AS date FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]
            return jsonify(records)
    except Exception as e:
        print(f"Error fetching turbidity data: {e}")
        return jsonify({'error': str(e)})

@app.route('/filtered-turbidity-data', methods=['GET'])
def get_filtered_turbidity_data():
    try:
        filter_type = request.args.get('filter', 'date')
        selected_date = request.args.get('selected_date')
        selected_week_start = request.args.get('week_start')
        
        if selected_date:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
        
        if selected_week_start:
            selected_week_start = datetime.strptime(selected_week_start, '%Y-%m-%d')
            end_of_week = selected_week_start + timedelta(days=6)

        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT turbidity, timeData FROM aquamans"))
            columns = result.keys()
            records = [dict(zip(columns, row)) for row in result]

            if filter_type == 'date' and selected_date:
                filtered_records = [
                    record for record in records if record['timeData'].date() == selected_date.date()
                ]
                return jsonify(filtered_records)

            elif filter_type == 'week' and selected_week_start:
                filtered_records = [
                    record for record in records if selected_week_start <= record['timeData'] <= end_of_week
                ]
                return jsonify(filtered_records)

            return jsonify(records)

    except Exception as e:
        print(f"Error fetching filtered turbidity data: {e}")
        return jsonify({'error': str(e)})

    
@app.route('/update_sensor_data', methods=['POST'])
def update_sensor_data():
    try:
        data = request.json
        new_record = aquamans(
            temperature=data.get('temperature'),
            oxygen=data.get('oxygen'),
            phlevel=data.get('phlevel'),
            turbidity=data.get('turbidity'),
            timeData=datetime.utcnow()
        )
        db.session.add(new_record)
        db.session.commit()

        logging.debug(f"Updated sensor data: {new_record}")
        return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error updating sensor data: {e}")
        return jsonify({'status': 'failure', 'error': str(e)})

@app.route('/update_detection', methods=['POST'])
def update_detection():
    try:
        data = request.json
        catfish_count = int(data.get('catfish', 0))
        dead_catfish_count = int(data.get('dead_catfish', 0))

        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            latest_record.catfish = catfish_count
            latest_record.dead_catfish = dead_catfish_count
            db.session.commit()
            return jsonify({'status': 'success', 'message': 'Detection data updated'})
        else:
            return jsonify({'status': 'failure', 'message': 'No record to update'})
    except Exception as e:
        logging.error(f"Error updating detection data: {e}")
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/check_dead_catfish', methods=['GET'])
def check_dead_catfish():
    try:
        dead_catfish_records = aquamans.query.filter(aquamans.dead_catfish > 0).order_by(aquamans.timeData.desc()).all()

        if not dead_catfish_records:
            latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
            if latest_record:
                if (latest_record.temperature == 0 and
                    latest_record.oxygen == 0 and
                    latest_record.phlevel == 0 and
                    latest_record.turbidity == 0):
                    return jsonify({
                        'message': 'No valid data available in the system.',
                    })

                return jsonify({
                    'message': 'No dead catfish detected in the system.',
                    'latest_data': {
                        'temperature': latest_record.temperature,
                        'oxygen': latest_record.oxygen,
                        'phlevel': latest_record.phlevel,
                        'turbidity': latest_record.turbidity
                    }
                })

        latest_record = dead_catfish_records[0]

        if (latest_record.temperature == 0 and
            latest_record.oxygen == 0 and
            latest_record.phlevel == 0 and
            latest_record.turbidity == 0):
            return jsonify({
                'message': 'No valid data available in the system.',
            })

        possible_causes = []

        # Temperature Analysis
        temperature_possibilities =[]
        if 26 <= latest_record.temperature <= 32:
            temperature_status = "The Water had a Normal Temperature"
        elif 20 < latest_record.temperature < 26:
            temperature_status = "The Water had a Below Average Temperature"
            temperature_possibilities.extend(["Sub Par Cold Temperature in Environment", "Cold Water was used"])
        elif latest_record.temperature <= 20:
            temperature_status = "The Water had a Cold Temperature"
            temperature_possibilities.extend(["Cold Temperature in Environment", "Cold Water was used", "Cold Wind"])
        elif 26 < latest_record.temperature < 35:
            temperature_status = "The Water had an Above Average Temperature"
            temperature_possibilities.extend(["Hot Temperature in Environment", "Lukewarm Water was used", "Slightly Exposed to a Sunlight"])
        elif latest_record.temperature >= 35:
            temperature_status = "The Water had a Hot Temperature"
            temperature_possibilities.extend(["Very Hot Temperature in Environment", "Boiling Water was used", "Full Exposure to Sunlight"])
            
        if temperature_possibilities:
            temp_cause_message = f"The Temperature suggests the presence of: {', '.join(temperature_possibilities)}."
            possible_causes.append(temp_cause_message)

        # Oxygen Analysis
        oxygen_possibilities = []
        if latest_record.oxygen <= 0.8:
            oxygen_status = "The Water had a Very Low Oxygen"
            oxygen_possibilities.extend(["Overstocking of Catfish", "Stagnant Water", "No Ventilation", "Overfeeding"])
        elif latest_record.oxygen < 1.5:
            oxygen_status = "The Water had a Low Oxygen"
            oxygen_possibilities.extend(["High Volumes of Catfish", "Low Movement of Water", "Little Ventilation"])
        elif 1.5 <= latest_record.oxygen <= 5:
            oxygen_status = "The Water had a Normal Oxygen"
        else:
            oxygen_status = "The Water had a High Oxygen"
            oxygen_possibilities.extend(["Over-aeration of Water", "Chemicals", "Hyperoxygenation"])
        
        if oxygen_possibilities:
            oxygen_cause_message = f"The Oxygen Level suggests the presence of: {', '. join(oxygen_possibilities)}."
            possible_causes.append(oxygen_cause_message)

        ph_possibilities = []
        if latest_record.phlevel < 4:
            ph_status = "The Water was Very Acidic"
            ph_possibilities.extend(["Baking Soda", "Acid Rain", "Vinegar"])
        elif 4 <= latest_record.phlevel < 6:
            ph_status = "The Water was Acidic"
            ph_possibilities.extend(["Acidic Products", "Coffee"])
        elif 6 <= latest_record.phlevel <= 7.5:
            ph_status = "The Water was Normal pH Level"
        elif 7.6 <= latest_record.phlevel <= 8.9:
            ph_status = "The Water was Alkaline"
            ph_possibilities.extend(["Saltwater, Baking Soda"])
        elif latest_record.phlevel > 9:
            ph_status = "The Water was Very Alkaline"
            ph_possibilities.extend(["Dishwashing Liquid", "Ammonia Solution", "Bleach", "Soap"])

        if ph_possibilities:
            ph_cause_message = f"The pH level suggests the presence of: {', '.join(ph_possibilities)}."
            possible_causes.append(ph_cause_message)

        if temperature_status != "The Water had a Normal Temperature":
            possible_causes.append(temperature_status)
        if oxygen_status != "The Water had a Normal Oxygen":
            possible_causes.append(oxygen_status)
        if ph_status != "The Water was Normal pH Level":
            possible_causes.append(ph_status)

        possible_causes_message = " \n"
        for cause in possible_causes:
            possible_causes_message += f" {cause}\n"

        message = {
            "alert": "A catfish has died! Please remove it immediately.",
            "details": {
                "temperature": latest_record.temperature,
                "temperature_status": temperature_status,
                "oxygen": latest_record.oxygen,
                "oxygen_status": oxygen_status,
                "phlevel": latest_record.phlevel,
                "phlevel_status": ph_status,
                "turbidity": latest_record.turbidity,
                "turbidity_status": latest_record.turbidityResult,
                "dead_catfish_count": latest_record.dead_catfish,
                "time_detected": latest_record.timeData.strftime("%Y-%m-%d %H:%M:%S"),
                "note": "These possiblities most likely have stressed the Catfish(es). Please Remove the dead catfish immediately to avoid water contamination.",
                "possible_causes": possible_causes_message.strip(),
            },
        }
        logging.warning(f"Dead catfish detected: {message}")
        return jsonify(message)

    except Exception as e:
        logging.error(f"Error checking for dead catfish: {e}")
        return jsonify({'error': str(e)})
    
@app.route('/update_aquamans', methods=['POST'])
def update_aquamans():
    global dead_catfish_counter

    try:
        new_record = request.json
        dead_catfish_count = new_record.get("dead_catfish", 0)

        if dead_catfish_count > 0:
            dead_catfish_counter += 1
        else:
            dead_catfish_counter = 0

        if dead_catfish_counter >= 5:
            dead_catfish_counter = 0
            
            response = print_dead_catfish_report()
            return response 

        record = aquamans(
            temperature=new_record["temperature"],
            oxygen=new_record["oxygen"],
            phlevel=new_record["phlevel"],
            turbidity=new_record["turbidity"],
            catfish=new_record["catfish"],
            dead_catfish=new_record["dead_catfish"],
            dead_catfish_image=new_record["dead_catfish_image"],
            timeData=new_record["timeData"],
        )
        db.session.add(record)
        db.session.commit()

        return jsonify({"message": "Record updated successfully!"})

    except Exception as e:
        logging.error(f"Error updating aquamans: {e}")
        return jsonify({"error": str(e)})

@app.route('/check_dead_catfish/print/<alert_id>', methods=['GET'])
def print_dead_catfish_report(alert_id):
    try:
        print("Alert ID received:", alert_id)
        latest_dead_record = (
            aquamans.query.filter(aquamans.dead_catfish > 0)
            .order_by(aquamans.timeData.desc())
            .first()
        )

        if not latest_dead_record:
            return jsonify({"message": "No dead catfish detected in the system."})

        three_hours_ago = latest_dead_record.timeData - timedelta(hours=3)
        recent_data = (
            aquamans.query.filter(
                aquamans.timeData.between(three_hours_ago, latest_dead_record.timeData)
            )
            .order_by(aquamans.timeData)
            .all()
        )

        data = [["ID", "Temperature (°C)", "Oxygen (mg/L)", "pH", "Turbidity (NTU)", "Alive Catfish", "Dead Catfish", "Time"]]
        total_catfish = 0 
        total_dead_catfish = 0 

        for record in recent_data:
            total_catfish += record.catfish + record.dead_catfish
            total_dead_catfish += record.dead_catfish

            data.append([ 
                record.id,
                f"{record.temperature:.1f}",
                f"{record.oxygen:.2f}",
                f"{record.phlevel:.2f}",
                f"{record.turbidity:.2f}",
                int(record.catfish),
                int(record.dead_catfish),
                record.timeData.strftime("%Y-%m-%d %H:%M:%S"),
            ])

        if total_catfish == 0:
            mortality_rate = 0
        else:
            mortality_rate = (total_dead_catfish / total_catfish) * 100

        temperature = latest_dead_record.temperature
        oxygen = latest_dead_record.oxygen
        phlevel = latest_dead_record.phlevel
        turbidity = latest_dead_record.turbidity

        # Determine temperature status and message
        if temperature > 35:
            temperature_status = "Warm Temperature"
            temperature_message = (
                "The Water had a Warm Temperature\nPossibly Due to:\n"
                "- Very Hot Temperature in Environment Near the Aquarium\n"
                "- Boiling Water was used to fill the Aquarium\n"
                "- Aquarium Directly Exposed to a Sunlight"
            )
        elif temperature >= 26:
            temperature_status = "Normal Temperature"
            temperature_message = "The Water had a Below Average Temperature"
        elif temperature <= 20:
            temperature_status = "Cold Temperature"
            temperature_message = (
                "The Water had a Cold Temperature\nPossibly Due to:\n"
                "- Very Cold Temperature in Environment Near the Aquarium\n"
                "- Very Cold Water was used to fill the Aquarium"
            )
        else:
            temperature_status = "Warm Temperature"
            temperature_message = (
                "The Water had a Warm Temperature\nPossibly Due to:\n"
                "- Hot Temperature in Environment Near the Aquarium\n"
                "- Lukewarm Water was used to fill the Aquarium\n"
                "- Aquarium Slightly Exposed to a Sunlight"
            )

        # Determine oxygen status and message
        if oxygen <= 0.8:
            oxygen_status = "Very Low Oxygen"
            oxygen_message = (
                "The Water had a Very Low Oxygen\nPossible Causes:\n"
                "- Overstocking of Catfish\n- Stagnant Water\n- No Ventilation\n- Overfeeding"
            )
        elif oxygen < 1.5:
            oxygen_status = "Low Oxygen"
            oxygen_message = (
                "The Water had a Low Oxygen\nPossible Causes:\n"
                "- High Volumes of Catfish\n- Low Movement of Water\n- Little Ventilation"
            )
        elif oxygen > 5:
            oxygen_status = "High Oxygen"
            oxygen_message = (
                "The Water had a High Oxygen\nPossible Causes:\n"
                "- Hyperoxygenation\n- Chemicals\n- Over-aeration of Water"
            )
        else:
            oxygen_status = "Normal Oxygen"
            oxygen_message = "Oxygen levels are within normal range."

        # Determine pH status and message
        if phlevel < 4:
            ph_status = "Very Acidic"
            ph_message = "The Water Possibly Contains: Baking Soda, Acid Rain, Vinegar"
        elif phlevel < 6:
            ph_status = "Acidic"
            ph_message = "The Water Possibly Contains: Acidic Products, Coffee"
        elif phlevel <= 8.9:
            ph_status = "Alkaline"
            ph_message = "The Water Possibly Contains: Salt, Saltwater"
        else:
            ph_status = "Very Alkaline"
            ph_message = "The Water Possibly Contains: Dishwashing Liquid, Ammonia Solution, Bleach, Soap"

        # Determine turbidity status
        if turbidity < 20:
            turbidity_status = "Clean Water"
        elif 20 <= turbidity < 50:
            turbidity_status = "Cloudy Water"
        else:
            turbidity_status = "Dirty Water"

        # Combine all the messages for the PDF output
        result_message = (
            "TALLIED DATA:\n"
            f"Temperature: {temperature:.1f} ({temperature_status})\n"
            f"Oxygen: {oxygen:.1f} ({oxygen_status})\n"
            f"pH Level: {phlevel:.1f} ({ph_status})\n"
            f"Turbidity: {turbidity:.1f} ({turbidity_status})\n"
            f"Mortality Rate: {mortality_rate:.2f}%\n\n"
            "POSSIBLE CAUSES:\n"
            f"The Water had a {temperature_status} Possibly Due to:\n"
            f"- {temperature_message.replace('Possibly Due to:', '').strip()}\n\n"
    
            f"The Water had a {ph_status} Possibly Due to Water containing:\n"
            f"- {ph_message.replace('The Water Possibly Contains:', '').strip()}\n\n"
    
            f"The Water had a {oxygen_status} Possible Causes:\n"
            f"- {oxygen_message.replace('Possible Causes:', '').strip()}\n\n"

            "NOTES:\n"
            "The underlying conditions may have caused the catfish to be stressed, which leads to the catfish(es) dying. "
            "Please remove the catfish immediately to prevent more water contamination."
        )
        # PDF generation part remains unchanged
        styles = getSampleStyleSheet()
        pdf_style = styles['Normal']

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        col_widths = [35, 55, 55, 55, 55, 45, 45, 80]

        table = Table(data, colWidths=col_widths)

        table.setStyle(TableStyle([ 
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (-1, -1), (-1, -1), "Helvetica-Bold"),
        ]))

        pdf.build([table])

        buffer.seek(0)
        output_pdf = BytesIO()
        pdf = SimpleDocTemplate(output_pdf, pagesize=letter)
        story = []

        story.append(table)

        result_paragraph = Paragraph(result_message, style=pdf_style)
        story.append(result_paragraph)

        pdf.build(story)

        output_pdf.seek(0)
        return send_file(output_pdf, as_attachment=True, download_name="dead-catfish-report.pdf", mimetype="application/pdf")

    except Exception as e:
        logging.error(f"Error generating dead catfish report: {e}")
        return jsonify({"error": str(e)})


@app.route('/check_data/print', methods=['GET'])
def print_data_report():
    try:
        time_filter = request.args.get('hours', default=0, type=int)
        date_filter = request.args.get('date', default=None, type=str)

        if time_filter > 0:
            if date_filter:
                filter_date = datetime.strptime(date_filter, "%Y-%m-%d")
                if filter_date.date() != datetime.today().date():
                    return jsonify({"message": "3 hours report only works with today's date."}), 400
            else:
                filter_date = datetime.now()
        else:
            if date_filter:
                filter_date = datetime.strptime(date_filter, "%Y-%m-%d")
            else:
                filter_date = datetime.now()

        if time_filter > 0:
            start_time = filter_date - timedelta(hours=time_filter)
        else:
            start_time = filter_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        end_time = filter_date.replace(hour=23, minute=59, second=59, microsecond=999999)

        recent_data = (
            aquamans.query.filter(aquamans.timeData >= start_time, aquamans.timeData <= end_time)
            .order_by(aquamans.timeData)
            .all()
        )

        if not recent_data:
            return jsonify({"message": "No records found in the selected time range."})

        # Prepare table data
        data = [["ID", "Temperature (°C)", "Oxygen (mg/L)", "pH Level", "Turbidity", "Catfish", "Dead Catfish", "Time"]]
        total_temperature = 0
        total_oxygen = 0
        total_phlevel = 0
        total_turbidity = 0
        count = 0

        for row in recent_data:
            data.append([row.id, row.temperature, row.oxygen, row.phlevel, row.turbidity, row.catfish, row.dead_catfish, row.timeData])
            if row.temperature:
                total_temperature += row.temperature
            if row.oxygen:
                total_oxygen += row.oxygen
            if row.phlevel:
                total_phlevel += row.phlevel
            if row.turbidity:
                total_turbidity += row.turbidity
            count += 1

        # Calculate averages
        avg_temperature = total_temperature / count if count > 0 else 0
        avg_oxygen = total_oxygen / count if count > 0 else 0
        avg_phlevel = total_phlevel / count if count > 0 else 0
        avg_turbidity = total_turbidity / count if count > 0 else 0

        # Add a summary row
        data.append(["Totals/Averages", f"{avg_temperature:.2f}", f"{avg_oxygen:.2f}", f"{avg_phlevel:.2f}", f"{avg_turbidity:.2f}", "", "", ""])

        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)
        table = Table(data)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (-1, -1), (-1, -1), "Helvetica-Bold"),
        ]))

        pdf.build([table])

        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="data-report.pdf", mimetype="application/pdf")
    
    except Exception as e:
        logging.error(f"Error generating report: {str(e)}")
        return jsonify({"message": "An error occurred while generating the report."}), 500

@app.before_request
def check_system_status():
    """
    """
    global active
    if not active:
        return jsonify({"message": "System is cooling down. Please try again in a few minutes."}), 503
    
    
@app.route('/latest-image', methods=['GET'])
def latest_image():
    try:
        record = aquamans.query.filter(aquamans.dead_catfish_image != None).order_by(aquamans.id.desc()).first()

        if record and record.dead_catfish_image:
            image_data = record.dead_catfish_image
            image = Image.open(BytesIO(image_data))
            img_io = BytesIO()
            image.save(img_io, 'JPEG')
            img_io.seek(0)
            return send_file(img_io, mimetype='image/jpeg')

        return jsonify({'message': 'No image available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)