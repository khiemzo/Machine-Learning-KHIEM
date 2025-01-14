# highly expermimental Clayton project

import os
import sys
import time
import socket


class RSOCK():

    ip = 'sockethop.com'
    #ip = '192.168.10.11'
    port = 8032

    username = None
    password = None
    email = None

    addr = None
    sock = None

    hop_id = None

    handshake_timeout = 10

    @property
    def creds(self):
        print('Hop_ID:', self.hop_id)
        print('URL:', "https://sockethop.netlify.app/" + self.hop_id)

    def open(self, username=None, password=None, email=None):

        # reset first
        self.close(show=False)

        # credentials
        username = username or self.username or 'dummy'
        password = password or self.password or 'dummy'
        email = email or self.email or 'dummy'

        try:

            # create socket
            self.addr = socket.getaddrinfo(self.ip, self.port)[0][-1]
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect(self.addr)

            # handshake
            handshake_start = time.time()
            self.sock.settimeout(self.handshake_timeout*1000)
            self.sock.write(b'Connection: Device\r\n')
            self.sock.write(b'Username: '+bytes(username, 'ascii')+b'\r\n')
            self.sock.write(b'Password: '+bytes(password, 'ascii')+b'\r\n')
            self.sock.write(b'Email: ' + bytes(email, 'ascii')+b'\r\n\r\n')
            while not self.hop_id:
                if handshake_start + self.handshake_timeout <= time.time():
                    self.close()
                    raise Exception('Socket handshake timeout.')
                data = ([x.strip() for x in self.sock.readline().decode(
                    'ascii').split(':')] + ['', ''])[:2]
                if data[0]:
                    print('Handshake:', data)
                    if data[0].lower() == 'hop_id':
                        self.hop_id = data[1]
                else:
                    time.sleep_ms(10)
            print('Hop_ID:', self.hop_id)
            print('URL:', "https://sockethop.netlify.app/" + self.hop_id)

            # attach to dupterm
            self.sock.settimeout(0.0)
            if hasattr(os, 'dupterm_notify'):
                self.sock.setsockopt(socket.SOL_SOCKET, 20, os.dupterm_notify)
            os.dupterm(self.sock)

            # ready
            print('REPL HOP open.')

        except Exception as e:
            sys.print_exception(e)
            print('REPL HOP failed.')
            self.close()

    def close(self, show=True):
        os.dupterm(None)
        try:
            # socket.shutdown is not an option
            self.sock.close()
        except Exception as e:
            if show:
                sys.print_exception(e)
                print('REPL HOP close error.')
        self.addr = None
        self.sock = None
        self.hop_id = None
        if show:
            print('REPL HOP closed.')
