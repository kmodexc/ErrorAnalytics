#!/usr/bin/env python

import socketserver
import os.path
import http.client
import mimetypes
mimetypes.init()

backlog = 5
size = 1024

newline = "\r\n"

class Request:
    def __init__(self, data):
        self.data = data.decode('utf8')

        self.lines = self.data.strip("\r").split("\n")

        self.req_line = self.lines[0]

        self.method = self.req_line.split(" ")[0]

        if len(self.req_line.strip()) == 0:
            print("Empty Header line")
            print("Complete request",self.data)
            self.req_line = "none none none"

        # Analyse query string
        self.path_with_query = self.req_line.split(" ")[1]
        args_path_split = self.path_with_query.split('?')
        self.path = args_path_split[0]
        self.query_string = args_path_split[1] if len(args_path_split) > 1 else ""
        self.query_args = {}
        for x in self.query_string.split('&'):
            if '=' in x:
                self.query_args[x.split('=')[0]] = x.split('=')[1]


        self.http_version = self.req_line.split(" ")[2]

        self.headers = {}
        for i in range(1, len(self.lines)):
            line = self.lines[i]
            if not ":" in line:
                #end of headers
                break
            header = line.split(":")[0].strip()
            value = line.split(":")[1].strip()
            self.headers[header] = value

        self.content = "\r\n".join(self.lines[len(self.headers)+1:])

class Response:
    def __init__(self,content=None,path="./index.html",status=200):
        self.headers = {}
        self.setCode(status)
        self.path = path
        self.content = content

    def header(self, name, value):
        if not (name == "Content-Length" or name == "Content-Type"):
            self.headers[name] = value
            return 1
        else:
            return 0

    def setCode(self, statusCode):
        self.statusCode = statusCode
        codeMeaning = http.client.responses[int(self.statusCode)]
        if codeMeaning:
            self.status = codeMeaning
        else:
            return 0
        return 1

    def form_headers(self, content):
        self.headers["Content-Type"] = mimetypes.types_map["." + self.path.split("/")[-1].split(".")[-1]]
        self.headers["Content-Length"] = len(content)
        return "".join([str(i)+": "+str(self.headers[i])+"\r\n" for i in self.headers])

    def getContent(self):
        if self.content is None:
            f = open(self.path, "rb")
            f_contents = f.read()
            f.close()
        else:
            f_contents = self.content
        return f_contents

    def form(self):
        global newline
        content = self.getContent()
        response = "HTTP/1.1 " + str(self.statusCode) + " " + self.status + newline +\
                   self.form_headers(content) + newline
        return response.encode('utf8') + content
