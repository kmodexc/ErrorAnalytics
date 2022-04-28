from matplotlib.pyplot import hist
import socketserver
import http_server
import os.path
import errors
import asyncio

HOST = 'localhost'
PORT = 8080

class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        req_data = self.request.recv(1024).strip()
        request = http_server.Request(req_data)
        if request.path[0] == '/':
            request.path = '.' + request.path
        print(request.path)
        if request.path == './analyse.html':
            _type = request.query_args['type']
            with open('./analyse.html') as f:
                text = f.read()
            graph_path = f'errors_{_type}.png'
            text = text.replace('image_source',graph_path)
            if not os.path.isfile(graph_path) or bool(request.query_args.get('refresh',False)):
                if asyncio.run(errors.get_errors_img(_type,True)):
                    response = http_server.Response(text.encode('utf8'))
                else:
                    response = http_server.Response(path="no_data.html")
            else:
                response = http_server.Response(text.encode('utf8'))
        else:
            if os.path.isfile(request.path):
                response = http_server.Response(path=request.path)
            else:
                response = http_server.Response(path="404.html")
        self.request.sendall(response.form())

def run_server():
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()

if __name__ == '__main__':
    run_server()
