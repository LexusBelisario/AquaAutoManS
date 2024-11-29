from flask import Flask, Response, jsonify, request, send_file, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
from datetime import datetime, timedelta
import threading
import logging
import time
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
import base64
import os
from PIL import Image

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


@app.route('/temperature', methods=['GET'])
def get_temperature():
    try:
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()  # Sort by timeData
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
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()  # Sort by timeData
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
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()  # Sort by timeData
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
        latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()  # Sort by timeData
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
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM aquamans"))
            columns = result.keys()
            records = []
            for row in result:
                record = dict(zip(columns, row))
                # Encode binary data to base64 if present
                if record.get('dead_catfish_image'):
                    record['dead_catfish_image'] = base64.b64encode(record['dead_catfish_image']).decode('utf-8')
                records.append(record)
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
            filtered_records = [
                record for record in records
                if datetime.fromisoformat(record['timeData']).hour % 3 == 0
            ]
            return jsonify(filtered_records)
        else:
            return jsonify(records)

    except Exception as e:
        print(f"Error fetching weekly pH data: {e}")
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
            timeData=datetime.utcnow()  # Explicitly set the timestamp
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
        # Retrieve JSON data
        data = request.json
        catfish_count = int(data.get('catfish', 0))
        dead_catfish_count = int(data.get('dead_catfish', 0))

        # Fetch the latest record
        latest_record = aquamans.query.order_by(aquamans.id.desc()).first()
        if latest_record:
            # Update the record
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
        # Fetch the last 10 records to analyze consecutive dead_catfish detections
        recent_records = (
            aquamans.query.order_by(aquamans.timeData.desc())
            .limit(10)
            .all()
        )

        if not recent_records:
            return jsonify({
                'message': 'No data available in the system.',
            })

        # Check for consecutive dead_catfish detections
        consecutive_count = 0
        latest_record = None

        for record in recent_records:
            if record.dead_catfish > 0:
                consecutive_count += 1
                latest_record = record
            else:
                # Reset the counter if a zero value is encountered
                consecutive_count = 0

            # If we reach 5 consecutive detections, confirm a dead catfish
            if consecutive_count >= 5:
                break

        # If a dead catfish is confirmed, notify the user
        if consecutive_count >= 5 and latest_record:
            # Determine possible causes based on temperature, oxygen, and pH level
            possible_causes = []

            # Temperature conditions
            if 26 <= latest_record.temperature <= 32:
                temperature_status = "The Water had a Normal Temperature"
            elif 20 < latest_record.temperature < 26:
                temperature_status = "The Water had a Below Average Temperature"
            elif latest_record.temperature <= 20:
                temperature_status = "The Water had a Cold Temperature"
            elif 26 < latest_record.temperature < 35:
                temperature_status = "The Water had an Above Average Temperature"
            elif latest_record.temperature >= 35:
                temperature_status = "The Water had a Hot Temperature"

            # Oxygen conditions
            if latest_record.oxygen == 0:
                oxygen_status = "The Water had a Very Low Oxygen"
            elif latest_record.oxygen < 1.5:
                oxygen_status = "The Water had a Low Oxygen"
            elif 1.5 <= latest_record.oxygen <= 5:
                oxygen_status = "The Water had a Normal Oxygen"
            else:
                oxygen_status = "The Water had a High Oxygen"

            # pH level conditions
            if latest_record.phlevel < 4:
                ph_status = "The Water was Very Acidic"
            elif 4 <= latest_record.phlevel < 6:
                ph_status = "The Water was Acidic"
            elif 6 <= latest_record.phlevel <= 7.5:
                ph_status = "The Water was Normal pH Level"
            elif 7.5 < latest_record.phlevel <= 9:
                ph_status = "The Water was Very Alkaline"

            # Add to the possible causes based on detected conditions (excluding normal conditions)
            if temperature_status != "The Water had a Normal Temperature":
                possible_causes.append(temperature_status)
            if oxygen_status != "The Water had a Normal Oxygen":
                possible_causes.append(oxygen_status)
            if ph_status != "The Water was Normal pH Level":
                possible_causes.append(ph_status)

            # Construct the possible causes message
            possible_causes_message = "The system detected that: " + " and that: ".join(possible_causes) + " volume(s). These are the high probable causes of death for catfishes."

            # Structure the response message
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
                    "note": "Remove the dead catfish immediately to avoid water contamination.",
                    "possible_causes": possible_causes_message,
                },
            }
            logging.warning(f"Dead catfish detected 5 or more times consecutively: {message}")
            return jsonify(message)

        # If no critical dead_catfish event, return a normal message
        return jsonify({
            'message': 'No critical dead catfish event detected.',
            'latest_data': {
                'temperature': recent_records[0].temperature,
                'oxygen': recent_records[0].oxygen,
                'phlevel': recent_records[0].phlevel,
                'turbidity': recent_records[0].turbidity
            }
        })

    except Exception as e:
        logging.error(f"Error checking for dead catfish: {e}")
        return jsonify({'error': str(e)})

    

