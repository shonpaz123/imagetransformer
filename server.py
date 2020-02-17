from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from PIL import Image
import json
import boto3 
import botocore
import cgi
from io import BytesIO
import os

access_key = os.environ['AWS_ACCESS_KEY_ID']
secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
endpoint_url = os.environ['ENDPOINT_URL']

s3 = boto3.client('s3','us-east-1', endpoint_url=endpoint_url,
                       aws_access_key_id = access_key,
                       aws_secret_access_key = secret_key,
                       use_ssl = False)

class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def do_HEAD(self):
        self._set_headers()
        
    # GET sends back a Hello world message
    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({'hello': 'welcome to our demo!'}))
        
    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
            
        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))
        
        # parse event to get the wanted bucket and object for fetching the image 
        self.bucket_name = message['s3']['bucket']['name']
        self.object_name = message['s3']['object']['key']

        # send the message back
        self._set_headers()
       
        # fetches image from s3 object storage 
        response = s3.get_object(Bucket=self.bucket_name, Key=self.object_name)['Body'].read()

        # open image and rotate
        image = Image.open(BytesIO(response))
        image = image.rotate(180)

        # put new image to s3 object storage
        buffer = BytesIO()
        image.save(buffer, format='JPEG')
        buffer.seek(0)
        s3.upload_fileobj(buffer, 'processed', self.object_name, ExtraArgs={'ACL': 'public-read'})
        
def run(server_class=HTTPServer, handler_class=Server, port=8009):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print('Starting httpd on port %d...' % port)
    httpd.serve_forever()
    
if __name__ == "__main__":
    from sys import argv
    
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
