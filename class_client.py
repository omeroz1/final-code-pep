import logging
import os
import queue
import socket
import threading

from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
import login_window


def open_gui(client):
    """
    open graphic user interface
    :param client: client socket
    """
    gui = login_window.LoginWindow(client)
    gui.start()


class ComData:
    """
    an object of command and data
    command -> from the COMMAND list
    data -> image data, encoded
    edit_extras -> more variables for the edit (level, color, amount)
    """

    def __init__(self, command, data, edit_extras):
        self.command = command
        self.data = data
        self.edit_extras = edit_extras

    def get_command(self):
        return self.command

    def get_data(self):
        return self.data

    def get_edit_extras(self):
        return self.edit_extras

    def set_command(self, command):
        self.command = command

    def set_data(self, data):
        self.data = data

    def set_edit_extras(self, edit_extras):
        self.edit_extras = edit_extras


class ID:
    """
    id -> stores the ID code of the image.
    version -> in case there is already a directory of the id, I use the version to create another directory.
    """

    def __init__(self):
        self.id = None
        self.version = 0
        self.path = None

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_version(self):
        return self.version

    def set_version(self, version):
        self.version = version

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path


client_id = ID()


class Client:
    """
    the client class
    """

    def __init__(self):
        """
        initializing the class
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER_IP = '10.100.102.7'
        self.SERVER_PORT = 58454
        self.COMMANDS = {"exit": 0,
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
        self.qcomdata = queue.Queue()
        self.receive_image_approval = False
        self.image_count = 0
        self.start_edit = False
        self.wait_for_edit = False
        self.update_image_approval = False
        self.valid_id = False
        self.wrong_id = False
        self.receive_view_request = False
        self.no_archive_image = False
        self.lock = threading.Lock()

    def start(self):
        """
        runs the client
        """
        self.gui_thread = threading.Thread(target=open_gui, args=(self,))  # creates a thread that will open the gui
        self.gui_thread.start()

        self.client_socket.connect((self.SERVER_IP, self.SERVER_PORT))  # open socket with the server

        self.done = False
        # loop until user requested to exit
        while not self.done:
            if self.qcomdata is not None:  # request will appear when you click an edit button
                command_data = self.qcomdata.get()
                self.request = command_data.get_command()
                self.img_data = command_data.get_data()
                self.edit_extras = command_data.get_edit_extras()
                if self.valid_request(self.request):
                    logging.info("the request given is: {}".format(self.request))
                    self.send_request_to_server()
                    self.response = self.receive_server_response(self.client_socket)
                    self.handle_server_response(self.client_socket, self.response)
                    if self.request == 'exit':
                        self.done = True
                else:
                    logging.info("Please enter a valid request!")
        self.client_socket.close()

    def set_request_data(self, request, data, edit_extras):
        """
        sets the request and data of the client.
        requests are from the COMMANDS dictionary
        :param request:
        """
        self.receive_image_approval = False
        if request == "vid":
            client_id.set_id(int(edit_extras[0]))
        cd = ComData(request, data, edit_extras)
        self.qcomdata.put(cd)

    def get_request(self):
        """
        :return: the request adn image data
        """
        return self.qcomdata.get()

    def valid_request(self, request):
        """
        check if the request is valid
        :param request:
        :return:
        """
        self.requestList = request.split()
        self.realRequest = self.requestList[0].strip()
        if self.realRequest in self.COMMANDS:
            return True
        return False

    def send_request_to_server(self):
        """
        send the request to the server
        protocol builder
        """
        # in recvimg theres an option to send the verson of the image to get the specific img
        cmd_length = len(self.request)
        if self.request == "sendimg":
            img_size = self.get_num_pixels(self.filename)
            logging.info("img length is {}".format(img_size))
            data = self.request + "#" + "0" + str(cmd_length) + "#" + str(img_size) + "#" + \
                   self.filename.split('\\')[-1] + "#"
            logging.info("the protocol format of the request: {}".format(data))
            self.client_socket.send(data.encode())
            self.client_socket.send(self.img_data)
        else:
            if self.edit_extras is not None:  # build a protocol with the extra variables for the edit
                # edit extras -> extra var for the edit (color, level, amount).
                if len(self.edit_extras) == 2:
                    if cmd_length < 10:
                        data = self.request + "#" + "0" + str(cmd_length) + "#" + str(self.edit_extras[0]) + \
                               "#" + str(self.edit_extras[1]) + "#"
                    else:
                        data = self.request + "#" + str(cmd_length) + "#" + str(self.edit_extras[0]) + "#" + \
                               str(self.edit_extras[1]) + "#"
                elif len(self.edit_extras) == 1:
                    if cmd_length < 10:
                        data = self.request + "#" + "0" + str(cmd_length) + "#" + str(self.edit_extras[0]) + "#"
                    else:
                        data = self.request + "#" + str(cmd_length) + "#" + str(self.edit_extras[0]) + "#"
            else:
                if cmd_length < 10:
                    data = self.request + "#" + "0" + str(cmd_length) + "#"
                else:
                    data = self.request + "#" + str(cmd_length) + "#"
            logging.info("the protocol format of the request: {}".format(data))
            self.client_socket.send(data.encode())

    def get_num_pixels(self, filename):
        """
        :param self.filename: image's path
        :return: the image's size in pixels
        """
        return os.path.getsize(filename)

    def receive_server_response(self, client_socket):
        """
        the server returns 4 letters word
        """
        response_from_server = client_socket.recv(4)
        return response_from_server.decode()

    def handle_server_response(self, client_socket, response):
        """
        deals with the protocol.
        this func takes from the request the image size and length size
        xrcv -> the "recv" command especially for the archived images.
        """
        logging.info("the server's response: {}".format(response))
        self.receive_image_approval = False
        if response == "recv":
            len_in_size = client_socket.recv(2)
            len_in_size = len_in_size.decode()
            client_socket.recv(1)  # get rid of the first #
            logging.info("len is:{}".format(len_in_size))
            img_size = client_socket.recv(int(len_in_size))
            img_size = img_size.decode()
            client_socket.recv(1)  # get rid of the last #
            logging.info("img_size is:{}".format(img_size))
            count = 0
            self.client_image_name = 'img_to_client_ver_{}.jpg'.format(self.image_count)
            with open(self.client_image_name, 'ab') as f:
                while count < int(img_size):
                    data = client_socket.recv(int(img_size))
                    count += len(data) # (for debugging purposes
                    f.write(data)
            # self.image_from_server = open(self.client_image_name, 'rb')
            logging.info('image received to the client!')
            self.image_received()
            self.image_count += 1
            if self.request == "reqedit":
                self.response = self.receive_server_response(self.client_socket)
                print(self.response)
                if self.response == "strt":
                    self.start_edit = True
                    print("start edit is true")
                elif self.response == "wait":
                    print("wait")
                    self.wait_for_edit = True

        elif response == "xrcv":  # xrcv -> the "recv" command especially for the archived images.
            self.archive_id = client_socket.recv(8)  # archive image id
            self.archive_id = self.archive_id.decode()
            client_socket.recv(1)  # get rid of the first #
            self.archive_version = client_socket.recv(2)  # archive image id
            self.archive_version = self.archive_version.decode()
            client_socket.recv(1)  # get rid of the first #
            len_in_size = client_socket.recv(2)
            len_in_size = len_in_size.decode()
            client_socket.recv(1)  # get rid of the first #
            img_size = client_socket.recv(int(len_in_size))
            img_size = img_size.decode()
            client_socket.recv(1)  # get rid of the last #
            archive_img_name = 'archived_{}_{}.jpg'.format(self.archive_id, self.archive_version)
            with open(archive_img_name, 'ab') as f:
                data = client_socket.recv(int(img_size))
                f.write(data)
            self.receive_view_request = True
            self.archived_image = open(archive_img_name, 'rb')
            logging.info('archived image received to the client!')

        elif response == "sent":
            self.send_image_approval = True

        elif response == "strt":
            self.start_edit = True

        elif response == "wait":
            self.wait_for_edit = True

        elif response == "vald":  # if the id is vald, prepare to receive the image from the other client.
            len_in_size = client_socket.recv(2)
            len_in_size = len_in_size.decode()
            client_socket.recv(1)  # get rid of the first #
            logging.info("len is:{}".format(len_in_size))
            img_size = client_socket.recv(int(len_in_size))
            img_size = img_size.decode()
            client_socket.recv(1)  # get rid of the last #
            logging.info("img_size is:{}".format(img_size))
            self.client_image_name = 'img_to_client_ver_{}.jpg'.format(self.image_count)
            with open(self.client_image_name, 'ab') as f:
                data = client_socket.recv(int(img_size))
                # count += len(data) # (for debugging purposes
                f.write(data)
            self.image_count += 1
            # self.image_from_server = open(self.client_image_name, 'rb')
            logging.info('image received to the client!')
            self.image_received()
            self.valid_id = True

        elif response == "unvd":
            self.wrong_id = True

        elif response == "novw":
            self.no_archive_image = True

        elif response == "exit":
            # TODO: exit button on gui (edit window)
            client_socket.close()

    def image_received(self):
        self.lock.acquire()
        self.receive_image_approval = True
        self.lock.release()

    def receive_image_approval_status(self):
        self.lock.acquire()
        ria = self.receive_image_approval
        self.lock.release()
        return ria

    def create_client_directory(self):
        path = os.getcwd()
        full_path = os.path.join(path, str(client_id.get_id()))
        if os.path.exists(full_path):
            os.mkdir(os.path.join(full_path, str("client_" + str(client_id.get_version()))))
            client_id.set_version(client_id.get_version() + 1)
            client_id.set_path(os.path.join(full_path, str(client_id.get_version())))
        else:
            os.mkdir(full_path)
            client_id.set_path(full_path)

    def get_client_image_name(self):
        return self.client_image_name

    def get_client_original_image(self):
        return 'img_to_client_ver_0.jpg'

    def get_image_from_server(self):
        return self.image_from_server

    def send_image(self, filename):
        """
        sends the image to te server
        :param filename: image's path
        """
        self.filename = filename
        image_name = filename.split('\\')[-1]
        logging.info(image_name)
        # self.send_request_to_server(self.client_socket, "sendimg")  # prepares the server for an image
        count = 0
        data = ""
        data = data.encode()
        size = self.get_num_pixels(filename)
        with open(filename, 'rb') as f:
            while count < size:
                l = f.read(1024)
                data += l
                count += len(l)
        self.set_request_data("sendimg", data, None)
        logging.info('image transferred successfully!')


def main():
    client_gui = Client()
    client_gui.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] CLIENT: %(message)s')
    main()
