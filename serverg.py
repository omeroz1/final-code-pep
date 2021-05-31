import io
import logging
import os
import queue
import socket
import threading

import edit_image

IP = "10.100.102.7"
PORT = 58454
COMMANDS = {"exit": 0,
            "sendimg": 1,
            "admin": 2,
            "recvimg": 3,
            "reqedit": 4,
            "comix": 5,
            "grey": 6,
            "bw": 7,
            "sharpness": 8,
            "contrast": 9,
            "brightness": 10,
            "color": 11,
            "crop": 12,
            "resize": 13,
            "rotate": 14,
            "vid": 15,
            "id": 16,
            "view": 17}


class Thread(threading.Thread):
    """
    creates a new thread.
    the thread's name is the given name
    the thread's target is the given function
    """

    def __init__(self, func, args, name):
        threading.Thread.__init__(self, target=func, args=args, name=name)
        # self.start()


DATA_Q = queue.Queue()


class Image:
    """
    creates an Image object.
    image_size -> the size of the image
    image -> the original image
    recent_image -> the recent image that was sent to the client
    """

    def __init__(self):
        self.image_size = 0
        self.image = None  # original image
        self.recent_image = None  # recent
        self.image_name = ""

    def get_image_size(self):
        return self.image_size

    def set_image_size(self, image_size):
        self.image_size = image_size

    def get_image(self):
        return self.image

    def set_image(self, image):
        self.image = image

    def get_recent_image(self):
        return self.recent_image

    def set_recent_image(self, image):
        self.recent_image = image

    def get_image_name(self):
        return self.image_name

    def set_image_name(self, name):
        self.image_name = name


image_obj = Image()


class RecvData:
    def __init__(self, command, cmd_size, data, image_name, first_extra, second_extra, client_socket):
        self.command = command
        self.cmd_size = cmd_size
        self.data = data
        self.image_name = image_name
        self.first_extra = first_extra
        self.second_extra = second_extra
        self.client_socket = client_socket

    def get_command(self):
        return self.command

    def get_command_size(self):
        return self.cmd_size

    def get_data(self):
        return self.data

    def get_name(self):
        return self.image_name

    def get_first_extra(self):
        return self.first_extra

    def get_second_extra(self):
        return self.second_extra

    def get_client(self):
        return self.client_socket

    def set_image_name(self, image_name):
        self.image_name = image_name


class Busy:
    def __init__(self):
        self.is_busy = False

    def check_if_busy(self):
        return self.is_busy

    def start_edit(self):
        self.is_busy = True

    def stop_edit(self):
        self.is_busy = False


b1 = Busy()


class IDlist:
    def __init__(self):
        self.id_list = []
        self.id_count = 0
        self.client_socket_list = []
        self.client_list_count = 0

    def add_id(self, id):
        self.id_list.append(id)
        self.id_count += 1

    def remove_id(self, id):
        for i in range(len(self.id_list)):
            if self.id_list[i] == id:
                self.id_list[i] = None

    def check_if_id_exists(self, id):
        for i in range(len(self.id_list)):
            if self.id_list[i] == id:
                return True
        return False

    def show_id_list(self):
        return self.id_list

    def add_client_to_list(self, client):
        self.client_socket_list.append(client)
        self.client_list_count += 1

    def remove_client_from_list(self, client):
        for i in range(len(self.client_socket_list)):
            if self.client_socket_list[i] == client:
                self.client_socket_list[i] = None


id_list = IDlist()


