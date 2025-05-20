import hashlib
import base64


class WebSocketFrame:
    def __init__(self, fin_bit, opcode, payload_length, payload, remaining_data=None):
        self.fin_bit = fin_bit
        self.opcode = opcode
        self.payload_length = payload_length
        self.payload = payload
        self.remaining_data = remaining_data

def compute_accept(key):
    GUID = key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
    hash = hashlib.sha1(GUID.encode()).digest()
    accept = base64.b64encode(hash).decode()

    return accept

def parse_ws_frame(buffer):
    if len(buffer) < 2:
        return None  

    first_byte = buffer[0]
    fin_bit = (first_byte >> 7) & 1
    opcode = first_byte & 0b00001111

    if opcode not in [0x0, 0x1, 0x8]: 
        return None  

    second_byte = buffer[1]
    mask_bit = (second_byte >> 7) & 1
    payload_length = second_byte & 0b01111111
    index = 2

    if payload_length == 126:
        if len(buffer) < 4:
            return None  
        payload_length = int.from_bytes(buffer[2:4], 'big')
        index += 2
    elif payload_length == 127:
        if len(buffer) < 10:
            return None  
        payload_length = int.from_bytes(buffer[2:10], 'big')
        index += 8

    if len(buffer) < index + (4 if mask_bit else 0) + payload_length:
        return None  

    masking_key = buffer[index:index + 4] if mask_bit else None
    index += 4 if mask_bit else 0
    payload_data = buffer[index:index + payload_length]

    if mask_bit:
        payload = bytearray((payload_data[i] ^ masking_key[i % 4]) for i in range(payload_length))
    else:
        payload = payload_data

    remaining_data = buffer[index + payload_length:]
    return WebSocketFrame(fin_bit, opcode, payload_length, payload, remaining_data)





def generate_ws_frame(payload_bytes):
    finbit = 1
    opcode = 0x1

    if len(payload_bytes) < 126:
        payload_length = len(payload_bytes)
        payload_length_encoded = bytes([payload_length])
        ws_frame = bytes([(finbit << 7) | opcode]) + payload_length_encoded + payload_bytes
        return ws_frame
    elif len(payload_bytes) < 65536:
        payload_length = 126
        payload_length_encoded = payload_length.to_bytes(1, 'big')
        payload_length_extended = len(payload_bytes)
        payload_length_extended_encoded = payload_length_extended.to_bytes(2, 'big')
    else:
        payload_length = 127
        payload_length_encoded = payload_length.to_bytes(1, 'big')
        payload_length_extended = len(payload_bytes)
        payload_length_extended_encoded = payload_length_extended.to_bytes(8, 'big')

    ws_frame = bytes([(finbit << 7) | opcode]) + payload_length_encoded + payload_length_extended_encoded + payload_bytes

    return ws_frame

'''def test1():
    print(parse_ws_frame(b'\x8F\x85\x37\xfa\x21\x3d\x7f\x9f\x4d\x51\x58'))
    bytes = b'\x8F\xFE\x24\x22\x21\x3d\x7f\x9f\x4d\x51\x58'
    print('hi')
    


if __name__ == '__main__':
    parse_ws_frame(b'\x8F\x7F\x24\x22\x21\x3d\x7f\x9f\x4d\x51\x58')'''