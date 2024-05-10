#!/usr/bin/env python

import configparser
import functools
import operator
import os.path
import pathlib
import sys
from dataclasses import dataclass

import customtkinter as ctk
from PIL import Image, ImageTk

# import tkinter.messagebox as box
from ctkmessagebox import CTkMessagebox as Box

# От вас и не ожидают, что вы это поймете.


class LookupDict(dict):
    """Обращение к словарю не по ключу, а как к атрибуту"""

    def __init__(self, d):
        for key in d:
            setattr(self, key, d[key])
        super().__init__()

    def __getitem__(self, key):
        return self.__dict__.get(key, None)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


@dataclass
class DataRequest:
    """Посылка данных в ХК"""

    start: str = "$"
    work: str = "W"  # 'N','V'
    rej: str = "S"  # 'R'
    depth: str = "L"  # 'M'
    not_used: str = "0"
    # ku: str = '5'               # 0 - 14
    ku: str = "\x06"
    # n_used: str = "0"
    sv: str = "\x05\xdc"  # 1500


@dataclass
class ViewDataUpr:
    """Представление данных"""

    depth: str
    ku: int
    cnt: int = 0
    m: int = 0
    ampl: float = 0
    len: float = 0
    distance: int = 0


COLOR = (
    "#c40373",
    "#e32322",
    "#ea621f",
    "#f18e1c",
    "#fdc60b",
    "#f4e500",
    "#8cbb26",
    "#008e5b",
    "#0696bb",
    "#2a71b0",
    "#444e99",
    "#552f6f",
)

dict_color = {
    0x14: "#552f6f",
    0x2C: "#444e99",
    0x3E: "#2a71b0",
    0x4E: "#0696bb",
    0x60: "#008e5b",
    0x72: "#8cbb26",
    0x80: "#f4e500",
    0x90: "#fdc60b",
    0xA0: "#f18e1c",
    0xB6: "#ea621f",
    0xD0: "#e32322",
    0xFE: "#c40373",
}

path = pathlib.Path(os.path.abspath("."))

config = configparser.ConfigParser()
file = path.joinpath("config.ini")
img_path = path.joinpath("images")

if not file.exists():
    # box.showerror('ERROR!', 'Отсутствует \nили поврежден\nфайл config.ini')
    Box(
        title="",
        message="Отсутствует \nили поврежден\nфайл config.ini",
        font=("Roboto Medium", -16),
        icon="cancel",
    )
    sys.exit(0)


# config.read(file, encoding='utf-8')
def read_config() -> None:
    """Прочитать файл сонфигурации"""
    config.read(file, encoding="utf-8")


read_config()

family = config.get("Font", "font")
font_size = config.getint("Font", "font_size")
# font = ctk.CTkFont(family=f"{family}", size=font_size)
font = (family, font_size)
# ("Roboto Thin", -16)
# ("Roboto Regular", -16)


def data_to_byte(kv: dataclass) -> bytes:
    """Преобразуем словарь данных в данные для передачи в модуль с добавлением ks"""
    data_str = "".join(i for i in kv.__dict__.values())
    ks = functools.reduce(operator.xor, (ord(i) for i in data_str[1:]), 0)
    sum_l = chr(ks & 0x0F)
    sum_h = chr((ks & 0xF0) >> 4)
    return data_str.encode("latin-1") + f"{sum_h}{sum_l}".encode("latin-1") + b"\r\n"


def write_config() -> None:
    """Сохранение файла конфигурации"""
    with open(file, "w", encoding="utf-8") as config_file:
        config.write(config_file)


def get_color(arg: int) -> str:
    """Вернуть цвет по амплитуде как в ПУИ"""
    if not arg:
        return "grey55"
    if arg > 255:
        arg = 255
    # a = (0x14, 0x2C, 0x3E, 0x4E, 0x60, 0x72, 0x80, 0x90, 0xA0, 0xB6, 0xD0, 0xFF)
    a = (2, 4, 6, 8, 10, 15, 21, 30, 45, 90, 180, 255)
    for i, j in enumerate(a):
        if arg <= j:
            return COLOR[11 - i]  # COLOR[0..11] от т красного  до т синего


def load_image(im, im_2=None, size: tuple = ()) -> ctk.CTkImage:
    """Загрузить изображения"""
    path_to_image = img_path.joinpath(im)
    if not size:
        size = (20, 20)
    if im_2:
        path_to_image2 = img_path.joinpath(im_2)
        return ctk.CTkImage(
            light_image=Image.open(path_to_image),
            dark_image=Image.open(path_to_image2),
            size=size,
        )
    else:
        return ctk.CTkImage(Image.open(path_to_image), size=size)


# img_records = load_image(
#     im=img_path.joinpath("record2.png"),
#     im_2=img_path.joinpath("record1.png"),
#     size=(25, 25),
# )


# img_pause = load_image(
#     im=img_path.joinpath("pause2.png"),
#     im_2=img_path.joinpath("pause1.png"),
#     size=(25, 25),
# )


def load_image_tk(im, size: tuple = ()) -> ImageTk.PhotoImage:
    """Загрузить изображения"""
    path_to_img = img_path.joinpath(im)
    if not size:
        size = (20, 20)
    return ImageTk.PhotoImage(Image.open(path_to_img).resize((size[0], size[1])))


# def create_images(light: tuple, dark: tuple = None, size: tuple = (20, 20)) -> dict:
#     """Содать словарь с изображениями в зависимости от темы"""
#     image_dict = {}
#     appearance_mode = config.getint("Font", "app_mode")
#     if dark:
#         list_images = light if appearance_mode else dark
#     else:
#         list_images = light
#     for im in list_images:
#         img = im[:-1] if dark else im
#         image_dict[img] = load_image(f"{im}.png", im_2=None, size=size)
#     return LookupDict(image_dict)


if getattr(sys, "frozen", False):
    bundle_dir = sys._MEIPASS  # PyInstaller
else:
    bundle_dir = path
