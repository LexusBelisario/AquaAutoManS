from flask import jsonify
from app.models import aquamans
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
import logging
import base64

class IncidentService:
    def __init__(self):
        self.current_timestamp = "2025-03-21 12:14:25"
        self.current_user = "User"

    def generate_incident_report(self):
        """Generate incident report based on water parameter fluctuations"""
        try:
            logging.info(f"Starting incident report generation at {self.current_timestamp}")
            
            # Get the latest record
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            
            if not latest_record:
                return {
                    "message": "No data available in the system.",
                    "timestamp": "2025-03-21 15:12:43",
                    "reported_by": "LexusBelisario"
                }

            # Get previous records for comparison (last 10 records)
            recent_records = (
                aquamans.query.order_by(aquamans.timeData.desc())
                .limit(10)
                .all()
            )
            
            # Initialize fluctuation tracking
            fluctuations = {
                'temperature': [],
                'oxygen': [],
                'phlevel': []
            }
            
            # Check the latest record's parameters for fluctuations
            # Temperature check
            temp = latest_record.temperature
            if temp < 19 or temp > 33:
                fluctuations['temperature'].append({
                    'type': 'major',
                    'value': temp,
                    'time': latest_record.timeData,
                    'status': 'Critical Temperature Level'
                })
            elif (20 <= temp < 26) or (32 < temp <= 33):
                fluctuations['temperature'].append({
                    'type': 'minor',
                    'value': temp,
                    'time': latest_record.timeData,
                    'status': 'Minor Temperature Level'
                })

            # Oxygen check
            oxy = latest_record.oxygen
            if oxy < 1 or oxy > 7:
                fluctuations['oxygen'].append({
                    'type': 'major',
                    'value': oxy,
                    'time': latest_record.timeData,
                    'status': 'Critical Oxygen Level'
                })
            elif (1.0 <= oxy < 1.5) or (5 < oxy <= 6):
                fluctuations['oxygen'].append({
                    'type': 'minor',
                    'value': oxy,
                    'time': latest_record.timeData,
                    'status': 'Stress Oxygen Range'
                })

            # pH check
            ph = latest_record.phlevel
            if ph < 4 or ph > 8.5:
                fluctuations['phlevel'].append({
                    'type': 'major',
                    'value': ph,
                    'time': latest_record.timeData,
                    'status': 'Major pH Level'
                })
            elif (5 <= ph < 6) or (7.5 < ph <= 8.5):
                fluctuations['phlevel'].append({
                    'type': 'minor',
                    'value': ph,
                    'time': latest_record.timeData,
                    'status': 'Minor pH Level'
                })

            # Count fluctuations more accurately
            minor_fluctuations = 0
            major_fluctuations = 0
            
            for param_fluctuations in fluctuations.values():
                if param_fluctuations:  # If there are any fluctuations for this parameter
                    if param_fluctuations[0]['type'] == 'major':
                        major_fluctuations += 1
                    elif param_fluctuations[0]['type'] == 'minor':
                        minor_fluctuations += 1

            # Check for Case 5 first (Catfish death)
            has_died = latest_record.dead_catfish > 0
            has_fluctuations = major_fluctuations > 0 or minor_fluctuations > 0

            if has_died:
                if has_fluctuations:
                    case = {
                        'number': 5,
                        'title': 'Case 5: Catfish Mortality with Parameter Fluctuations',
                        'description': 'Catfish death detected with water quality issues.',
                        'severity': 'Emergency',
                        'alert_level': 'Purple',
                        'death_cause': 'Parameter fluctuations likely contributed to mortality.'
                    }
                else:
                    case = {
                        'number': 5,
                        'title': 'Case 5: Unexpected Catfish Mortality',
                        'description': 'Catfish death detected with normal parameters.',
                        'severity': 'Emergency',
                        'alert_level': 'Purple',
                        'death_cause': 'No parameter fluctuations detected. Possible causes include:\n' +
                                    '• Natural causes or age\n' +
                                    '• Disease or parasites\n' +
                                    '• Physical injury\n' +
                                    '• Stress from handling\n' +
                                    '• Recent feeding issues\n' +
                                    '• Social aggression'
                    }
            # Determine case based on the latest readings if no death
            elif major_fluctuations > 0:
                case = {
                    'number': 4,
                    'title': 'Case 4: Major Parameter Fluctuations',
                    'description': 'Critical levels detected in water parameters.',
                    'severity': 'Critical',
                    'alert_level': 'Red'
                }
            elif minor_fluctuations >= 2:
                case = {
                    'number': 3,
                    'title': 'Case 3: Multiple Minor Fluctuations',
                    'description': 'Multiple stress conditions detected across parameters.',
                    'severity': 'High',
                    'alert_level': 'Orange'
                }
            elif minor_fluctuations == 1:
                case = {
                    'number': 2,
                    'title': 'Case 2: Single Minor Fluctuation',
                    'description': 'Minor stress condition detected.',
                    'severity': 'Medium',
                    'alert_level': 'Yellow'
                }
            else:
                case = {
                    'number': 1,
                    'title': 'Case 1: Normal Readings',
                    'description': 'All parameters within optimal ranges.',
                    'severity': 'Normal',
                    'alert_level': 'Green'
                }

            # Create parameter status messages
            current_status = {
                "temperature": {
                    "value": latest_record.temperature,
                    "status": self._get_temperature_status(latest_record.temperature),
                    "normal_range": "26-32°C",
                    "effects": self._get_temperature_effects(latest_record.temperature)
                },
                "oxygen": {
                    "value": latest_record.oxygen,
                    "status": self._get_oxygen_status(latest_record.oxygen),
                    "normal_range": "1.5-5.0 mg/L",
                    "effects": self._get_oxygen_effects(latest_record.oxygen)
                },
                "phlevel": {
                    "value": latest_record.phlevel,
                    "status": self._get_ph_status(latest_record.phlevel),
                    "normal_range": "6.0-7.5",
                    "effects": self._get_ph_effects(latest_record.phlevel)
                }
            }

            # Get catfish counts and image from latest record
            catfish_info = {
                "alive_count": latest_record.catfish if hasattr(latest_record, 'catfish') else "N/A",
                "dead_count": latest_record.dead_catfish if hasattr(latest_record, 'dead_catfish') else "N/A",
                "timestamp": latest_record.timeData.strftime('%Y-%m-%d %H:%M:%S') if latest_record.timeData else "2025-03-21 15:12:43",
                "dead_catfish_image": latest_record.dead_catfish_image if hasattr(latest_record, 'dead_catfish_image') else None
            }

            # Create response with all information
            response = {
                "case": case,
                "current_readings": current_status,
                "fluctuations": fluctuations,
                "recommendations": self._get_recommendations(case['number'], fluctuations),
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario",
                "incident_id": f"INC{latest_record.timeData.strftime('%Y%m%d%H%M')}",
                "catfish_info": catfish_info
            }

            return response

        except Exception as e:
            logging.error(f"Error generating incident report: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario"
            }
        
    def _get_temperature_status(self, temp):
        """Get temperature status based on range"""
        if 26 <= temp <= 32:
            return "Normal Temperature Level"
        elif (20 <= temp < 26) or (27 <= temp <= 32):
            return "Minor Temperature Level"
        elif temp < 19 or temp > 33:
            return "Critical Temperature Level"
        return "Temperature Out of Range"
    
    def _get_oxygen_status(self, oxy):
        """Get oxygen status based on range"""
        if 1.5 <= oxy <= 5:
            return "Normal Oxygen Level"
        elif (1.0 <= oxy <= 1.4) or (5 <= oxy <= 6):
            return "Stress Oxygen Range"
        elif oxy < 1 or oxy > 7:
            return "Critical Oxygen Level"
        return "Oxygen Out of Range"
    
    def _get_ph_status(self, ph):
        """Get pH status based on range"""
        if 6 <= ph <= 7.5:
            return "Normal pH Level"
        elif (5 <= ph <= 5.9) or (7.6 <= ph <= 8.5):
            return "Minor pH Level"
        elif ph < 4 or ph > 8.5:
            return "Critical pH Level"
        return "pH Out of Range"
    
    def _get_temperature_effects(self, temp):
        """Get temperature effects on catfish"""
        if 26 <= temp <= 32:
            return "Optimal for catfish growth, feed intake and health will significantly increase."
        elif (20 <= temp < 26) or (27 <= temp <= 32):
            return "Minor stress and slightly reduces growth rate and feed intake. Health rates may also decrease."
        elif temp < 19 or temp > 33:
            return "Rate of mortality significantly increases; catfish will possibly die in a few hours or days."
        return "Temperature conditions are severely affecting catfish health."
    
    def _get_oxygen_effects(self, oxy):
        """Get oxygen effects on catfish"""
        if 1.5 <= oxy <= 5:
            return "Optimal for catfish growth, feed intake and health will significantly increase."
        elif (1.0 <= oxy <= 1.4) or (5 <= oxy <= 6):
            return "Significant stress, reduced immunity, risk of disease."
        elif oxy < 1 or oxy > 7:
            return "High mortality risk; catfish may die within hours."
        return "Oxygen conditions are severely affecting catfish health."
    
    def _get_ph_effects(self, ph):
        """Get pH effects on catfish"""
        if 6 <= ph <= 7.5:
            return "Optimal for catfish growth, feed intake and health will significantly increase."
        elif (5 <= ph <= 5.9) or (7.6 <= ph <= 8.5):
            return "Minor stress conditions; reduced growth, feed intake, and immune function."
        elif ph < 4 or ph > 8.5:
            return "Severe stress; catfish will possibly die in a few hours or days."
        return "pH conditions are severely affecting catfish health."
    
    def _get_recommendations(self, case_number, fluctuations):
        """Generate recommendations based on case number and specific parameter ranges"""
        recommendations = []
        
        if case_number == 5:
            base_recommendations = {
                "priority": "Emergency",
                "action": "Immediate Mortality Investigation",
                "details": [
                    "Emergency Alert:",
                    "• Document time and conditions of death",
                    "• Collect water samples for testing",
                    "• Photograph deceased catfish",
                    "• Remove deceased catfish promptly",
                    "• Monitor remaining catfish closely"
                ],
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario"
            }
            
            if any(fluctuations.values()):
                # Death with parameter fluctuations
                base_recommendations["details"].extend([
                    "Parameter-Related Actions:",
                    "• Conduct full water quality analysis",
                    "• Prepare for emergency water change",
                    "• Check all equipment functionality",
                    "• Consider moving healthy fish if needed"
                ])
            else:
                # Death with normal parameters
                base_recommendations["details"].extend([
                    "Investigation Points:",
                    "• Check for physical injuries",
                    "• Examine for disease symptoms",
                    "• Review feeding records",
                    "• Assess tank conditions",
                    "• Consider pathogen testing"
                ])
            
            recommendations.append(base_recommendations)
            return recommendations
        
        elif case_number == 1:
            recommendations.append({
                "priority": "Low",
                "action": "Maintain Current Conditions",
                "details": [
                    "Current Status:",
                    "• Temperature (26-32°C): Optimal for catfish growth",
                    "• Oxygen (1.5-5 mg/L): Optimal for feed intake",
                    "• pH (6-7.5): Optimal for overall health",
                    "Actions Required:",
                    "• Continue regular monitoring schedule",
                    "• Document parameter readings",
                    "• Maintain feeding schedule",
                    "• Check equipment regularly",
                    "• Monitor catfish behavior"
                ],
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario"
            })
        
        elif case_number == 2:
            # Check which parameter has the minor fluctuation
            for param, fluc_list in fluctuations.items():
                if fluc_list and fluc_list[0]['type'] == 'minor':
                    if param == 'temperature':
                        if 20 <= fluc_list[0]['value'] < 26:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address Below Optimal Temperature",
                                "details": [
                                    "Minor stress condition detected",
                                    "Current temperature reducing growth rate",
                                    "Actions required:",
                                    "• Gradually increase water temperature",
                                    "• Check heater functionality",
                                    "• Monitor temperature every 2 hours",
                                    "• Document temperature changes",
                                    "• Check environmental factors"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        elif 32 < fluc_list[0]['value'] <= 33:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address Above Optimal Temperature",
                                "details": [
                                    "Minor stress condition detected",
                                    "Temperature affecting feed intake",
                                    "Actions required:",
                                    "• Gradually reduce water temperature",
                                    "• Check for external heat sources",
                                    "• Monitor temperature every 2 hours",
                                    "• Document temperature changes",
                                    "• Evaluate cooling system"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                    
                    elif param == 'oxygen':
                        if 1.0 <= fluc_list[0]['value'] < 1.5:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address Low Oxygen Stress",
                                "details": [
                                    "Stress oxygen range detected",
                                    "Reduced immunity risk identified",
                                    "Actions required:",
                                    "• Increase aeration immediately",
                                    "• Check water circulation",
                                    "• Monitor oxygen levels hourly",
                                    "• Reduce feeding temporarily",
                                    "• Prepare for water change if needed"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        elif 5 < fluc_list[0]['value'] <= 6:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address High Oxygen Stress",
                                "details": [
                                    "Above optimal oxygen range",
                                    "Stress conditions present",
                                    "Actions required:",
                                    "• Adjust aeration system",
                                    "• Reduce water agitation",
                                    "• Monitor oxygen levels hourly",
                                    "• Check equipment functionality",
                                    "• Document oxygen changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                    
                    elif param == 'phlevel':
                        if 5 <= fluc_list[0]['value'] < 6:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address Acidic pH Condition",
                                "details": [
                                    "Minor acidic conditions detected",
                                    "Growth and immune impact possible",
                                    "Actions required:",
                                    "• Plan 25% water change",
                                    "• Test source water pH",
                                    "• Monitor pH every 2 hours",
                                    "• Check for acidic influences",
                                    "• Document pH changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        elif 7.5 < fluc_list[0]['value'] <= 8.5:
                            recommendations.append({
                                "priority": "Medium",
                                "action": "Address Alkaline pH Condition",
                                "details": [
                                    "Minor alkaline conditions detected",
                                    "Growth and immune impact possible",
                                    "Actions required:",
                                    "• Plan 25% water change",
                                    "• Test source water pH",
                                    "• Monitor pH every 2 hours",
                                    "• Check for alkaline influences",
                                    "• Document pH changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                    break  # Exit after finding the first minor fluctuation for Case 2
        
        elif case_number == 3:
            recommendations.append({
                "priority": "High",
                "action": "Address Multiple Parameter Fluctuations",
                "details": [
                    "Multiple stress conditions detected",
                    "Significant impact on catfish health",
                    "Immediate actions required:",
                    "• Perform 30-40% water change",
                    "• Monitor all parameters hourly",
                    "• Check all equipment functionality",
                    "• Document all parameter changes",
                    "• Prepare for emergency measures"
                ],
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario"
            })
            
            # Add specific recommendations for each affected parameter
            for param, fluc_list in fluctuations.items():
                if fluc_list:
                    if param == 'temperature':
                        recommendations.append({
                            "priority": "High",
                            "action": "Temperature Stress Management",
                            "details": [
                                "Combined stress with other parameters",
                                "Actions required:",
                                "• Stabilize temperature gradually",
                                "• Monitor every hour",
                                "• Check environmental factors",
                                "• Verify equipment operation",
                                "• Prepare backup temperature control"
                            ],
                            "timestamp": "2025-03-21 15:12:43",
                            "reported_by": "LexusBelisario"
                        })
                    elif param == 'oxygen':
                        recommendations.append({
                            "priority": "High",
                            "action": "Oxygen Level Management",
                            "details": [
                                "Combined stress with other parameters",
                                "Actions required:",
                                "• Optimize aeration system",
                                "• Monitor oxygen hourly",
                                "• Check for oxygen depletion",
                                "• Reduce stressful activities",
                                "• Prepare emergency aeration"
                            ],
                            "timestamp": "2025-03-21 15:12:43",
                            "reported_by": "LexusBelisario"
                        })
                    elif param == 'phlevel':
                        recommendations.append({
                            "priority": "High",
                            "action": "pH Level Management",
                            "details": [
                                "Combined stress with other parameters",
                                "Actions required:",
                                "• Monitor pH changes hourly",
                                "• Prepare for water change",
                                "• Test water source quality",
                                "• Check for pH influences",
                                "• Document all changes"
                            ],
                            "timestamp": "2025-03-21 15:12:43",
                            "reported_by": "LexusBelisario"
                        })
        
        elif case_number == 4:
            recommendations.append({
                "priority": "Critical",
                "action": "CRITICAL PARAMETER ALERT",
                "details": [
                    "IMMEDIATE ACTION REQUIRED",
                    "Critical water parameters detected",
                    "Core actions required:",
                    "• Prepare for emergency water change",
                    "• Monitor parameters every 30 minutes",
                    "• Check all life support systems",
                    "• Document all changes",
                    "• Prepare emergency equipment"
                ],
                "timestamp": "2025-03-21 15:12:43",
                "reported_by": "LexusBelisario"
            })
            
            # Add specific critical recommendations
            for param, fluc_list in fluctuations.items():
                if fluc_list and fluc_list[0]['type'] == 'major':
                    if param == 'temperature':
                        if fluc_list[0]['value'] < 19:
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical Low Temperature Alert",
                                "details": [
                                    "Mortality risk - Temperature too low",
                                    "Emergency actions required:",
                                    "• Increase temperature (max 2°C/hour)",
                                    "• Verify heater operation",
                                    "• Prepare warm water exchange",
                                    "• Monitor catfish behavior",
                                    "• Document temperature changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        else:  # > 33
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical High Temperature Alert",
                                "details": [
                                    "Mortality risk - Temperature too high",
                                    "Emergency actions required:",
                                    "• Decrease temperature (max 2°C/hour)",
                                    "• Remove heat sources",
                                    "• Add cooling measures",
                                    "• Monitor catfish behavior",
                                    "• Document temperature changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                    
                    elif param == 'oxygen':
                        if fluc_list[0]['value'] < 1:
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical Low Oxygen Alert",
                                "details": [
                                    "Severe hypoxia condition",
                                    "Emergency actions required:",
                                    "• Maximize aeration immediately",
                                    "• Emergency water change",
                                    "• Add supplemental oxygen",
                                    "• Monitor fish continuously",
                                    "• Document oxygen changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        else:  # > 7
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical High Oxygen Alert",
                                "details": [
                                    "Dangerous supersaturation",
                                    "Emergency actions required:",
                                    "• Reduce aeration immediately",
                                    "• Check equipment malfunction",
                                    "• Perform water change",
                                    "• Monitor fish continuously",
                                    "• Document oxygen changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                    
                    elif param == 'phlevel':
                        if fluc_list[0]['value'] < 4:
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical Low pH Alert",
                                "details": [
                                    "Severe acidic conditions",
                                    "Emergency actions required:",
                                    "• Immediate water change",
                                    "• Test source water",
                                    "• Check for contamination",
                                    "• Monitor fish continuously",
                                    "• Document pH changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
                        else:  # > 8.5
                            recommendations.append({
                                "priority": "Critical",
                                "action": "Critical High pH Alert",
                                "details": [
                                    "Severe alkaline conditions",
                                    "Emergency actions required:",
                                    "• Immediate water change",
                                    "• Test source water",
                                    "• Check contamination sources",
                                    "• Monitor fish continuously",
                                    "• Document pH changes"
                                ],
                                "timestamp": "2025-03-21 15:12:43",
                                "reported_by": "LexusBelisario"
                            })
        
        return recommendations

    def generate_pdf_report(self, report_data, incident_id):
        """Generate a PDF report from the incident data"""
        try:
            buffer = BytesIO()
            
            # Create the PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=50,
                bottomMargin=50
            )
            
            # Container for PDF elements
            elements = []
            styles = getSampleStyleSheet()
            
            # Custom styles with proper spacing and formatting
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                spaceBefore=20,
                alignment=1,  # Center alignment
                textColor=colors.HexColor('#2C3E50')
            )
            
            heading2_style = ParagraphStyle(
                'CustomHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=10,
                spaceBefore=15,
                textColor=colors.HexColor('#2C3E50')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=8
            )
            
            bold_style = ParagraphStyle(
                'CustomBold',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                spaceAfter=8,
                bold=True
            )
            
            # Add title
            title = f"Water Quality Incident Report - Case {report_data['case']['number']}"
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 20))
            
            # Add report metadata with catfish information
            metadata = [
                ['Report ID:', incident_id],
                ['Generated On:', report_data['catfish_info']['timestamp']],
                ['Generated By:', "LexusBelisario"],
                ['Case Level:', f"Case {report_data['case']['number']} - {report_data['case']['severity']}"],
                ['Description:', report_data['case']['description']],
                ['Catfish Count:', f"Alive: {report_data['catfish_info']['alive_count']} | Dead: {report_data['catfish_info']['dead_count']}"]
            ]
            
            # Create metadata table
            meta_table = Table(metadata, colWidths=[120, 350])
            meta_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BACKGROUND', (0, 0), (0, -1), colors.grey),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ]))
            elements.append(meta_table)
            elements.append(Spacer(1, 20))

            # Add Case 5 specific information if applicable
            if report_data['case'].get('number') == 5:
                elements.append(Paragraph("Mortality Analysis", heading2_style))
                elements.append(Spacer(1, 10))
                
                mortality_data = [
                    ['Death Cause:', report_data['case']['death_cause']],
                    ['Time of Death:', report_data['catfish_info']['timestamp']],
                    ['Parameters Status:', 
                    'Abnormal - Contributing to mortality' if any(report_data['fluctuations'].values()) 
                    else 'Normal - Other causes suspected']
                ]
                
                mortality_table = Table(mortality_data, colWidths=[120, 350])
                mortality_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.purple),
                    ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(mortality_table)
                elements.append(Spacer(1, 15))

                # Add image if available
                if report_data['catfish_info'].get('dead_catfish_image'):
                    try:
                        img_path = report_data['catfish_info']['dead_catfish_image']
                        img = Image(img_path)
                        
                        # Scale image to fit in the document
                        max_width = 400
                        max_height = 300
                        img.drawWidth = min(img.drawWidth, max_width)
                        img.drawHeight = min(img.drawHeight, max_height)
                        
                        elements.append(Paragraph("Mortality Documentation", heading2_style))
                        elements.append(Spacer(1, 10))
                        elements.append(img)
                        elements.append(Spacer(1, 15))
                    except Exception as img_error:
                        logging.error(f"Error adding image to PDF: {str(img_error)}")
                        elements.append(Paragraph("Image could not be loaded", normal_style))
            
            # Add current readings section
            elements.append(Paragraph("Current Readings", heading2_style))
            elements.append(Spacer(1, 10))
            
            for param, data in report_data['current_readings'].items():
                readings_data = [
                    [Paragraph(f"{param.title()}:", bold_style), 
                    Paragraph(f"{data['value']} {data.get('unit', '')}", normal_style)],
                    [Paragraph("Status:", bold_style), 
                    Paragraph(data['status'], normal_style)],
                    [Paragraph("Normal Range:", bold_style), 
                    Paragraph(data['normal_range'], normal_style)],
                    [Paragraph("Effects:", bold_style), 
                    Paragraph(data['effects'], normal_style)]
                ]
                
                readings_table = Table(readings_data, colWidths=[120, 350])
                readings_table.setStyle(TableStyle([
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('TOPPADDING', (0, 0), (-1, -1), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 8),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ]))
                elements.append(readings_table)
                elements.append(Spacer(1, 15))
            
            # Add recommendations section
            if report_data.get('recommendations'):
                elements.append(Paragraph("Recommendations", heading2_style))
                elements.append(Spacer(1, 10))
                
                for rec in report_data['recommendations']:
                    # Format recommendation details
                    formatted_details = []
                    for detail in rec['details']:
                        if detail.endswith(':'):
                            # Bold headers
                            formatted_details.append(Paragraph(f"<b>{detail}</b>", normal_style))
                        elif detail.startswith('•'):
                            # Bullet points already formatted
                            formatted_details.append(Paragraph(f"{detail}", normal_style))
                        elif detail.startswith('-'):
                            # Convert dashes to bullet points
                            formatted_details.append(Paragraph(f"    • {detail[2:]}", normal_style))
                        else:
                            formatted_details.append(Paragraph(detail, normal_style))
                    
                    rec_data = [
                        [Paragraph("Priority:", bold_style), 
                        Paragraph(rec['priority'], normal_style)],
                        [Paragraph("Action:", bold_style), 
                        Paragraph(f"<b>{rec['action']}</b>", normal_style)],
                        [Paragraph("Details:", bold_style), 
                        formatted_details]
                    ]
                    
                    rec_table = Table([[cell] if not isinstance(cell, list) else cell for cell in rec_data], 
                                    colWidths=[120, 350])
                    rec_table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    elements.append(rec_table)
                    elements.append(Spacer(1, 15))
            
            # Add footer with database timestamp
            footer_text = (
                f"Report generated on {report_data['catfish_info']['timestamp']} by LexusBelisario\n"
                f"This report is automatically generated by the Aquaman Monitoring System"
            )
            elements.append(Spacer(1, 20))
            elements.append(Paragraph(footer_text, normal_style))
            
            # Build PDF and convert to base64
            doc.build(elements)
            buffer.seek(0)
            pdf_bytes = buffer.getvalue()
            pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
            
            return {
                "success": True,
                "data": pdf_base64,
                "timestamp": "2025-03-21 15:22:05",
                "reported_by": "LexusBelisario",
                "content_type": "application/pdf",
                "encoding": "base64"
            }
            
        except Exception as e:
            logging.error(f"Error generating PDF report: {str(e)}")
            return {
                "error": True,
                "message": str(e),
                "timestamp": "2025-03-21 15:22:05",
                "reported_by": "LexusBelisario"
            }