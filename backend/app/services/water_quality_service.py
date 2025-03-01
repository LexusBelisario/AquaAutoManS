# app/services/water_quality_service.py
from flask import jsonify, send_file
from app.models import aquamans
from app import db
from datetime import datetime, timedelta
import logging
from io import BytesIO
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.pdfgen import canvas
from app import db

class WaterQualityService:
    def __init__(self):
        self.parameter_thresholds = {
            'temperature': {
                'critical_low': 15,
                'warning_low': 20,
                'normal_low': 26,
                'normal_high': 32,
                'warning_high': 35,
                'critical_high': 38
            },
            'oxygen': {
                'critical_low': 0.8,
                'warning_low': 1.5,
                'normal_low': 5.0,
                'normal_high': 7.0,
                'warning_high': 8.0,
                'critical_high': 10.0
            },
            'ph': {
                'critical_low': 4.0,
                'warning_low': 6.0,
                'normal_low': 6.5,
                'normal_high': 7.5,
                'warning_high': 8.5,
                'critical_high': 9.0
            },
            'turbidity': {
                'normal': 20,
                'warning': 50,
                'critical': 100
            }
        }

    def check_water_quality(self):
        try:
            # Get latest record
            latest_record = aquamans.query.order_by(aquamans.timeData.desc()).first()
            if not latest_record:
                return jsonify({"message": "No data available"})

            # Get historical data for trend analysis
            three_hours_ago = latest_record.timeData - timedelta(hours=3)
            historical_data = (
                aquamans.query
                .filter(aquamans.timeData >= three_hours_ago)
                .order_by(aquamans.timeData)
                .all()
            )

            # Analyze trends and calculate status
            analysis = self._analyze_parameters(latest_record, historical_data)
            
            return jsonify({
                "alert": "Water Quality Status Update",
                "details": {
                    "alert_id": f"wq_{latest_record.id}",
                    "time_detected": latest_record.timeData.strftime("%Y-%m-%d %H:%M:%S"),
                    "all_parameters_normal": analysis['all_normal'],
                    "alive_catfish": latest_record.catfish,
                    "priority_level": analysis['priority_level'],
                    
                    # Current readings with trends
                    "temperature": latest_record.temperature,
                    "temperature_status": analysis['temperature']['status'],
                    "temperature_trend": analysis['temperature']['trend'],
                    
                    "oxygen": latest_record.oxygen,
                    "oxygen_status": analysis['oxygen']['status'],
                    "oxygen_trend": analysis['oxygen']['trend'],
                    
                    "phlevel": latest_record.phlevel,
                    "phlevel_status": analysis['ph']['status'],
                    "ph_trend": analysis['ph']['trend'],
                    
                    "turbidity": latest_record.turbidity,
                    "turbidity_status": analysis['turbidity']['status'],
                    "turbidity_trend": analysis['turbidity']['trend'],

                    # Historical data for graphs
                    "temperature_history": self._format_historical_data(historical_data, 'temperature'),
                    "oxygen_history": self._format_historical_data(historical_data, 'oxygen'),
                    "ph_history": self._format_historical_data(historical_data, 'phlevel'),
                    "turbidity_history": self._format_historical_data(historical_data, 'turbidity'),

                    # Detailed analysis
                    "parameter_analysis": analysis['detailed_analysis'],
                    "detected_issues": analysis['issues'],
                    "recommendations": analysis['recommendations'],
                    "monitoring_schedule": self._get_monitoring_schedule(analysis['priority_level']),
                    
                    # Predictions
                    "predictions": self._generate_predictions(historical_data),
                    
                    # Correlations
                    "parameter_correlations": self._calculate_correlations(historical_data)
                }
            })

        except Exception as e:
            logging.error(f"Error checking water quality: {e}")
            return jsonify({'error': str(e)})

    def _analyze_parameters(self, latest_record, historical_data):
        analysis = {
            'all_normal': True,
            'priority_level': 'Normal',
            'issues': [],
            'recommendations': [],
            'detailed_analysis': []
        }

        # Analyze each parameter
        params = {
            'temperature': latest_record.temperature,
            'oxygen': latest_record.oxygen,
            'ph': latest_record.phlevel,
            'turbidity': latest_record.turbidity
        }

        for param, value in params.items():
            param_analysis = self._analyze_single_parameter(param, value, historical_data)
            analysis[param] = param_analysis
            
            if param_analysis['severity'] != 'normal':
                analysis['all_normal'] = False
                analysis['issues'].append(param_analysis['issue'])
                analysis['recommendations'].extend(param_analysis['recommendations'])
                analysis['detailed_analysis'].append({
                    'severity': param_analysis['severity'],
                    'message': param_analysis['message']
                })

        # Determine overall priority level
        if any(p['severity'] == 'critical' for p in analysis['detailed_analysis']):
            analysis['priority_level'] = 'Critical'
        elif any(p['severity'] == 'warning' for p in analysis['detailed_analysis']):
            analysis['priority_level'] = 'Warning'

        return analysis

    def _analyze_single_parameter(self, param, value, historical_data):
        thresholds = self.parameter_thresholds[param]
        
        # Calculate trend
        trend = self._calculate_trend(historical_data, param)
        
        # Determine status and severity
        status, severity = self._get_parameter_status(param, value)
        
        # Generate specific recommendations
        recommendations = self._generate_recommendations(param, value, status, trend)
        
        return {
            'status': status,
            'severity': severity,
            'trend': trend,
            'issue': f"{param.title()} is {status.lower()}",
            'message': f"{param.title()} reading of {value} is {status.lower()}",
            'recommendations': recommendations
        }

    def _calculate_trend(self, historical_data, param):
        if len(historical_data) < 2:
            return "→"
            
        values = [getattr(record, param) for record in historical_data[-5:]]
        slope = np.polyfit(range(len(values)), values, 1)[0]
        
        if abs(slope) < 0.1:
            return "→"
        return "↑" if slope > 0 else "↓"

    def _generate_predictions(self, historical_data):
        predictions = {}
        for param in ['temperature', 'oxygen', 'phlevel', 'turbidity']:
            values = [getattr(record, param) for record in historical_data]
            times = [(record.timeData - historical_data[0].timeData).total_seconds() / 3600 
                    for record in historical_data]
            
            if len(values) > 1:
                model = LinearRegression()
                X = np.array(times).reshape(-1, 1)
                y = np.array(values)
                model.fit(X, y)
                
                # Predict next 6 hours
                future_hours = np.array(range(max(times) + 1, max(times) + 7)).reshape(-1, 1)
                predictions[param] = model.predict(future_hours).tolist()
            else:
                predictions[param] = []
                
        return predictions

    def _calculate_correlations(self, historical_data):
        if len(historical_data) < 2:
            return {}
            
        df = pd.DataFrame([{
            'temperature': record.temperature,
            'oxygen': record.oxygen,
            'ph': record.phlevel,
            'turbidity': record.turbidity
        } for record in historical_data])
        
        return df.corr().to_dict()

    def _format_historical_data(self, historical_data, parameter):
        return {
            'labels': [record.timeData.strftime("%H:%M") for record in historical_data],
            'datasets': [{
                'label': parameter.title(),
                'data': [getattr(record, parameter) for record in historical_data],
                'borderColor': 'rgb(75, 192, 192)',
                'tension': 0.1
            }]
        }

    def _get_parameter_status(self, param, value):
        thresholds = self.parameter_thresholds[param]
        
        if param != 'turbidity':
            if value <= thresholds['critical_low'] or value >= thresholds['critical_high']:
                return 'Critical', 'critical'
            elif value <= thresholds['warning_low'] or value >= thresholds['warning_high']:
                return 'Warning', 'warning'
            elif thresholds['normal_low'] <= value <= thresholds['normal_high']:
                return 'Normal', 'normal'
            else:
                return 'Abnormal', 'warning'
        else:
            if value >= thresholds['critical']:
                return 'Critical', 'critical'
            elif value >= thresholds['warning']:
                return 'Warning', 'warning'
            else:
                return 'Normal', 'normal'

    def _generate_recommendations(self, param, value, status, trend):
        recommendations = []
        
        if status == 'Critical':
            recommendations.append(f"URGENT: Immediate action required for {param}")
            
            if param == 'temperature':
                if value > self.parameter_thresholds[param]['critical_high']:
                    recommendations.extend([
                        "Activate emergency cooling system",
                        "Add shade covers to reduce sun exposure",
                        "Consider partial water exchange with cooler water"
                    ])
                else:
                    recommendations.extend([
                        "Activate water heaters",
                        "Check for cold water inflow",
                        "Insulate exposed pipes"
                    ])
                    
            elif param == 'oxygen':
                if value < self.parameter_thresholds[param]['critical_low']:
                    recommendations.extend([
                        "Increase aeration immediately",
                        "Add emergency oxygen supply",
                        "Reduce feeding temporarily",
                        "Check for equipment malfunction"
                    ])
                    
            elif param == 'ph':
                if value < self.parameter_thresholds[param]['critical_low']:
                    recommendations.extend([
                        "Add pH buffer to increase alkalinity",
                        "Check for acid contamination",
                        "Prepare for partial water exchange"
                    ])
                else:
                    recommendations.extend([
                        "Add pH buffer to decrease alkalinity",
                        "Check for alkaline contamination",
                        "Prepare for partial water exchange"
                    ])
                    
            elif param == 'turbidity':
                recommendations.extend([
                    "Activate emergency filtration",
                    "Check for system malfunction",
                    "Prepare for immediate water exchange",
                    "Stop feeding temporarily"
                ])

        elif status == 'Warning':
            recommendations.append(f"Important: Monitor {param} closely")
            
            if trend == "↑":
                recommendations.append(f"Monitor increasing trend in {param}")
            elif trend == "↓":
                recommendations.append(f"Monitor decreasing trend in {param}")

        return recommendations

    def _get_monitoring_schedule(self, priority_level):
        schedules = {
            'Critical': {
                'parameter_checking': 'Every 5 minutes',
                'water_sampling': 'Every 30 minutes',
                'equipment_inspection': 'Every hour',
                'catfish_observation': 'Continuous monitoring'
            },
            'Warning': {
                'parameter_checking': 'Every 15 minutes',
                'water_sampling': 'Every 2 hours',
                'equipment_inspection': 'Every 4 hours',
                'catfish_observation': 'Every 30 minutes'
            },
            'Normal': {
                'parameter_checking': 'Every 30 minutes',
                'water_sampling': 'Every 4 hours',
                'equipment_inspection': 'Every 8 hours',
                'catfish_observation': 'Every hour'
            }
        }
        return schedules.get(priority_level, schedules['Normal'])

    def _analyze_trends_detailed(self, historical_data):
        """Analyze detailed trends including rate of change and patterns"""
        trend_analysis = {}
        
        for param in ['temperature', 'oxygen', 'phlevel', 'turbidity']:
            values = [getattr(record, param) for record in historical_data]
            times = [(record.timeData - historical_data[0].timeData).total_seconds() / 3600 
                    for record in historical_data]
            
            if len(values) > 1:
                # Calculate rate of change
                rate_of_change = (values[-1] - values[0]) / (times[-1] - times[0])
                
                # Calculate acceleration (change in rate of change)
                if len(values) > 2:
                    half_point = len(values) // 2
                    first_half_rate = (values[half_point] - values[0]) / (times[half_point] - times[0])
                    second_half_rate = (values[-1] - values[half_point]) / (times[-1] - times[half_point])
                    acceleration = second_half_rate - first_half_rate
                else:
                    acceleration = 0

                trend_analysis[param] = {
                    'rate_of_change': rate_of_change,
                    'acceleration': acceleration,
                    'pattern': self._detect_pattern(values),
                    'stability': self._calculate_stability(values)
                }

        return trend_analysis

    def _detect_pattern(self, values):
        """Detect patterns in the data (cyclic, steady, erratic)"""
        if len(values) < 3:
            return "insufficient_data"
            
        # Calculate differences between consecutive values
        differences = np.diff(values)
        
        # Check for cyclic pattern
        if len(values) >= 6:
            autocorr = np.correlate(differences, differences, mode='full')
            if np.any(autocorr[len(differences)+1:] > 0.7 * autocorr[len(differences)]):
                return "cyclic"
                
        # Check for stability
        if np.std(differences) < 0.1 * np.mean(np.abs(values)):
            return "steady"
            
        # Check for erratic behavior
        if np.std(differences) > 0.5 * np.mean(np.abs(values)):
            return "erratic"
            
        return "gradual_change"

    def _calculate_stability(self, values):
        """Calculate stability score (0-1, where 1 is most stable)"""
        if len(values) < 2:
            return 1.0
            
        std_dev = np.std(values)
        mean_val = np.mean(np.abs(values))
        
        if mean_val == 0:
            return 1.0
            
        stability = 1.0 - min(1.0, std_dev / mean_val)
        return round(stability, 2)

    def print_water_quality_report(self, alert_id):
        """Generate detailed PDF report for water quality"""
        try:
            # Implementation similar to print_dead_catfish_report but focused on water quality
            # Would you like to see this implementation as well?
            pass
            
        except Exception as e:
            logging.error(f"Error generating water quality report: {e}")
            return jsonify({"error": str(e)})
        
    def print_water_quality_report(self, alert_id):
            try:
                # Get the data for the report
                latest_record = aquamans.query.get(alert_id.replace('wq_', ''))
                if not latest_record:
                    return jsonify({"message": "No data found for this alert."})

                # Get historical data
                three_hours_ago = latest_record.timeData - timedelta(hours=3)
                historical_data = (
                    aquamans.query
                    .filter(aquamans.timeData >= three_hours_ago)
                    .order_by(aquamans.timeData)
                    .all()
                )

                # Analyze data
                analysis = self._analyze_parameters(latest_record, historical_data)
                trend_analysis = self._analyze_trends_detailed(historical_data)
                correlations = self._calculate_correlations(historical_data)
                predictions = self._generate_predictions(historical_data)

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
                normal_style = ParagraphStyle(
                    'CustomNormal',
                    parent=styles['Normal'],
                    fontSize=10,
                    leading=12
                )
                warning_style = ParagraphStyle(
                    'WarningStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    textColor=colors.red,
                    leading=14
                )

                # Create story for PDF
                story = []

                # Add title and timestamp
                story.append(Paragraph("Water Quality Analysis Report", title_style))
                story.append(Paragraph(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    normal_style
                ))
                story.append(Spacer(1, 20))

                # Add current readings table
                current_readings = [
                    ["Parameter", "Current Value", "Status", "Trend", "Normal Range"],
                    ["Temperature", f"{latest_record.temperature:.1f}°C", 
                    analysis['temperature']['status'], analysis['temperature']['trend'],
                    f"{self.parameter_thresholds['temperature']['normal_low']}-"
                    f"{self.parameter_thresholds['temperature']['normal_high']}°C"],
                    ["Oxygen", f"{latest_record.oxygen:.2f} mg/L",
                    analysis['oxygen']['status'], analysis['oxygen']['trend'],
                    f"{self.parameter_thresholds['oxygen']['normal_low']}-"
                    f"{self.parameter_thresholds['oxygen']['normal_high']} mg/L"],
                    ["pH Level", f"{latest_record.phlevel:.2f}",
                    analysis['ph']['status'], analysis['ph']['trend'],
                    f"{self.parameter_thresholds['ph']['normal_low']}-"
                    f"{self.parameter_thresholds['ph']['normal_high']}"],
                    ["Turbidity", f"{latest_record.turbidity:.1f} NTU",
                    analysis['turbidity']['status'], analysis['turbidity']['trend'],
                    f"< {self.parameter_thresholds['turbidity']['warning']} NTU"]
                ]

                story.append(Paragraph("Current Readings", heading2_style))
                table = Table(current_readings, colWidths=[100, 100, 100, 50, 100])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(table)
                story.append(Spacer(1, 20))

                # Add trend analysis
                story.append(Paragraph("Trend Analysis", heading2_style))
                for param, analysis in trend_analysis.items():
                    story.append(Paragraph(
                        f"<b>{param.title()}</b>",
                        normal_style
                    ))
                    story.append(Paragraph(
                        f"• Rate of change: {analysis['rate_of_change']:.2f} units/hour",
                        normal_style
                    ))
                    story.append(Paragraph(
                        f"• Pattern: {analysis['pattern'].replace('_', ' ').title()}",
                        normal_style
                    ))
                    story.append(Paragraph(
                        f"• Stability score: {analysis['stability']}",
                        normal_style
                    ))
                    story.append(Spacer(1, 10))

                story.append(PageBreak())

                # Add predictions
                story.append(Paragraph("Predictions (Next 6 Hours)", heading2_style))
                for param, pred_values in predictions.items():
                    if pred_values:
                        pred_data = [
                            ["Hour", "Predicted Value", "Status"],
                            *[(f"+{i+1}h", f"{value:.2f}", 
                            self._get_parameter_status(param, value)[0])
                            for i, value in enumerate(pred_values)]
                        ]
                        
                        story.append(Paragraph(f"{param.title()} Predictions:", normal_style))
                        pred_table = Table(pred_data, colWidths=[80, 100, 100])
                        pred_table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ]))
                        story.append(pred_table)
                        story.append(Spacer(1, 15))

                # Add recommendations
                story.append(Paragraph("Recommendations", heading2_style))
                for rec in analysis['recommendations']:
                    story.append(Paragraph(f"• {rec}", normal_style))
                story.append(Spacer(1, 20))

                # Add monitoring schedule
                story.append(Paragraph("Monitoring Schedule", heading2_style))
                schedule = self._get_monitoring_schedule(analysis['priority_level'])
                schedule_data = [[k.replace('_', ' ').title(), v] for k, v in schedule.items()]
                schedule_table = Table([["Task", "Frequency"]] + schedule_data, colWidths=[200, 200])
                schedule_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))
                story.append(schedule_table)

                # Build PDF
                doc.build(story)
                buffer.seek(0)

                return send_file(
                    buffer,
                    as_attachment=True,
                    download_name=f"water_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mimetype="application/pdf"
                )

            except Exception as e:
                logging.error(f"Error generating water quality report: {e}")
                return jsonify({"error": str(e)})