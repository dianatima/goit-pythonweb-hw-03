import mimetypes
import json
from pathlib import Path
import os
import urllib.parse
from http.server import BaseHTTPRequestHandler
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from utils import load_file

BASE_DIR = Path(__file__).parent
env = Environment(loader=FileSystemLoader("templates"))

class MyHandler(BaseHTTPRequestHandler):
    file_path = "storage/data.json"
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/read':
                self.render_read_page(env)
            case '/message':
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)


    def do_POST(self):
        size = self.headers.get("Content-Length")
        body = self.rfile.read(int(size)).decode('utf-8')
        parse_body = urllib.parse.unquote_plus(body)
        form_data = {key: value for key, value in [el.split('=') for el in parse_body.split('&')]}
        data_key = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        json_data: json = load_file(file_path="storage/data.json")
        json_data[data_key] = form_data
        with open('storage/data.json', 'w') as fd:
            json.dump(json_data, fd, indent=4)

        self.send_response(302)
        self.send_header('Location', '/read')
        self.end_headers()

    def send_html(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        path = os.path.join("templates", filename)
        with open(path, 'rb') as file:
            self.wfile.write(file.read())

    def render_read_page(self, env):

        json_data = load_file(file_path="storage/data.json")
        data = [{"datetime": dt, **info} for dt, info in json_data.items()]

        template = env.get_template("read.html")
        print(data)
        content = template.render(messages=data)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(content.encode())

    def send_static(self, filename, status=200):
        self.send_response(status)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'text/plain')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())
