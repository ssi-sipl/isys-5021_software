import json

class DataManager:
    def __init__(self):
        self.history = {}

    def save_packet(self, frame_id, targets):
        if frame_id not in self.history:
            self.history[frame_id] = []
        self.history[frame_id].append(targets)  # Save targets for each frame ID

    def get_by_frame_id(self, frame_id):
        # Retrieve all serials for a specific frame ID
        return self.history.get(frame_id, [])

    def save_to_json(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.history, file, indent=4)

    def load_from_json(self, filename):
        try:
            with open(filename, 'r') as file:
                self.history = json.load(file)
        except FileNotFoundError:
            print("No previous data found.")
