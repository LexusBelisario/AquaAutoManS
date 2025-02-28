
from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
from sqlalchemy import text
import base64
import logging
from io import BytesIO
from PIL import Image
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

class DataService:
    def print_data_report(self, time_filter, date_filter):
        try:
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

            # Optimize query to select only needed columns
            recent_data = (
                aquamans.query
                .with_entities(
                    aquamans.timeData,
                    aquamans.temperature,
                    aquamans.tempResult,
                    aquamans.oxygen,
                    aquamans.oxygenResult,
                    aquamans.phlevel,
                    aquamans.phResult,
                    aquamans.turbidity,
                    aquamans.turbidityResult,
                    aquamans.catfish,
                    aquamans.dead_catfish
                )
                .filter(
                    aquamans.timeData.between(start_time, end_time)
                )
                .order_by(aquamans.timeData)
                .all()
            )

            if not recent_data:
                return jsonify({"message": "No records found in the selected time range."})

            # Calculate totals while processing data
            totals = {
                'temperature': 0,
                'oxygen': 0,
                'phlevel': 0,
                'turbidity': 0,
                'count': 0
            }

            # Prepare data for PDF
            data = [["Time", "Temperature", "Result", "Oxygen", "Result", 
                    "pH Level", "Result", "Turbidity", "Result", 
                    "Alive Catfish", "Dead Catfish"]]

            for record in recent_data:
                data.append([
                    record.timeData.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{record.temperature:.2f}",
                    record.tempResult,
                    f"{record.oxygen:.2f}",
                    record.oxygenResult,
                    f"{record.phlevel:.2f}",
                    record.phResult,
                    f"{record.turbidity:.2f}",
                    record.turbidityResult,
                    str(record.catfish),
                    str(record.dead_catfish)
                ])
                
                # Update totals
                totals['temperature'] += float(record.temperature or 0)
                totals['oxygen'] += float(record.oxygen or 0)
                totals['phlevel'] += float(record.phlevel or 0)
                totals['turbidity'] += float(record.turbidity or 0)
                totals['count'] += 1

            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            # Define styles
            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            normal_style = styles["Normal"]

            # Create story for PDF
            story = []

            # Add title
            title = "Catfish Data Report"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))

            # Create table
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]))
            story.append(table)

            # Add summary statistics
            if totals['count'] > 0:
                story.append(Spacer(1, 20))
                story.append(Paragraph("Summary Statistics", styles["Heading2"]))
                summary_data = [
                    ["Metric", "Average Value"],
                    ["Temperature", f"{totals['temperature']/totals['count']:.2f}°C"],
                    ["Oxygen", f"{totals['oxygen']/totals['count']:.2f} mg/L"],
                    ["pH Level", f"{totals['phlevel']/totals['count']:.2f}"],
                    ["Turbidity", f"{totals['turbidity']/totals['count']:.2f} NTU"]
                ]
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(summary_table)

            # Build PDF
            doc.build(story)
            buffer.seek(0)

            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"aquamans_report_{filter_date.strftime('%Y%m%d')}.pdf",
                mimetype="application/pdf"
            )

        except Exception as e:
            logging.error(f"Error generating report: {str(e)}")
            return jsonify({"message": "An error occurred while generating the report."}), 500

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