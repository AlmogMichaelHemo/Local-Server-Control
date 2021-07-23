import socket, os

client_file_path = r'C:\Users\USER\Desktop\client\1.jpeg'
server_file_path = r'C:\Users\USER\Desktop\server\2.jpeg'
server_dir_path = r'C:'
server_delete_file_path = r'C:\Users\USER\Desktop\server\2.jpeg'
server_copy_src_file_path = r'C:\Users\USER\Desktop\server\2.jpeg'
server_copy_dst_file_path = r'C:\Users\USER\Desktop\server_2_copy\2.jpeg'
server_exe_file_path = r'C:\Windows\notepad.exe'

IP = '127.0.0.1'
PORT = 1800
NORMAL_SIZE = 1024
BIG_SIZE = NORMAL_SIZE * 8 # for DIR command

# Commands names
DI = 'DIR'
DE = 'DELETE'
T = 'TAKE_SCREENSHOT'
S = 'SEND_FILE'
C = 'COPY'
EXE = 'EXECUTE'
EXI = 'EXIT'

# Requests lines
DI_REQUEST = DI + "-" + server_dir_path
DE_REQUEST =  DE + "-" + server_delete_file_path
T_REQUEST = T + "-" + server_file_path
S_REQUEST =  S + "-" + server_file_path
C_REQUEST = C + "-" + server_copy_src_file_path + "-" + server_copy_dst_file_path
EXE_REQUEST = EXE + "-" + server_exe_file_path

def valid_request(request):
    """
    Check if the request is valid (included in the available commands)
    """

    return request == C or request == EXI or request == DE or request == S\
           or request == EXE or request == T or request == DI

def send_request_to_server(my_socket, request):
    """
    Send the request to the server. First the length of the request (2 digits), then the request itself
    """

    switch_to_commands = {
        C : C_REQUEST,
        EXI: EXI,
        DE: DE_REQUEST,
        S : S_REQUEST,
        EXE: EXE_REQUEST,
        T : T_REQUEST,
        DI : DI_REQUEST}

    if os.path.exists(client_file_path) and request == T :
            os.remove(client_file_path)

    switch_result = (switch_to_commands.get(request))
    my_socket.send(switch_result.encode())

def handle_server_response(my_socket, request):
    """
    Receive the server's response and handle it, according to the request
   """
    if request == C or request == DE or request == EXE or request == DI :
        server_response = my_socket.recv(NORMAL_SIZE).decode()
        print(server_response)

    elif request == S or request == T :
        try:
            finish = True
            file = open(client_file_path, 'wb+')
            information = my_socket.recv(1024)

            while finish:
                file.write(information)
                my_socket.send('ACK'.encode())
                information = my_socket.recv(1024)
                if information == "LAST".encode():
                    finish=False
            file.close()

            if request == S:
                print(S + " command has been done")

            else:
                print(T + " command has been done and send to you the image")

        except OSError:
            print(my_socket.recv(1024).decode())

def main():
    """
    Main function
    """

    # open socket with the server
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((IP, PORT))

    # printing the instructions
    print('Welcome to remote computer application. Here are the available commands:\n')
    print(' TAKE_SCREENSHOT\n SEND_FILE\n DIR\n DELETE\n COPY\n EXECUTE\n EXIT')

    done = False
    # loop until user requested to exit
    while not done:
        request = input("Please enter command:\n")
        if valid_request(request):
            send_request_to_server(my_socket, request)
            handle_server_response(my_socket, request)
            if request == EXI:
                print("Closing the project")
                done = True
        else:
            print("Your input is not valid!\n"
                  "Please write an Available command from this list :\n"
                  "TAKE_SCREENSHOT\n"
                  "SEND_FILE\n"
                  "DIR\n"
                  "DELETE\n"
                  "COPY\n"
                  "EXECUTE\n"
                  "EXIT")

    my_socket.close()

if __name__ == '__main__':
    main()
