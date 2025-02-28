from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
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
        
    def _get_temp_status(self, temp):
        if 26 <= temp <= 32:
            return "Normal"
        elif 20 < temp < 26:
            return "Below Average"
        elif temp <= 20:
            return "Cold"
        elif 32 <= temp < 35:
            return "Above Average"
        else:
            return "Hot"

    def _get_oxygen_status(self, oxy):
        if oxy == 0:
            return "Very Low"
        elif oxy < 1.5:
            return "Low"
        elif 1.5 <= oxy <= 5:
            return "Normal"
        else:
            return "High"

    def _get_ph_status(self, ph):
        if ph < 4:
            return "Very Acidic"
        elif 4 <= ph < 6:
            return "Acidic"
        elif 6 <= ph <= 7.5:
            return "Normal"
        elif 7.5 < ph <= 9:
            return "Alkaline"
        else:
            return "Very Alkaline"

    def _get_turbidity_status(self, turb):
        if turb < 20:
            return "Clean"
        elif 20 <= turb < 50:
            return "Cloudy"
        else:
            return "Dirty"


    def print_data_report(self, time_filter, date_filter):
        try:
            logging.info(f"Starting report generation with time_filter: {time_filter}, date_filter: {date_filter}")
            
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

            logging.info(f"Querying data from {start_time} to {end_time}")

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

            logging.info(f"Found {len(recent_data)} records")

            # Prepare data for PDF
            data = [["Time", "Temperature", "Result", "Oxygen", "Result", 
                    "pH Level", "Result", "Turbidity", "Result", 
                    "Alive Catfish", "Dead Catfish"]]

            totals = {
                'temperature': 0,
                'oxygen': 0,
                'phlevel': 0,
                'turbidity': 0,
                'count': 0,
                'alive_catfish': 0,
                'dead_catfish': 0
            }

            # Process data
            for record in recent_data:
                time_str = record.timeData.strftime("%Y-%m-%d %H:%M:%S")
                data.append([
                    time_str,
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

                totals['temperature'] += float(record.temperature or 0)
                totals['oxygen'] += float(record.oxygen or 0)
                totals['phlevel'] += float(record.phlevel or 0)
                totals['turbidity'] += float(record.turbidity or 0)
                totals['alive_catfish'] += float(record.catfish or 0)
                totals['dead_catfish'] += float(record.dead_catfish or 0)
                totals['count'] += 1

            logging.info("Creating PDF document")

            # Create PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            # Define styles
            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            heading2_style = styles["Heading2"]
            normal_style = styles["Normal"]

            # Create story for PDF
            story = []

            # Add title
            title = "Aquamans Data Report"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))

            # Add date/time range info
            if time_filter > 0:
                period = f"Last {time_filter} Hours"
            else:
                period = f"Date: {filter_date.strftime('%Y-%m-%d')}"
            story.append(Paragraph(f"Period: {period}", normal_style))
            story.append(Spacer(1, 12))

            # Add data table
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(PageBreak())

            # Add summary statistics
            if totals['count'] > 0:
                story.append(Paragraph("Data Findings", heading2_style))
                
                avg_temp = totals['temperature']/totals['count']
                avg_oxy = totals['oxygen']/totals['count']
                avg_ph = totals['phlevel']/totals['count']
                avg_turb = totals['turbidity']/totals['count']
                avg_alive = totals['alive_catfish']/totals['count']
                avg_dead = totals['dead_catfish']/totals['count']

                summary_data = [
                    ["Parameter", "Average Value", "Status"],
                    ["Temperature", f"{avg_temp:.2f}°C", self._get_temp_status(avg_temp)],
                    ["Oxygen", f"{avg_oxy:.2f} mg/L", self._get_oxygen_status(avg_oxy)],
                    ["pH Level", f"{avg_ph:.2f}", self._get_ph_status(avg_ph)],
                    ["Turbidity", f"{avg_turb:.2f} NTU", self._get_turbidity_status(avg_turb)],
                    ["Alive Catfish", f"{avg_alive:.2f}", "Average Count"],
                    ["Dead Catfish", f"{avg_dead:.2f}", "Average Count"]
                ]
                
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 20))
                
                story.append(Paragraph("Critical Incidents Analysis", heading2_style))
            story.append(Spacer(1, 12))

            # Track first occurrences of incidents
            critical_incidents = {}

            # Analyze all records
            for record in recent_data:
                time_str = record.timeData.strftime("%Y-%m-%d %H:%M:%S")
                
                # Temperature incidents
                temp = float(record.temperature)
                if temp <= 20:
                    if 'cold_temp' not in critical_incidents:
                        critical_incidents['cold_temp'] = {
                            'time': time_str,
                            'value': f"{temp:.2f}°C",
                            'parameter': "Temperature",
                            'status': "Cold Temperature",
                            'causes': [
                                "Cold Temperature in Environment",
                                "Cold Water was used",
                                "Cold Wind"
                            ]
                        }
                elif 20 < temp < 26:
                    if 'below_avg_temp' not in critical_incidents:
                        critical_incidents['below_avg_temp'] = {
                            'time': time_str,
                            'value': f"{temp:.2f}°C",
                            'parameter': "Temperature",
                            'status': "Below Average Temperature",
                            'causes': [
                                "Sub Par Cold Temperature in Environment",
                                "Cold Water was used"
                            ]
                        }
                elif 32 <= temp < 35:
                    if 'above_avg_temp' not in critical_incidents:
                        critical_incidents['above_avg_temp'] = {
                            'time': time_str,
                            'value': f"{temp:.2f}°C",
                            'parameter': "Temperature",
                            'status': "Above Average Temperature",
                            'causes': [
                                "Hot Temperature in Environment",
                                "Lukewarm Water was used",
                                "Slightly Exposed to Sunlight"
                            ]
                        }
                elif temp >= 35:
                    if 'hot_temp' not in critical_incidents:
                        critical_incidents['hot_temp'] = {
                            'time': time_str,
                            'value': f"{temp:.2f}°C",
                            'parameter': "Temperature",
                            'status': "Hot Temperature",
                            'causes': [
                                "Very Hot Temperature in Environment",
                                "Boiling Water was used",
                                "Full Exposure to Sunlight"
                            ]
                        }

                # Oxygen incidents
                oxy = float(record.oxygen)
                if oxy <= 0.8:
                    if 'very_low_oxygen' not in critical_incidents:
                        critical_incidents['very_low_oxygen'] = {
                            'time': time_str,
                            'value': f"{oxy:.2f} mg/L",
                            'parameter': "Oxygen",
                            'status': "Very Low Oxygen",
                            'causes': [
                                "Overstocking of Catfish",
                                "Stagnant Water",
                                "No Ventilation",
                                "Overfeeding"
                            ]
                        }
                elif oxy < 1.5:
                    if 'low_oxygen' not in critical_incidents:
                        critical_incidents['low_oxygen'] = {
                            'time': time_str,
                            'value': f"{oxy:.2f} mg/L",
                            'parameter': "Oxygen",
                            'status': "Low Oxygen",
                            'causes': [
                                "High Volumes of Catfish",
                                "Low Movement of Water",
                                "Little Ventilation"
                            ]
                        }
                elif oxy > 5:
                    if 'high_oxygen' not in critical_incidents:
                        critical_incidents['high_oxygen'] = {
                            'time': time_str,
                            'value': f"{oxy:.2f} mg/L",
                            'parameter': "Oxygen",
                            'status': "High Oxygen",
                            'causes': [
                                "Over-aeration of Water",
                                "Chemicals",
                                "Hyperoxygenation"
                            ]
                        }

                # pH incidents
                ph = float(record.phlevel)
                if ph < 4:
                    if 'very_acidic' not in critical_incidents:
                        critical_incidents['very_acidic'] = {
                            'time': time_str,
                            'value': f"{ph:.2f}",
                            'parameter': "pH Level",
                            'status': "Very Acidic",
                            'causes': [
                                "Presence of Strong Acids",
                                "Acid Rain",
                                "Vinegar Contamination"
                            ]
                        }
                elif 4 <= ph < 6:
                    if 'acidic' not in critical_incidents:
                        critical_incidents['acidic'] = {
                            'time': time_str,
                            'value': f"{ph:.2f}",
                            'parameter': "pH Level",
                            'status': "Acidic",
                            'causes': [
                                "Acidic Products",
                                "Coffee Contamination"
                            ]
                        }
                elif ph > 9:
                    if 'very_alkaline' not in critical_incidents:
                        critical_incidents['very_alkaline'] = {
                            'time': time_str,
                            'value': f"{ph:.2f}",
                            'parameter': "pH Level",
                            'status': "Very Alkaline",
                            'causes': [
                                "Dishwashing Liquid",
                                "Ammonia Solution",
                                "Bleach",
                                "Soap Contamination"
                            ]
                        }

                # Turbidity incidents
                turb = float(record.turbidity)
                if turb >= 50:
                    if 'high_turbidity' not in critical_incidents:
                        critical_incidents['high_turbidity'] = {
                            'time': time_str,
                            'value': f"{turb:.2f} NTU",
                            'parameter': "Turbidity",
                            'status': "Dirty",
                            'causes': [
                                "High Particle Content",
                                "Poor Filtration",
                                "Excess Waste"
                            ]
                        }
                elif 20 <= turb < 50:
                    if 'medium_turbidity' not in critical_incidents:
                        critical_incidents['medium_turbidity'] = {
                            'time': time_str,
                            'value': f"{turb:.2f} NTU",
                            'parameter': "Turbidity",
                            'status': "Cloudy",
                            'causes': [
                                "Suspended Particles",
                                "Organic Matter",
                                "Moderate Waste Build-up"
                            ]
                        }

            # Display critical incidents
            if critical_incidents:
                story.append(Paragraph("First Occurrences of Critical Incidents:", normal_style))
                story.append(Spacer(1, 12))
                
                # Sort incidents by time
                sorted_incidents = sorted(critical_incidents.values(), key=lambda x: x['time'])
                
                for incident in sorted_incidents:
                    story.append(Paragraph(
                        f"<b>{incident['time']}</b> - {incident['parameter']}: {incident['value']} ({incident['status']})",
                        normal_style
                    ))
                    story.append(Paragraph("Possible causes:", normal_style))
                    for cause in incident['causes']:
                        story.append(Paragraph(f"• {cause}", normal_style))
                    story.append(Spacer(1, 8))
                
                story.append(Spacer(1, 12))
                story.append(Paragraph(
                    "<b>Note:</b> These conditions may cause stress to the catfish and should be addressed promptly.",
                    normal_style
                ))
            else:
                story.append(Paragraph(
                    "No critical incidents detected during this period. All parameters were within normal ranges.",
                    normal_style
                ))

            logging.info("Building PDF")
            doc.build(story)
            buffer.seek(0)

            logging.info("Sending PDF file")
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"aquamans_report_{filter_date.strftime('%Y%m%d')}.pdf",
                mimetype="application/pdf"
            )

        except Exception as e:
            logging.error(f"Error generating report: {str(e)}")
            return jsonify({"message": "An error occurred while generating the report."}), 500