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
    def get_data(self, date_filter=None, page=1, per_page=100):
        try:
            # Calculate offset
            offset = (page - 1) * per_page

            with db.engine.connect() as connection:
                # Base query with pagination
                if date_filter:
                    # Convert date_filter to datetime
                    filter_date = datetime.strptime(date_filter, "%Y-%m-%d").date()
                    
                    # Parameterized query with pagination
                    query = """
                        SELECT 
                            id, 
                            temperature, 
                            tempResult, 
                            oxygen, 
                            oxygenResult, 
                            phlevel, 
                            phResult, 
                            turbidity, 
                            turbidityResult, 
                            catfish, 
                            dead_catfish, 
                            timeData 
                        FROM aquamans 
                        WHERE DATE(timeData) = :filter_date 
                        ORDER BY timeData DESC
                        LIMIT :per_page OFFSET :offset
                    """
                    result = connection.execute(text(query), {
                        'filter_date': filter_date,
                        'per_page': per_page,
                        'offset': offset
                    })

                    # Count total records for the date
                    count_query = """
                        SELECT COUNT(*) as total 
                        FROM aquamans 
                        WHERE DATE(timeData) = :filter_date
                    """
                    total_result = connection.execute(text(count_query), {
                        'filter_date': filter_date
                    })
                    total_records = total_result.scalar()

                else:
                    # Get paginated records if no date filter
                    query = """
                        SELECT 
                            id, 
                            temperature, 
                            tempResult, 
                            oxygen, 
                            oxygenResult, 
                            phlevel, 
                            phResult, 
                            turbidity, 
                            turbidityResult, 
                            catfish, 
                            dead_catfish, 
                            timeData 
                        FROM aquamans 
                        ORDER BY timeData DESC
                        LIMIT :per_page OFFSET :offset
                    """
                    result = connection.execute(text(query), {
                        'per_page': per_page,
                        'offset': offset
                    })

                    # Count total records
                    count_query = "SELECT COUNT(*) as total FROM aquamans"
                    total_result = connection.execute(text(count_query))
                    total_records = total_result.scalar()

                # Get column names
                columns = result.keys()

                # Convert results to list of dictionaries
                records = []
                for row in result:
                    record = {
                        col: getattr(row, col) for col in columns
                    }
                    
                    # Convert datetime to ISO string if needed
                    if 'timeData' in record and record['timeData']:
                        record['timeData'] = record['timeData'].isoformat()
                    
                    records.append(record)

                # Return results with pagination info
                return jsonify({
                    'data': records,
                    'total': total_records,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': (total_records + per_page - 1) // per_page
                })

        except Exception as e:
            logging.error(f"Error in get_data service: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'message': str(e),
                'data': []
            }), 500

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