import socket
import struct
import random
import time

def calculate_checksum(data):
    checksum = 0
    for byte in data:
        checksum += byte
        checksum &= 0xFFFFFFFF  # Ensure it fits within 32-bit boundary
    return checksum

def generate_header(frame_id, fw_version, detections, targets, bytes_per_target, data_packets, checksum):
    fw_major, fw_minor, fw_fix = fw_version
    header_format = '<HHHHHHIHH118x'
    header = struct.pack(
        header_format,
        frame_id, fw_major, fw_fix, fw_minor,
        detections, targets, checksum,
        bytes_per_target, data_packets
    )
    return header

def generate_data_packet(targets, bytes_per_target):
    target_format = '<ffffII'  # Signal Strength, Range, Velocity, Azimuth, Reserved1, Reserved2
    target_size = struct.calcsize(target_format)
    data = b''
    
    target_values = []  # Store unpacked target values for printing
    for _ in range(targets):
        signal_strength = round(random.uniform(0.0, 100.0), 2)
        range_ = round(random.uniform(0.0, 200.0), 2)
        velocity = round(random.uniform(-20.0, 20.0), 2)
        azimuth = round(random.uniform(0.0, 360.0), 2)
        reserved1, reserved2 = 0, 0
        target = struct.pack(target_format, signal_strength, range_, velocity, azimuth, reserved1, reserved2)
        data += target
        target_values.append((signal_strength, range_, velocity, azimuth, reserved1, reserved2))
    
    # Add padding if necessary
    padding_size = (targets * bytes_per_target) - len(data)
    if padding_size > 0:
        data += b'\x00' * padding_size

    return data, target_values

def main():
    server_ip = '127.0.0.1'
    server_port = 2050
    header_size = 256
    bytes_per_target = 24
    data_packet_size = 1012
    targets_per_packet = data_packet_size // bytes_per_target

    frame_id = 1
    fw_version = (1, 0, 0)  # Major, Minor, Fix
    detections = 5  # Arbitrary number of detections
    data_packets = 1

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        print(f"Test server running on {server_ip}:{server_port}...")
        
        while True:
            # Generate target data dynamically
            targets = random.randint(1, targets_per_packet)
            data_packet, target_values = generate_data_packet(targets, bytes_per_target)
            
            # Calculate checksum
            checksum = calculate_checksum(data_packet)
            
            # Generate header
            header = generate_header(frame_id, fw_version, detections, targets, bytes_per_target, data_packets, checksum)
            
            # Print header and data packet values
            print(f"\nFrame ID: {frame_id}")
            print(f"Header: Firmware Version: {fw_version}, Detections: {detections}, Targets: {targets}, Bytes/Target: {bytes_per_target}, Data Packets: {data_packets}, Checksum: {checksum}")
            print("Data Packet:")
            for index, target in enumerate(target_values, start=1):
                print(f"  Target {index}: Signal Strength: {target[0]:.2f} dB, Range: {target[1]:.2f} m, "
                      f"Velocity: {target[2]:.2f} m/s, Azimuth: {target[3]:.2f}°, Reserved1: {target[4]}, Reserved2: {target[5]}")
            
            # Send header and data packet
            server_socket.sendto(header, (server_ip, server_port))
            time.sleep(0.1)  # Short delay to simulate real-time behavior
            server_socket.sendto(data_packet, (server_ip, server_port))
            
            print(f"Frame {frame_id} sent")
            frame_id += 1
            time.sleep(1)  # Delay to mimic radar's frame interval

if __name__ == "__main__":
    main()
