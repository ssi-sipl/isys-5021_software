import socket
import struct

def calculate_checksum(data, nrOfTargets,bytesPerTarget):
    checksum = 0
    for i in range(nrOfTargets * bytesPerTarget):
        checksum += data[i]
        checksum &= 0xFFFFFFFF
    return checksum

def parse_header(data):
    """
    Parse the 256-byte header and print relevant information.
    """
    header_format = '<HHHHHHIHH118x'  # Define the header structure
    header_size = struct.calcsize(header_format)
    
    if len(data) < header_size:
        print("Incomplete header data.")
        return None  # Return None if header is incomplete
    
    # Unpack the header data
    frame_id, fw_major, fw_fix, fw_minor, detections, targets, checksum, bytes_per_target, data_packets = struct.unpack(
        header_format, data[:header_size]
    )
    
    print(f"Frame ID: {frame_id}")
    print(f"Firmware Version: {fw_major}.{fw_minor}.{fw_fix}")
    print(f"Number of Detections: {detections}")
    print(f"Number of Targets: {targets}")
    print(f"Bytes per Target: {bytes_per_target}")
    print(f"Number of Data Packets: {data_packets}")
    print(f"Checksum: {hex(checksum)}")
    
    # Return the number of targets, data packets, and the checksum for validation
    return targets, data_packets, checksum, bytes_per_target

def parse_targets(data, targets, data_packets):
    """
    Parse the target data from the data packet.
    Skip the entire packet if all targets are empty.
    """
    target_format = '<ffffII'  # Signal Strength, Range, Velocity, Azimuth, Reserved1, Reserved2
    target_size = struct.calcsize(target_format)
    
    offset = 0
    non_empty_targets = False  # Flag to track if there are any non-empty targets in the packet
    print("\nTarget Details:")

    for packet_index in range(data_packets):
        print(f"\nData Packet {packet_index + 1}:")
        packet_non_empty = False  # Flag to track if the current data packet has non-empty targets
        
        for target_index in range(targets // data_packets):
            if offset + target_size > len(data):
                print("Incomplete target data.")
                return
            
            target_data = data[offset:offset + target_size]
            signal_strength, range_, velocity, azimuth, reserved1, reserved2 = struct.unpack(target_format, target_data)

            # Skip empty targets (all zeros)
            if signal_strength == 0 and range_ == 0 and velocity == 0 and azimuth == 0:
                continue  # Skip empty or padded targets
            
            # If we found a non-empty target, we set the flag to true
            packet_non_empty = True
            non_empty_targets = True

            print(f"Target {packet_index * (targets // data_packets) + target_index + 1}: "
                  f"Signal Strength: {signal_strength:.2f} dB, Range: {range_:.2f} m, "
                  f"Velocity: {velocity:.2f} m/s, Azimuth: {azimuth:.2f}°")
            
            offset += target_size
        
        # If the current packet has no non-empty targets, don't print it
        if not packet_non_empty:
            print(f"Data Packet {packet_index + 1} contains only empty targets. Skipping...")

    # If no non-empty targets were found in the entire frame, print a message
    if not non_empty_targets:
        print("All targets in the received packet were empty.")

def process_packet(header_data, data_packet):
    """
    Process a single pair of packets that includes both the header (256 bytes) and data packet (1024 bytes).
    """
    targets, data_packets, expected_checksum, bytes_per_target = parse_header(header_data)
    
    if targets is None:
        return  # If header parsing failed, return
    
    # Calculate the checksum over the received data (header + data packet)
    packet_data = header_data + data_packet  # Concatenate header and data
    calculated_checksum = calculate_checksum(data_packet, targets, bytes_per_target)
    
    # Compare the calculated checksum with the checksum in the header
    if calculated_checksum != expected_checksum:
        print(f"Checksum mismatch: Calculated {calculated_checksum} != Expected {expected_checksum}")
    else:
        print(f"Checksum valid: {calculated_checksum}")

        # Parse the target data from the packet
        parse_targets(data_packet, targets, data_packets)

def main():
    radar_ip = '192.168.252.10'  # IP of the radar device
    radar_port = 2050  # Port for radar data transmission
    local_ip = "127.0.0.1"  # Bind to all available interfaces
    local_port = 2050  # Listening on the same port as the radar

    header_size = 256  # Header packet size
    data_packet_size = 1012  # Data packet size

    max_packet_size = max(header_size, data_packet_size)  # Max size for a single packet

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((local_ip, local_port))
        print(f"Listening on {local_ip}:{local_port}...")
        frame_count = 0

        while True:
            frame_count += 1

            # Receive both header (256 bytes) and data packet (1024 bytes) in sequence
            header_data, addr = sock.recvfrom(header_size)
            print(f"Received header data from {addr}")

            # Receive the corresponding data packet
            data_packet, addr = sock.recvfrom(data_packet_size)
            print(f"Received data packet from {addr}")
            print(f"Packet sizes: Header = {len(header_data)}, Data Packet = {len(data_packet)}")

            # Process the header and data packet
            process_packet(header_data, data_packet)

            print("-" * 50)
            print(f"Total frames received: {frame_count}")

if __name__ == "__main__":
    main()
