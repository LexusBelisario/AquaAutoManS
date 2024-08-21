import serial
import MySQLdb
import time
import sys

# Connect to the MySQL database
try:
    dbConn = MySQLdb.connect(host="localhost", user="root", passwd="", db="dbserial")
    cursor = dbConn.cursor()
except MySQLdb.Error as err:
    print(f"Could not connect to database: {err}")
    sys.exit(1)

device = 'COM4'  # Change this to your actual serial port

try:
    print("Trying...", device)
    arduino = serial.Serial(device, 9600)
except serial.SerialException as e:
    print(f"Failed to connect on {device}: {e}")
    sys.exit(1)

try:
    while True:
        try:
            time.sleep(1)  # Wait for the connection to stabilize
            data = arduino.readline().decode('utf-8').strip()  # Ensure data is decoded and stripped of newlines
            print(f"Received data: {data}")

            # Assuming data is space-separated, like "23.4 7.8 6.5 3.2"
            pieces = data.split()

            if len(pieces) == 4:  # Ensure you have exactly 4 pieces of data
                try:
                    cursor.execute("INSERT INTO aquamans (temperature, oxygen, phlevel, turbidity) VALUES (%s, %s, %s, %s)", 
                                   (pieces[0], pieces[1], pieces[2], pieces[3]))
                    dbConn.commit()
                except MySQLdb.IntegrityError as err:
                    print(f"Failed to insert data: {err}")
            else:
                print("Unexpected data format")

        except serial.SerialException as e:
            print(f"Error reading from serial port: {e}")
        except MySQLdb.Error as err:
            print(f"Database error: {err}")

except KeyboardInterrupt:
    print("Terminating...")

finally:
    cursor.close()
    dbConn.close()
    arduino.close()
