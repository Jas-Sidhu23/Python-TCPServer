from util.request import Request
from util.auth import *
from pymongo import MongoClient
import secrets
import bcrypt
import json
import uuid
import html
import hashlib
import os
from util.multipart import parse_multipart
from util.websockets import *

mongo_client = MongoClient("mongo")
db = mongo_client["cse312"]
chat_collection = db["chat"]
users_collection = db["users"]
tokens_colection = db["tokens"]

# ------------------ SERVE PUBLIC ---------------------------------------------------

def serve_html(request: Request, TCPHandler):
    with open('public/index.html', 'r') as file:
        index = file.read()

    visits = request.cookies.get('visits')
    if visits is None:
        count = 1
    else:
        count = int(visits) + 1
    index = index.replace('{{visits}}', str(count))

    authtoken = request.cookies.get('authtoken')
    if authtoken:
        hashedtoken = hashlib.sha256(authtoken.encode()).hexdigest()
        tokendata = tokens_colection.find_one({"auth token": hashedtoken})
        if tokendata:
            #print('hi')
            #username = tokendata['username']
            xsrf_token = secrets.token_hex(16)
            tokens_colection.update_one({"auth token":hashedtoken},{"$set":{"token": xsrf_token}})
            #if '<input id="xsrf-token" value="" hidden>' in index:
               # print('true')
            index = index.replace('<input id="xsrf-token" value="" hidden>', f'<input id="xsrf-token" value={xsrf_token} hidden>')
            #print(xsrf_token)
            index = index.replace('<input type="submit" value="Submit"', '<input type="submit" value="Log Out" formaction="/logout"')
            #index = index.replace('<div class="user-list">', '<form action="/logout" method="post">' '<input type="submit" value="Log Out"></form></div>')
        #print(index)
    contentLength = len(index.encode())

    return ('HTTP/1.1 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\nSet-Cookie: visits=' + str(count) + '; Max-Age=3600; HttpOnly\r\n\r\n' + index).encode()
    
def serve_css(request: Request, TCPHandler):
    with open('public/style.css', 'r') as file:
        css = file.read()
    contentLength = len(css.encode())
    return ('HTTP/1.1 200 OK\r\nContent-Type: text/css; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n' + css).encode()
    
def serve_funcjs(request:Request, TCPHandler):
    with open('public/functions.js', 'r') as file:
        fjs = file.read()
    contentLength = len(fjs.encode())
    return ('HTTP/1.1 200 OK\r\nContent-Type: text/javascript; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n' + fjs).encode()
    
def serve_webjs(request: Request, TCPHandler):
    with open('public/webrtc.js', 'r') as file:
        wjs = file.read()
    contentLength = len(wjs.encode())
    return ('HTTP/1.1 200 OK\r\nContent-Type: text/javascript; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n' + wjs).encode()
    
def serve_ico(request: Request, TCPHandler):
    with open('public/favicon.ico', 'rb') as file:
        ico = file.read()
    contentLength = len(ico)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/x-icon\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + ico
    
    # ------------------ IMAGES START HERE ----------------------------------------------------------------------------------------------------
    
def serve_cat(request: Request, TCPHandler):
    with open('public/image/cat.jpg', 'rb') as file:
        cat = file.read()
    contentLength = len(cat)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + cat

def serve_dog(request: Request, TCPHandler):
    with open('public/image/dog.jpg', 'rb') as file:
        dog = file.read()
    contentLength = len(dog)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + dog

def serve_eagle(request: Request, TCPHandler):
    with open('public/image/eagle.jpg', 'rb') as file:
        eagle = file.read()
    contentLength = len(eagle)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + eagle

def serve_elephant_small(request: Request, TCPHandler):
        with open('public/image/elephant-small.jpg', 'rb') as file:
            smallele = file.read()
        contentLength = len(smallele)
        return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + smallele

def serve_elephant(request: Request, TCPHandler):
    with open('public/image/elephant.jpg', 'rb') as file:
        elephant = file.read()
    contentLength = len(elephant)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + elephant

def serve_flamingo(request: Request, TCPHandler):
    with open('public/image/flamingo.jpg', 'rb') as file:
        flamingo = file.read()
    contentLength = len(flamingo)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + flamingo

def serve_kitten(request: Request, TCPHandler):
    with open('public/image/kitten.jpg', 'rb') as file:
        kitten = file.read()
    contentLength = len(kitten)
    return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + kitten
    
#------------------- CHAT MESSAGES ----------------------------------------