@app.route('/check_dead_catfish/print', methods=['GET'])
def print_dead_catfish_report():
    try:
        # Fetch the last 5 records where dead_catfish is detected
        recent_records = (
            aquamans.query.filter(aquamans.dead_catfish > 0)
            .order_by(aquamans.timeData.desc())
            .limit(5)
            .all()
        )

        if len(recent_records) == 5 and all(record.dead_catfish > 0 for record in recent_records):
            # Notify user of dead catfish
            latest_record = recent_records[0]  # Most recent record

        # Fetch data from the last 3 hours
        three_hours_ago = latest_record.timeData - timedelta(hours=3)
        recent_data = (
            aquamans.query.filter(
                aquamans.timeData.between(three_hours_ago, latest_record.timeData)
            )
            .order_by(aquamans.timeData)
            .all()
        )

        # Prepare data for the PDF
        data = [["ID", "Temperature (°C)", "Oxygen (mg/L)", "pH", "Turbidity (NTU)", "Alive Catfish", "Dead Catfish", "Time"]]
        total_catfish = 0  # To accumulate total catfish (alive + dead)
        total_dead_catfish = 0  # To accumulate total dead catfish

        for record in recent_data:
            total_catfish += record.catfish + record.dead_catfish  # Add alive and dead catfish to total
            total_dead_catfish += record.dead_catfish  # Add dead catfish to total

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

        # If there are no catfish, we can't compute the mortality rate
        if total_catfish == 0:
            mortality_rate = 0
        else:
            mortality_rate = (total_dead_catfish / 5) * 100  # Calculate mortality rate as a percentage

        # Tallied Results
        temperature = latest_dead_record.temperature
        oxygen = latest_dead_record.oxygen
        phlevel = latest_dead_record.phlevel
        turbidity = latest_dead_record.turbidity

        # Temperature status
        if 26 <= temperature <= 32:
            temperature_status = "Normal Temperature"
        elif 20 < temperature < 26:
            temperature_status = "Below Average Temperature"
        elif temperature <= 20:
            temperature_status = "Cold Temperature"
        elif 26 < temperature < 35:
            temperature_status = "Above Average Temperature"
        elif temperature >= 35:
            temperature_status = "Hot Temperature"

        # Oxygen status
        if oxygen == 0:
            oxygen_status = "Very Low Oxygen"
        elif oxygen < 1.5:
            oxygen_status = "Low Oxygen"
        elif 1.5 <= oxygen <= 5:
            oxygen_status = "Normal Oxygen"
        else:
            oxygen_status = "High Oxygen"

        # pH level status
        if phlevel < 4:
            ph_status = "Very Acidic"
        elif 4 <= phlevel < 6:
            ph_status = "Acidic"
        elif 6 <= phlevel <= 7.5:
            ph_status = "Normal pH Level"
        elif 7 < phlevel <= 9:
            ph_status = "Very Alkaline"

        # Turbidity status
        if turbidity < 20:
            turbidity_status = "Clean Water"
        elif 20 <= turbidity < 50:
            turbidity_status = "Cloudy Water"
        else:
            turbidity_status = "Dirty Water"

        # Concatenating the result in the desired format
        result_message = (
            f"Temperature: {temperature:.1f} ({temperature_status})\n"
            f"Oxygen: {oxygen:.1f} ({oxygen_status})\n"
            f"pH Level: {phlevel:.1f} ({ph_status})\n"
            f"Turbidity: {turbidity:.1f} ({turbidity_status})\n"
            f"Mortality Rate: {mortality_rate:.2f}%"
        )

        # Define the PDF style for the paragraph
        styles = getSampleStyleSheet()
        pdf_style = styles['Normal']  # You can customize this style further if needed

        # Generate PDF with adjusted table fit
        buffer = BytesIO()
        pdf = SimpleDocTemplate(buffer, pagesize=letter)

        # Set column widths to prevent overlap
        col_widths = [35, 55, 55, 55, 55, 45, 45, 80]  # Adjust these values as needed

        table = Table(data, colWidths=col_widths)

        # Apply table style with adjustments
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),  # Header font size
            ("FONTSIZE", (0, 1), (-1, -1), 8),  # Data font size
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),  # Center align vertically
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
            ("WORDWRAP", (0, 0), (-1, -1), True),  # Allow word wrapping
            ("LEFTPADDING", (0, 0), (-1, -1), 5),  # Add padding to the left side
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),  # Add padding to the right side
            ("TOPPADDING", (0, 0), (-1, -1), 5),  # Add padding to the top
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),  # Add padding to the bottom
        ]))

        # Build the PDF
        pdf.build([table])

        # Append result message below the table in the PDF
        buffer.seek(0)
        output_pdf = BytesIO()
        pdf = SimpleDocTemplate(output_pdf, pagesize=letter)
        story = []

        # Rebuild table and add to PDF
        story.append(table)

        # Add result message below the table
        result_paragraph = Paragraph(result_message, style=pdf_style)
        story.append(result_paragraph)

        pdf.build(story)

        output_pdf.seek(0)
        return send_file(output_pdf, as_attachment=True, download_name="dead_catfish_report_with_mortality_rate.pdf", mimetype="application/pdf")

    except Exception as e:
        logging.error(f"Error generating dead catfish report: {e}")
        return jsonify({"error": str(e)})

    

if __name__ == '__main__':
    app.run(debug=True)