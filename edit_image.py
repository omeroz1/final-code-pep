import os

import PIL.Image
import numpy as np
from PIL import ImageEnhance


class ImgTk:
    def __init__(self):
        self.path = ""  # the image path given
        self.img_name = ""  # the full original image name
        self.full_name = ""  # the full image name in the id directories
        self.latest_path = ""  # the latest edit's path of the image
        self.name = ""  # just the name of the image
        self.type = ""  # the image type (example: jpg)
        self.admin = ""  # the admin image's name
        self.xsize = 0  # the width of the image
        self.ysize = 0  # the height of the image
        self.id = 0  # the unique id of the image (time based)
        self.version_number = 0  # the version of the edit
        self.save_count = 0  # number of times the photo saved to the local computer

    def get_version_number(self):
        return self.version_number

    def set_version_number(self, number):
        self.version_number = number

    def get_save_count(self):
        return self.save_count

    def set_save_count(self, number):
        self.save_count = number

    def get_path(self):
        return self.path

    def set_path(self, path):
        self.path = path

    def get_latest_path(self):
        return self.latest_path

    def set_latest_path(self, latest_path):
        self.latest_path = latest_path

    def get_og_name(self):
        return self.img_name

    def set_og_name(self, img_name):
        self.img_name = img_name

    def get_full_name(self):
        return self.full_name

    def set_full_name(self, full_name):
        self.full_name = full_name

    def get_xsize(self):
        return self.xsize

    def set_xsize(self, xsize):
        self.xsize = xsize

    def get_ysize(self):
        return self.ysize

    def set_ysize(self, ysize):
        self.ysize = ysize

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def get_admin(self):
        return self.admin

    def set_admin(self, admin):
        self.admin = admin


new_img = ImgTk()


def read_image(path):
    """
   :param path: the path of the image
   :return: the photo in the variable: 'image'
   """
    try:
        image = PIL.Image.open(path)
        return image
    except Exception as e:
        print(e)


def get_image_size(image):
    """
   :param image: the image given
   :return: image size in pixels
   """
    return image.size


def resize_image(image, height, width):
    """
   change the image's size, without changing the image ratio.
   :param image: the image given
   :param height: new height in pixels
   :param width:new width in pixels
   :return: new image
   """
    resized_image = image.resize((height, width))
    save_to_dir(resized_image, None, None)
    return resized_image


def resize_image_start(image, height, width):
    """
    THE SAME FUNCTION AS RESIZE IMAGE, BUT FOR THE INITIALIZING (TO SHOW IN GUI)
   change the image's size, without changing the image ratio.
   :param image: the image given
   :param height: new height in pixels
   :param width:new width in pixels
   :return: new image
   """
    resized_image = image.resize((height, width))
    return resized_image


def save_to_dir(image, id, image_name):
    """
    saves the image in the specific id's directory
    iname: the image original name (deni)
    iend: the image type (jpg)
    id: image's id
    this_version: the version of the edit
    main_id_path: example -'C://Users//omero//PycharmProjects//pythonProject6//28012147'
    full_path: example - 'C://Users//omero//PycharmProjects//pythonProject6//28012147//1'
    full name: example - C://Users//omero//PycharmProjects//pythonProject6//28012209//0/da_280122090.jpg
    :return:
    """
    path = os.getcwd()
    if image_name is not None:
        iname = image_name.split('.')[0]
        iend = image_name.split('.')[1]
        new_img.set_name(iname)
        new_img.set_type(iend)
    if id is not None:
        new_img.set_id(id)
    this_version = new_img.get_version_number()
    main_id_path = os.path.join(path, str(new_img.get_id()))
    full_path = os.path.join(main_id_path, str(this_version))
    new_img.set_latest_path(full_path)
    new_img.set_og_name('{}{}'.format(new_img.get_name(), new_img.get_type()))
    new_img.set_full_name('{}\\{}_{}{}.{}'.format(full_path, new_img.get_name(), str(new_img.get_id()),
                                                  str(this_version), new_img.get_type()))
    if os.path.exists(main_id_path):
        if os.path.exists(os.path.join(main_id_path, str(this_version))):
            image.save(new_img.get_full_name())
        else:
            os.mkdir(os.path.join(main_id_path, str(this_version)))
            image.save(new_img.get_full_name())
    else:
        os.mkdir(main_id_path)
        os.mkdir(os.path.join(main_id_path, str(this_version)))
        image.save(new_img.get_full_name())
    new_img.set_version_number(new_img.get_version_number() + 1)


