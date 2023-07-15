from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import os
import sqlite3 as db
import database_conector as dbc
import json

class FileServer(BaseHTTPRequestHandler):
    
    def do_GET(self):
        client_ip = self.client_address[0]
        if good_IP(client_ip):
            # Get url
            base_front = "static"
            url = str(self.path)
            
            if self.path.startswith('/drive'):
                path = getPath("save/", self.path, "/drive", createDIR=False)
                path = path[0:len(path)-1]
                if os.path.isfile(path):
                    name = os.path.basename(path)
                    try:
                        with open(path, 'rb') as file:
                            file_contents = file.read()
                    except FileNotFoundError:
                        self.send_error(404, 'File Not Found')
                        return
                    self.send_response(200)
                    self.send_header('Content-Disposition', 'attachment; filename="' + name + '"')
                    self.send_header('Content-type', 'application/octet-stream')
                    self.send_header('Content-length', str(len(file_contents)))
                    self.end_headers()

                    self.wfile.write(file_contents)
                    return
                elif os.path.isdir(path):
                    file_list = os.listdir(path)
                    # Create a JSON object or dictionary
                    data = {
                        "go_back": "..",
                    }
                    filen = 1
                    dirn = 1
                    for dfile in file_list:
                        if os.path.isfile(os.path.join(path, dfile)):
                            data["file" + str(filen)] = dfile
                            filen += 1
                        else:
                            data["dir" + str(dirn)] = dfile
                            dirn += 1
                    
                    # Convert the data to a JSON string
                    json_data = json.dumps(data)

                    # Set the response headers
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()

                    # Send the JSON data as the response
                    self.wfile.write(json_data.encode())
                    return

            
            # check dir to replace it with index.html if exists
            elif os.path.isdir(base_front + url):
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
                    #end_index = len(request_data) - 1
                    end_index = len(request_data) - len(b'--------------------------1b0f8f562f0c2933--')
                            
                    
                    # data without the prefix
                    data = request_data[start_index:end_index]
                    
                    path = getPath("save/", self.path, "/upload")
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
    


def getPath(prefix, url, normal_access, createDIR=True):
    path = prefix
    st = len(normal_access) + 1
    file_path = prefix
    
    if url != normal_access and url != normal_access + "/":
        if url.startswith(normal_access + "/"):
            url = url[st:len(url)]
            url_split = url.split("/")
            for i in range(len(url_split)):
                file_path = prefix
                for j in range(i+1):
                    file_path += url_split[j] + "/"
                if os.path.exists(file_path) == False and os.path.exists(file_path[0:len(file_path)-1]) == False:
                    if createDIR:
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


