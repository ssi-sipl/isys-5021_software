import socket
import struct

def parse_radar_data(data):
    header_format = '<HHHHHHIHH118x'
    header_size = struct.calcsize(header_format)
    
    if len(data) < header_size:
        print("Incomplete header data.")
        return
    
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
    
    target_format = '<ffffII'
    target_size = struct.calcsize(target_format)
    
    offset = header_size
    print("\nTarget Details:")
    
    for packet_index in range(data_packets):
        print(f"\nData Packet {packet_index + 1}:")
        for target_index in range(targets // data_packets):
            if offset + target_size > len(data):
                print("Incomplete target data.")
                return
            
            target_data = data[offset:offset + target_size]
            signal_strength, range_, velocity, azimuth, reserved1, reserved2 = struct.unpack(target_format, target_data)
            
            print(f"Target {packet_index * (targets // data_packets) + target_index + 1}: "
                  f"Signal Strength: {signal_strength:.2f} dB, Range: {range_:.2f} m, "
                  f"Velocity: {velocity:.2f} m/s, Azimuth: {azimuth:.2f}°")
            
            offset += target_size

def parse_radar_packet(data):
    ethernet_header_size = 14
    ipv4_header_size = 20
    udp_header_size = 8

    total_protocol_headers = ethernet_header_size + ipv4_header_size + udp_header_size

    if len(data) <= total_protocol_headers:
        print("Packet too short to include protocol headers and payload.")
        return

    radar_payload = data[total_protocol_headers:]
    parse_radar_data(radar_payload)

def main():
    radar_ip = '127.0.0.1'
   
    #workstation_ip='192.168.252.2'
    radar_port = 2050
    local_ip = "192.168.252.2"  # Change to the IP address you want to bind
    local_port = 2050  # Port 2050 as per your setup

    max_packet_size = 7370 + 42

    
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind((local_ip, local_port))
        print(f"Listening on {local_ip}:{local_port}...")
        frame_count = 0

        while True:
            frame_count+=1
            data, addr = sock.recvfrom(max_packet_size)
            print(f"Packet size: {len(data)}")
            print(f"Data: {data}")
            # print(f"Received data from {addr}")
            # parse_radar_packet(data)
            # print("-" * 50)
            # print(f"Total frames recieved: {frame_count}")

if __name__ == "__main__":
    main()
