import os
import json

def load_file(file_path):
        json_data = {}
        if not os.path.exists(file_path):
            with open(file_path, "w") as fd:
                json.dump(json_data, fd, indent=4)
        else:
            with open(file_path, 'r') as fd:
                json_data = json.load(fd)
        return json_data