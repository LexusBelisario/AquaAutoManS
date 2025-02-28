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

            # Initialize analysis dictionaries
            analysis = {
                'temperature': {
                    'normal': [], 'below_average': [], 'cold': [],
                    'above_average': [], 'hot': []
                },
                'oxygen': {
                    'very_low': [], 'low': [], 'normal': [], 'high': []
                },
                'ph': {
                    'very_acidic': [], 'acidic': [], 'normal': [],
                    'alkaline': [], 'very_alkaline': []
                },
                'turbidity': {
                    'clean': [], 'cloudy': [], 'dirty': []
                }
            }

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

            for record in recent_data:
                # Add to data table
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

                # Update totals
                totals['temperature'] += float(record.temperature or 0)
                totals['oxygen'] += float(record.oxygen or 0)
                totals['phlevel'] += float(record.phlevel or 0)
                totals['turbidity'] += float(record.turbidity or 0)
                totals['alive_catfish'] += float(record.catfish or 0)
                totals['dead_catfish'] += float(record.dead_catfish or 0)
                totals['count'] += 1

                # Analyze Temperature
                temp = float(record.temperature)
                if 26 <= temp <= 32:
                    analysis['temperature']['normal'].append(time_str)
                elif 20 < temp < 26:
                    analysis['temperature']['below_average'].append(time_str)
                elif temp <= 20:
                    analysis['temperature']['cold'].append(time_str)
                elif 32 <= temp < 35:
                    analysis['temperature']['above_average'].append(time_str)
                elif temp >= 35:
                    analysis['temperature']['hot'].append(time_str)

                # Analyze Oxygen
                oxy = float(record.oxygen)
                if oxy == 0:
                    analysis['oxygen']['very_low'].append(time_str)
                elif oxy < 1.5:
                    analysis['oxygen']['low'].append(time_str)
                elif 1.5 <= oxy <= 5:
                    analysis['oxygen']['normal'].append(time_str)
                elif oxy > 5:
                    analysis['oxygen']['high'].append(time_str)

                # Analyze pH
                ph = float(record.phlevel)
                if ph < 4:
                    analysis['ph']['very_acidic'].append(time_str)
                elif 4 <= ph < 6:
                    analysis['ph']['acidic'].append(time_str)
                elif 6 <= ph <= 7.5:
                    analysis['ph']['normal'].append(time_str)
                elif 7.5 < ph <= 9:
                    analysis['ph']['alkaline'].append(time_str)
                elif ph > 9:
                    analysis['ph']['very_alkaline'].append(time_str)

                # Analyze Turbidity
                turb = float(record.turbidity)
                if turb < 20:
                    analysis['turbidity']['clean'].append(time_str)
                elif 20 <= turb < 50:
                    analysis['turbidity']['cloudy'].append(time_str)
                elif turb >= 50:
                    analysis['turbidity']['dirty'].append(time_str)

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
            story.append(Spacer(1, 20))

            # Add summary statistics
            story.append(Paragraph("Summary Statistics", heading2_style))
            if totals['count'] > 0:
                summary_data = [
                    ["Metric", "Average Value", "Total"],
                    ["Temperature", f"{totals['temperature']/totals['count']:.2f}°C", f"{totals['temperature']:.2f}°C"],
                    ["Oxygen", f"{totals['oxygen']/totals['count']:.2f} mg/L", f"{totals['oxygen']:.2f} mg/L"],
                    ["pH Level", f"{totals['phlevel']/totals['count']:.2f}", f"{totals['phlevel']:.2f}"],
                    ["Turbidity", f"{totals['turbidity']/totals['count']:.2f} NTU", f"{totals['turbidity']:.2f} NTU"],
                    ["Catfish", "N/A", f"Alive: {int(totals['alive_catfish'])} Dead: {int(totals['dead_catfish'])}"]
                ]
                summary_table = Table(summary_data)
                summary_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(summary_table)
                story.append(Spacer(1, 20))

            # Add detailed analysis
            story.append(Paragraph("Detailed Analysis", heading2_style))
            story.append(Spacer(1, 12))

            # Temperature Analysis
            story.append(Paragraph("Temperature Incidents:", normal_style))
            for category, times in analysis['temperature'].items():
                if times and category != 'normal':  # Skip normal readings
                    story.append(Paragraph(
                        f"- {category.replace('_', ' ').title()}: {len(times)} occurrences",
                        normal_style
                    ))
                    for t in times:
                        story.append(Paragraph(f"  • {t}", normal_style))
            story.append(Spacer(1, 12))

            # Oxygen Analysis
            story.append(Paragraph("Oxygen Level Incidents:", normal_style))
            for category, times in analysis['oxygen'].items():
                if times and category != 'normal':  # Skip normal readings
                    story.append(Paragraph(
                        f"- {category.replace('_', ' ').title()}: {len(times)} occurrences",
                        normal_style
                    ))
                    for t in times:
                        story.append(Paragraph(f"  • {t}", normal_style))
            story.append(Spacer(1, 12))

            # pH Analysis
            story.append(Paragraph("pH Level Incidents:", normal_style))
            for category, times in analysis['ph'].items():
                if times and category != 'normal':  # Skip normal readings
                    story.append(Paragraph(
                        f"- {category.replace('_', ' ').title()}: {len(times)} occurrences",
                        normal_style
                    ))
                    for t in times:
                        story.append(Paragraph(f"  • {t}", normal_style))
            story.append(Spacer(1, 12))

            # Turbidity Analysis
            story.append(Paragraph("Turbidity Incidents:", normal_style))
            for category, times in analysis['turbidity'].items():
                if times and category != 'clean':  # Skip clean readings
                    story.append(Paragraph(
                        f"- {category.replace('_', ' ').title()}: {len(times)} occurrences",
                        normal_style
                    ))
                    for t in times:
                        story.append(Paragraph(f"  • {t}", normal_style))

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