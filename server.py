#!/usr/bin/env python3

import socket
import os
import sys

class Server:
    def __init__(self, server_port):
        self.server_port = server_port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.bind(('', self.server_port))
        self.control_socket.settimeout(20)
        self.retry = True

    def connect_control(self):
        while self.retry:
            print("\nListening...")

            try:
                self.control_socket.listen(1)
                connected_socket, addr = self.control_socket.accept()
                print("Accepted connection from client: ", addr)

                try:
                    self.control_loop(connected_socket, addr[0])
                except Exception as e:
                    print("\nSomething else went wrong! Forced termination.")

                self.retry = False
            except:
                print("\nSomething went wrong with the connection!")
                bool_continue = False

                while not bool_continue:
                    str_continue = input('Would you like to try again? ')
                    if str_continue.lower() == "yes":
                        self.retry = True
                        bool_continue = True
                    elif str_continue.lower() == "no":
                        self.retry = False
                        bool_continue = True
                    else:
                        print("Please say 'Yes' or 'No'")

        self.control_socket.close()
        
    def control_loop(self, connected_socket, data_port_server):
        not_finished = True

        while not_finished:
            print("\nWaiting on client request...")
            temporary_buffer = ""
            client_request = ""
            
            while len(client_request) != 4:
                temporary_buffer = connected_socket.recv(4)
                if not temporary_buffer:
                    print("Error. Cannot read request.")
                    connected_socket.send("e".encode())
                    break
                client_request += temporary_buffer.decode()

            if client_request == "gets":
                print("\nClient is trying to download a file from the server. Connecting to temporary port...")
                temporary_buffer = ""
                client_request = ""

                while len(client_request) != 12:
                    temporary_buffer = connected_socket.recv(12)

                    if not temporary_buffer:
                        print("Error. Cannot read data.")
                        connected_socket.send("e".encode())
                        break

                    client_request += temporary_buffer.decode()

                if client_request.isdigit():
                    self.get_request(data_port_server, int(client_request))
                else:
                    connected_socket.send("e".encode())

            elif client_request == "puts":
                print("\nClient is trying to upload a file to the server. Connecting to temporary port...")
                temporary_buffer = ""
                client_request = ""

                while len(client_request) != 12:
                    temporary_buffer = connected_socket.recv(12)

                    if not temporary_buffer:
                        print("Error. Cannot read data.")
                        connected_socket.send("e".encode())
                        break

                    client_request += temporary_buffer.decode()

                if client_request.isdigit():
                    self.put_request(data_port_server, int(client_request))
                else:
                    connected_socket.send("e".encode())

            
            elif client_request == "lsls":
                print("\nClient is requesting list of files. Connecting to temporary port...")
                temporary_buffer = ""
                client_request = ""

                while len(client_request) != 12:
                    temporary_buffer = connected_socket.recv(12)

                    if not temporary_buffer:
                        print("Error. Cannot read data.")
                        connected_socket.send("e".encode())
                        break

                    client_request += temporary_buffer.decode()
                    
                if client_request.isdigit():
                    self.list_request(data_port_server, int(client_request))
                else:
                    connected_socket.send("e".encode())

            elif client_request == "quit":
                not_finished = self.quit_request(connected_socket)
            else:
                print("\nUnknown request. Forcing termination...")
                not_finished = False

    def get_request(self, data_port_server, data_port_number):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.settimeout(20)

        try:
            data_socket.connect((data_port_server, data_port_number))
            print("Temporary connection established!  Grabbing file name...")
            receive_buffer = ""
            temporary_buffer = ""

            while len(receive_buffer) < 12:
                temporary_buffer = data_socket.recv(12)

                if not temporary_buffer:
                    print("Error. Could not receive size of file name.")
                    break

                receive_buffer += temporary_buffer.decode()

            file_name_size = int(receive_buffer)
            receive_buffer = ""
            temporary_buffer = ""

            while len(receive_buffer) < file_name_size:
                temporary_buffer = data_socket.recv(file_name_size)

                if not temporary_buffer:
                    print("Error. Could not receive file name.")
                    break

                receive_buffer += temporary_buffer.decode()

            file_name = receive_buffer

            try:
                file_object = open(file_name, 'rb')
                file_data = file_object.read()
                data_socket.send("1".encode())
                print("File found! Beginning to transfer data...")
                file_data_size = str(len(file_data))

                while len(file_data_size) < 12:
                    file_data_size = "0" + file_data_size

                bytes_sent = 0

                while len(file_data_size) > bytes_sent:
                    bytes_sent += data_socket.send(file_data_size[bytes_sent:].encode())

                bytes_sent = 0

                while len(file_data) > bytes_sent:
                    bytes_sent += data_socket.send(file_data[bytes_sent:])

                temporary_buffer = ""
                data_buffer = ""
                received = False

                while len(data_buffer) != 1:
                    temporary_buffer = data_socket.recv(1)

                    if not temporary_buffer:
                        print("Could not determine if client obtained file.")
                        break

                    data_buffer += temporary_buffer.decode()

                if data_buffer == "1":
                    print(file_name, " sent to client!")
            except Exception as e:
                print("Something was wrong with the file!!")
                data_socket.send("0".encode())
        except Exception as e:
            print("Something went wrong with the temporary connection.")
        data_socket.close()

    def put_request(self, data_port_server, data_port_number):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.settimeout(20)

        try:
            data_socket.connect((data_port_server, data_port_number))
            print("Temporary connection established!  Grabbing file name...")
            receive_buffer = ""
            temporary_buffer = ""
            
            while len(receive_buffer) < 12:
                temporary_buffer = data_socket.recv(12)

                if not temporary_buffer:
                    print("Error. Could not receive size of file name.")
                    break
                
                receive_buffer += temporary_buffer.decode()
                
            file_name_size = int(receive_buffer)
            receive_buffer = ""
            temporary_buffer = ""

            while len(receive_buffer) < file_name_size:
                temporary_buffer = data_socket.recv(file_name_size)

                if not temporary_buffer:
                    print("Error. Could not receive file name.")
                    break

                receive_buffer += temporary_buffer.decode()
                
            file_name = receive_buffer
            print("File name obtained! Beginning download of file data...")
            receive_buffer = ""
            temporary_buffer = ""

            while len(receive_buffer) < 12:
                temporary_buffer = data_socket.recv(12)

                if not temporary_buffer:
                    print("Error. Could not receive size of file data.")
                    break

                receive_buffer += temporary_buffer.decode()

            file_data_size = int(receive_buffer)
            receive_buffer = "".encode()
            temporary_buffer = ""

            while len(receive_buffer) < file_data_size:
                temporary_buffer = data_socket.recv(file_data_size)

                if not temporary_buffer:
                    print("Error. Could not receive file data.")
                    break

                receive_buffer += temporary_buffer

            file_data = receive_buffer
            f = open(file_name, 'wb')
            f.write(file_data)
            f.close()
            print(file_name, " completely downloaded!")
            bytes_sent = 0

            while 1 > bytes_sent:
                bytes_sent += data_socket.send("1".encode())
        except Exception as e:
            print("Something went wrong with the temporary connection.")

        data_socket.close()

    def list_request(self, data_port_server, data_port_number):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.settimeout(20)

        try:
            data_socket.connect((data_port_server, data_port_number))
            print("Temporary connection established!  Compiling list for client...")
            list = ""
            files = [f for f in os.listdir('.') if os.path.isfile(f)]

            for f in files:
                list = list + "\n" + f

            list_size = str(len(list))

            while len(list_size) < 12:
                list_size = "0" + list_size

            bytes_sent = 0

            while len(list_size) > bytes_sent:
                bytes_sent += data_socket.send(list_size[bytes_sent:].encode())

            bytes_sent = 0

            while bytes_sent < len(list):
                bytes_sent += data_socket.send(list[bytes_sent:].encode()) 
        except Exception:
            print("Temporary connection could not be established.")
        data_socket.close()

    def quit_request(self, connected_socket):
        print("\nClient is disconnecting. Sending acknowledgement...")
        bytes_sent = 0
        ack = "ack"

        while bytes_sent < 3:
            bytes_sent += connected_socket.send(ack[bytes_sent:].encode())

        print("Acknowldgement sent!")
        return False

def main():
    if len(sys.argv) != 2 or not sys.argv[1].isdigit():
        print("\nInvalid entry!  Please use the following format if on Windows:\npy " + sys.argv[0] + " <server_port [integer]>")
        print("\nUse the following format if linux:\npython3 " + sys.argv[0] + " <server_name> <server_port [integer]>")
        sys.exit()

    server = Server(int(sys.argv[1]))
    server.connect_control()
    print("\nFinished.")

main()