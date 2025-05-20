#from request import Request

class Part:
    def __init__(self, headers, name, content):
        self.headers = headers
        self.name = name
        self.content = content

class FinalParse:
    def __init__(self, boundary, parts):
        self.boundary = boundary
        self.parts = parts

def parse_multipart(request):
    content_type = request.headers.get("Content-Type", "")
    _, subsections = content_type.split(";", 1)
    boundary_line = [subsection.strip() for subsection in subsections.split(";") if subsection.strip().startswith("boundary=")]
    if boundary_line:
        boundary = (boundary_line[0].split("=", 1)[1]).encode()
    else:
        boundary = ''

    parts = request.body.split(b"--" + boundary)[1:-1]

    parsed_parts = []
    for part in parts:
        part = part.strip(b"\r\n")
        headers, content = part.split(b"\r\n\r\n", 1)
        
        header_value = {}
        for header in headers.split(b"\r\n"):
            key, value = header.split(b":", 1)
            header_value[key.strip().decode()] = value.strip().decode()
            if b"Content-Disposition" in key:
                dispo = value.split(b";")
                name_line = [i.strip() for i in dispo if i.strip().startswith(b"name=")]
                if name_line:
                    name = name_line[0].split(b"=", 1)[1].strip(b"\"")
                else:
                    name = ''
        parsed_parts.append(Part(headers = header_value, name = name.decode(), content = content))
    
    return FinalParse(boundary=boundary.decode(), parts=parsed_parts)


'''def test():
    check = parse_multipart(Request(b'POST /form-path HTTP/1.1\r\nContent-Length: 252\r\nContent-Type: multipart/form-data; boundary=----WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\n\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\nContent-Disposition: form-data; name="commenter"\r\n\r\nJesse\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4\r\nContent-Disposition: form-data; name="comment"\r\n\r\nGood morning!\r\n------WebKitFormBoundaryfkz9sCA6fR3CAHN4--'))
    assert check.boundary == '----WebKitFormBoundaryfkz9sCA6fR3CAHN4'
    print(check.boundary)
    print(check.parts[1].headers)
    print(check.parts[1].name)
    print(check.parts[1].content)

if __name__ == '__main__':
    test()'''