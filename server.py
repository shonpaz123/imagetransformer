import SimpleHTTPServer
import BaseHTTPServer

class SpostHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def do_POST(self):
        print self.command + " " + self.path 
        print self.headers
        print self.rfile.read(int(self.headers['Content-Length']))
        self.end_headers()
        self.send_response(100, "") 

if __name__ == '__main__':
    SimpleHTTPServer.test(HandlerClass=SpostHTTPRequestHandler)
