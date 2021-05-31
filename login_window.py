from tkinter import Tk, Canvas, Frame

from edit_window import *


class Line(Frame):
    """
    creates a line in the gui.
    to create a line: l = Line()
    """

    def __init__(self):
        super().__init__()
        self.init()

    def init(self):
        self.master.title("Lines")
        self.grid()

        canvas = Canvas(self)
        # canvas.create_line(15, 25, 200, 25)
        canvas.create_line(350, 20, 350, 400, dash=(4, 2), fill="#05f")
        # canvas.create_line(55, 85, 155, 85, 105, 180, 55, 85)

        canvas.grid(row=0, column=1)


def move_to_win1(root, name, client, image):
    """
    moves from the login window to the edit window
    """
    win_edit = EditWindow(root, name, client, image)
    win_edit.start()


def time():
    """
    :return: a greet based on the time
    """
    date = datetime.datetime.now()
    if 6 < int(date.strftime('%H')) <= 12:
        return 'good morning!'
    elif 12 < int(date.strftime('%H')) <= 18:
        return 'good afternoon!'
    elif 18 < int(date.strftime('%H')) <= 20:
        return 'good evening!'
    elif 20 < int(date.strftime('%H')) < 24 or 0 < int(date.strftime('%H')) <= 6:
        return 'good night!'


