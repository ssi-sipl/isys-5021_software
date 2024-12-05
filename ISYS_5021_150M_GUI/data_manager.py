import json

class DataManager:
    def __init__(self):
        self.history = {}

    def save_packet(self, frame_id, targets):
        self.history[frame_id] = targets  # Directly map frame_id to its targets

    def get_by_frame_id(self, frame_id):
        return self.history.get(frame_id)  # Return the list of targets for the frame_id

    def save_to_json(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.history, file, indent=4)

    def load_from_json(self, filename):
        try:
            with open(filename, 'r') as file:
                self.history = json.load(file)
        except FileNotFoundError:
            print("No previous data found.")
