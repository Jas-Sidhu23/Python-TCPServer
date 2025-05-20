class Request:

    def __init__(self, request: bytes):
        # TODO: parse the bytes of the request and populate the following instance variables

        self.body = b""
        self.method = ""
        self.path = ""
        self.http_version = ""
        self.headers = {}
        self.cookies = {}

        self.body = request.split(b'\r\n\r\n', 1)[1]

        headers = request.split(b'\r\n\r\n')[0].split(b'\r\n')
        reqLine = headers[0].split(b' ')

        self.method = reqLine[0].decode()
        self.path = reqLine[1].decode()
        self.http_version = reqLine[2].decode()

        for header in headers[1:]:
            if header != b'':
                key, value = header.split(b':', 1)
                self.headers[key.decode()] = value.decode().strip()

        if "Cookie" in self.headers:
            cookies = self.headers["Cookie"].split(";")
            for cookie in cookies:
                key, value = cookie.split("=")
                self.cookies[key.strip()] = value

def test1():
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nCookie: id=X6kAwpgW29M; visits=4\r\nConnection: keep-alive\r\n\r\n')
    assert request.method == "GET"
    assert "Host" in request.headers
    assert request.headers["Host"] == "localhost:8080"  # note: The leading space in the header value must be removed
    assert request.body == b""  # There is no body for this request.
    assert request.cookies["id"] == "X6kAwpgW29M"
    # When parsing POST requests, the body must be in bytes, not str

    # This is the start of a simple way (ie. no external libraries) to test your code.
    # It's recommended that you complete this test and add others, including at least one
    # test using a POST request. Also, ensure that the types of all values are correct


if __name__ == '__main__':
    test1()
    request = Request(b'GET / HTTP/1.1\r\nHost: localhost:8080\r\nCookie: id=X6kAwpgW29M; visits=4\r\nConnection: keep-alive\r\n\r\n')
    print("Body:", request.body)
    print("Method:", request.method)
    print("Path:", request.path)
    print("HTTP Version:", request.http_version)
    print("Host:", request.headers["Host"])
    print("Connection:", request.headers["Connection"])
    print("Headers:", request.headers)
    print("Cookie-id:", request.cookies["id"])
    print("Cookie-visits:", request.cookies["visits"])
    print("Cookie Headers:", request.cookies)

