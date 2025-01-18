import serial
import MySQLdb
import time
import sys

try:
    dbConn = MySQLdb.connect(host="localhost", user="root", passwd="", db="dbserial")
    cursor = dbConn.cursor()
except MySQLdb.Error as err:
    print(f"Could not connect to database: {err}")
    sys.exit(1)

device = 'COM9' 

try:
    print("Trying...", device)
    arduino = serial.Serial(device, 115200)
except serial.SerialException as e:
    print(f"Failed to connect on {device}: {e}")
    sys.exit(1)

try:
    while True:
        try:
            time.sleep(1) 
            data = arduino.readline().decode('utf-8').strip()
            print(f"Received data: {data}")

            pieces = data.split()

            if len(pieces) == 8:  
                try:
                    cursor.execute("INSERT INTO aquamans (temperature, tempResult, oxygen, oxygenResult, phlevel, phResult, turbidity, turbidityResult) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                                   (pieces[0], pieces[1], pieces[2], pieces[3], pieces[4], pieces[5], pieces[6], pieces[7]))
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