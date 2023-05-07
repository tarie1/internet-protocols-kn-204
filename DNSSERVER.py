import os
import socket
import datetime
import json
import struct

PORT = 53
HOST = '127.0.0.1'
OTHER_SERVER = '8.8.8.8'


def query_other_server(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(data, (OTHER_SERVER, PORT))
        data, dummy = sock.recvfrom(2048)
    finally:
        sock.close()
    return data


class DNSServer:
    def __init__(self):
        self.cache = {}
        socket.setdefaulttimeout(55)
        if os.path.exists('cache.json'):
            with open('cache.json') as file:
                self.cache = json.load(file)

    def dns_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((HOST, PORT))
        while True:
            data, address = server_socket.recvfrom(1024)
            packet = self.parse_dns_packet(data)
            if packet:
                server_socket.sendto(packet, address)

    def parse_dns_packet(self, data):
        answer = b""
        qname, qtype, qclass, flags, count, offset = self.unpack_dns_packet(data)

        offset += 4
        if qtype in (1, 2):
            cache_key = f"{qname.lower()}"
            if cache_key in self.cache:
                cached_answer, qtype, qclass, flags, count, ttl = self.cache[cache_key]
                if datetime.datetime.now() < datetime.datetime.fromtimestamp(ttl):
                    answer = data[:2] + bytes.fromhex(cached_answer)
                else:
                    del self.cache[cache_key]
                    self.update_cache()
            if not answer:
                new_data = query_other_server(data)
                ttl = self.get_ttl(new_data)
                answer = new_data[2:]
                if answer:
                    self.cache[cache_key] = (
                        answer.hex(), f'{qtype}', f'{qclass}', flags, count, ttl)
                    self.update_cache()
                    answer = data[:2] + answer

        return answer

    def parse_dns_domain_name(self, data, offset):
        parts = []
        while True:
            length = struct.unpack('!B', data[offset:offset + 1])[0]
            offset += 1
            if length == 0:
                break
            elif (length & 0xc0) == 0xc0:
                pointer = struct.unpack('!H', data[offset - 1:offset + 1])[0] & 0x3fff
                parts.append(self.parse_dns_domain_name(data, pointer)[0])
                offset += 1
                break
            else:
                parts.append(data[offset:offset + length].decode('utf-8'))
                offset += length
        return '.'.join(parts), offset

    def get_ttl(self, data):
        _, offset = self.parse_dns_domain_name(data, 12)
        offset += 10
        num_answers = struct.unpack('!H', data[6:8])[0]
        min_ttl = float('inf')
        for _ in range(num_answers):
            if bytes(10) > data[offset:offset + 10]:
                return min_ttl
            _, _, ttl, rdlength = struct.unpack('!HHIH', data[offset:offset + 10])
            offset += 10
            if ttl < min_ttl:
                min_ttl = ttl
            offset += rdlength
        return min_ttl

    def unpack_dns_packet(self, data):
        offset = 12
        qname, offset = self.parse_dns_domain_name(data, offset)
        qtype, qclass = struct.unpack("!HH", data[offset: offset + 4])

        header = struct.unpack('!6H', data[:12])
        qr = (header[0] & 0x8000) >> 15
        opcode = (header[0] & 0x7800) >> 11
        aa = (header[0] & 0x400) >> 10
        tc = (header[0] & 0x200) >> 9
        rd = (header[0] & 0x100) >> 8
        ra = (header[0] & 0x80) >> 7
        z = (header[0] & 0x70) >> 4
        rcode = header[0] & 0xF

        qdcount = header[1]
        ancount = header[2]
        nscount = header[3]
        arcount = header[4]

        return qname, qtype, f'qclass: {qclass}', (
            f'qr: {qr}', f'opcode: {opcode}', f'aa: {aa}', f'tc: {tc}', f'rd: {rd}', f'ra: {ra}', f'z: {z}',
            f'rcode: {rcode}'), (
                   f'qdcount: {qdcount}', f'ancount: {ancount}', f'nscount: {nscount}', f'arcount: {arcount}'), \
               offset

    def update_cache(self):
        with open('cache.json', 'w') as file:
            json.dump(self.cache, file)


if __name__ == '__main__':
    DNSServer().dns_server()