def save_to_computer(image, path):
    """
    saves the image in the local computer in a chosen directory
    :param path: the directory the client wanted to save in
    """
    iname, iend = new_img.get_name(), "." + new_img.get_type()
    image.save(('{}/{}_{}{}{}'.format(path, iname, "edited", new_img.save_count, iend)))


def copy_all_to_file():
    """
   copy the image to the directory named after the image ID.
   example: 'deni.jpg' will be 'deni_ID.jpg'
   """
    path = os.getcwd()
    ID = new_img.get_id()
    for f in os.listdir(''):
        if f.endswith('.jpg') or f.endswith('.png') or f.endswith('.JPG') or f.endswith('.PNG'):
            i = PIL.Image.open(f)
            iname, iend = os.path.splitext(f)
            if os.path.exists(os.path.join(path, str(ID))):
                i.save('{}/{}_{}{}'.format(str(ID), iname, str(ID), iend))
            else:
                os.mkdir(os.path.join(path, str(ID)))
                i.save('{}/{}_{}{}'.format(str(ID), iname, str(ID), iend))


def crop_image(image, xtop, ytop, xbottom, ybottom):
    """
   crops the image.
   xtop & ytop = the top left cordinates (xtop, ytop)
   xbottom & ybottom = the bottom right cordinates (xbottom, ybottom)
   :param image: image given
   :return: a cropped image
   """
    cropped = image.crop((xtop, ytop, xbottom, ybottom))
    save_to_dir(cropped, None, None)
    return cropped


def get_center_image(image):
    """
   finds the center of the image.
   xtop & ytop = the top left cordinates (xtop, ytop)
   xbottom & ybottom = the bottom right cordinates (xbottom, ybottom)
   :param image: image given
   :return: the pixels pf the center image
   """
    width, height = image.size
    xtop = width / 4
    ytop = height / 4
    xbottom = 3 * width / 4
    ybottom = 3 * height / 4
    return xtop, ytop, xbottom, ybottom


def rotate_image(image, angle):
    """
   rotates the image
   :param image: the image given
   :param angle: the angle to rotate the image
   :return: a rotated image
   """
    updated_image = image.rotate(angle)
    save_to_dir(updated_image, None, None)
    return updated_image


def change_image_color(image, color, level):
    """
   changes the image to any color given with 3 different levels.
   :param image: the image given
   :param color: the dominant color of the new image. 'red' 'green' 'blue' 'turquoise' 'yellow' 'purple'
   :param level: the level of selected_color in the picture. variable must be 1,2 or 3.
   """
    global selected_color
    rl = (
        0.4, 0.4, 0.4, 0,
        0.1, 0.1, 0.1, 0,
        0.1, 0.1, 0.1, 0)

    rm = (
        0.5, 0.5, 0.5, 0,
        0.1, 0.1, 0.1, 0,
        0.1, 0.1, 0.1, 0)

    rs = (
        0.7, 0.7, 0.7, 0,
        0.1, 0.1, 0.1, 0,
        0.1, 0.1, 0.1, 0)

    gl = (
        0.1, 0.1, 0.1, 0,
        0.3, 0.3, 0.3, 0,
        0.1, 0.1, 0.1, 0)

    gm = (
        0.1, 0.1, 0.1, 0,
        0.5, 0.5, 0.5, 0,
        0.1, 0.1, 0.1, 0)

    gs = (
        0.1, 0.1, 0.1, 0,
        0.7, 0.7, 0.7, 0,
        0.1, 0.1, 0.1, 0)

    bl = (
        0.2, 0.2, 0.2, 0,
        0.2, 0.2, 0.2, 0,
        0.5, 0.5, 0.5, 0)

    bm = (
        0.2, 0.2, 0.2, 0,
        0.2, 0.2, 0.2, 0,
        0.9, 0.9, 0.9, 0)

    bs = (
        0.15, 0.15, 0.15, 0,
        0.15, 0.15, 0.15, 0,
        0.9, 0.9, 0.9, 0)

    tl = (
        0.5, 0.5, 0.5, 0,
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0)

    tm = (
        0.3, 0.3, 0.3, 0,
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0)

    ts = (
        0.1, 0.1, 0.1, 0,
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0)

    yl = (
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0,
        0.5, 0.5, 0.5, 0)

    ym = (
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0,
        0.3, 0.3, 0.3, 0)

    ys = (
        0.6, 0.6, 0.6, 0,
        0.6, 0.6, 0.6, 0,
        0.1, 0.1, 0.1, 0)

    pl = (
        0.6, 0.6, 0.6, 0,
        0.5, 0.5, 0.5, 0,
        0.6, 0.6, 0.6, 0)

    pm = (
        0.6, 0.6, 0.6, 0,
        0.3, 0.3, 0.3, 0,
        0.6, 0.6, 0.6, 0)

    ps = (
        0.6, 0.6, 0.6, 0,
        0.1, 0.1, 0.1, 0,
        0.6, 0.6, 0.6, 0)

    if color == 'red':
        if level == 1:
            selected_color = rl
        elif level == 2:
            selected_color = rm
        elif level == 3:
            selected_color = rs
        else:
            print("ERROR. level value can be: 1,2,3")
    elif color == 'green':
        if level == 1:
            selected_color = gl
        elif level == 2:
            selected_color = gm
        elif level == 3:
            selected_color = gs
        else:
            print("ERROR. level value can be: 1,2,3")
    elif color == 'blue':
        if level == 1:
            selected_color = bl
        elif level == 2:
            selected_color = bm
        elif level == 3:
            selected_color = bs
        else:
            print("ERROR. level value can be: 1,2,3")
    elif color == 'turquoise':
        if level == 1:
            selected_color = tl
        elif level == 2:
            selected_color = tm
        elif level == 3:
            selected_color = ts
        else:
            print("ERROR. level value can be: 1,2,3")
    elif color == 'yellow':
        if level == 1:
            selected_color = yl
        elif level == 2:
            selected_color = ym
        elif level == 3:
            selected_color = ys
        else:
            print("ERROR. level value can be: 1,2,3")
    elif color == 'purple':
        if level == 1:
            selected_color = pl
        elif level == 2:
            selected_color = pm
        elif level == 3:
            selected_color = ps
        else:
            print("ERROR. level value can be: 1,2,3")
    if color == 'red' or color == 'green' or color == 'blue' or color == 'turquoise' or color == 'yellow' \
            or color == 'purple':
        updated_image = image.convert("RGB", selected_color)
        save_to_dir(updated_image, None, None)
        return updated_image
    else:
        if color == 'grey' or color == 'gray':
            grayscale = image.convert("L")
            save_to_dir(grayscale, None, None)
            return grayscale
        else:
            print("ERROR. color not found. color can be: red, green, blue, turquoise, yellow, purple or grey")