def main():
    consumer_thread = threading.Thread(target=handler_queue)
    consumer_thread.start()
    logging.info("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.listen(5)
    logging.info("Listening for clients...")
    while True:
        connection, client_address = server_socket.accept()
        logging.info("New client joined! Client ip and port: [{}].".format(client_address))
        recv_thread = Thread(handler_thread, (connection,), client_address[0])
        recv_thread.start()


def handler_queue():
    global DATA_Q
    while True:
        if not DATA_Q.empty():
            logging.info("command queue isn't empty")
            que = DATA_Q.get()
            command = que.get_command()
            cmd_size = que.get_command_size()
            img_data = que.get_data()
            image_name = que.get_name()
            first_extra = que.get_first_extra()
            second_extra = que.get_second_extra()
            client_sock = que.get_client()
            if command == 'exit':
                client_sock.close()
                logging.info("program finished successfully")
            valid, error_msg = check_client_request(command)
            if valid:
                response = handle_client_request(command, img_data)
                send_response_to_client(response, image_name, client_sock, extra1=first_extra, extra2=second_extra)
            else:
                send_response_to_client(error_msg, image_name, client_sock, extra1=first_extra, extra2=second_extra)


def handler_thread(client_socket):
    global DATA_Q
    while True:
        command, cmd_size, data, image_name, first_extra, second_extra = receive_client_request(client_socket)
        rd = RecvData(command, cmd_size, data, image_name, first_extra, second_extra, client_socket)
        DATA_Q.put(rd)


def receive_client_request(client_socket):
    """
    receives from the client:
    command -> request from client. should be in the COMMAND list.
    size -> the size of the image (if the command is 'sendimg') or the size of the command itself.
    data -> the image data when the command is 'sendimg'.
    :param client_socket: the client socket
    """
    global image_obj
    command = ""
    cmd_size = ""
    data = ""
    image_name = ""
    img_size = ""
    first_extra = ""
    second_extra = ""
    data = data.encode()

    command_tav = None
    while command_tav != '#':
        command_tav = client_socket.recv(1)
        command_tav = command_tav.decode()
        command += command_tav
    command = command[:-1]
    size_command_tav = None
    while size_command_tav != '#':
        size_command_tav = client_socket.recv(1)
        size_command_tav = size_command_tav.decode()
        cmd_size += size_command_tav
    cmd_size = cmd_size[:-1]
    if command == "sendimg":  # need to extract image size and image name
        size_image_tav = None
        while size_image_tav != '#':
            size_image_tav = client_socket.recv(1)
            size_image_tav = size_image_tav.decode()
            img_size += size_image_tav
        img_size = img_size[:-1]
        image_obj.set_image_size(img_size)

        img_name_tav = None
        while img_name_tav != '#':
            img_name_tav = client_socket.recv(1)
            img_name_tav = img_name_tav.decode()
            image_name += img_name_tav
        image_name = image_name[:-1]
        image_obj.set_image_name(image_name)

        count = 0  # receiving the image data from the client
        while count < int(img_size):
            semi_data = client_socket.recv(1024)
            data += semi_data
            count += len(semi_data)

        return command, int(cmd_size), data, image_name, None, None

    elif command == "color" or command == "crop" or command == "resize" or command == "view":
        # need to extract 2 edit extras
        first_extra_tav = None
        while first_extra_tav != '#':
            first_extra_tav = client_socket.recv(1)
            first_extra_tav = first_extra_tav.decode()
            first_extra += first_extra_tav
        first_extra = first_extra[:-1]

        second_extra_tav = None
        while second_extra_tav != '#':
            second_extra_tav = client_socket.recv(1)
            second_extra_tav = second_extra_tav.decode()
            second_extra += second_extra_tav
        second_extra = second_extra[:-1]

        return command, int(cmd_size), None, None, first_extra, second_extra

    elif command == "sharpness" or command == "brightness" or command == "contrast" or command == "rotate" \
            or command == "vid" or command == "id":  # need to extract one edit extra
        first_extra_tav = None
        while first_extra_tav != '#':
            first_extra_tav = client_socket.recv(1)
            first_extra_tav = first_extra_tav.decode()
            first_extra += first_extra_tav
        first_extra = first_extra[:-1]

        return command, int(cmd_size), None, None, first_extra, None

    logging.info("THE COMMAND IS: '{}'. THE IMAGE SIZE IS: {}".format(command, img_size))
    return command, int(cmd_size), None, None, None, None


def check_client_request(command):
    if command in COMMANDS:
        return True, None
    return False, "Command does not exist!"


def handle_client_request(command, data):
    # all of the return values should be the same length
    if command == "sendimg":
        with open('img_to_server.jpg', 'ab') as f:
            f.write(data)
            logging.info("LEN OF THE IMG DATA IS: {}".format(len(data)))
            f.close()
            logging.info('transfer completed!')
        image_to_server_path = os.path.abspath('img_to_server.jpg')
        image = edit_image.read_image(image_to_server_path)
        image_obj.set_image(image)
        return 'sent'
    if command == "recvimg":
        return 'recv'
    if command == "admin":
        return 'omer'
    if command == "reqedit":
        if b1.check_if_busy() is False:
            b1.start_edit()
            return "strt"
        else:
            return "wait"
    else:
        return command


def send_image_to_client(image, client_socket):
    """
    send image to the server with command 'recvimg'
    """
    img_byte_arr = io.BytesIO()
    image_obj.set_recent_image(image)
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    length = len(str(int(len(img_byte_arr))))
    size = int(len(img_byte_arr))
    logging.info("the image size is: {}".format(int(len(img_byte_arr))))
    if length < 10:
        data = "0" + str(length) + "#" + str(size) + "#"
    else:
        data = str(length) + "#" + str(size) + "#"
    client_socket.send(data.encode())
    logging.info('sending to the server img size data: {}'.format(data))
    count = 0
    while count < int(len(img_byte_arr)):
        if count - int(len(img_byte_arr)) < 1024:
            client_socket.send(img_byte_arr)
            break
        client_socket.send(img_byte_arr[0:1024])
        img_byte_arr = img_byte_arr[1024:]
        count += int(len(img_byte_arr[0:1024]))
    b1.stop_edit()
    logging.info("image sent successfully to the client!")


def check_valid_id(unknown_id, client_socket):
    if id_list.check_if_id_exists(unknown_id):
        send_response_to_client("vald", None, client_socket, None, None)
        # SEND THE RECENT IMAGE TO THE CLIENT
        id_list.add_client_to_list(client_socket)
        send_image_to_client(image_obj.get_recent_image(), client_socket)
    else:
        send_response_to_client("unvd", None, client_socket, None, None)


def send_img_from_db(id, version, client_socket):
    p = os.getcwd()
    semi_path = os.path.join(p, str(id))
    full_path = os.path.join(semi_path, str(version))
    img_name = os.listdir(full_path)[0]
    image = edit_image.read_image(os.path.join(full_path, img_name))
    send_archived_data(str(id), str(version), client_socket)
    send_image_to_client(image, client_socket)


def send_archived_data(id, version, client_socket):
    if len(version) < 10:
        version = "0" + version
    protocol = "{}#{}#".format(id, version)
    logging.info("the archived image extra data protocol: {}".format(protocol))
    client_socket.send(protocol.encode())


def send_response_to_client(response, image_name, client_socket, extra1, extra2):
    image_name = image_obj.get_image_name()
    logging.info('the server response is: {}'.format(response))
    if response == 'recv':
        client_socket.send(response.encode())
        logging.info("sending image to the client (:")
        logging.info("image path is: {}".format(image_name))
        send_image_to_client(image_obj.get_image(), client_socket)
    elif response == "view":
        # the server extracts the image from its database
        p = os.getcwd()
        path = os.path.join(p, str(extra1))
        full_path = os.path.join(path, str(extra2))
        if os.path.exists(full_path):  # check if id exists
            client_socket.send('xrcv'.encode())  # xrcv is the response when the image is archived
            send_img_from_db(extra1, extra2, client_socket)
        else:
            client_socket.send('novw'.encode())  # cannot view
    elif response == "vid":
        client_socket.send("okid".encode())
        edit_image.save_to_dir(image_obj.get_image(), int(extra1), image_name)
        id_list.add_id(str(extra1))
        id_list.add_client_to_list(client_socket)
        logging.info("ID list: {}".format(id_list.show_id_list()))
    elif response == "id":
        check_valid_id(str(extra1), client_socket)
    elif response == "comix":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("comix", client_socket, None, None)
    elif response == "grey":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("grey", client_socket, None, None)
    elif response == "bw":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("bw", client_socket, None, None)
    elif response == "sharpness":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("sharpness", client_socket, int(extra1), None)
    elif response == "contrast":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("contrast", client_socket, int(extra1), None)
    elif response == "brightness":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("brightness", client_socket, int(extra1), None)
    elif response == "rotate":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("rotate", client_socket, int(extra1), None)
    elif response == "color":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("color", client_socket, extra1, int(extra2))
    elif response == "crop":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("crop", client_socket, int(extra1), int(extra2))
    elif response == "resize":
        for client_socket in id_list.client_socket_list:
            client_socket.send('recv'.encode())
            handle_image_edit("resize", client_socket, int(extra1), int(extra2))
    else:
        client_socket.send(response.encode())


def handle_image_edit(request, client_socket, extra1, extra2):
    if request == "comix":
        comix_image = edit_image.comix_image(image_obj.get_image())
        send_image_to_client(comix_image, client_socket)
    if request == "grey":
        grey_image = edit_image.gray_image(image_obj.get_image())
        send_image_to_client(grey_image, client_socket)
    if request == "bw":
        bw_image = edit_image.bw_image(image_obj.get_image())
        send_image_to_client(bw_image, client_socket)
    if request == "contrast":
        contrast_image = edit_image.contrast_image(image_obj.get_image(), amount=extra1)
        send_image_to_client(contrast_image, client_socket)
    if request == "brightness":
        brightness_image = edit_image.brightness_image(image_obj.get_image(), amount=extra1)
        send_image_to_client(brightness_image, client_socket)
    if request == "sharpness":
        sharpness_image = edit_image.sharpness_image(image_obj.get_image(), amount=extra1)
        send_image_to_client(sharpness_image, client_socket)
    if request == "color":
        color_image = edit_image.change_image_color(image_obj.get_image(), color=extra1, level=extra2)
        send_image_to_client(color_image, client_socket)
    if request == "crop":
        crop_image = edit_image.crop_image(image_obj.get_image(), 0, 0, xbottom=extra1, ybottom=extra2)
        send_image_to_client(crop_image, client_socket)
    if request == "resize":
        resize_image = edit_image.resize_image(image_obj.get_image(), height=extra1, width=extra2)
        send_image_to_client(resize_image, client_socket)
    if request == "rotate":
        rotate_image = edit_image.rotate_image(image_obj.get_image(), angle=extra1)
        send_image_to_client(rotate_image, client_socket)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] SERVER: %(message)s')
    main()
