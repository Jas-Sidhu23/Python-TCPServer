import socketserver
from util.request import Request
from util.router import Router
from handler import *


class MyTCPHandler(socketserver.BaseRequestHandler):
    connections = {} 

    def serve_websocket(self, request):
        key = request.headers["Sec-WebSocket-Key"]
        if key:
            accept = compute_accept(key)
            self.request.sendall(('HTTP/1.1 101 Switching Protocols\r\nConnection: Upgrade\r\nUpgrade: websocket\r\nSec-WebSocket-Accept: ' + str(accept) + '\r\n\r\n').encode())

            username = 'Guest'
            auth = request.cookies.get("authtoken")
            if auth:
                hashed_token = hashlib.sha256(auth.encode()).hexdigest()
                find = tokens_colection.find_one({"auth token": hashed_token})
                if find:
                    username = find.get("username")

            MyTCPHandler.connections[self.request] = username
            self.user_list_update()

            message_payload = bytearray()
            buffer = bytearray()
            try:
                while True:
                    data = self.request.recv(2048)
                    if not data:
                        break

                    buffer.extend(data)

                    while True:
                        frame = parse_ws_frame(buffer) 
                        if frame is None:
                            break

                        buffer = frame.remaining_data  

                        if frame.opcode == 0x8:
                            return

                        if frame.opcode == 0x1 or frame.opcode == 0x0:
                            message_payload.extend(frame.payload)
                            if frame.fin_bit == 1:
                                try:
                                    complete_message = message_payload.decode()
                                    message_dict = json.loads(complete_message)
                                    message = html.escape(message_dict['message'])
                                    insert = chat_collection.insert_one({'message': message, 'username': username})
                                    output = {
                                        "messageType": "chatMessage",
                                        "username": username,
                                        "message": message,
                                        "id": str(insert.inserted_id)
                                    }
                                    self.export(output)
                                except json.JSONDecodeError:
                                    pass
                                except UnicodeDecodeError:
                                    pass
                                finally:
                                    message_payload.clear()

            finally:
                if self.request in MyTCPHandler.connections:
                    del MyTCPHandler.connections[self.request]
                    self.user_list_update()



    def export(self, outputdict):
        payload = json.dumps(outputdict).encode()
        ws_frame = generate_ws_frame(payload)
        failed_connections = []
        for connection in MyTCPHandler.connections.keys():
            try:
                connection.sendall(ws_frame)
            except OSError:
                failed_connections.append(connection)

        for connection in failed_connections:
            del MyTCPHandler.connections[connection]
            self.user_list_update()

    def user_list_update(self):
        user_list = list(MyTCPHandler.connections.values())
        message = json.dumps({"messageType": "userListUpdate", "users": user_list})
        failed_connections = []
        for connection in MyTCPHandler.connections.keys():
            try:
                connection.sendall(generate_ws_frame(message.encode()))
            except OSError:
                failed_connections.append(connection)

        for connection in failed_connections:
            del MyTCPHandler.connections[connection]


    router = Router()
    router.add_route('GET', '/$', serve_html)
    router.add_route('GET', '/public/style.css$', serve_css)
    router.add_route('GET', '/public/functions.js$', serve_funcjs)
    router.add_route('GET', '/public/webrtc.js$', serve_webjs)
    router.add_route('GET', '/public/favicon.ico$', serve_ico)
    router.add_route('GET', '/public/image/cat.jpg$', serve_cat)
    router.add_route('GET', '/public/image/dog.jpg$', serve_dog)
    router.add_route('GET', '/public/image/eagle.jpg$', serve_eagle)
    router.add_route('GET', '/public/image/elephant-small.jpg$', serve_elephant_small)
    router.add_route('GET', '/public/image/elephant.jpg$', serve_elephant)
    router.add_route('GET', '/public/image/flamingo.jpg$', serve_flamingo)
    router.add_route('GET', '/public/image/kitten.jpg$', serve_kitten)
    router.add_route('GET', '/chat-messages$', serve_getchat)
    router.add_route('POST', '/chat-messages$', serve_postchat)
    router.add_route('POST', '/register$', serve_register)
    router.add_route('POST', '/login$', serve_login)
    router.add_route('POST', '/logout', serve_logout)
    router.add_route('DELETE', '/chat-messages', serve_delete)
    router.add_route('POST', '/upload-image$', serve_upload_image)
    router.add_route('GET', '/public/image.', serve_public_image)
    #router.add_route('GET', '/websocket', serve_websocket)

    


    def handle(self):
        #self.connections.add(self)
        received_data = self.request.recv(2048)
        print(self.client_address)
        print("--- received data ---")
        print(received_data)
        print("--- end of data ---\n\n")
        request = Request(received_data)

        if request.path == '/websocket':
            self.serve_websocket(request)

        response = self.router.route_request(request, self)

        self.request.sendall(response)

        # TODO: Parse the HTTP request and use self.request.sendall(response) to send your response


def main():
    host = "0.0.0.0"
    port = 8080

    socketserver.TCPServer.allow_reuse_address = True

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)

    print("Listening on port " + str(port))

    server.serve_forever()


if __name__ == "__main__":
    main()
