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
        self.socket_manager = SocketManager("127.0.0.1", 2050, self.process_data)
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
        frame_id = self.frame_id_var.get()
        serials = self.data_manager.get_by_frame_id(frame_id)
        self.clear_display()
        for serial in serials:
            self.text_display.insert(tk.END, f"{serial}\n")

    def process_data(self, header_data, data_packet):
        # Parse header
        frame_id, *_ = struct.unpack('<HHHHHHIHH118x', header_data[:256])
        # Parse data packet and collect serials (mocked here)
        serials = [f"Serial {i}" for i in range(5)]  # Replace with real parsing logic
        self.data_manager.save_packet(frame_id, serials)

        # Update dropdown with new frame ID
        self.frame_id_dropdown['values'] = list(self.data_manager.history.keys())

    def run(self):
        self.root.mainloop()
