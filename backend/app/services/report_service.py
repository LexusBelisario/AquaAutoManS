from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.units import inch

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
        """Generate a detailed report for dead catfish incidents"""
        try:
            logging.info(f"Starting dead catfish report generation for alert ID: {alert_id}")
            
            latest_dead_record = (
                aquamans.query.filter(aquamans.dead_catfish > 0)
                .order_by(aquamans.timeData.desc())
                .first()
            )

            if not latest_dead_record:
                return jsonify({
                    "message": "No dead catfish detected in the system.",
                    "timestamp": "2025-03-20 13:29:31",
                    "reported_by": "New User"
                })

            recent_data = (
                aquamans.query.filter(aquamans.timeData <= latest_dead_record.timeData)
                .order_by(aquamans.timeData.desc())
                .limit(1800)
                .all()
            )
            recent_data.reverse() 

            logging.info(f"Found {len(recent_data)} records in the data log")

            totals = {
                'temperature': 0,
                'oxygen': 0,
                'phlevel': 0,
                'turbidity': 0,
                'count': 0,
                'alive_catfish': 0,
                'dead_catfish': 0
            }

            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1
            )
            heading2_style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=12
            )
            warning_style = ParagraphStyle(
                'WarningStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.red,
                leading=14
            )
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                leading=12
            )

            story = []

            story.append(Paragraph("Case 5 - Dead Catfish Detected", title_style))
            story.append(Paragraph(
                "IMMEDIATE ACTION REQUIRED: Remove dead catfish immediately to prevent water contamination!",
                warning_style
            ))
            story.append(Spacer(1, 12))

            water_regulations = []
            
            if latest_dead_record.temperature >= 35:
                water_regulations.append(
                    "• CRITICAL: Water temperature is dangerously high. Take immediate action:\n"
                    "  - Cool down water temperature immediately\n"
                    "  - Add fresh, cooler water\n"
                    "  - Provide shade from direct sunlight\n"
                    "  - Consider adding cooling system"
                )
            elif latest_dead_record.temperature >= 32:
                water_regulations.append(
                    "• Water temperature is above optimal range:\n"
                    "  - Gradually reduce water temperature\n"
                    "  - Monitor temperature every hour\n"
                    "  - Check for heat sources"
                )
            elif latest_dead_record.temperature <= 20:
                water_regulations.append(
                    "• CRITICAL: Water temperature is dangerously low. Take immediate action:\n"
                    "  - Increase water temperature gradually\n"
                    "  - Add warm water carefully\n"
                    "  - Check heater functionality"
                )
            elif latest_dead_record.temperature < 26:
                water_regulations.append(
                    "• Water temperature is below optimal range:\n"
                    "  - Gradually increase water temperature\n"
                    "  - Monitor temperature every hour"
                )

            if latest_dead_record.oxygen <= 0.8:
                water_regulations.append(
                    "• CRITICAL: Oxygen levels are critically low. Take immediate action:\n"
                    "  - Increase aeration immediately\n"
                    "  - Add air stones or oxygen supply\n"
                    "  - Perform partial water change"
                )
            elif latest_dead_record.oxygen < 1.5:
                water_regulations.append(
                    "• Low oxygen levels detected:\n"
                    "  - Increase water movement\n"
                    "  - Check aeration system\n"
                    "  - Monitor oxygen levels hourly"
                )

            if latest_dead_record.phlevel < 4 or latest_dead_record.phlevel > 9:
                water_regulations.append(
                    "• CRITICAL: pH levels are at extreme levels. Take immediate action:\n"
                    "  - Perform immediate water change\n"
                    "  - Test water source before adding\n"
                    "  - Monitor pH levels every hour"
                )
            elif latest_dead_record.phlevel < 6 or latest_dead_record.phlevel > 7.5:
                water_regulations.append(
                    "• pH levels are outside optimal range:\n"
                    "  - Perform partial water change\n"
                    "  - Monitor pH levels regularly"
                )

            if water_regulations:
                story.append(Paragraph("Water Quality Regulation Required:", heading2_style))
                for regulation in water_regulations:
                    story.append(Paragraph(regulation, normal_style))
                    story.append(Spacer(1, 8))

            story.append(Paragraph("Required Immediate Actions:", heading2_style))
            immediate_actions = [
                "1. Remove dead catfish IMMEDIATELY regardless of water parameters",
                "2. Document time and conditions of death",
                "3. Perform water quality tests",
                "4. Implement recommended water regulations as listed above",
                "5. Monitor remaining catfish for signs of stress",
                "6. Test water parameters every 2-3 hours after changes"
            ]
            for action in immediate_actions:
                story.append(Paragraph(action, normal_style))
                story.append(Spacer(1, 4))

            story.append(Paragraph("Incident Summary", heading2_style))
            incident_summary = [
                ["Time of Death", "Total Catfish", "Dead Catfish", "Mortality Rate"],
                [
                    latest_dead_record.timeData.strftime("%Y-%m-%d %H:%M:%S"),
                    str(latest_dead_record.catfish),
                    str(latest_dead_record.dead_catfish),
                    f"{(latest_dead_record.dead_catfish / (latest_dead_record.catfish + latest_dead_record.dead_catfish) * 100):.2f}%"
                ]
            ]
            summary_table = Table(incident_summary)
            summary_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            story.append(Paragraph("Water Parameters at Time of Death", heading2_style))
            death_params = [
                ["Parameter", "Value", "Status", "Normal Range"],
                ["Temperature", f"{latest_dead_record.temperature:.2f}°C",
                self._get_temp_status(latest_dead_record.temperature), "26-32°C"],
                ["Oxygen", f"{latest_dead_record.oxygen:.2f} mg/L",
                self._get_oxygen_status(latest_dead_record.oxygen), "1.5-5.0 mg/L"],
                ["pH Level", f"{latest_dead_record.phlevel:.2f}",
                self._get_ph_status(latest_dead_record.phlevel), "6.0-7.5"],
                ["Turbidity", f"{latest_dead_record.turbidity:.2f} NTU",
                self._get_turbidity_status(latest_dead_record.turbidity), "<20 NTU"]
            ]
            params_table = Table(death_params, colWidths=[100, 100, 100, 100])
            params_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
            ]))
            story.append(params_table)
            story.append(Spacer(1, 20))

            natural_causes = self._check_natural_causes(latest_dead_record)
            if natural_causes:
                story.append(Paragraph("Analysis of Non-Water Quality Factors", heading2_style))
                for section in natural_causes:
                    story.append(Paragraph(section, normal_style))
                    story.append(Spacer(1, 4))

            story.append(PageBreak())
            story.append(Paragraph("Detailed Data Log", heading2_style))
            story.append(Spacer(1, 12))

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

            story.append(Paragraph("Dead Catfish Documentation", heading2_style))
            story.append(Spacer(1, 12))

            image_added = False
            for record in recent_data:
                if (record.dead_catfish > 0 and 
                    hasattr(record, 'dead_catfish_image') and 
                    record.dead_catfish_image):
                    try:
                        image = Image(BytesIO(record.dead_catfish_image))
                        
                        aspect = image.imageWidth / float(image.imageHeight)
                        
                        image.drawWidth = 6 * inch
                        image.drawHeight = (6 * inch) / aspect
                        
                        story.append(Paragraph(
                            f"Image captured at: {record.timeData.strftime('%Y-%m-%d %H:%M:%S')}",
                            normal_style
                        ))
                        story.append(Spacer(1, 6))
                        story.append(image)
                        story.append(Spacer(1, 12))
                        image_added = True
                        break
                        
                    except Exception as img_error:
                        logging.error(f"Error processing image for record at {record.timeData}: {str(img_error)}")
                        story.append(Paragraph(
                            f"Error: Unable to process image for record at {record.timeData}",
                            normal_style
                        ))

            if not image_added:
                story.append(Paragraph(
                    "No image available for this incident.",
                    normal_style
                ))

            story.append(PageBreak())
            story.append(Spacer(1, 20))
            
            footer_text = [
                f"Report Generated: 2025-03-20 13:29:31 UTC",
                f"Generated By: LexusBelisario",
                f"Report ID: DCR-{alert_id}",
                "This report is automatically generated by the Aquaman Monitoring System",
                "For questions or concerns, please contact the system administrator"
            ]
            
            for line in footer_text:
                story.append(Paragraph(line, normal_style))
                story.append(Spacer(1, 4))

            doc.build(story)
            buffer.seek(0)

            logging.info("Sending PDF file")
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f"dead-catfish-report-{latest_dead_record.timeData.strftime('%Y%m%d')}.pdf",
                mimetype="application/pdf"
            )

        except Exception as e:
            logging.error(f"Error generating dead catfish report: {str(e)}")
            return jsonify({
                "error": "Failed to generate report",
                "message": str(e),
                "timestamp": "2025-03-20 13:29:31",
                "alert_id": alert_id,
                "reported_by": "User"
            })
    
    def _generate_analysis_message(self, record, mortality_rate):
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
        
    def _get_temperature_causes(self, temp):
        if temp <= 20:
            return (
                "Cold temperature in environment, "
                "Cold water used for replacement, "
                "Exposure to cold wind"
            )
        elif 20 < temp < 26:
            return (
                "Below average environmental temperature, "
                "Cooler water used during water change"
            )
        elif 32 <= temp < 35:
            return (
                "High environmental temperature, "
                "Warm water used during water change, "
                "Partial sun exposure"
            )
        elif temp >= 35:
            return (
                "Very high environmental temperature, "
                "Hot water used during water change, "
                "Direct sunlight exposure"
            )
        return "Temperature within normal range"

    def _get_ph_causes(self, ph):
        if ph < 4:
            return (
                "Strong acid contamination, "
                "Chemical spill, "
                "Acid rain effect"
            )
        elif 4 <= ph < 6:
            return (
                "Mild acid contamination, "
                "Organic waste buildup, "
                "Recent water change with acidic water"
            )
        elif ph > 9:
            return (
                "Alkaline contamination, "
                "Cleaning products residue, "
                "High mineral content in water source"
            )
        elif 7.5 < ph <= 9:
            return (
                "Slightly alkaline conditions, "
                "Mineral buildup, "
                "Recent concrete contact"
            )
        return "pH within normal range"

    def _get_oxygen_causes(self, oxy):
        if oxy <= 0.8:
            return (
                "Severe oxygen depletion, "
                "Overcrowding, "
                "Poor aeration, "
                "Excess organic waste"
            )
        elif oxy < 1.5:
            return (
                "Insufficient oxygen levels, "
                "Limited water circulation, "
                "High fish density"
            )
        elif oxy > 5:
            return (
                "Excessive aeration, "
                "Possible supersaturation, "
                "Chemical interference"
            )
        return "Oxygen within normal range"

    def _get_turbidity_causes(self, turb):
        if turb >= 50:
            return (
                "High waste content, "
                "Poor filtration, "
                "Excess suspended particles"
            )
        elif 20 <= turb < 50:
            return (
                "Moderate particle suspension, "
                "Partial filtration issues, "
                "Recent water disturbance"
            )
        return "Turbidity within normal range"

    def _analyze_parameter_trend(self, start_val, end_val, param_type):
        """Analyzes the trend of a parameter over time."""
        change = end_val - start_val
        percent_change = (change / start_val * 100) if start_val != 0 else 0
        
        if param_type == 'temperature':
            if abs(change) >= 5:
                return f"Critical {param_type} change of {change:+.1f}°C ({percent_change:+.1f}%)"
            elif abs(change) >= 2:
                return f"Significant {param_type} change of {change:+.1f}°C ({percent_change:+.1f}%)"
        
        elif param_type == 'oxygen':
            if abs(change) >= 1:
                return f"Critical {param_type} change of {change:+.2f} mg/L ({percent_change:+.1f}%)"
            elif abs(change) >= 0.5:
                return f"Significant {param_type} change of {change:+.2f} mg/L ({percent_change:+.1f}%)"
        
        elif param_type == 'ph':
            if abs(change) >= 1:
                return f"Critical pH change of {change:+.2f} ({percent_change:+.1f}%)"
            elif abs(change) >= 0.5:
                return f"Significant pH change of {change:+.2f} ({percent_change:+.1f}%)"
        
        elif param_type == 'turbidity':
            if abs(change) >= 20:
                return f"Critical turbidity change of {change:+.1f} NTU ({percent_change:+.1f}%)"
            elif abs(change) >= 10:
                return f"Significant turbidity change of {change:+.1f} NTU ({percent_change:+.1f}%)"
        
        return f"Minor {param_type} change of {change:+.2f} ({percent_change:+.1f}%)"

    def _get_stress_indicators(self, record):
        """Identifies potential stress indicators from water parameters."""
        indicators = []
        
        if record.temperature <= 20 or record.temperature >= 35:
            indicators.append("Extreme temperature")
        elif 20 < record.temperature < 26 or 32 <= record.temperature < 35:
            indicators.append("Suboptimal temperature")

        if record.oxygen <= 0.8:
            indicators.append("Critical oxygen levels")
        elif record.oxygen < 1.5:
            indicators.append("Low oxygen levels")
        elif record.oxygen > 5:
            indicators.append("Excessive oxygen")

        if record.phlevel < 4 or record.phlevel > 9:
            indicators.append("Extreme pH levels")
        elif 4 <= record.phlevel < 6 or 7.5 < record.phlevel <= 9:
            indicators.append("Suboptimal pH")

        if record.turbidity >= 50:
            indicators.append("High turbidity")
        elif 20 <= record.turbidity < 50:
            indicators.append("Elevated turbidity")

        return indicators
    
    def _check_natural_causes(self, record):
        """
        Detailed analysis of natural or external causes when water parameters are normal.
        Includes specific checks and targeted recommendations.
        """
        is_temp_normal = 26 <= record.temperature <= 32
        is_oxygen_normal = 1.5 <= record.oxygen <= 5
        is_ph_normal = 6 <= record.phlevel <= 7.5
        is_turbidity_normal = record.turbidity < 20

        if is_temp_normal and is_oxygen_normal and is_ph_normal and is_turbidity_normal:
            possible_causes = {
                "Feeding Issues": {
                    "Indicators": [
                        "• Insufficient feeding frequency",
                        "• Poor quality feed",
                        "• Irregular feeding schedule",
                        "• Competition for food among catfish"
                    ],
                    "Recommendations": [
                        "→ Maintain a regular feeding schedule (2-3 times daily)",
                        "→ Use high-quality catfish feed",
                        "→ Monitor feeding behavior",
                        "→ Ensure equal food distribution",
                        "→ Consider feed supplements if needed"
                    ]
                },
                "Water Level Issues": {
                    "Indicators": [
                        "• Insufficient water depth",
                        "• Rapid water level changes",
                        "• Limited swimming space",
                        "• Stress from crowding"
                    ],
                    "Recommendations": [
                        "→ Maintain proper water depth (minimum 2-3 feet)",
                        "→ Check for leaks in the aquarium",
                        "→ Monitor water level daily",
                        "→ Ensure adequate space per catfish",
                        "→ Install water level markers"
                    ]
                },
                "Natural Health Issues": {
                    "Indicators": [
                        "• Age-related factors",
                        "• Possible disease",
                        "• Genetic factors",
                        "• Stress from breeding season"
                    ],
                    "Recommendations": [
                        "→ Regular health monitoring of remaining catfish",
                        "→ Watch for unusual behavior",
                        "→ Consider quarantine if disease is suspected",
                        "→ Maintain detailed health records",
                        "→ Consult a fish health specialist if needed"
                    ]
                },
                "Physical Factors": {
                    "Indicators": [
                        "• Signs of physical injury",
                        "• Aggressive behavior among catfish",
                        "• Sharp objects in aquarium",
                        "• Equipment-related injuries"
                    ],
                    "Recommendations": [
                        "→ Inspect aquarium for hazardous objects",
                        "→ Check filtration equipment for safety",
                        "→ Monitor catfish behavior",
                        "→ Provide adequate hiding spaces",
                        "→ Remove any dangerous decorations"
                    ]
                },
                "External Intervention": {
                    "Indicators": [
                        "• Unexplained deaths",
                        "• Signs of tampering",
                        "• Unauthorized access",
                        "• Unusual timing of incidents"
                    ],
                    "Recommendations": [
                        "→ Install security cameras if possible",
                        "→ Restrict access to authorized personnel",
                        "→ Maintain incident logs",
                        "→ Implement safety protocols",
                        "→ Regular security checks"
                    ]
                }
            }

            report_sections = []
            report_sections.append("All water parameters are within normal ranges.")
            report_sections.append("Detailed Analysis of Other Possible Causes:\n")

            for cause, details in possible_causes.items():
                report_sections.append(f"\n{cause}:")
                report_sections.append("Potential Indicators:")
                report_sections.extend(details["Indicators"])
                report_sections.append("\nRecommended Actions:")
                report_sections.extend(details["Recommendations"])
                report_sections.append("\n")

            report_sections.append("\nImmediate Actions Required:")
            report_sections.extend([
                "1. Remove deceased catfish immediately",
                "2. Document all observations and findings",
                "3. Implement recommended preventive measures",
                "4. Monitor remaining catfish closely for 48-72 hours",
                "5. Keep detailed records of any changes or unusual behavior"
            ])

            return report_sections
        return None


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
            
            def classify_case(data):
                fluctuations = {
                    'temperature': [],
                    'oxygen': [],
                    'phlevel': [],
                    'turbidity': []
                }
                
                for i in range(1, len(data)):
                    prev_record = data[i-1]
                    curr_record = data[i]
                    
                    temp = curr_record.temperature
                    if temp <= 20:
                        fluctuations['temperature'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.temperature - prev_record.temperature),
                            'prev_value': prev_record.temperature,
                            'curr_value': curr_record.temperature,
                            'status': "Cold Temperature"
                        })
                    elif 20 < temp < 26:
                        fluctuations['temperature'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.temperature - prev_record.temperature),
                            'prev_value': prev_record.temperature,
                            'curr_value': curr_record.temperature,
                            'status': "Below Average Temperature"
                        })
                    elif 32 <= temp < 35:
                        fluctuations['temperature'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.temperature - prev_record.temperature),
                            'prev_value': prev_record.temperature,
                            'curr_value': curr_record.temperature,
                            'status': "Above Average Temperature"
                        })
                    elif temp >= 35:
                        fluctuations['temperature'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.temperature - prev_record.temperature),
                            'prev_value': prev_record.temperature,
                            'curr_value': curr_record.temperature,
                            'status': "Hot Temperature"
                        })
                    
                    oxy = curr_record.oxygen
                    if oxy <= 0.8:
                        fluctuations['oxygen'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.oxygen - prev_record.oxygen),
                            'prev_value': prev_record.oxygen,
                            'curr_value': curr_record.oxygen,
                            'status': "Very Low Oxygen"
                        })
                    elif oxy < 1.5:
                        fluctuations['oxygen'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.oxygen - prev_record.oxygen),
                            'prev_value': prev_record.oxygen,
                            'curr_value': curr_record.oxygen,
                            'status': "Low Oxygen"
                        })
                    elif oxy > 5:
                        fluctuations['oxygen'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.oxygen - prev_record.oxygen),
                            'prev_value': prev_record.oxygen,
                            'curr_value': curr_record.oxygen,
                            'status': "High Oxygen"
                        })
                    
                    ph = curr_record.phlevel
                    if ph < 4:
                        fluctuations['phlevel'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.phlevel - prev_record.phlevel),
                            'prev_value': prev_record.phlevel,
                            'curr_value': curr_record.phlevel,
                            'status': "Very Acidic"
                        })
                    elif 4 <= ph < 6:
                        fluctuations['phlevel'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.phlevel - prev_record.phlevel),
                            'prev_value': prev_record.phlevel,
                            'curr_value': curr_record.phlevel,
                            'status': "Acidic"
                        })
                    elif ph > 9:
                        fluctuations['phlevel'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.phlevel - prev_record.phlevel),
                            'prev_value': prev_record.phlevel,
                            'curr_value': curr_record.phlevel,
                            'status': "Very Alkaline"
                        })
                    
                    turb = curr_record.turbidity
                    if turb >= 50:
                        fluctuations['turbidity'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.turbidity - prev_record.turbidity),
                            'prev_value': prev_record.turbidity,
                            'curr_value': curr_record.turbidity,
                            'status': "Dirty"
                        })
                    elif 20 <= turb < 50:
                        fluctuations['turbidity'].append({
                            'time': curr_record.timeData,
                            'change': abs(curr_record.turbidity - prev_record.turbidity),
                            'prev_value': prev_record.turbidity,
                            'curr_value': curr_record.turbidity,
                            'status': "Cloudy"
                        })
                
                total_abnormal_params = sum(
                    1 for param_fluc in fluctuations.values() if param_fluc
                )
                
                dead_fish = any(record.dead_catfish > 0 for record in data)
                
                if dead_fish:
                    return {
                        'case': "Case 5: A Fish Died",
                        'case_description': "Fish mortality detected during the monitoring period.",
                        'fluctuations': fluctuations
                    }
                
                if total_abnormal_params == 0:
                    return {
                        'case': "Case 1: Normal Readings",
                        'case_description': "All water parameters remained stable during the monitored period.",
                        'fluctuations': fluctuations
                    }
                elif total_abnormal_params == 1:
                    abnormal_param = next(
                        param for param, fluc in fluctuations.items() if fluc
                    )
                    return {
                        'case': "Case 2: 1 Minor Fluctuation",
                        'case_description': f"Detected a minor fluctuation in {abnormal_param}",
                        'fluctuations': fluctuations
                    }
                elif total_abnormal_params == 2:
                    return {
                        'case': "Case 3: 2 or More Minor Fluctuations",
                        'case_description': "Multiple minor fluctuations detected across different water parameters.",
                        'fluctuations': fluctuations
                    }
                else:
                    return {
                        'case': "Case 4: 1 or More Major Fluctuations",
                        'case_description': "Significant variations observed in multiple water parameters.",
                        'fluctuations': fluctuations
                    }
            case_classification = classify_case(recent_data)

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

            buffer = BytesIO()
            doc = SimpleDocTemplate(
                buffer,
                pagesize=landscape(letter),
                rightMargin=36,
                leftMargin=36,
                topMargin=36,
                bottomMargin=36
            )

            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            heading2_style = styles["Heading2"]
            normal_style = styles["Normal"]

            story = []

            title = "Aquamans Data Report"
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 12))

            if time_filter > 0:
                period = f"Last {time_filter} Hours"
            else:
                period = f"Date: {filter_date.strftime('%Y-%m-%d')}"
            story.append(Paragraph(f"Period: {period}", normal_style))
            story.append(Spacer(1, 12))

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

            critical_incidents = {}

            for record in recent_data:
                time_str = record.timeData.strftime("%Y-%m-%d %H:%M:%S")
                
                temp = float(record.temperature)
                if temp <= 20:
                    if 'cold_temp' not in critical_incidents:
                        critical_incidents['cold_temp'] = {
                            'time': time_str,
                            'value': f"{temp:.2f}°C",
                            'parameter': "Temperature",
                            'status': "Cold Temperature",
                            'causes': [
                                "Cold Temperature in Environment of the Aquarium",
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

            if critical_incidents:
                story.append(Paragraph("First Occurrences of Critical Incidents:", normal_style))
                story.append(Spacer(1, 12))
                
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
                
            story.insert(1, Paragraph(f"Case: {case_classification['case']}", normal_style))
            story.insert(2, Paragraph(f"Case Description: {case_classification['case_description']}", normal_style))
            story.insert(3, Spacer(1, 12))

            if case_classification['case'] != "Case 1: Normal Readings":
                story.insert(4, Paragraph("Fluctuations Detected:", heading2_style))
                for param, fluc_list in case_classification['fluctuations'].items():
                    if fluc_list:
                        story.insert(5, Paragraph(f"{param.capitalize()} Fluctuations:", normal_style))
                        for fluc in fluc_list:
                            story.insert(6, Paragraph(
                                f"Time: {fluc['time'].strftime('%Y-%m-%d %H:%M:%S')}, Change: {fluc['change']:.2f}", 
                                normal_style
                            ))
                story.insert(7, Spacer(1, 12))

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
        
    
