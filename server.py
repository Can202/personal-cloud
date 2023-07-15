from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import os
import sqlite3 as db
import database_conector as dbc

class FileServer(BaseHTTPRequestHandler):
    
    def do_GET(self):
        client_ip = self.client_address[0]
        if good_IP(client_ip):
            # Get url
            base_front = "static"
            url = str(self.path)
            # check dir to replace it with index.html if exists
            if os.path.isdir(base_front + url):
                if os.path.exists(base_front + url + "index.html"):
                    content_type = 'text/html'
                    url += "index.html"
                elif os.path.exists(base_front + url + "/index.html"):
                    content_type = 'text/html'
                    url += "/index.html"
                else:
                    self.send_error(404, 'File Not Found')
                    return
            # put content type of the file
            elif url.endswith('.html'):
                content_type = 'text/html'
            elif url.endswith('.css'):
                content_type = 'text/css'
            elif url.endswith('.js'):
                content_type = 'application/javascript'
            else:
                self.send_error(404, 'File Not Found')
                return

            try:
                # send content
                with open(base_front + url, 'rb') as file:
                    file_contents = file.read()
            except FileNotFoundError:
                self.send_error(404, 'File Not Found')
                return
            
            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(file_contents)
        else:
            self.send_error(400, 'No Verified')
            


    def do_POST(self):
        client_ip = self.client_address[0]
        if good_IP(client_ip):
            content_type = self.headers['Content-Type']
            if content_type.startswith('multipart/form-data'):
                if self.path.startswith('/upload'):
                    content_length = int(self.headers['Content-Length'])
                    name_of_file = self.headers['Name']
                    
                    # data on binary
                    request_data = self.rfile.read(content_length)
                    # part of the data that has to be removed
                    start_index = request_data.find(b'\r\n\r\n') + 4
                    # data without the prefix
                    data = request_data[start_index:len(request_data)-1]
                    
                    path = getPath("save/", self.path)
                    name = name_of_file
                    
                    with open(path + name, 'wb') as file:
                        file.write(data)
                    # Send a response
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    response = f'The file {name} has been saved on {path}'
                    self.wfile.write(response.encode())
                else:
                    self.send_error(400, 'Bad Request')
                    
            else:
                # If content type is not multipart/form-data
                self.send_error(400, 'Bad Request')
        else:
            self.send_error(400, f'{client_ip} is not Verified')
    


def getPath(prefix, url):
    path = prefix
    normal_access = "/upload"
    file_path = ""
    
    if url != normal_access and url != normal_access + "/":
        if url.startswith("/upload/"):
            url = url[8:len(url)]
            url_split = url.split("/")
            for i in range(len(url_split)):
                file_path = prefix
                for j in range(i+1):
                    file_path += url_split[j] + "/"
                if os.path.exists(file_path) == False:
                    os.mkdir(file_path)
    return file_path

def good_IP(IP):
    command = "SELECT DeviceIP FROM Devices\n"
    command += "WHERE DeviceIP = '" + str(IP) + "'"
    is_ip = dbc.create_list_with_database(command)
    if len(is_ip) > 0:
        return True
    else:
        return False

def run_server():
    server_address = ('', 8000)  # Replace with your desired port number
    httpd = HTTPServer(server_address, FileServer)
    print('Server running...')
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()


