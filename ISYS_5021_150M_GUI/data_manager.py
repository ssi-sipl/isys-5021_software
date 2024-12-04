import json

class DataManager:
    def __init__(self):
        self.history = {}

    def save_packet(self, frame_id, serials):
        self.history[frame_id] = serials

    def get_by_frame_id(self, frame_id):
        return self.history.get(frame_id, [])

    def save_to_json(self, filename):
        with open(filename, 'w') as file:
            json.dump(self.history, file, indent=4)
