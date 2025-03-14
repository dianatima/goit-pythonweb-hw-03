from http.server import HTTPServer
from handlers import MyHandler

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