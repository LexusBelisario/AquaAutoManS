
from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
from sqlalchemy import text
import base64
import logging
from io import BytesIO
from PIL import Image

class DataService:
    def get_data(self, date_filter):
        try:
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
            logging.error(f"Error fetching data: {e}")
            return jsonify({'error': str(e)}), 500

    def get_temperature_data(self):
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT id, temperature, timeData AS date FROM aquamans"))
                columns = result.keys()
                records = [dict(zip(columns, row)) for row in result]
                return jsonify(records)
        except Exception as e:
            logging.error(f"Error fetching temperature data: {e}")
            return jsonify({'error': str(e)})

    def get_filtered_data(self, query, filter_type, selected_date, selected_week_start):
        try:
            if selected_date:
                selected_date = datetime.strptime(selected_date, '%Y-%m-%d')
            
            if selected_week_start:
                selected_week_start = datetime.strptime(selected_week_start, '%Y-%m-%d')
                end_of_week = selected_week_start + timedelta(days=6)

            with db.engine.connect() as connection:
                result = connection.execute(text(query))
                columns = result.keys()
                records = [dict(zip(columns, row)) for row in result]

                if filter_type == 'date' and selected_date:
                    filtered_records = [
                        record for record in records 
                        if record['timeData'].date() == selected_date.date()
                    ]
                    return jsonify(filtered_records)

                elif filter_type == 'week' and selected_week_start:
                    filtered_records = [
                        record for record in records 
                        if selected_week_start <= record['timeData'] <= end_of_week
                    ]
                    return jsonify(filtered_records)

                return jsonify(records)

        except Exception as e:
            logging.error(f"Error fetching filtered data: {e}")
            return jsonify({'error': str(e)})

    def get_filtered_temperature_data(self, filter_type, selected_date, selected_week_start):
        return self.get_filtered_data(
            "SELECT temperature, timeData FROM aquamans",
            filter_type, selected_date, selected_week_start
        )

    def get_oxygen_data(self):
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT id, oxygen, timeData AS date FROM aquamans"))
                columns = result.keys()
                records = [dict(zip(columns, row)) for row in result]
                return jsonify(records)
        except Exception as e:
            logging.error(f"Error fetching oxygen data: {e}")
            return jsonify({'error': str(e)})

    def get_filtered_oxygen_data(self, filter_type, selected_date, selected_week_start):
        return self.get_filtered_data(
            "SELECT oxygen, timeData FROM aquamans",
            filter_type, selected_date, selected_week_start
        )

    def get_phlevel_data(self):
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT id, phlevel, timeData AS date FROM aquamans"))
                columns = result.keys()
                records = [dict(zip(columns, row)) for row in result]
                return jsonify(records)
        except Exception as e:
            logging.error(f"Error fetching pH level data: {e}")
            return jsonify({'error': str(e)})

    def get_filtered_phlevel_data(self, filter_type, selected_date, selected_week_start):
        return self.get_filtered_data(
            "SELECT phlevel, timeData FROM aquamans",
            filter_type, selected_date, selected_week_start
        )

    def get_turbidity_data(self):
        try:
            with db.engine.connect() as connection:
                result = connection.execute(text("SELECT id, turbidity, timeData AS date FROM aquamans"))
                columns = result.keys()
                records = [dict(zip(columns, row)) for row in result]
                return jsonify(records)
        except Exception as e:
            logging.error(f"Error fetching turbidity data: {e}")
            return jsonify({'error': str(e)})

    def get_filtered_turbidity_data(self, filter_type, selected_date, selected_week_start):
        return self.get_filtered_data(
            "SELECT turbidity, timeData FROM aquamans",
            filter_type, selected_date, selected_week_start
        )

    def get_latest_image(self):
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