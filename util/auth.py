import re
#from request import Request

def extract_credentials(request):

    # username_reg=hi&password_reg=bye

    credentials = []
    decodedbody = request.body.decode()
    cut = decodedbody.split('&')

    username_reg = cut[0]
    password_reg = cut[1]

    username = username_reg.split('=')[1]
    per_password = password_reg.split('=')[1]

    password = per_password.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$').replace('%5E', '^').replace('%26', '&').replace('%28', '(').replace('%29', ')').replace('%2D', '-').replace('%5F', '_').replace('%3D', '=').replace('%25', '%')

    credentials.append(username)
    credentials.append(password)

    return credentials    


def validate_password(password):

    if len(password) < 8:
        return False
    
    if not any(i.islower() for i in password):
        return False
    
    if not any(i.isupper() for i in password):
        return False
    
    if not any(i.isdigit() for i in password):
        return False
    
    spechar = "!@#$%^&(),-_="
    valchar = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789" + spechar)
    
    if not any(i in spechar for i in password):
        return False
    
    for i in password: 
        if i not in valchar:
            return False
    
    return True

'''def test1():
    request = Request(b'POST /register HTTP/1.1\r\nHost: localhost:8080\r\nConnection: keep-alive\r\nContent-Length: 32\r\n\r\nusername_reg=hi&password_reg=bye%21')
    assert(extract_credentials(request) == ['hi', 'bye!'])'''

def test2():
    goodpassword = "Watermelon3!"
    nocaps = "watermelon3!"
    nolowercase = "WATERMELON3!"
    nonumbers = "Watermelon!"
    nospechar = "Watermelon3"
    invalidchar = "Watermelon3!<"
    
    assert(validate_password(nocaps) == False)
    assert(validate_password(nolowercase) == False)
    assert(validate_password(nonumbers) == False)
    assert(validate_password(nospechar) == False)
    assert(validate_password(invalidchar) == False)
    assert(validate_password(goodpassword) == True)


if __name__ == '__main__':
    #test1()
    test2()
    


    
    
    

    
    

    
    

    

