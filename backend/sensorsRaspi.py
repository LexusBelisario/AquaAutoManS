import serial
import mysql.connector  # Import MySQL Connector
import time
import sys

# Establishing a connection to the MySQL database
try:
    dbConn = mysql.connector.connect(
        host="localhost",
        user="admin",
        password="password",  # Set your MySQL password
        database="dbserial"
    )
    cursor = dbConn.cursor()
except mysql.connector.Error as err:
    print(f"Could not connect to database: {err}")
    sys.exit(1)

device = '/dev/ttyUSB0'  # Update for Raspberry Pi

# Establishing a connection to the Arduino
try:
    print("Trying...", device)
    arduino = serial.Serial(device, 9600)
except serial.SerialException as e:
    print(f"Failed to connect on {device}: {e}")
    sys.exit(1)

# Reading data from the Arduino
try:
    while True:
        time.sleep(1)  # Delay to prevent overwhelming the serial port
        raw_data = arduino.readline()  # Read raw bytes
        print(f"Raw data: {raw_data}")  # Print raw bytes for debugging

        # Attempt to decode the data, changing encoding as necessary
        try:
            data = raw_data.decode('utf-8', errors='ignore').strip()
        except UnicodeDecodeError as e:
            print(f"Decoding error: {e}")
            continue  # Skip to the next iteration if decoding fails

        print(f"Received data: {data}")

        pieces = data.split()

        if len(pieces) == 8:
            try:
                cursor.execute(
                    "INSERT INTO aquamans (temperature, tempResult, oxygen, oxygenResult, phlevel, phResult, turbidity, turbidityResult) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (pieces[0], pieces[1], pieces[2], pieces[3], pieces[4], pieces[5], pieces[6], pieces[7])
                )
                dbConn.commit()
            except mysql.connector.IntegrityError as err:
                print(f"Failed to insert data: {err}")
        else:
            print("Unexpected data format")


except KeyboardInterrupt:
    print("Terminating...")

finally:
    cursor.close()
    dbConn.close()
    arduino.close()
