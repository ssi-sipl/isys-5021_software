import socket
import struct
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread

def calculate_checksum(data, nrOfTargets, bytesPerTarget):
    target_list = data[4:]
    checksum = 0
    for i in range(nrOfTargets * bytesPerTarget):
        checksum += target_list[i]
        checksum &= 0xFFFFFFFF
    return checksum

def parse_header(data):
    header_format = '<HHHHHHIHH118x'
    header_size = struct.calcsize(header_format)
    
    if len(data) < header_size:
        return None
    
    frame_id, fw_major, fw_fix, fw_minor, detections, targets, checksum, bytes_per_target, data_packets = struct.unpack(
        header_format, data[:header_size]
    )
    
    return detections, targets, data_packets, checksum, bytes_per_target

def parse_data_packet(data, text_widget):
    target_format = '<ffffII'
    target_size = struct.calcsize(target_format)

    frame_id, number_of_data_packet = struct.unpack('<HH', data[:4])
    target_list = data[4:]
    
    targets = []
    for i in range(42):
        target_data = target_list[i * target_size:(i + 1) * target_size]
        signal_strength, range_, velocity, azimuth, reserved1, reserved2 = struct.unpack(target_format, target_data)
        
        if signal_strength == 0 and range_ == 0 and velocity == 0 and azimuth == 0:
            continue
        
        targets.append({
            'signal_strength': round(signal_strength, 2),
            'range': round(range_, 2),
            'velocity': round(velocity, 2),
            'azimuth': round(azimuth, 2),
        })
    
        if targets:
            text_widget.insert(tk.END, "Serial List:\n")
            text_widget.insert(tk.END, f"{'Serial':<8} {'Signal Strength (dB)':<25} {'Range (m)':<15} {'Velocity (m/s)':<25} {'Direction':<15} {'Azimuth (°)'}\n")
            text_widget.insert(tk.END, "-" * 110 + '\n')
            for idx, target in enumerate(targets, start=1):
                direction = "Static" if target["velocity"] == 0 else "Incoming" if target["velocity"] > 0 else "Outgoing"
                text_widget.insert(
                    tk.END, 
                    f"{idx:<8} {target['signal_strength']:<25} {target['range']:<15} {target['velocity']:<25} {direction:<15} {target['azimuth']}\n"
                )
        else:
            text_widget.insert(tk.END, f"Frame ID: {frame_id}, Data Packet Number: {number_of_data_packet} contains no valid targets.\n")


def process_packet(header_data, data_packet, text_widget):
    parsed_header = parse_header(header_data)
    if parsed_header is None:
        text_widget.insert(tk.END, "Incomplete header data.\n")
        return

    detections, targets, data_packets, expected_checksum, bytes_per_target = parsed_header
    calculated_checksum = calculate_checksum(data_packet, targets, bytes_per_target)
    
    if calculated_checksum != expected_checksum:
        text_widget.insert(tk.END, "Checksum: Not Okay\n")
    else:
        text_widget.insert(tk.END, "Checksum: Okay\n")
        parse_data_packet(data_packet, text_widget)

def start_listening(sock, text_widget, stop_flag):
    header_size = 256
    data_packet_size = 1012
    frame_count = 0

    text_widget.insert(tk.END, "Started Listening...\n")
    while not stop_flag["stop"]:
        try:
            sock.settimeout(1)
            header_data, addr = sock.recvfrom(header_size)
            data_packet, addr = sock.recvfrom(data_packet_size)

            process_packet(header_data, data_packet, text_widget)

            frame_count += 1
            text_widget.insert(tk.END, f"Total frames received: {frame_count}\n")
            text_widget.insert(tk.END, "-" * 50 + '\n')
        except socket.timeout:
            continue
        except OSError:
            break
    text_widget.insert(tk.END, "Stopped Listening...\n")

def run_server(sock, text_widget, stop_flag):
    listening_thread = Thread(target=start_listening, args=(sock, text_widget, stop_flag))
    listening_thread.daemon = True
    listening_thread.start()
    return listening_thread

def main():
    local_ip = "127.0.0.1"
    local_port = 2050

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((local_ip, local_port))

    window = tk.Tk()
    window.title("Radar Data Parser")

    text_widget = scrolledtext.ScrolledText(window, width=120, height=30)
    text_widget.pack(padx=10, pady=10)

    stop_flag = {"stop": False}
    listening_thread = None

    def start():
        nonlocal listening_thread
        if listening_thread is None or not listening_thread.is_alive():
            stop_flag["stop"] = False
            listening_thread = run_server(sock, text_widget, stop_flag)

    def stop():
        stop_flag["stop"] = True
        text_widget.insert(tk.END, "Stopping server...\n")

    start_button = tk.Button(window, text="Start Listening", command=start)
    start_button.pack(pady=5)

    stop_button = tk.Button(window, text="Stop Listening", command=stop)
    stop_button.pack(pady=5)

    window.protocol("WM_DELETE_WINDOW", lambda: (stop(), window.destroy()))

    window.mainloop()

    sock.close()

if __name__ == "__main__":
    main()
