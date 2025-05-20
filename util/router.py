from util.request import Request
import re


#Dont call add_route in the route_request method
#Route request method should bot look like handler methods
#Call re.match in the route request method
class Router:

    def __init__(self):
        self.lis=[]

    def add_route(self, meth, pat, serve_func):
        self.lis.append((meth, pat, serve_func))


    def route_request(self, request: Request, TCPHandler): 
        for meth, pat, serve_func in self.lis:
            if meth == request.method and re.match(pat, request.path):
                return serve_func(request, TCPHandler)
            
        error = b'404 - Content was not found.'
        contentLength = len(error)
        return ('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + error
    

            
