from flask import Flask, request, jsonify, render_template_string
from datetime import datetime, timedelta, timezone
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

# Initialize Flask app
app = Flask(__name__)

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "mithran07.mv@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "mebs vpqj cphx ttsz".replace("\xa0", " ")  # Replace with your app-specific password

# File to store pressure data
DATA_FILE = "pressure_data.json"

# Function to save data to JSON file
def save_to_file(data):
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            file_data = json.load(file)
    else:
        file_data = []

    file_data.append(data)

    with open(DATA_FILE, 'w') as file:
        json.dump(file_data, file, indent=4)

# Function to send warning email
def send_warning_email():
    subject = "WARNING: Gas Leakage Detected"
    body = """
    A potential gas leakage has been detected.
    Please check the system immediately.
    """

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = "vloginnovations@gmail.com"
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, "vloginnovations@gmail.com", msg.as_string())
            print("Warning email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Helper function to get current time in IST
def get_current_ist_time():
    ist = timezone(timedelta(hours=5, minutes=30))
    return datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

# Route to monitor pressure status
@app.route('/monitor', methods=['GET'])
def monitor_pressure():
    try:
        status = int(request.args.get('status'))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid 'status' parameter. Must be 0 or 1."}), 400

    # Prepare data point
    data_point = {
        "timestamp": get_current_ist_time(),
        "status": "Leaking" if status == 1 else "Safe"
    }

    # Save data to file
    save_to_file(data_point)

    # If status is 1, send warning email
    if status == 1:
        send_warning_email()

    # Return response
    return jsonify(data_point)

# Route to display dashboard
@app.route('/dashboard', methods=['GET'])
def dashboard():
    # Load pressure data from file
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as file:
            pressure_data = json.load(file)
    else:
        pressure_data = []

    dashboard_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gas Leakage Monitoring Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f7f9fc;
                color: #333;
            }
            header {
                background-color: #007bff;
                color: white;
                padding: 15px 20px;
                text-align: center;
                font-size: 24px;
            }
            footer {
                background-color: #007bff;
                color: white;
                text-align: center;
                padding: 10px;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
            .container {
                padding: 20px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                background-color: white;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: center;
            }
            th {
                background-color: #007bff;
                color: white;
            }
            .safe {
                background-color: #d4edda;
                color: #155724;
                font-weight: bold;
            }
            .leaking {
                background-color: #f8d7da;
                color: #721c24;
                font-weight: bold;
            }
            .status-safe {
                display: inline-block;
                background-color: #28a745;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 14px;
            }
            .status-leaking {
                display: inline-block;
                background-color: #dc3545;
                color: white;
                padding: 5px 10px;
                border-radius: 5px;
                font-size: 14px;
            }
        </style>
        <script>
            // Auto-reload the page every 10 seconds
            setInterval(() => {
                window.location.reload();
            }, 10000); // 10000 milliseconds = 10 seconds
        </script>
    </head>
    <body>
        <header>
            Gas Leakage Monitoring Dashboard
        </header>
        <div class="container">
            <h2>Monitoring Data</h2>
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for entry in data %}
                        <tr class="{{ 'safe' if entry['status'] == 'Safe' else 'leaking' }}">
                            <td>{{ entry['timestamp'] }}</td>
                            <td>
                                <span class="{{ 'status-safe' if entry['status'] == 'Safe' else 'status-leaking' }}">
                                    {{ entry['status'] }}
                                </span>
                            </td>
                        </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        <footer>
            &copy; 2024 Gas Leakage Monitoring System | All Rights Reserved
        </footer>
    </body>
    </html>
    """
    return render_template_string(dashboard_html, data=pressure_data)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
