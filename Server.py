import socket, os, glob, subprocess, shutil
from PIL import ImageGrab

NORMAL_SIZE = 1024
IP = '0.0.0.0'
PORT = 1800

# Commands names
DI = 'DIR'
DE = 'DELETE'
T = 'TAKE_SCREENSHOT'
S = 'SEND_FILE'
C = 'COPY'
EXE = 'EXECUTE'
EXI = 'EXIT'

LAST = 'LAST'.encode()

def receive_client_request(client_socket):
    """
    Receives the full message sent by the client
    Works with the protocol defined in the client's "send_request_to_server" function:
    first the command name,then the parameters
    """

    information_on_string = client_socket.recv(NORMAL_SIZE).decode()
    return information_on_string.split("-")

def check_client_request(command_and_params):
    """
    Checking if the parameters are valid
    """

    valid, msg = False, "-+-"

    if command_and_params[0] == C:
        valid, msg = check__copy(command_and_params[1], command_and_params[2])

    elif command_and_params[0] == S or command_and_params[0] == DI \
            or command_and_params[0] == DE or command_and_params[0] == EXE:
        valid, msg = check__send_file__dir__delete__execute(command_and_params[0], command_and_params[1])

    elif command_and_params[0] == T:
        valid, msg =  check__take_screenshot(command_and_params[1])

    return valid, msg

def check__send_file__dir__delete__execute(command, file_param):
    """
    Checking if the files that the files that some commands need for being execute are exist
    """

    if os.path.exists(file_param):
        return True , "-"

    else:
        return False , command + "+" + command + " command cant work because - " + file_param + \
               " is not exist on the server computer !"

def check__copy(src_file, dst_file):
    """
    Checking if the parameters for "COPY" command are fit for check_client_request function
    """

    dst_files_list = dst_file.split("\\")
    del dst_files_list[-1]
    dst_folder = "\\".join(dst_files_list)

    if os.path.exists(src_file) and os.path.exists(dst_folder):
        return True, "-"

    else:
        if not os.path.exists(src_file):
            return False, C + "+" + C + " command cant be done because - " + src_file +\
                   " is not exist in the server computer !"

        else:
            return False, C + "+" + C + " command cant be done because - " + dst_folder +\
                   " is not exist in the server computer !"

def check__take_screenshot(file_param):
    """
    Checking if the parameters for TAKE_SCREENSHOT command are fit for check_client_request function
    """

    file_param_path = file_param.split('\\')
    del file_param_path[-1]
    dir_folder = '\\'.join(file_param_path)

    if os.path.exists(dir_folder):
        return True , "-"

    else:
        return False , T + "+" + dir_folder + " is not exist on the server computer !"

def handle_client_request(command_plus_params):
    """
     Creating the response to the client
    """

    if command_plus_params[0] == S:
        return send_file_function(command_plus_params[1])

    elif command_plus_params[0] == DE:
        return delete_function(command_plus_params[1])

    elif command_plus_params[0] == C:
        return copy_function(command_plus_params[1], command_plus_params[2])

    elif command_plus_params[0] == DI:
        return dir_function(command_plus_params[1])

    elif command_plus_params[0] == EXE:
       return exe_function(command_plus_params[1])

    elif command_plus_params[0] == T:
        return take_screenshot_function(command_plus_params[1])

def delete_function(file_param):

    if os.path.exists(file_param):
        os.remove(file_param)
    return DE + "+"  + DE + ' command has been done and delete - ' + file_param

def send_file_function(file_param):

    return S + "+" + file_param

def take_screenshot_function(file_param):

    if os.path.exists(file_param):
        os.remove(file_param)
    screenshot_file = ImageGrab.grab()
    screenshot_file.save(file_param)
    return T + "+" + file_param

def dir_function(file_param):

    files_names = "\n".join(glob.glob(file_param + '\*.*'))
    return  DI + "+" + files_names

def exe_function(file_param):

    subprocess.call(file_param)
    return EXE + "+" + EXE +' command has been done and open ' + file_param + '.txt'

def copy_function(src_file_param, dst_file_param):

    shutil.copy(src_file_param , dst_file_param)
    return C + "+" + C + ' command has been done and copied - ' + src_file_param + ' - to - ' + dst_file_param

def send_response_to_client(response, client_socket):
    """
    Create a protocol which sends the response to the client
    The protocol should be able to handle short responses as well as files
    """

    command , message = response.split('+')

    if  command == EXE or command == DI or command == C or command == DE:
        client_socket.send(message.encode())

    elif command == S  or command == T:
        try:
            file = open(message, 'rb+')
            information = file.read(NORMAL_SIZE)

            while information:
                client_socket.send(information)
                ack = client_socket.recv(1024).decode()
                information = file.read(NORMAL_SIZE)
            client_socket.send(LAST)
            file.close()
        except OSError:
            client_socket.send("There is a problem with the file names !".encode())

def main():
    """
    Main function
    """

    # open socket with client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(1)
    client_socket, address = server_socket.accept()
    print(str(address[0]) + " got connected to the server")

    # handle requests until the user asks for exit
    done = False
    while not done:
        try:
            command_plus_params = receive_client_request(client_socket)
            command = command_plus_params[0]
            if command == EXI:
                done = True
            else:
                valid, error_msg = check_client_request(command_plus_params)
                if valid:
                    response = handle_client_request(command_plus_params)
                    send_response_to_client(response, client_socket)
                else:
                    send_response_to_client(error_msg, client_socket)

        except ConnectionResetError:
            print("The connection with the client was forcibly closed")
            done = True

    client_socket.close()
    server_socket.close()


if __name__ == '__main__':
    main()