def comix_image(image):
    """
   :return: comix image
   """
    comix = image.convert("P")
    updated_image = comix.convert("RGB")
    save_to_dir(updated_image, None, None)
    return comix


def gray_image(image):
    grayscale = image.convert("L")
    save_to_dir(grayscale, None, None)
    # new_path = os.getcwd() + "\\" + str(new_img.get_id() + "\\" + new_img.get_full_name())
    return grayscale


def bw_image(image):
    """
   convert the image to black & white
   :param image: image given
   :param hardness: bigger value -> more black.
                     lower value -> more white.
   :return: binary image
   """
    updated_img = image.convert('1')
    save_to_dir(updated_img, None, None)
    return updated_img


def flip_image(image):
    """
   flips the image
   """
    img_array = np.array(image)
    img_flipped_data = np.flip(img_array, axis=1)
    img_flipped = PIL.Image.fromarray(img_flipped_data)
    return img_flipped


def brightness_image(image, amount):
    """
   increase or decrese the brightness.
   img_light > 1 = brighter
   img_light < 1 = darker
   """
    enhancer = ImageEnhance.Brightness(image)
    img_light = enhancer.enhance(amount)
    save_to_dir(img_light, None, None)
    return img_light


def contrast_image(image, amount):
    """
   increase or decrese the contrast.
   updated_img > 1 = more contrast
   updated_img < 1 = less contrast
   """
    enhancer = ImageEnhance.Contrast(image)
    updated_img = enhancer.enhance(amount)
    save_to_dir(updated_img, None, None)
    return updated_img


def sharpness_image(image, amount):
    """
   increase or decrese the sharpness.
   updated_img > 1 = more sharpness
   updated_img < 1 = less sharpness
   """
    enhancer = ImageEnhance.Sharpness(image)
    updated_img = enhancer.enhance(amount)
    save_to_dir(updated_img, None, None)
    # new_path = os.getcwd() + "\\" + str(new_img.get_id() + "\\" + new_img.get_full_name())
    return updated_img
    # new_img.set_path(new_path)


def enhance_color_image(image):
    """
   increase or decrese the color.
   updated_img > 1 = more color
   updated_img < 1 = less color
   """
    enhancer = ImageEnhance.Color(image)
    updated_img = enhancer.enhance(3)  # 3 can be replaced with var - enhance
    save_to_dir(updated_img, None, None)
    return updated_img