def serve_getchat(request: Request, TCPHandler):
    mess = list(chat_collection.find({}))

    for i in mess:
        del i['_id']

    body = json.dumps(mess)
        #print(body)
        #body = html.escape(body)
    body = body.encode()
    contentLength = len(body)
        #print(list(chat_collection.find({})))
        #print(contentLength)

    return ('HTTP/1.1 200 OK\r\nContent-Type: application/json; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + body
    
def serve_postchat(request: Request, TCPHandler):
    postbody = request.body.decode()
    message = json.loads(postbody)

    token = request.cookies.get('authtoken')
    if token:
        hashedtoken = hashlib.sha256(token.encode()).hexdigest()
        tokendata = tokens_colection.find_one({"auth token": hashedtoken})
        if tokendata:
            username = tokendata['username']
            xsrf_data = tokens_colection.find_one({"username": username})
            if xsrf_data:
                xsrf_token = xsrf_data['token']
                if message['xsrf_token'] == xsrf_token:
                    id = str(uuid.uuid4())
                    chat_message = {'id': id, 'username': username, 'message': html.escape(message['message']), "message_format": "message"}
                    chat_collection.insert_one(chat_message)
                    return ('HTTP/1.1 201 Created\r\nContent-Type: application/json; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode()
                else:
                    return b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nX-Content-Type-Options: nosniff\r\n\r\n'
            else:
                return b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nX-Content-Type-Options: nosniff\r\n\r\n'
        else:
            id = str(uuid.uuid4())
            chatt = {'id':id, 'username': "Guest", 'message': html.escape(message['message']), "message_format": "message"}
            chat_collection.insert_one(chatt)
            return ('HTTP/1.1 201 Created\r\nContent-Type: application/json; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode()
    else:
        id = str(uuid.uuid4())
        chatt = {'id':id, 'username': "Guest", 'message': html.escape(message['message']), "message_format": "message"}
        chat_collection.insert_one(chatt)
                
        return ('HTTP/1.1 201 Created\r\nContent-Type: application/json; charset=utf-8\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode()

def serve_register(request: Request, TCPHandler):
    cred = extract_credentials(request)
    username = cred[0]
    password = cred[1]

    if validate_password(password) == False:
        return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'
    
    encodedpw = password.encode()
    salted_hash = bcrypt.hashpw(encodedpw, bcrypt.gensalt())
    safepw = salted_hash.decode()

    user = {"username": username, "password": safepw}
    users_collection.insert_one(user)

    return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'

def serve_login(request: Request, TCPHandler):
    cred = extract_credentials(request)
    username = cred[0]
    password = cred[1]

    user = users_collection.find_one({'username': username})

    if not user:
        return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'
    
    
    if bcrypt.checkpw(password.encode(), user['password'].encode()):
        token = secrets.token_hex(32)

        hashed = hashlib.sha256(token.encode()).hexdigest()
        store_token = {'username': username, 'auth token': hashed}
        tokens_colection.insert_one(store_token)

        return ('HTTP/1.1 302 Found\r\nContent-Length: 0\r\nSet-Cookie: authtoken=' + token + '; HttpOnly; Max-Age=3600\r\nLocation: /\r\n\r\n').encode()
    else:
        return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'
    
def serve_logout(request: Request, TCPHandler):
    authtoken = request.cookies.get('authtoken')
    if authtoken:
        tokens_colection.delete_one({'auth token': hashlib.sha256(authtoken.encode()).hexdigest()})

    response = 'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nSet-Cookie: authtoken=' + authtoken + '; Expires=Wed, 7 Feb 2024 16:35:00 GMT\r\nLocation: /\r\n\r\n'
    return response.encode()

def serve_delete(request: Request, TCPHandler):
    authtoken = request.cookies.get('authtoken')
    delrequest = request.path.split('/')
    chatid = delrequest[-1]

    if authtoken:
        hashedtoken = hashlib.sha256(authtoken.encode()).hexdigest()
        tokendata = tokens_colection.find_one({'auth token': hashedtoken})
        if tokendata:
            username = tokendata['username']

            chat = chat_collection.find_one({'id': chatid})
    
            if chat['username'] == username:
                chat_collection.delete_one({'id': chatid})
            else:
                return b'HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nX-Content-Type-Options: nosniff\r\n\r\n'

    return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'

def serve_public_image(request: Request, TCPHandler):
    filename = request.path.split("/")[-1]
    print('hi' + filename)
    path = os.path.join("./public/image", filename)
    #print("hi" + path)
    try:
        with open(path, 'rb') as file:
            body = file.read()
            contentLength = len(body)
            return ('HTTP/1.1 200 OK\r\nContent-Type: image/jpeg; charset=utf-8\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + body
    except:
        error = b'404 - Content was not found.'
        contentLength = len(error)
        return ('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + error
    
def serve_upload_image(request: Request, TCPHandler):
    contentLength = int(request.headers['Content-Length'])
    received_data = request.body
    while len(received_data) < contentLength:
        received_data += TCPHandler.request.recv(2048)
    request.body = received_data

    final_parse = parse_multipart(request)
    for part in final_parse.parts:
        headers = part.headers
        #print("Headers:", headers)

        name = part.name
        #print("Name:", name)

        content = part.content
        #print("Content:", content)

        filename = headers['Content-Disposition'].split("=")[-1]
        
    #print('here' + name)
    if name == 'upload':
        print('reached this statement')
        file_type = filename.split('.')[-1]
        file_type = file_type.split('"')[0]
        print("hi" + file_type)
        if file_type == 'jpg':
            message_format = "image"
        else:
            message_format = "video"
            
        path = os.path.join('./public/image', f"{uuid.uuid4().hex}.{file_type}")

        with open(path, 'wb') as file:
            file.write(content)

        username = 'Guest'
        auth = request.cookies.get("authtoken")
        if auth:
            hashed_token = hashlib.sha256(auth.encode()).hexdigest()
            find = tokens_colection.find_one({"auth token": hashed_token})
            if find:
                username = find.get("username")

        chat_collection.insert_one({"id": uuid.uuid4().hex, "username": username, 'message': f'{path}', "message_format": message_format})

        return b'HTTP/1.1 302 Found\r\nContent-Length: 0\r\nLocation: /\r\n\r\n'
    
    error = b'404 - Content was not found.'
    contentLength = len(error)
    return ('HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\nContent-Length: ' + str(contentLength) + '\r\nX-Content-Type-Options: nosniff\r\n\r\n').encode() + error

    










    





        

