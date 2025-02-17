# app/services/report_service.py
from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors

class ReportService:
    def check_dead_catfish(self):
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
            temperature_possibilities = []
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

            # pH Analysis
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
                ph_possibilities.extend(["Saltwater"])
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

    def print_dead_catfish_report(self, alert_id):
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

            data = [["ID", "Temperature (°C)", "Oxygen (mg/L)", "pH", "Turbidity (NTU)", 
                    "Alive Catfish", "Dead Catfish", "Time"]]
            
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

            mortality_rate = (total_dead_catfish / total_catfish) * 100 if total_catfish > 0 else 0

            # Generate analysis message
            result_message = self._generate_analysis_message(latest_dead_record, mortality_rate)

            # Create PDF
            output_pdf = BytesIO()
            pdf = SimpleDocTemplate(output_pdf, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Add table
            table = Table(data, colWidths=[35, 55, 55, 55, 55, 45, 45, 80])
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
            story.append(table)

            # Add analysis
            result_paragraph = Paragraph(result_message, styles['Normal'])
            story.append(result_paragraph)

            pdf.build(story)
            output_pdf.seek(0)

            return send_file(
                output_pdf,
                as_attachment=True,
                download_name="dead-catfish-report.pdf",
                mimetype="application/pdf"
            )

        except Exception as e:
            logging.error(f"Error generating dead catfish report: {e}")
            return jsonify({"error": str(e)})

    def _generate_analysis_message(self, record, mortality_rate):
        # Temperature analysis
        if record.temperature > 35:
            temp_status = "Warm Temperature"
            temp_message = (
                "The Water had a Warm Temperature\nPossibly Due to:\n"
                "- Very Hot Temperature in Environment Near the Aquarium\n"
                "- Boiling Water was used to fill the Aquarium\n"
                "- Aquarium Directly Exposed to a Sunlight"
            )
        elif record.temperature >= 26:
            temp_status = "Normal Temperature"
            temp_message = "The Water had a Normal Temperature"
        elif record.temperature <= 20:
            temp_status = "Cold Temperature"
            temp_message = (
                "The Water had a Cold Temperature\nPossibly Due to:\n"
                "- Very Cold Temperature in Environment Near the Aquarium\n"
                "- Very Cold Water was used to fill the Aquarium"
            )
        else:
            temp_status = "Below Average Temperature"
            temp_message = (
                "The Water had a Below Average Temperature\nPossibly Due to:\n"
                "- Cold Temperature in Environment Near the Aquarium\n"
                "- Cold Water was used to fill the Aquarium"
            )

        # Oxygen analysis
        if record.oxygen <= 0.8:
            oxygen_message = (
                "The Water had Very Low Oxygen\nPossible Causes:\n"
                "- Overstocking of Catfish\n- Stagnant Water\n"
                "- No Ventilation\n- Overfeeding"
            )
        elif record.oxygen < 1.5:
            oxygen_message = (
                "The Water had Low Oxygen\nPossible Causes:\n"
                "- High Volumes of Catfish\n- Low Movement of Water\n"
                "- Little Ventilation"
            )
        elif record.oxygen > 5:
            oxygen_message = (
                "The Water had High Oxygen\nPossible Causes:\n"
                "- Hyperoxygenation\n- Chemicals\n- Over-aeration of Water"
            )
        else:
            oxygen_message = "Oxygen levels were within normal range"

        return (
            f"ANALYSIS REPORT\n\n"
            f"Temperature Status: {temp_status}\n{temp_message}\n\n"
            f"Oxygen Status:\n{oxygen_message}\n\n"
            f"Mortality Rate: {mortality_rate:.2f}%\n\n"
            "Note: These conditions may have stressed the catfish(es). "
            "Please remove dead catfish immediately to prevent water contamination."
        )

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

            recent_data = (
                aquamans.query.filter(
                    aquamans.timeData >= start_time,
                    aquamans.timeData <= end_time
                )
                .order_by(aquamans.timeData)
                .all()
            )

            if not recent_data:
                return jsonify({"message": "No records found in the selected time range."})

            # Create PDF report
            buffer = BytesIO()
            pdf = SimpleDocTemplate(buffer, pagesize=letter)
            
            # Prepare data for table
            data = [["ID", "Temperature", "Oxygen", "pH Level", "Turbidity", "Catfish", "Dead Catfish", "Time"]]
            for record in recent_data:
                data.append([
                    record.id,
                    f"{record.temperature:.2f}",
                    f"{record.oxygen:.2f}",
                    f"{record.phlevel:.2f}",
                    f"{record.turbidity:.2f}",
                    str(record.catfish),
                    str(record.dead_catfish),
                    record.timeData.strftime("%Y-%m-%d %H:%M:%S")
                ])

            # Create table
            table = Table(data)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ]))

            # Build PDF
            pdf.build([table])
            buffer.seek(0)
            
            return send_file(
                buffer,
                as_attachment=True,
                download_name="data-report.pdf",
                mimetype="application/pdf"
            )

        except Exception as e:
            logging.error(f"Error generating report: {str(e)}")
            return jsonify({"message": "An error occurred while generating the report."}), 500