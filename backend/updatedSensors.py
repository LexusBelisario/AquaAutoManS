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

device_arduino1 = 'COM8'
device_arduino2 = 'COM9'

try:
    print(f"Trying Arduino 1 on {device_arduino1}...")
    arduino1 = serial.Serial(device_arduino1, 9600)
except serial.SerialException as e:
    print(f"Failed to connect to Arduino 1 on {device_arduino1}: {e}")
    sys.exit(1)

try:
    print(f"Trying Arduino 2 on {device_arduino2}...")
    arduino2 = serial.Serial(device_arduino2, 115200)
except serial.SerialException as e:
    print(f"Failed to connect to Arduino 2 on {device_arduino2}: {e}")
    sys.exit(1)

try:
    while True:
        time.sleep(1)

        try:
            data1 = arduino1.readline().decode('utf-8').strip()
            print(f"Arduino 1 Data: {data1}")
            pieces1 = data1.split()
            if len(pieces1) == 6:
                cursor.execute(
                    "INSERT INTO aquamans (temperature, tempResult, phlevel, phResult, turbidity, turbidityResult) "
                    "VALUES (%s, %s, %s, %s, %s, %s)", 
                    (pieces1[0], pieces1[1], pieces1[2], pieces1[3], pieces1[4], pieces1[5])
                )
                dbConn.commit()
        except serial.SerialException as e:
            print(f"Error reading from Arduino 1: {e}")

        try:
            data2 = arduino2.readline().decode('utf-8').strip()
            print(f"Arduino 2 Data: {data2}")
            pieces2 = data2.split()
            if len(pieces2) == 2:
                cursor.execute(
                    "UPDATE aquamans SET oxygen = %s, oxygenResult = %s WHERE id = (SELECT MAX(id) FROM aquamans)", 
                    (pieces2[0], pieces2[1])
                )
                dbConn.commit()
        except serial.SerialException as e:
            print(f"Error reading from Arduino 2: {e}")

except KeyboardInterrupt:
    print("Terminating...")

finally:
    cursor.close()
    dbConn.close()
    arduino1.close()
    arduino2.close()
