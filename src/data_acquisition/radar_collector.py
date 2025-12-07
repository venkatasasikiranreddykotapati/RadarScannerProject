import serial
import time
import os

def collect_radar_data(port='COM6', baudrate=115200, output_file=None, duration=None):
    """
    Connects to a specified serial port, reads incoming data, and prints it to the console.
    Optionally saves the raw data to a file.

    Args:
        port (str): The serial port to connect to (e.g., 'COM6', '/dev/ttyUSB0').
        baudrate (int): The baud rate for serial communication.
        output_file (str, optional): Path to a file to save the raw collected data.
        duration (int, optional): Duration in seconds to collect data. If None, collects indefinitely.
    """
    ser = None
    f = None # Initialize f to None
    try:
        print(f"Attempting to open serial port {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate, timeout=1) # 1-second timeout
        ser = serial.Serial('COM6', baudrate=115200, timeout=1) # 1-second timeout
        print(f"Successfully opened serial port {port}.")

        if output_file:
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
            f = open(output_file, 'wb') # Open in binary write mode
            print(f"Saving raw data to {output_file}")
        else:
            f = None

        start_time = time.time()
        while True:
            if duration and (time.time() - start_time > duration):
                print(f"Collection duration of {duration} seconds reached. Stopping.")
                break

            if ser.in_waiting > 0:
                # Read all available bytes
                data = ser.read(ser.in_waiting)
                
                # Print raw bytes (hex representation) and also try to decode as ASCII for readability
                print(f"Received ({len(data)} bytes): {data.hex()} | ASCII: {data.decode('ascii', errors='ignore')}")
                
                if f:
                    f.write(data)
            else:
                print("Waiting for data...", end='\r') # Indicate waiting without new line
                time.sleep(0.01) # Small delay to prevent busy-waiting

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
    finally:
        if ser and ser.is_open:
            ser.close()
            print(f"Serial port {port} closed.")
        if f:
            f.close()

if __name__ == "__main__":
    # Example usage:
    # To collect data for 10 seconds and save to a file:
    # collect_radar_data(port='COM6', baudrate=115200, output_file='raw_radar_data.bin', duration=10)
    
    # To collect data indefinitely and print to console:
    collect_radar_data(port='COM6', baudrate=115200)
