#!/usr/bin/env python3

import socket
import os
import sys

class Client:
    def __init__(self, server_name, server_port):
        self.server_name = server_name
        self.server_port = server_port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.settimeout(20)
        self.retry = True

    def connect_control(self):
        while self.retry:
            print("\nWaiting...")

            try:
                self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.control_socket.connect((self.server_name, self.server_port))
                print("Connected!")
                try:
                    self.control_loop()
                except Exception as e:
                    print("Something else went wrong! Forced termination.")
                    print(e)
                self.retry = False
            except:
                print("Something went wrong with the connection!")
                bool_continue = False
                while not bool_continue:
                    str_continue = input('Would you like to try to connect again? ')
                    if str_continue.lower() == "yes":
                        self.retry = True
                        bool_continue = True
                    elif str_continue.lower() == "no":
                        self.retry = False
                        bool_continue = True
                    else:
                        print("Please say 'Yes' or 'No'")

            self.control_socket.close()

    def control_loop(self):
        not_finished = True
        print("\nCommands:\nget <file name> (download file from server)\nput <file name>(upload file to server)\nls (lists files from server)\nquit (disconnects from server and exits)\n")

        while not_finished:
            input_initial = input('ftp> ')
            input_string = input_initial.split(' ', 1)

            if input_string[0].lower() == "get" and len(input_string) == 2:
                file_obtained = False
                file_obtained = self.get_command(input_string[1])

                if file_obtained:
                    print(input_string[1], " downloaded!\n")
                else:
                    print(input_string[1], " was not downloaded...\n")
            elif input_string[0].lower() == "put" and len(input_string) == 2:
                try:
                    file_object = open(input_string[1], 'rb')
                    file_data = file_object.read()
                    self.put_command(input_string[1], file_data)
                except Exception as e:
                    print(input_string[1], " is not recognized. Please try again.")
            elif input_string[0].lower() == "ls":
                list = self.ls_command(input_string[0])
                print("List from server:\n", list, "\n")
            elif input_string[0].lower() == "quit":
                not_finished = self.quit_command(input_string[0]);
            else:
                print("Please enter one of the commands.")

    def get_command(self, file_name):
        bytes_sent = 0
        tmp_string = "gets"

        while bytes_sent < 4:
            bytes_sent += self.control_socket.send(tmp_string[bytes_sent:].encode())

        print("\nEstablishing temporary socket connection for exchange...")

        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(('', 0))
        data_socket.settimeout(20)
        bytes_sent = 0
        data_port_number = str(data_socket.getsockname()[1])

        while len(data_port_number) < 12:
            data_port_number = "0" + data_port_number

        while bytes_sent < len(data_port_number):
            bytes_sent += self.control_socket.send(data_port_number[bytes_sent:].encode())
            
        try:
            data_socket.listen(1)
            connected_socket, addr = data_socket.accept()
            print("Connection established! Sending file name...")
            file_name_size = str(len(file_name))

            while len(file_name_size) < 12:
                file_name_size = "0" + file_name_size

            bytes_sent = 0

            while len(file_name_size) > bytes_sent:
                bytes_sent += connected_socket.send(file_name_size[bytes_sent:].encode())

            bytes_sent = 0

            while len(file_name) > bytes_sent:
                bytes_sent += connected_socket.send(file_name[bytes_sent:].encode())

            receive_buffer = ""
            temporary_buffer = ""

            while len(receive_buffer) < 1:
                temporary_buffer = connected_socket.recv(1)

                if not temporary_buffer:
                    print("Error. Could not determine if file exists in server.")
                    break

                receive_buffer += temporary_buffer.decode()

            file_exists = int(receive_buffer)

            if file_exists == 1:
                print("File exists in the server! Beginning download...")
                receive_buffer = ""
                temporary_buffer = ""

                while len(receive_buffer) < 12:
                    temporary_buffer = connected_socket.recv(12)

                    if not temporary_buffer:
                        print("Error. Could not receive size of file data.")
                        break

                    receive_buffer += temporary_buffer.decode()

                file_data_size = int(receive_buffer)
                receive_buffer = "".encode()
                temporary_buffer = ""

                while len(receive_buffer) < file_data_size:
                    temporary_buffer = connected_socket.recv(file_data_size)

                    if not temporary_buffer:
                        print("Error. Could not receive file data.")
                        break

                    receive_buffer += temporary_buffer

                file_data = receive_buffer
                f = open(file_name, 'wb')
                f.write(file_data)
                f.close()
                bytes_sent = 0

                while 1 > bytes_sent:
                    bytes_sent += connected_socket.send("1".encode())
                
                connected_socket.close()
                data_socket.close()
                print("Total transfer size: ", int(file_data_size), " bytes")
                return True
            else:
                print("File does not exist in the server.")
                connected_socket.close()
                data_socket.close()
                return False
        except Exception as e:
            print("Something occurred to the temporary connection!\n")
            data_socket.close()
            return False

    def put_command(self, file_name, file_data):
        bytes_sent = 0
        tmp_string = "puts"

        while bytes_sent < 4:
            bytes_sent += self.control_socket.send(tmp_string[bytes_sent:].encode())

        print("\nEstablishing temporary socket connection for exchange...")
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(('', 0))
        data_socket.settimeout(20)
        bytes_sent = 0
        data_port_number = str(data_socket.getsockname()[1])

        while len(data_port_number) < 12:
            data_port_number = "0" + data_port_number

        while bytes_sent < len(data_port_number):
            bytes_sent += self.control_socket.send(data_port_number[bytes_sent:].encode())

        try:
            data_socket.listen(1)
            connected_socket, addr = data_socket.accept()
            print("Connection established! Sending file name...")
            file_name_size = str(len(file_name))

            while len(file_name_size) < 12:
                file_name_size = "0" + file_name_size
                
            bytes_sent = 0

            while len(file_name_size) > bytes_sent:
                bytes_sent += connected_socket.send(file_name_size[bytes_sent:].encode())
                
            bytes_sent = 0

            while len(file_name) > bytes_sent:
                bytes_sent += connected_socket.send(file_name[bytes_sent:].encode())

            print("File name sent! Sending file data...")
            file_data_size = str(len(file_data))

            while len(file_data_size) < 12:
                file_data_size = "0" + file_data_size

            bytes_sent = 0

            while len(file_data_size) > bytes_sent:
                bytes_sent += connected_socket.send(file_data_size[bytes_sent:].encode())

            bytes_sent = 0

            while len(file_data) > bytes_sent:
                bytes_sent += connected_socket.send(file_data[bytes_sent:])

            temporary_buffer = ""
            data_buffer = ""
            received = False

            while len(data_buffer) != 1:
                temporary_buffer = connected_socket.recv(1)

                if not temporary_buffer:
                    print("Could not determine if server obtained file.")
                    break
                    
                data_buffer += temporary_buffer.decode()

            connected_socket.close()

            if data_buffer == "1":
                print("Total transfer size: ", int(file_data_size), " bytes")
                print(file_name, " uploaded to server!\n")
        except Exception as e:
            print("Something occurred to the temporary connection!\n")

        data_socket.close()

    def ls_command(self, input_string):
        bytes_sent = 0
        tmp_string = "lsls"

        while bytes_sent < 4:
            bytes_sent += self.control_socket.send(tmp_string[bytes_sent:].encode())

        print("\nEstablishing temporary socket connection for exchange...")
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        data_socket.bind(('', 0))
        data_socket.settimeout(20)
        bytes_sent = 0
        data_port_number = str(data_socket.getsockname()[1])

        while len(data_port_number) < 12:
            data_port_number = "0" + data_port_number

        while bytes_sent < len(data_port_number):
            bytes_sent += self.control_socket.send(data_port_number[bytes_sent:].encode())

        try:
            data_socket.listen(1)
            connected_socket, addr = data_socket.accept()
            print("Connection established! Grabbing list...")
            temporary_buffer = ""
            data = ""

            while len(data) != 12:
                temporary_buffer = connected_socket.recv(12)

                if not temporary_buffer:
                    print("Error. Size of list cannot be determined.")
                    break

                data += temporary_buffer.decode()

            data2 = ""

            if data.isdigit():
                temporary_buffer2 = ""

                while len(data2) < int(data):
                    temporary_buffer2 = connected_socket.recv(int(data))

                    if not temporary_buffer:
                        print("Error. Cannot read list.")
                        break

                    data2 += temporary_buffer2.decode()
            else:
                print("Error. Size of list was not given.")

            connected_socket.close()
            data_socket.close()
            return data2
        except:
            print("Temporary connection failed!")
            data_socket.close()

    def quit_command(self, input_string):
        bytes_sent = 0

        while bytes_sent < len(input_string):
            bytes_sent += self.control_socket.send(input_string[bytes_sent:].encode())

        temporary_buffer = ""
        data = ""

        while len(data) != 3:
            temporary_buffer = self.control_socket.recv(3)

            if not temporary_buffer:
                print("Error.")
                break

            data += temporary_buffer.decode()

        print("\nDisconnected from server.")

        if data == "ack":
            print("Server acknowledges disconnection.")
        else:
            print("Unknown if Server acknowledges disonnnection.")

        return False


def main():
    if len(sys.argv) != 3 or not isinstance(sys.argv[1], str) or not sys.argv[2].isdigit():
        print("\nInvalid entry! Please use the following format if Windows:\npy " + sys.argv[0] +  " <server_name> <server_port [integer]>")
        print("\nUse the following format if linux:\npython3 " + sys.argv[0] + " <server_name> <server_port [integer]>")
        sys.exit()

    client = Client(sys.argv[1], int(sys.argv[2]))
    client.connect_control()
    print("\nFinished.")

main()