class LoginWindow:
    """
    the first GUI window
    """

    def __init__(self, client):
        """
        initializing the class of the login window
        :param client: the client socket
        """
        self.root = Tk()
        self.root.title("PEP - photo edit platform")
        self.root.iconbitmap('gallery.ico')
        # self.bg = PhotoImage(file='bg2.png')
        # self.place_bg = Label(self.root, image=self.bg)
        # self.place_bg.place(x=0, y=0, relwidth=1, relheight=1)
        self.root["bg"] = "light blue"
        self.root.geometry("940x480")
        self.client = client
        # self.root.wm_attributes('-transparentcolor', self.root['bg']) # the whole background will be transperent

    def start(self):
        """
        starts to run the window
        """
        self.main_title()
        self.title1()
        self.title2()
        self.enter_name()
        self.enter_name_2()
        self.open_help()
        self.submit_image()
        self.enter_id()
        self.join_client()
        self.lets_edit()
        self.root.mainloop()

    def main_title(self):
        self.title_txt = "Hello! Welcome to PEP - Photo Edit Platform."
        self.title_lbl = Message(self.root, text=self.title_txt, bg="light blue", fg="blue", width=1000, borderwidth=5)
        self.title_lbl.config(font=("Fixedsys", 5))
        self.title_lbl.grid(row=0, column=0, padx=10, pady=10)

        self.title_txt_2 = "Choose between STARTING an edit or JOINING"
        self.title_lbl_2 = Message(self.root, text=self.title_txt_2, bg="light blue", fg="blue", width=1000,
                                   borderwidth=5)
        self.title_lbl_2.config(font=("Fixedsys", 5))
        self.title_lbl_2.grid(row=0, column=2, padx=10, pady=10)

    def title1(self):
        self.msg_txt = "START EDIT -\n  \nTo start an edit\nEnter your name and\nselect an image to edit!"
        self.name_lbl = Message(self.root, text=self.msg_txt, bg="steel blue", fg="blue", width=1000, borderwidth=5)
        self.name_lbl.config(font=("Fixedsys", 5))
        self.name_lbl.grid(row=1, column=0, columnspan=2, sticky='W', padx=20, pady=10)

    def title2(self):
        self.msg_txt_2 = "JOIN EDIT -\n  \nYou can connect to\nan existing client and\nedit with the the image!"
        self.name_lbl_2 = Message(self.root, text=self.msg_txt_2, bg="steel blue", fg="blue", width=1000, borderwidth=5)
        self.name_lbl_2.config(font=("Fixedsys", 5))
        self.name_lbl_2.grid(row=1, column=2, columnspan=2, sticky='W', padx=10, pady=10)

    def enter_name(self):
        """
        asks the client to submit name
        """
        self.step_1 = LabelFrame(self.root, text=" 1. Enter Your Name: ", bg="SteelBlue1")
        self.step_1.grid(row=2, column=0, columnspan=7, sticky='W', padx=20, pady=5, ipadx=5, ipady=5)

        self.name = Entry(self.step_1, bg="SteelBlue1", borderwidth=10, width=30)
        self.name.get()
        self.name.grid(row=2, column=0, ipady=0)

    def enter_name_2(self):
        """
        asks the client to submit name
        """
        self.step_1_id = LabelFrame(self.root, text=" 1. Enter Your Name: ", fg="black", bg="RoyalBlue1")
        self.step_1_id.grid(row=2, column=2, columnspan=7, sticky='W', padx=10, pady=5, ipadx=5, ipady=5)

        self.name = Entry(self.step_1_id, bg="RoyalBlue2", borderwidth=10, width=30)
        self.name.get()
        self.name.grid(row=2, column=2, ipady=0)

    def open_help(self):
        """
        opens the quick help window
        """
        self.helpLf = LabelFrame(self.root, text=" Quick Help ", bg="PaleTurquoise2")
        self.helpLf.grid(row=0, column=9, columnspan=2, rowspan=8, sticky='NS', padx=5, pady=10)
        self.helpLbl = Label(self.helpLf, text="Please Enter Your Name\nand Upload the Image\nyou Want to edit."
                             , bg="PaleTurquoise2")
        self.helpLbl.grid(row=0, sticky="WE", pady=0, padx=0)

    def submit_image(self):
        """
        asks the client to upload image
        """
        self.step_2 = LabelFrame(self.root, text=" 2. Upload Your Image: ", bg="SteelBlue2")
        self.step_2.grid(row=3, columnspan=7, sticky='W', padx=20, pady=20, ipadx=5, ipady=5)
        self.upload_image()

    def upload_image(self):
        """
        button to upload the image
        """
        self.upload_button = Button(self.step_2, text="Browse a File", command=self.file_dialog, bg="SteelBlue3")
        self.upload_button.config(anchor="center")
        self.upload_button.grid(row=5, column=0, padx=10, pady=10)

    def lets_edit(self):
        """
        asks the client to start the edit and move to the EDIT WINDOW
        """
        self.step_3 = LabelFrame(self.root, text=" 3. Lets Edit ! ", bg="SteelBlue3")
        self.step_3.grid(row=4, columnspan=7, sticky='W', padx=20, pady=5, ipadx=5, ipady=5)

        self.b_to_win1 = Button(self.step_3, text="LETS GO!", command=self.submit_name, bg="SteelBlue4")
        self.b_to_win1.config(anchor="center")
        self.b_to_win1.grid(row=4, column=0, padx=5, pady=5, sticky="news")

    def submit_name(self):
        """
        greet the client
        """
        self.greet = "hello {}".format(self.name.get())
        self.name_lbl = Label(self.root, text=self.greet)
        self.name_lbl.grid()
        self.submit_valid_id()

    def file_dialog(self):
        """
        creates the unique id
        open the image file the client wanted
        sets the image path, name, type
        """
        date = datetime.datetime.now()
        new_img.set_id(date.strftime('%d') + date.strftime('%m') + date.strftime('%H') + date.strftime('%M'))
        file_name = filedialog.askopenfilename(initialdir="/", title="Select A File",
                                               filetype=(("jpeg", "*.jpg"), ("png", "*.png")))
        upload_lbl = Label(text="the image {} uploaded successfully!\nclick the 'lets go' button to start edit!" \
                           .format(file_name.split('/')[-1]))
        full_img_name = file_name.split('/')[-1]
        upload_lbl.grid(row=5, column=0, pady=15)
        correct_path = file_name.replace("/", "\\")
        new_img.set_path(correct_path)  # C:\da.jpg
        # latest path: C:\Users\omero\PycharmProjects\pythonProject6\28041041\0
        new_img.set_name(full_img_name.split('.')[0])
        new_img.set_type(full_img_name.split('.')[-1])
        self.client.send_image(filename=new_img.get_path())

    def enter_id(self):
        """
        asks the client to enter a valid image id
        """
        self.step_1_id = LabelFrame(self.root, text=" 2. Enter Image ID: ", fg="black", bg="RoyalBlue2")
        self.step_1_id.grid(row=3, column=2, columnspan=7, sticky='W', padx=10, pady=5, ipadx=5, ipady=5)

        self.image_id = Entry(self.step_1_id, bg="RoyalBlue2", borderwidth=10, width=30)
        self.image_id.get()
        self.image_id.grid(row=3, column=2, ipady=0)

    def join_client(self):
        """
        asks the client to start the edit and move to the EDIT WINDOW
        """
        self.step_2_id = LabelFrame(self.root, text=" 3. Submit ID!", fg="black", bg="RoyalBlue3")
        self.step_2_id.grid(row=4, column=2, columnspan=8, sticky='W', padx=10, pady=5, ipadx=5, ipady=5)

        # check if id is valid, with sending, and move to edit window
        self.b_send_id = Button(self.step_2_id, text="LETS CONNECT", bg="RoyalBlue4", command=self.submit_unknown_id)
        self.b_send_id.config(anchor="center")
        self.b_send_id.grid(row=4, column=2, padx=5, pady=5, sticky="news")

    def submit_unknown_id(self):
        id_list = [self.image_id.get()]
        self.client.set_request_data("id", None, id_list)
        wU = True
        while wU:
            if self.client.valid_id:  # checks the condition
                # NEED TO SEND THE RECENT IMAGE TO MOVE_TO_WIN1
                self.get_image()

                move_to_win1(self.root, self.name, self.client, image=self.image_server)
                wU = False
                self.client.valid_id = False
            if self.client.wrong_id:  # checks the condition
                # SHOW A MESSAGE TO THE CLIENT TO ENTER ID AGAIN
                error_lbl = Label(text="ID not found. please try to enter another ID\nOr upload your own image.")
                error_lbl.grid(row=6, column=0, pady=15)
                wU = False
                self.client.wrong_id = False

    def get_image(self):
        # img_path = (os.path.abspath(self.client.client_image_name))
        # img_dir_path = img_path.rsplit('\\', 1)[0]  # the path's directory of the image given.
        # for example : 'C:\Users\omero\PycharmProjects\pythonProject6'
        self.image_server = open(self.client.client_image_name, 'rb')

    def submit_valid_id(self):
        id_list = [int(new_img.get_id())]
        self.client.set_request_data("vid", None, id_list)
        move_to_win1(self.root, self.name, self.client, None)


def main():
    obj = LoginWindow(None)
    obj.start()


if __name__ == '__main__':
    main()
