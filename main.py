import mimetypes
import json
from pathlib import Path
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import os
from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).parent

class MyHandler(BaseHTTPRequestHandler):
    file_path = "storage/data.json"
    def do_GET(self):
        route = urllib.parse.urlparse(self.path)
        match route.path:
            case '/':
                self.send_html('index.html')
            case '/read':
                env = Environment(loader=FileSystemLoader("."))
                self.render_read_page(env)
            case '/message':
                self.send_html('message.html')
            case _:
                file = BASE_DIR.joinpath(route.path[1:])
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('error.html', 404)

    def load_file(self):
        json_data = {}
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as fd:
                json.dump(json_data, fd, indent=4)
        else:
            with open(self.file_path, 'r') as fd:
                json_data = json.load(fd)
        return json_data

    def do_POST(self):
        size = self.headers.get("Content-Length")
        body = self.rfile.read(int(size)).decode('utf-8')
        parse_body = urllib.parse.unquote_plus(body)
        form_data = {key: value for key, value in [el.split('=') for el in parse_body.split('&')]}
        data_key = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        json_data: json = self.load_file()
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
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def render_read_page(self, env):
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     data = json.load(file)

        json_data = self.load_file()
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

def run():
    server_address = ('', 3000)
    httpd = HTTPServer(server_address, MyHandler)
    print('Starting server...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server is shutting down...')
    except Exception as e:
        print(f'An error occurred: {e}')
    finally:
        httpd.server_close()


if __name__ == '__main__':
    run()