import serial

ser = serial.Serial("COM3", 115200, timeout=1)

print("Listening...")

while True:
    line = ser.readline().decode(errors="ignore").strip()

    if line:
        print("UID:", line)