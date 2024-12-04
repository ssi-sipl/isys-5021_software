import tkinter as tk
from tkinter import ttk, filedialog
from socket_manager import SocketManager
from data_manager import DataManager
import struct

class RadarApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Radar GUI")
        self.data_manager = DataManager()
        self.socket_manager = SocketManager("192.168.252.2", 2050, self.process_data)
        self.build_gui()

    def build_gui(self):
        # Connect/Disconnect Button
        self.connect_btn = tk.Button(self.root, text="Connect", command=self.toggle_connection)
        self.connect_btn.pack()

        # Clear Button
        self.clear_btn = tk.Button(self.root, text="Clear", command=self.clear_display)
        self.clear_btn.pack()

        # Save JSON Button
        self.save_btn = tk.Button(self.root, text="Save to JSON", command=self.save_to_json)
        self.save_btn.pack()

        # Frame ID Dropdown
        self.frame_id_var = tk.StringVar()
        self.frame_id_dropdown = ttk.Combobox(self.root, textvariable=self.frame_id_var)
        self.frame_id_dropdown.bind("<<ComboboxSelected>>", self.display_by_frame_id)
        self.frame_id_dropdown.pack()

        # Data Display
        self.text_display = tk.Text(self.root, height=20, width=80)
        self.text_display.pack()

    def toggle_connection(self):
        if self.socket_manager.is_connected():
            self.socket_manager.disconnect()
            self.connect_btn.config(text="Connect")
        else:
            self.socket_manager.connect()
            self.connect_btn.config(text="Disconnect")

    def clear_display(self):
        self.text_display.delete(1.0, tk.END)

    def save_to_json(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            self.data_manager.save_to_json(filename)

    def display_by_frame_id(self, event):
        # Get the selected frame ID
        frame_id = self.frame_id_var.get()

        # Retrieve serials for the selected frame ID from the data manager
        serials = self.data_manager.get_by_frame_id(frame_id)

        # Clear the text area before displaying new data
        self.clear_display()

        if serials:
            # Display serial data for the selected frame ID
            self.text_display.insert(tk.END, f"Serial Data for Frame ID: {frame_id}\n")
            self.text_display.insert(tk.END, "-" * 50 + "\n")
            for serial in serials:
                for idx, target in enumerate(serial, start=1):
                    direction = "Static" if target["velocity"] == 0 else "Incoming" if target["velocity"] > 0 else "Outgoing"
                    self.text_display.insert(tk.END, f"Serial {idx}: "
                                                     f"Signal Strength: {target['signal_strength']} dB, "
                                                     f"Range: {target['range']} m, "
                                                     f"Velocity: {target['velocity']} m/s, "
                                                     f"Direction: {direction}, "
                                                     f"Azimuth: {target['azimuth']}°\n")
                self.text_display.insert(tk.END, "-" * 50 + "\n")
        else:
            self.text_display.insert(tk.END, "No serial data available for this Frame ID.\n")

    def process_data(self, header_data, data_packet):
        frame_id, targets = self.socket_manager.process_packet(header_data, data_packet)
        
        if not targets:
            return  # If no valid targets, return
        
        # Add parsed targets to the data manager and update the dropdown list
        self.data_manager.save_packet(frame_id, targets)
        self.frame_id_dropdown['values'] = list(self.data_manager.history.keys())
        
        # Optionally update the GUI with parsed targets for the current frame
        self.clear_display()
        for idx, target in enumerate(targets, start=1):
            direction = "Static" if target["velocity"] == 0 else "Incoming" if target["velocity"] > 0 else "Outgoing"
            self.text_display.insert(tk.END, f"Serial {idx}: "
                                             f"Signal Strength: {target['signal_strength']} dB, "
                                             f"Range: {target['range']} m, "
                                             f"Velocity: {target['velocity']} m/s, "
                                             f"Direction: {direction}, "
                                             f"Azimuth: {target['azimuth']}°\n")

    def run(self):
        self.root.mainloop()
