import socket
import os
import mimetypes
from template import *

def tcp_server():
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 8080
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    print('Listen on http://127.0.0.1')
    while True:
        client_connection, client_address = server_socket.accept()
        #request
        request = client_connection.recv(1024).decode()
        #handle request
        response = handle_request(request)
        #response
        client_connection.sendall(response)
        client_connection.close()
    server_socket.close()

def handle_request(request):
    request_message = str(request).split('\r\n')
    request_line = request_message[0]
    words = request_line.split()
    method = words[0]
    uri = words[1].strip("/")
    query = uri.split('?')
    query_string = ''
    http_version = words[2]
    if(uri == ''):
        uri = 'index.html'
    url = uri
    if(len(query) > 1):
        query_string = query[1]
        url = query[0]
    if(method == 'GET'):
        query_string = query_string
        response = handle_get(url, http_version,query_string)
    elif(method == 'POST'):
        data = request_message[len(request_message)-1]
        response = handle_post(url, http_version,data,query_string)
    return response

def handle_get(url, http_version,query_string = ''):
    url = "htdocs/%s"%(url)
    if os.path.exists(url) and not os.path.isdir(url):
        response_line = b''.join([http_version.encode(), b'200', b'OK'])
        content_type = mimetypes.guess_type(url)[0] or 'text/html'
        entity_header = b''.join([b'Content-type: ', content_type.encode()])
        if(query_string == ''):
            file = open(url, 'rb')
            message_body = file.read()
            file.close()
        else:
            file = open(url, 'r')
            html = file.read()
            file.close()
            template = Template(html)
            _QUERY_STRING = {}
            for x in query_string.split('&'):
                y = x.split('=')
                _QUERY_STRING[y[0]]=y[1]
            context = {
                '_QUERY_STRING' : _QUERY_STRING
            }
            message_body = template.render(context).encode()
    else :
        response_line = b''.join([http_version.encode(), b'404', b'Not Found'])
        entity_header = b'Content-Type: text/html'
        message_body = b'<h1>404 Not Found</h1>'
    crlf = b'\r\n'
    response = b''.join([response_line, crlf, entity_header, crlf, crlf, message_body])
    return response

def handle_post(url, http_version, data, query_string):
    url = "htdocs/%s"%(url)
    if os.path.exists(url) and not os.path.isdir(url):
        response_line = b''.join([http_version.encode(), b'200', b'OK'])
        content_type = mimetypes.guess_type(url)[0] or 'text/html'
        entity_header = b''.join([b'Content-type: ', content_type.encode()])
        file = open(url, 'r')
        html = file.read()
        file.close()
        template = Template(html)
        _POST = {}
        _QUERY_STRING = {}
        for x in query_string.split('&'):
                y = x.split('=')
                _QUERY_STRING[y[0]]=y[1]
        for x in data.split('&'):
            y = x.split('=')
            _POST[y[0]]=y[1]
        context = {
            '_POST' : _POST,
            '_QUERY_STRING' : _QUERY_STRING,
        }
        message_body = template.render(context).encode()
    else :
        response_line = b''.join([http_version.encode(), b'404', b'Not Found'])
        entity_header = b'Content-Type: text/html'
        message_body = b'<h1>404 Not Found</h1>'
    crlf = b'\r\n'
    response = b''.join([response_line, crlf, entity_header, crlf, crlf, message_body])
    return response

if __name__ == "__main__":
    tcp_server()
