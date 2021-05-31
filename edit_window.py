import datetime
import logging
import os
import time as Time
from tkinter import *
from tkinter import filedialog
from tkinter.messagebox import showinfo

from PIL import ImageTk

import edit_image
from edit_image import new_img


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


def wait_until(condition, output):  # defines function
    wU = True
    while wU == True:
        if condition:  # checks the condition
            output
            wU = False
        Time.sleep(1)  # waits 60s for preformance


def get_current_path():
    """
    returns the full image's path
    """
    path = os.getcwd()
    ID = new_img.get_id()
    this_version = new_img.get_version_number()
    main_id_path = os.path.join(path, str(ID))
    full_path = os.path.join(main_id_path, str(this_version - 1))
    return full_path


def do_save():
    """
    saves the edited image in the computer with a special name
    """
    image = edit_image.read_image(os.path.join(new_img.get_latest_path(), new_img.get_full_name()))
    path = filedialog.askdirectory()
    edit_image.save_to_computer(image, path)
    new_img.save_count += 1
    saved_lbl = Label(text="the image saved succesfully!")
    saved_lbl.grid(row=4, column=0, pady=15)


class EditWindow():
    """
    creates new gui window
    """

    # -------- EDIT WINDOW --------
    # the settings of the window

    def __init__(self, root, name, client, image):
        self.root = root
        self.root.withdraw()
        self.new_img = edit_image.new_img
        self.win1 = Toplevel()
        self.win1.title("PEP - photo edit platform")
        self.win1.iconbitmap('gallery.ico')
        self.win1.geometry("750x600")
        self.win1["bg"] = "light blue"
        self.name = name
        self.client = client
        self.image = image
        self.label_count = 0

    def start(self):
        """
        starts the EDIT WINDOW
        """
        self.take_image_from_server()
        self.hello_text()
        # self.refresh_button()
        self.image_id()
        self.comix_style()
        self.grey()
        self.bw()
        self.sharp()
        self.contrast()
        self.brightness()
        self.change_color()
        self.crop()
        self.resize()
        self.rotate()
        self.request_edit()
        self.view_old_images()
        self.original_image()
        self.disable_all_buttons()
        self.win1.mainloop()

    def take_image_from_server(self):
        if self.image is None:
            self.client.set_request_data("recvimg", None, None)
        wU = True
        while wU == True:
            if self.client.receive_image_approval_status() == True:  # checks the condition
                self.get_image(None)
                self.client.receive_image_approval = False
                wU = False

    def get_image(self, edit):
        """
        reads the image
        sets the admin name, width and height of the image
        """
        self.image_server = open(self.client.get_client_image_name(), 'rb')
        logging.info("recent client version: {}".format(self.image_server))
        self.image = edit_image.read_image(self.image_server)
        self.semi_path = os.path.join(os.getcwd(), str(new_img.get_id()))
        self.full_path = os.path.join(self.semi_path, str(new_img.get_version_number() - 1))
        self.new_img.set_ysize(int(str(str(str(self.image).split(" ")[3:4]).split('x')[-1]).split("'")[0]))
        self.new_img.set_xsize(int(str(str(str(self.image).split(" ")[3:4]).split('x')[0]).split("=")[-1]))
        self.new_img.set_admin(self.name.get())
        self.recent_edit = edit
        self.client.start_edit = False  # the edit pass will no longer be active
        self.client.wait_for_edit = False
        if edit is not None:
            self.disable_all_buttons()  # disable all the buttons
        # present the image to the gui
        self.show_image()

    def update_image(self, edit):
        # Time.sleep(1)
        wU = True
        while wU == True:
            if self.client.receive_image_approval_status() == True:  # checks the condition
                self.get_image(edit)
                self.client.receive_image_approval = False
                wU = False

    def hello_text(self):
        """
        a hello text in the top of thw window
        """
        self.hello_txt = "hello {}! and {}.\nlets edit the image!".format(self.name.get(), time())
        self.hello_lbl = Message(self.win1, text=self.hello_txt, bg="steel blue", fg="blue", width=1000, borderwidth=5)
        self.hello_lbl.config(font=("Fixedsys", 10))
        self.hello_lbl.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

    def refresh_button(self):
        """
        creates a refresh button to show the most recent images
        :return:
        """
        self.b_refresh = Button(self.win1, text="REFRESH",
                                command=self.do_refresh(), fg="black", bg="light blue", width=8)
        self.b_refresh.grid(row=0, column=3)

    def do_refresh(self):
        # SHOW LATEST IMAGES OF THE SEVERAL CLIENTS
        # HANDLE THE WAIT FOR EDIT VARIABLE
        # if self.refresh_image is not self.image_server:
        self.image_server = open(self.client.get_client_image_name(), 'rb')
        self.img = edit_image.read_image(self.image_server)
        if self.new_img.get_xsize() > self.new_img.get_ysize():
            self.x_divided = self.new_img.get_xsize() / 300
            self.new_y_size = self.new_img.get_ysize() / self.x_divided
            self.shown_image = ImageTk.PhotoImage(
                edit_image.resize_image_start(self.img, 300, int(self.new_y_size)))
        else:
            self.y_divided = self.new_img.get_ysize() / 300
            self.new_x_size = self.new_img.get_xsize() / self.y_divided
            self.shown_image = ImageTk.PhotoImage(
                edit_image.resize_image_start(self.img, int(self.new_x_size), 300))
        self.img_lbl = Label(self.win1, image=self.shown_image)
        self.img_lbl.grid(row=8, columnspan=3)

    def image_id(self):
        """
        a label that show the image's id - for the group edit
        """
        self.id_label = Message(self.win1, text="IMAGE ID: " + str(self.new_img.get_id()), fg="blue", width=1000,
                                borderwidth=5)
        self.id_label.config(font=("Fixedsys", 10))
        self.id_label.grid(row=0, column=9, padx=10, pady=10)

    def request_edit(self):
        """
        creates a button for request edit.
        only one client can edit at a time. to achieve that, the client who clicked the request button first
        will be the client that can edit the image.
        Note: if a client clicked the button: "request edit". the button is clickable until the edit is finished.
        """
        self.b_request_edit = Button(self.win1, text="REQUEST EDIT",
                                     command=self.do_edit, fg="black", bg="yellow", width=20)
        self.b_request_edit.grid(row=1, column=9)

    def do_edit(self):
        """
        handles the request edit button.
        self.client.start_edit -> when True, the recent image is shown in the gui, enable all edit buttons.
        self.client.wait_for_edit -> when True, a popup window of wiat is shown, disable all edit buttons.
        :return:
        """
        self.client.set_request_data("reqedit", None, None)
        wU = True
        while wU == True:
            if self.client.start_edit == True:  # checks the condition
                self.do_refresh()
                self.enable_all_buttons()
                logging.info("server accepted for this client to edit")
                wU = False
            if self.client.wait_for_edit == True:  # checks the condition
                self.disable_all_buttons()
                # self.b_request_edit["state"] = "disabled"
                showinfo("WAIT", "please wait.\nAnother client is still editing.\nTry again soon.")
                logging.info("someone else is editing now")
                self.client.wait_for_edit = False
                wU = False

    def quick_help(self):
        """
        a quick help label on the right side of the window
        """
        self.help_win1 = LabelFrame(self.win1, text=" Quick Help ")
        self.help_win1.grid(row=2, column=9, columnspan=2, rowspan=8, sticky='NS', padx=20, pady=20)
        self.help_lbl_win1 = Label(self.help_win1, text="RECENT EDIT MADE BY YOU:")
        self.help_lbl_win1.grid(row=0, sticky="WE")
        if self.recent_edit is None:
            text = str(self.name.get()) + " | " + "uploaded!"
        else:
            text = str(self.name.get()) + " | " + str(self.recent_edit)

        edit_lbl = self.add_new_label(text)
        edit_lbl.grid(row=1, sticky="WE")

    def add_new_label(self, text):
        edit_lbl = Label(self.help_win1, text=text)
        self.label_count += 1
        return edit_lbl

    def show_image(self):
        """
        display the image
        x_devided: a parameter that shows the ratio of the height and width of the image
        """
        self.do_refresh()
        # show the local edit history
        self.quick_help()

    def comix_style(self):
        """
        the comix style edit button
        """
        self.b_comix = Button(self.win1, text="click for comix style",
                              command=lambda: self.do_comix(self.image), fg="black", bg="blue", width=20)
        self.b_comix.grid(row=1, column=0)

    def do_comix(self, image):
        """
        handles the comix edit
        """
        request = "comix"
        self.client.set_request_data(request, None, None)
        self.update_image(request)

    def grey(self):
        """
        the grey edit button
        """
        self.b_grey = Button(self.win1, text="click for grey",
                             command=lambda: self.do_grey(self.image), fg="black", bg="blue", width=20)
        self.b_grey.grid(row=1, column=1)

    def do_grey(self, image):
        """
        handles the grey edit
        """
        request = "grey"
        self.client.set_request_data(request, None, None)
        self.update_image(request)

    def bw(self):
        """
        the black & white edit button
        """
        self.b_bw = Button(self.win1, text="click for black&white",
                           command=lambda: self.do_bw(self.image), fg="black", bg="blue", width=20)
        self.b_bw.grid(row=1, column=2)

    def do_bw(self, image):
        """
        handles the black&white edit
        """
        request = "bw"
        self.client.set_request_data(request, None, None)
        self.update_image("black&white")

    def sharp(self):
        """
        the sharpness edit button
        """
        self.b_sharp = Button(self.win1, text="click for sharpness",
                              command=lambda: self.do_sharpness(self.image, self.sharpness_slider.get()),
                              fg="black", bg="turquoise", width=20)
        self.b_sharp.grid(row=2, column=0)
        self.sharpness_slider = Scale(self.win1, from_=1, to=5, orient=HORIZONTAL, bg="turquoise")
        self.sharpness_slider.grid(row=3, column=0)

    def do_sharpness(self, image, slider):
        """
        handles the sharpness edit
        """
        request = "sharpness"
        edit_extras = [slider]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}, amount:{}".format(request, str(edit_extras[0])))

    def contrast(self):
        """
        the contrast edit button
        """
        self.b_contrast = Button(self.win1, text="click for contrast",
                                 command=lambda: self.do_contrast(self.image, self.contrast_slider.get()), fg="black",
                                 bg="turquoise", width=20)
        self.b_contrast.grid(row=2, column=1)
        self.contrast_slider = Scale(self.win1, from_=1, to=5, orient=HORIZONTAL, bg="turquoise")
        self.contrast_slider.grid(row=3, column=1)

    def do_contrast(self, image, slider):
        """
        handles the contrast edit
        """
        request = "contrast"
        edit_extras = [slider]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}, amount:{}".format(request, str(edit_extras[0])))

    def brightness(self):
        """
        the brightness edit button
        """
        self.b_bright = Button(self.win1, text="click for brightness",
                               command=lambda: self.do_brightness(self.image, self.brightness_slider.get()), fg="black",
                               bg="turquoise", width=20)
        self.b_bright.grid(row=2, column=2)
        self.brightness_slider = Scale(self.win1, from_=1, to=5, orient=HORIZONTAL, bg="turquoise")
        self.brightness_slider.grid(row=3, column=2)

    def do_brightness(self, image, slider):
        """
        handles the brightness edit
        """
        request = "brightness"
        edit_extras = [slider]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}, amount:{}".format(request, str(edit_extras[0])))

    def change_color(self):
        """
        the change image color edit button
        """
        self.b_color = Button(self.win1, text="click to change image color",
                              command=lambda: self.do_color_effect(self.image, self.color_entry.get(),
                                                                   self.color_slider.get()),
                              fg="black", bg="green", height=2, width=20)
        self.b_color.grid(row=4, column=0)
        self.color_entry = Entry(self.win1, fg="black", bg="green", borderwidth=10, width=20)
        self.color_entry.grid(row=4, column=1)
        self.color_slider = Scale(self.win1, from_=1, to=3, orient=HORIZONTAL, bg="green", width=20)
        self.color_slider.grid(row=4, column=2)

    def do_color_effect(self, image, color, slider):
        """
        handles the color effect edit
        """
        request = "color"
        edit_extras = [color, slider]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{} {}".format(request, str(edit_extras[0])))

    def crop(self):
        """
        the crop edit button
        """
        self.b_crop = Button(self.win1, text="click to crop",
                             command=lambda: self.win_crop(self.image), fg="black", bg="light green", width=20)
        self.b_crop.grid(row=5, column=0)

    def win_crop(self, image):
        """
        creates a popup window to crop the image
        """
        global win_crop
        win_crop = Toplevel()
        win_crop.title("PEP - photo edit platform")
        win_crop.iconbitmap('gallery.ico')
        win_crop.geometry("500x200")
        win_crop["bg"] = "light blue"
        crop_lbl = Label(win_crop, text="enter the x cordinate and the y cordinate to crop the image")
        crop_lbl.config(font=("Fixedsys", 10))
        crop_lbl.grid(row=0, column=0, columnspan=2)
        crop_x_lbl = Label(win_crop, text="enter the x cordinate:", bg="light green")
        crop_x_lbl.grid(row=1, column=0)
        crop_x_entry = Entry(win_crop, fg="black", bg="green", borderwidth=10, width=20)
        crop_x_entry.grid(row=1, column=1)
        crop_y_lbl = Label(win_crop, text="enter the y cordinate:", bg="light green")
        crop_y_lbl.grid(row=2, column=0)
        crop_y_entry = Entry(win_crop, fg="black", bg="green", borderwidth=10, width=20)
        crop_y_entry.grid(row=2, column=1)
        crop_button = Button(win_crop, text="submit and crop",
                             command=lambda: self.do_crop(image, int(crop_x_entry.get()), int(crop_y_entry.get())),
                             fg="black", bg="turquoise", width=20, borderwidth=15)
        crop_button.grid(row=3, column=0)

    def do_crop(self, image, x, y):
        """
        handles the crop edit
        """
        request = "crop"
        edit_extras = [x, y]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}: x={}, y={}".format(request, str(edit_extras[0]), str(edit_extras[1])))

    def resize(self):
        """
        the resize edit button
        """
        self.b_resize = Button(self.win1, text="click to resize",
                               command=lambda: self.win_resize(self.image), fg="black", bg="light green", width=20)
        self.b_resize.grid(row=5, column=1)

    def win_resize(self, image):
        """
        creates a popup window to resize the image
        """
        global win_resize
        win_resize = Toplevel()
        win_resize.title("PEP - photo edit platform")
        win_resize.iconbitmap('gallery.ico')
        win_resize.geometry("500x200")
        win_resize["bg"] = "light blue"
        resize_lbl = Label(win_resize, text="enter the height and the width to resize the image")
        resize_lbl.config(font=("Fixedsys", 10))
        resize_lbl.grid(row=0, column=0, columnspan=2)
        height_lbl = Label(win_resize, text="enter the height", bg="light green")
        height_lbl.grid(row=1, column=0)
        height_entry = Entry(win_resize, fg="black", bg="green", borderwidth=10, width=20)
        height_entry.grid(row=1, column=1)
        width_lbl = Label(win_resize, text="enter the width", bg="light green")
        width_lbl.grid(row=2, column=0)
        width_entry = Entry(win_resize, fg="black", bg="green", borderwidth=10, width=20)
        width_entry.grid(row=2, column=1)
        resize_button = Button(win_resize, text="submit and resize",
                               command=lambda: self.do_resize(image, int(height_entry.get()), int(width_entry.get())),
                               fg="black", bg="turquoise", width=20, borderwidth=15)
        resize_button.grid(row=3, column=0)

    def do_resize(self, image, height, width):
        """
        handles the resize edit
        """
        request = "resize"
        edit_extras = [height, width]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}: height={}, width={}".format(request, str(edit_extras[0]), str(edit_extras[1])))

    def rotate(self):
        """
        the rotation edit button
        """
        self.b_rotate = Button(self.win1, text="click to rotate",
                               command=lambda: self.win_rotate(self.image), fg="black", bg="light green", width=20)
        self.b_rotate.grid(row=5, column=2)

    def win_rotate(self, image):
        """
        creates a popup window to rotate the image
        """
        global win_rotate
        win_rotate = Toplevel()
        win_rotate.title("PEP - photo edit platform")
        win_rotate.iconbitmap('gallery.ico')
        win_rotate.geometry("500x200")
        win_rotate["bg"] = "light blue"
        rotate = Label(win_rotate, text="enter the angle to rotate the image")
        rotate.config(font=("Fixedsys", 10))
        rotate.grid(row=0, column=0, columnspan=2)
        angle_lbl = Label(win_rotate, text="enter the angle", bg="light green")
        angle_lbl.grid(row=1, column=0)
        angle_entry = Entry(win_rotate, fg="black", bg="green", borderwidth=10, width=20)
        angle_entry.grid(row=1, column=1)
        crop_button = Button(win_rotate, text="submit and rotate",
                             command=lambda: self.do_rotate(image, int(angle_entry.get())),
                             fg="black", bg="turquoise", width=20, borderwidth=15)
        crop_button.grid(row=3, column=0)

    def do_rotate(self, image, angle):
        """
        handles the rotation edit
        """
        request = "rotate"
        edit_extras = [angle]
        self.client.set_request_data(request, None, edit_extras)
        self.update_image("{}, angle: {}".format(request, str(edit_extras[0])))

    def view_old_images(self):
        """
        the archive edit button
        """
        self.b_view = Button(self.win1, text="view archive images",
                             command=lambda: self.view_image(self.password.get()), fg="black", bg="red", width=20)
        self.b_view.grid(row=10, column=0)
        self.password = Entry(self.win1, fg="black", bg="red", show="*", borderwidth=10, width=20)
        self.password.grid(row=10, column=1)

    def view_image(self, password):
        """
        creates a popup window to rotate the image
        """

        if password == "lovepython":  # the password for viewing archived posts.
            global win_view
            win_view = Toplevel()
            win_view.title("PEP - photo edit platform")
            win_view.iconbitmap('gallery.ico')
            win_view.geometry("500x200")
            win_view["bg"] = "light blue"
            view_lbl = Label(win_view, text="enter the id of the image and the version you want to view:")
            view_lbl.config(font=("Fixedsys", 10))
            view_lbl.grid(row=0, column=0, columnspan=2)
            view_lbl_1 = Label(win_view, text="enter the ID", bg="light green")
            view_lbl_1.grid(row=1, column=0)
            id_entry = Entry(win_view, fg="black", bg="green", borderwidth=10, width=20)
            id_entry.grid(row=1, column=1)
            view_lbl_2 = Label(win_view, text="enter the version", bg="light green")
            view_lbl_2.grid(row=2, column=0)
            version_entry = Entry(win_view, fg="black", bg="green", borderwidth=10, width=20)
            version_entry.grid(row=2, column=1)
            view_button = Button(win_view, text="submit and view",
                                 command=lambda: self.do_view(int(id_entry.get()), int(version_entry.get())),
                                 fg="black", bg="turquoise", width=20, borderwidth=15)
            view_button.grid(row=3, column=0)
        else:
            showinfo("EROOR", "password is incorrect")

    def do_view(self, id, version):
        """
        handles the rotation edit
        """
        request = "view"
        edit_extras = [id, version]
        self.client.set_request_data(request, None, edit_extras)
        if len(str(id)) != 8 or len(str(version)) != 1:
            showinfo("Error", "ID or version incorrect.\nPlease try again.")
        else:
            wU = True
            while wU == True:
                if self.client.receive_view_request:  # checks the condition
                    # create a window that will show the image
                    self.open_image_window()
                    wU = False
                if self.client.no_archive_image:
                    # send an error message
                    showinfo("Error", "ID or version incorrect.\nPlease try again.")
                    self.client.no_archive_image = False
                    break

        self.client.receive_view_request = False

    def open_image_window(self):
        global win_view_image
        win_view_image = Toplevel()
        win_view_image.title("PEP - photo edit platform")
        win_view_image.iconbitmap('gallery.ico')
        win_view_image.geometry("300x400")
        win_view_image["bg"] = "light blue"
        self.show_archive_image(image=self.client.archived_image)

    def show_archive_image(self, image):
        """
        display the image
        x_devided: a parameter that shows the ratio of the height and width of the image
        """
        global win_view_image
        img = edit_image.read_image(image)
        view_lbl = Label(win_view_image, text="The image from client: ")
        view_lbl.config(font=("Fixedsys", 10))
        view_lbl.grid(row=0, column=0, columnspan=2, sticky="news")
        self.do_refresh()
        self.exit_b = Button(win_view_image, text="Quit", command=self.close_window, fg="black", bg="orange", width=20)
        self.exit_b.grid(row=2, column=0, padx=10, pady=10)

    def close_window(self):
        global win_view_image
        self.show_image()
        win_view_image.destroy()

    def original_image(self):
        """
        the original image button
        """
        self.b_og = Button(self.win1, text="view original image",
                           command=lambda: self.show_og_image(), fg="white", bg="black", width=20)
        self.b_og.grid(row=10, column=2)

    def show_og_image(self):
        global win_og
        win_og = Toplevel()
        win_og.title("PEP - photo edit platform")
        win_og.iconbitmap('gallery.ico')
        win_og.geometry("300x400")
        win_og["bg"] = "light blue"
        og_lbl = Label(win_og, text="The Original Image is:")
        og_lbl.config(font=("Fixedsys", 10))
        og_lbl.grid(row=0, column=0, columnspan=2, padx=40, pady=20, sticky="news")
        self.original_img = open(self.client.get_client_original_image(), 'rb')
        logging.info("origianl image name: {}".format(self.original_img))
        self.image = edit_image.read_image(self.original_img)
        # self.image.show()
        if self.new_img.get_xsize() > self.new_img.get_ysize():
            self.x_divided = self.new_img.get_xsize() / 300
            self.new_y_size = self.new_img.get_ysize() / self.x_divided
            self.shown_image = ImageTk.PhotoImage(
                edit_image.resize_image_start(self.image, 300, int(self.new_y_size)))
        else:
            self.y_divided = self.new_img.get_ysize() / 300
            self.new_x_size = self.new_img.get_xsize() / self.y_divided
            self.shown_image = ImageTk.PhotoImage(
                edit_image.resize_image_start(self.image, int(self.new_x_size), 300))
        self.img_lbl = Label(win_og, image=self.shown_image)
        self.img_lbl.grid(row=8, columnspan=3)
        self.exit_b_og = Button(win_og, text="Quit", command=self.close_og_window, fg="black", bg="orange", width=20)
        self.exit_b_og.grid(row=10, column=0, padx=50, pady=10)

    def close_og_window(self):
        global win_og
        self.show_image()
        win_og.destroy()

    def save(self):
        # the save to computer edit button
        self.b_save = Button(self.win1, text="SAVE TO COMPUTER", command=do_save, fg="black", bg="orange", width=20)
        self.b_save.config(font=("Fixedsys", 3))
        self.b_save.grid(row=70, column=0)

    def undo(self):
        # the undo edit button
        self.b_undo = Button(self.win1, text="UNDO",
                             command=lambda: do_undo(self.image), fg="black", bg="orange", width=20)
        self.b_undo.config(font=("Fixedsys", 3))
        self.b_undo.grid(row=70, column=1)

    def disable_all_buttons(self):
        self.b_comix["state"] = "disable"
        self.b_grey["state"] = "disable"
        self.b_bw["state"] = "disable"
        self.b_contrast["state"] = "disable"
        self.b_sharp["state"] = "disable"
        self.b_bright["state"] = "disable"
        self.b_color["state"] = "disable"
        self.b_crop["state"] = "disable"
        self.b_resize["state"] = "disable"
        self.b_rotate["state"] = "disable"

    def enable_all_buttons(self):
        self.b_comix["state"] = "normal"
        self.b_grey["state"] = "normal"
        self.b_bw["state"] = "normal"
        self.b_contrast["state"] = "normal"
        self.b_sharp["state"] = "normal"
        self.b_bright["state"] = "normal"
        self.b_color["state"] = "normal"
        self.b_crop["state"] = "normal"
        self.b_resize["state"] = "normal"
        self.b_rotate["state"] = "normal"
