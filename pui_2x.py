#!/usr/bin/env python

import array
import csv
import time
import tkinter as tk
from collections import deque
from pathlib import Path
from tkinter import ttk
import customtkinter as ctk

from common import (
    DataRequest,
    ViewDataUpr,
    config,
    data_to_byte,
    family,
    font_size,
    load_image,
    write_config,
)
from scr import Screen
from fild import Fild
from form import ToplevelHelp
from head import Head
from portthread import PortThread, port_exc
from simpleedit import SimpleEditor
from stbar import Footer
from title import TitleTop
from tools import Tools
from top_widget import CTkTop
from upravl import Uprav

show = config.getboolean("Verbose", "visible")
scheme = config.get("Font", "scheme")

one_port = config.getboolean("Port", "one")

Width = config.getint("Size", "width")
Height = config.getint("Size", "height")

trace = print if show else lambda *x: None

# ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme(scheme)  # Themes: "blue" (standard), "green", "dark-blue"


class BtnStart(ctk.CTkFrame):
    """Фреим кнопи старт и переключателя"""

    def __init__(self, master):
        super().__init__(master, corner_radius=0, border_width=0, border_color="grey75")
        self.root = master.root
        ttk.Separator(self).grid(row=0, column=0, columnspan=3, padx=5, sticky="we")
        self.btn_start = ctk.CTkButton(
            master=self,
            image=self.root.im_korabl,
            text=self.root.START,
            width=130,
            text_color=("gray10", "gray90"),
            border_width=2,
            corner_radius=10,
            compound="bottom",
            border_color="#D35B58",
            font=self.root.font,
            fg_color=("gray84", "gray25"),
            hover_color="#C77C78",
            command=self.root.btn_start_,
        )
        self.btn_start.grid(row=1, column=0, columnspan=2, padx=20, pady=8, sticky="s")
        self.sw_25 = ctk.CTkSwitch(
            master=self,
            text="50кГц",
            onvalue="$",
            offvalue="%",
            font=self.root.font,
            state="disabled",
        )
        self.sw_25.grid(row=1, column=2, padx=2, pady=10, sticky="w")


class RF(ctk.CTkFrame):
    """Правый фрейм"""

    def __init__(self, root):
        super().__init__(root, corner_radius=0, border_width=2, border_color="grey75")
        self.root = root
        self.tools = Tools(self)    # настройки + метки
        self.tools.grid(row=0, column=0, pady=(2, 0), padx=2, sticky="we")
        self.tools.grid_columnconfigure(0, weight=1)
        self.tools.grid_columnconfigure(1, weight=1)

        self.u_panel = Uprav(self)  # панель управления
        self.u_panel.grid(row=1, column=0, pady=(0, 0), padx=2, sticky="nsew")

        self.izl = BtnStart(self)
        self.izl.grid(row=2, column=0, pady=2, padx=2, sticky="s")

        self.btn_start = self.izl.btn_start
        self.sw_25 = self.izl.sw_25


class App(ctk.CTk):
    """Корневой класс приложения"""

    WIDTH = 1340
    HEIGHT = 900
    theme_mode = None  # 1-'dark', 0-'light'
    START = "СТАРТ"     # Излучение
    STOP = "СТОП"       # Ожидание

    def __init__(self):
        super().__init__()
        self.title("")
        self.after(300, lambda: self.iconbitmap("view.ico"))
        self.xk1 = False  # XK_01 разрешить БГ (False)
        self.geometry(f"{Width}x{Height}+100+0")
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.minsize(1080, 680)
        self.wm_state = True  # во весь экран True
        self.theme_mode = 0
        # self.toplevel_created = False
        self.s = ttk.Style()  # for TSizegrip
        self.s.theme_use("clam")
        appearance_mode = config.getint("Font", "app_mode")
        value = "Dark" if appearance_mode else "Light"
        ctk.set_appearance_mode(value)
        self._change_appearance_mode(value)
        TitleTop(self, "ПУИ_2")
        self.im_korabl = load_image("korab.png", im_2=None, size=(48, 24))
        self.font = ctk.CTkFont(family=f"{family}", size=font_size)

        self.crashes_50 = 0  # число сбоев для ППУ Неисправен
        self.crashes_25 = 0
        self.crashes_gps = 5  # число сбоев gps
        self.enable_50 = True
        self.enable_25 = True
        self.id_timeout = None

        self.delay_mg = config.getfloat("System", "delay_mg")
        self.delay_sg = config.getfloat("System", "delay_sg")
        self.delay_bg = config.getfloat("System", "delay_bg")
        self.delay_b6 = config.getfloat("System", "delay_b6")
        self.delay = self.delay_mg
        self.delay_50 = self.delay
        self.delay_25 = self.delay
        self.schift = config.getint("System", "schift")

        self._vz = config.getint("System", "vz")  # скорость звука
        self._zg = config.getfloat("System", "zagl")
        self._zona = config.getfloat("System", "vzona")
        vz = self._vz.to_bytes(2, "big").decode("latin-1")
        DataRequest.sv = vz

        self.start_work = False  # пауза

        # для запрета постановки всех меток
        self.loop_50 = tk.BooleanVar(value=False)
        self.loop_25 = tk.BooleanVar(value=False)

        self.win = None  # нет окна заглубления
        self.choose_gals = False  # признак выбора галса

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.screen = Screen(self)
        self.screen.grid(row=1, column=0, sticky="nsew", padx=(2, 0), pady=1)
        self.screen.grid_rowconfigure((0, 1), weight=1)  # minsize=80
        self.screen.grid_columnconfigure(0, weight=1)

        self.r_frame = RF(self)
        self.r_frame.grid(row=0, column=1, rowspan=2, sticky="ns", padx=2)
        self.r_frame.rowconfigure(0, weight=1)
        self.r_frame.rowconfigure(1, weight=100)
        self.r_frame.columnconfigure(0, weight=0)

        self.u_panel = self.r_frame.u_panel
        self.tools = self.r_frame.tools
        self.sw_25 = self.r_frame.sw_25
        self.btn_start = self.r_frame.btn_start

        self.adr = "$"  # $ or % (50 or 25) kHz

        self.head = Head(self)
        self.head.grid(row=0, column=0, padx=(2, 0), sticky="we")
        self.head.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        w_scr = self.winfo_screenwidth() - 296
        self.data_deq_50 = deque(maxlen=w_scr)
        self.data_deq_25 = deque(maxlen=w_scr)
        mod = config.getint("System", "mod")
        self.enable_50 = True
        self.enable_25 = True
        self.flip_flop = False  # поочередная работа 50 25 если True
        height = App.HEIGHT + 230
        mod_msg = "50&25"
        if mod == 1:
            self.enable_25 = False
            self.screen.frame_fild_25.grid_forget()
            mod_msg = "50"
        elif mod == 2:
            self.enable_50 = False
            self.screen.frame_fild_50.grid_forget()
            self.sw_25.configure(text="25кГц")
            self.sw_25.deselect()
            self.adr = "%"
            mod_msg = "25"
        else:
            if mod == 3:
                self.flip_flop = True
                mod_msg = "50|25"
            self.sw_25.configure(state="normal", command=self._mod_25)
            self.sw_25.select()
        self.mod = mod
        self.board_50 = Fild(self, App.WIDTH + 400, height)  # экран эхограммы
        self.board_25 = Fild(self, App.WIDTH + 400, height, sel=True)
        self.board = self.board_50  # for bind_

        self.st_bar = Footer(self)  # строка состояния
        self.st_bar.grid(row=2, column=0, columnspan=2, sticky="we", pady=(0, 0))
        self.st_bar.grid_columnconfigure(0, weight=1)

        self.g_ser = PortThread(self.gps_read_data)
        self.g_ser.max_message_len = 1024
        if one_port:
            self.ser_50 = PortThread(self.on_receive_func)
            self.ser_25 = self.ser_50
            msg = self._open_ports(self.ser_50, self.g_ser)
        else:
            self.ser_50 = PortThread(self.on_receive_func_50)  # объект Serial
            self.ser_25 = PortThread(self.on_receive_func_25)
            msg = self._open_ports(self.ser_50, self.g_ser, self.ser_25)
        self.depth = "L"
        self.data_upr_50 = ViewDataUpr("L", "5")  # данные для панели управления
        self.data_upr_25 = ViewDataUpr("L", "7")
        self.u_panel.update_upr(self.data_upr_50)
        self.send_data_50 = DataRequest()  # данные для передачи в ХК 50
        self.send_data_25 = DataRequest()  # данные для передачи в ХК 25
        self.send_data_25.start = "%"
        self.answer = False  # флаг принятых данных
        self.reqwest = ""  # тип запроса (data, versia, noise)
        self.records = False  # флаг записи галса в файл

        self._check_project(self.st_bar)
        self.st_bar.set_device(msg)
        self.st_bar.set_info_gals("")

        self.init_fild()
        self.old_secs = 0

        self.gps_manager = GpsManager(self.g_ser, self)
        self.gps_receive = 0  # прием данных с НСП
        self.view_mod(mod_msg)
        self.set_flag = False
        self.view_delay(self.delay)
        self.win_help = None
        self._tick()

    def view_mod(self, msg: str) -> None:
        """Отобразить режим работы"""
        self.st_bar.set_mod(msg)

    def view_delay(self, delay: float) -> None:
        """Отобразить интервал запуска"""
        self.st_bar.set_delay(delay)

    def btn_start_(self) -> None:
        """Обработчик кнопки излучение"""
        if self.btn_start.cget("text") == self.START and not self.start_work:
            self.btn_start.configure(text=self.STOP)
            self.start_work = True
            self._clr_board_tag_all(("version", "noise"))
            if self.tools.flag_rec:
                self.tools.tick_gals()
                self.tools.flag_rec_color = False
                self.tools.blink_rec()
            self.unbind("<Control-z>")
        else:
            self.btn_start.configure(text=self.START)
            self.start_work = False
            self.bind("<Control-z>", self._full_scr)
            # self.tools.record()                    # нажаь кнопку запись для остановки
            try:
                self.after_cancel(self.tools.id_g)
                self.after_cancel(self.tools.id_rec)
            except ValueError:
                pass
            self._clr_board_tag_all(("glub",))
            if self.mod == 0 or self.mod == 3:
                self.sw_25.configure(state="normal")
            self._clr()
        # self.iconify()
        # self.resizable(not self.start_work, not self.start_work)
        # self.deiconify()

    def blink(self, arg=None) -> None:
        """Мигнуть рамкой кнопки излучения"""
        self.btn_start.configure(border_color="green")
        self.after(200, lambda: self.btn_start.configure(border_color="#D35B58"))

    def _mod_25(self) -> None:
        """Обработчик кнопки 25kHz"""
        # if self.btn_start.cget('text') == self.START:
        self.set_flag = True
        if self.sw_25.get() == "%":
            self.adr = "%"
            self.sw_25.configure(text="25кГц")
            self.u_panel.update_upr(self.data_upr_25)
            if self.send_data_50.rej == "R":
                self.u_panel.b6.grid(row=8, column=0, pady=10, padx=10, sticky="w")
        elif self.sw_25.get() == "$":
            self.adr = "$"
            self.sw_25.configure(text="50кГц")
            self.u_panel.b6.grid_forget()
            self.u_panel.update_upr(self.data_upr_50)
        self.after(20, self.reset_flag)

    def reset_flag(self) -> None:
        """Сбросить флаг для update_upr"""
        self.set_flag = False

    def gps_read_data(self, data: bytes) -> None:
        """Чтение порта GPS"""
        self.gps_manager.gps_read_data(data)

    def set_local_time(self) -> None:
        """Установка машинного времени в head"""
        t = time.strftime("%d.%m.%y %H:%M:%S")
        arg = ("", "", "", "", t, False)
        self.head.set_(*arg)

    @staticmethod
    def _open_ports(ser: PortThread, g_ser: PortThread, ser_2: PortThread = None) -> str:
        """Открытие портов"""
        port_pui = config.get("Port", "port_pui")
        baudrate_pui = config.getint("Port", "baudrate_pui")
        port_pui_2 = config.get("Port", "port_pui_2")
        port_gps = config.get("Port", "port_gps")
        baudrate_gps = config.getint("Port", "baudrate_gps")
        timeout = config.getfloat("Port", "timeout")
        timeout_gps = config.getfloat("Port", "timeout_gps")
        error_p, error_p_2, error_g = "", "", ""
        try:
            ser.open_port(port_pui)
            ser.tty.baudrate = baudrate_pui
            ser.tty.timeout = timeout
            ser.start()
        except port_exc:
            error_p = "не"
        if ser_2:
            try:
                ser_2.open_port(port_pui_2)
                ser_2.tty.baudrate = baudrate_pui
                ser_2.tty.timeout = timeout
                ser_2.start()
            except port_exc:
                error_p_2 = "не"
        if g_ser:
            try:
                g_ser.open_port(port_gps)
                g_ser.tty.baudrate = baudrate_gps
                g_ser.tty.timeout = timeout_gps
                g_ser.start()
            except port_exc:
                error_g = "не"
        else:
            error_g = "не"
        msg_2 = (
            f"Порты:  ППУ  <{port_pui}> {error_p} открыт,  <{port_pui_2}>"
            f" {error_p_2} открыт,   НСП  <{port_gps}> {error_g} открыт."
        )
        msg_1 = f"Порты:  ППУ  <{port_pui}> {error_p} открыт," f"   НСП  <{port_gps}> {error_g} открыт."
        return msg_2 if ser_2 else msg_1

    def init_fild(self) -> None:
        """Создание нового полотна и очередей"""
        self.board_50.create_fild()
        self.board_25.create_fild()
        # self.update_idletasks()
        self.update()
        self.after(100, self.bind_)
        # self.bind_()

    def bind_(self) -> None:
        """Привязки событий"""
        self.bind("<Up>", self.brd_up)
        self.bind("<Down>", self.brd_down)
        self.bind("<Home>", self.brd_home)
        self.bind("<End>", self.brd_end)
        self.bind("<Alt-F4>", self._on_closing)
        self.bind("<Return>", lambda: None)
        self.bind("<Control-p>", self.brd_all_one_echo)
        self.bind("<Control-l>", self.brd_show_duration_echo)
        # self.bind("<Control-b>", self.board.fon_color_ch)
        self.bind("<Control-b>", self.brd_fon_color_ch)
        self.bind("<Control-m>", self.brd_off_scale)
        self.bind("<Control-t>", self.brd_time_metka_on)
        self.bind("<Control-w>", self.brd_hide_metki)
        self.bind("<Control-h>", self.create_toplevel_help)
        self.bind("<Control-o>", self.change_app_mode)
        self.bind("<Control-v>", self.get_version)
        self.bind("<Control-n>", self.get_noise)
        self.bind("<Control-e>", self.edit_config)
        # self.bind("<Control-z>", self._full_scr)
        self.bind("<Escape>", self._clr)
        # self.withdraw()
        self.deiconify()

    def _full_scr(self, arg=None):
        """Развернуть на весь экран"""
        self.state("zoomed") if self.wm_state else self.state("normal")
        self.attributes("-fullscreen", self.wm_state)
        self.wm_state = not self.wm_state
        self._change_appearance_mode("Light")
        self._change_appearance_mode("Dark")

    def brd_up(self, arg=None):
        """Up"""
        self.board_50.up()
        self.board_25.up()

    def brd_down(self, arg=None):
        """Down"""
        self.board_50.down()
        self.board_25.down()

    def brd_home(self, arg=None):
        """Home"""
        self.board_50.home()
        self.board_25.home()

    def brd_end(self, arg=None):
        """End"""
        self.board_50.en()
        self.board_25.en()

    def brd_all_one_echo(self, arg=None):
        """Показать все цели"""
        self.board_50.all_one_echo()
        self.board_25.all_one_echo()

    def brd_show_duration_echo(self, arg=None):
        """Показать длительность"""
        self.board_50.show_duration_echo()
        self.board_25.show_duration_echo()

    def brd_off_scale(self, arg=None):
        """Авто шкала"""
        self.board_50.off_scale()
        self.board_25.off_scale()

    def brd_hide_metki(self, arg=None):
        """Скрыть метки"""
        self.board_50.hide_metki()
        self.board_25.hide_metki()

    def brd_time_metka_on(self, arg=None):
        """Скрыть время на метках"""
        self.board_50.time_metka_on()
        self.board_25.time_metka_on()

    def brd_fon_color_ch(self, arg=None):
        """Сменить фон"""
        self.board_50.fon_color_ch()
        self.board_25.fon_color_ch()

    def _clr_board_tag_all(self, tag: tuple) -> None:
        """Очистить на холстах элементы с тегами"""
        self.board_50.clr_item(tag)
        self.board_25.clr_item(tag)

    def _clr(self, arg=None) -> None:
        """Обработчик клавиши ESC"""
        self._clr_board_tag_all(("version", "noise", "not_data"))

    def _tick(self) -> None:
        """Системный тик"""
        secs = time.time()
        if secs - self.old_secs >= self.delay:  # задержка 1.0, 3.2, 9.0
            self.old_secs = secs
            if self.btn_start.cget("text") == self.STOP:
                self._step_on_50()
            else:
                self.old_secs = 0
                self._clr_board_tag_all(("error", "glub"))  # убрать Нет связи с ППУ!!
                self.board_50.old_glub = 0
                self.board_25.old_glub = 0
                self.crashes_50 = 0
                self.crashes_25 = 0
            if self.gps_receive < 0:
                self.set_local_time()  # показать локал. время
        self.update()
        self.after(20, self._tick)

    def _step_on_50(self) -> None:
        """Один цикл работы с модулем 50"""
        # self.t = time.time()
        self.gps_receive -= 1
        if self.enable_50:
            # print('50')                             # !!!
            self.reqwest = "data"
            self.answer = False  # сбросить флаг ответа
            self._clr_board_tag_all(("versbindion", "noise"))
            dat = data_to_byte(self.send_data_50)
            trace(f"50 {dat}")
            self.crashes_50 += 1
            # if self.crashes_50 > 1:
            #     print(f"25 {self.crashes_50}")
            if self.ser_50.is_open():
                self.ser_50.clear_port()
                self.ser_50.send(dat)  # посылка данных в ХК без потока
                # self.ser_50.send_thread(dat)
            if self.crashes_50 >= 3:
                self.crashes_50 = 3
                self.board_50.create_error("error")  # Надпись Нет связи с ППУ на холст    !!
                self.loop_50.set(0)
                # self.delay_50 = self.delay_mg
            self.id_timeout = self.after(self.schift, self._step_on_25)  # 565 min
            if self.flip_flop:
                self.enable_50 = False
                self.after_cancel(self.id_timeout)
        else:
            if self.flip_flop:
                self.enable_25 = True
            self._step_on_25()

    def _step_on_25(self) -> None:
        """Один цикл работы с модулем 25"""
        # print(time.time() - self.t)
        if self.id_timeout:
            self.after_cancel(self.id_timeout)
            self.id_timeout = None
        if self.enable_25:
            # print('25')                                 # !!!
            self.reqwest = "data"
            self.answer = False  # сбросить флаг
            self._clr_board_tag_all(("version", "noise"))
            dat = data_to_byte(self.send_data_25)
            trace(f"25 {dat}")
            self.crashes_25 += 1
            # if self.crashes_25 > 1:
            # print(f'25 {self.crashes_25}')
            if self.ser_25.is_open():
                self.ser_25.clear_port()
                self.ser_25.send(dat)  # посылка данных в ХК без потока
                # self.ser_25.send_thread(dat)
            if self.crashes_25 >= 3:
                self.crashes_25 = 3
                self.board_25.create_error("error")  # Надпись Нет связи с ППУ на холст    !!
                self.loop_25.set(0)
                # self.delay_25 = self.delay_mg
            if self.flip_flop:
                self.enable_50 = True

    def on_receive_func_50(self, data: bytes) -> None:
        """Чтение порта XK"""
        self.on_receive_func(data, num=True)

    def on_receive_func_25(self, data: bytes) -> None:
        """Чтение порта XK"""
        self.on_receive_func(data, num=False)

    def on_receive_func(self, data: bytes, num: bool = True) -> None:
        """Чтение порта XK"""
        self.update()
        ser = self.ser_50 if num else self.ser_25
        timeout = config.getfloat("Port", "timeout")
        ser.tty.timeout = timeout
        match self.reqwest:
            case "data":
                if data == b"!":
                    ser.max_message_len = 91
                    trace(f"{data} > #")
                    ser.send(b"#")
                    # ser.send_thread(b'#')
                elif len(data) == 91 and data[-2:] == b"\r\n":
                    if data[0] == 36:  # $
                        num = True
                        self.crashes_50 = 0
                        self.loop_50.set(True)
                    elif data[0] == 37:  # %
                        num = False
                        self.crashes_25 = 0
                        self.loop_25.set(True)
                    else:
                        ser.max_message_len = 1
                        trace("<@>")
                        return
                    ser.max_message_len = 1
                    trace(f"{data}")
                    self._work(data[1:-2], num)
                    self.blink()  # мигнуть
                else:
                    ser.max_message_len = 1
                    trace(f"*{len(data)}")
            case "version":
                if data == b"!":
                    ser.max_message_len = 1024
                    trace(data)
                elif len(data) > 20:
                    self._show_version(data)
                    ser.max_message_len = 1
                # else:
                #     print("error version")
            case "noise":
                if data == b"!":
                    ser.max_message_len = 1024
                    trace(data)
                    ser.send(b"#")
                    ser.tty.timeout = 0.5
                elif len(data) == 403:
                    # print(len(data))  # 403
                    self._show_noise(data[1:])
                    ser.max_message_len = 1
                # else:
                #     print(len(data))
                #     print("error noise")
        self.update()

    def _work(self, data: bytes, num: bool) -> None:
        """Режим работа"""
        # self.t = time.perf_counter()
        self.answer = True
        self.board = self.board_50 if num else self.board_25
        # depth = chr(data[0])
        data_point, data_ampl, data_len = self._parce_data(data, num)
        # d_len = array.array("B")
        # for i in data_len:
        #     d_len.append(self.cal_len(i, depth))  # !@
        # self._update_data_deque(data_point, data_ampl, d_len, num)
        # self.board.show(data_point, data_ampl, d_len)  # отобразить на холсте
        self._update_data_deque(data_point, data_ampl, data_len, num)
        self.board.show(data_point, data_ampl, data_len)  # отобразить на холсте
        if self.records:
            f_gals = self.tools.file_gals if num else self.tools.file_gals_25
            self._write_gals(f_gals, data_point, data_ampl, data_len, num)  # если надо то пишем в файл
        # print(num, time.perf_counter() - self.t)

    def _update_data_deque(self, data_p: array.array, data_a: array.array, data_l: array.array, num: bool) -> None:
        """Очередь для хранения данных всего экрана"""
        shot = ([n / 10 for n in data_p], data_a, data_l, self.board.mark_type)
        self.data_deq_50.appendleft(shot) if num else self.data_deq_25.appendleft(shot)  # !!

    def _parce_data(self, data: bytes, num: bool) -> tuple[array.array, ...]:
        """
        Разбор данных, глубин и амплитуд
        (b'depth,ku,m,cnt,g0h,g0l,a0h,a0l,d0h,d0l,
         g1h,g1l,a1h,a1l,c1,l1, ... gnh,gnl,anh,anl,cn,ln')
        """
        zg = int(self._zg * 10)  # заглубление
        depth = chr(data[0])
        self.depth = depth
        ku = chr(data[1])
        send_data = self.send_data_50 if num else self.send_data_25
        if num and self.send_data_50.rej == "S":
            send_data.depth = depth  # в ручке не обнавлять
            send_data.ku = ku
        elif not num and self.send_data_25.rej == "S":
            send_data.depth = depth  # в ручке не обнавлять
            send_data.ku = ku
        # print(depth, self.old_depth)
        # if depth != self.old_depth and self.send_data_50.rej == 'S':     # в ручке не обнавлять
        if self.send_data_50.rej == "S":
            # self.old_depth = depth
            delay = self.change_delay(send_data.depth)
            if num:
                self.delay_50 = delay
            else:
                self.delay_25 = delay
            self.delay = max(self.delay_50, self.delay_25)
            self.view_delay(self.delay)  # вывод время цикла
        m_cnt = data[2]
        cnt = data[3]
        distance = int.from_bytes(data[4:6], "big")
        distance = distance + zg if distance else 0
        ampl = data[6]
        len_ = data[7]
        # len__ = self.cal_len_(len_, depth)
        data_upr = ViewDataUpr(depth, ku, cnt, m_cnt, ampl, len_, distance)
        if num:
            self.data_upr_50 = data_upr
            if self.adr == "$":
                self.u_panel.update_upr(data_upr)  # данные для панели управления 50
        else:
            self.data_upr_25 = data_upr
            if self.adr == "%":
                self.u_panel.update_upr(data_upr)  # данные для панели управления 25
        self.board.view_glub(distance)  # вывод глубины
        data_point = array.array("H")  # 'H' 2 bytes 'B' 1 bytes
        data_ampl = array.array("B")
        data_len = array.array("B")
        data_point.append(distance)
        data_ampl.append(ampl)
        data_len.append(len_)
        dat = data[8:]
        cnt = 20 if cnt > 20 else cnt
        for i in range(0, cnt * 4, 4):
            dist_ = int.from_bytes(dat[i:i + 2], "big") + zg
            ampl_ = dat[i + 2]
            len_ = dat[i + 3]
            data_point.append(dist_)
            data_ampl.append(ampl_)
            data_len.append(len_)
        return data_point, data_ampl, data_len

    def change_delay(self, depth: str) -> float:
        """Вычисление периода запуска"""
        if depth == "L":
            delay = self.delay_mg
        elif depth == "M":
            delay = self.delay_sg
        elif depth == "H":
            delay = self.delay_bg
        else:
            delay = self.delay_b6
        return delay

    @staticmethod
    def calc_n(depth: str) -> float:
        """Вычислить множитель"""
        if depth == "L":
            n = 0.4
        elif depth == "M":
            n = 1.6
        elif depth == "H":
            n = 12.8
        elif depth == "B":
            n = 12.8  # !!
        else:
            n = 0.0
        return n

    def cal_len_(self, cod: int, depth: str) -> float:
        """Вычислить длительность эхо для файла"""
        n = self.calc_n(depth)
        if n > 12 and cod > 126:
            cod = 126
        return round(cod * n * self._vz / 10000, 2)

    def _show_version(self, data: bytes) -> None:
        """Показать номер версии на холсте"""
        self.answer = True
        board = self.board_50 if self.adr == "$" else self.board_25
        self._clr_board_tag_all(("noise", "not_data", "glub"))
        data = data.decode("latin-1")  # str
        # if len(data) == 33:
        board.view_version(data)  # !!

    def _show_noise(self, data: bytes) -> None:
        """Вывести шум на холст"""
        # print(f"len = {len(data)}")
        self.answer = True
        board = self.board_50 if self.adr == "$" else self.board_25
        # data = data.decode('latin-1')         # str
        self._clr_board_tag_all(("version", "not_data", "glub"))
        # if len(data) == 402:
        # print(len(data))
        board.view_noise(data)  # !!

    def get_version(self, arg=None) -> None:
        """Callback для номера версии"""
        self._get_noise_version("V")
        self.close_help()

    def get_noise(self, arg=None) -> None:
        """Callback для шума"""
        self._get_noise_version("N")
        self.close_help()

    def _get_noise_version(self, type_) -> None:
        """Получить данные для шума или версии"""
        # b'$NRL05\x05\xdc8c\r\n'                    # request noise     50
        # b'$VRL05\x05\xdc94\r\n'                    # request version   50
        if self.win_help:
            self.win_help.destroy()
        data = self.send_data_50 if self.adr == "$" else self.send_data_25
        ser = self.ser_25 if self.adr == "%" else self.ser_50
        if not self.start_work:
            self.reqwest = "noise" if type_ == "N" else "version"
            work_ = "N" if type_ == "N" else "V"
            work = data.work
            data.work = work_
            start = data.start
            data.start = self.adr
            dat = data_to_byte(data)
            data.work = work
            data.start = start
            # ser.send_thread(dat)
            ser.send(dat)
            self.answer = False
            time.sleep(1)
            self.after(500, self._not_data)

    def _not_data(self) -> None:
        """Вывести на холст Нет данных"""
        if not self.answer:
            self._clr_board_tag_all(("version", "noise"))
            self.board.create_error("not_data")

    def change_data_upr(self, rej: str, depth: str, ku: str) -> None:
        """Были изменения в ручном режиме обнавляем DataRequest"""
        data = self.send_data_50 if self.adr == "$" else self.send_data_25
        data.depth = depth
        data.ku = ku
        data.rej = rej
        if self.adr == "$":
            if depth == "L":
                self.delay_50 = self.delay_mg
            elif depth == "M":
                self.delay_50 = self.delay_sg
            else:
                self.delay_50 = self.delay_bg
        else:
            self.data_upr_25.ku = ku
            self.data_upr_25.depth = depth
            if depth == "L":
                self.delay_25 = self.delay_mg
            elif depth == "M":
                self.delay_25 = self.delay_sg
            elif depth == "H":
                self.delay_25 = self.delay_bg
            else:
                self.delay_25 = self.delay_b6
            if rej == "R":
                self.u_panel.b6.grid(row=8, column=0, pady=10, padx=10, sticky="w")
            else:
                self.u_panel.b6.grid_forget()
        self.delay = max(self.delay_50, self.delay_25)
        self.view_delay(self.delay)

    def _write_gals(
        self,
        filename: Path,
        data_p: array.array,
        data_a: array.array,
        data_l: array.array,
        num: bool,
    ) -> None:
        """Пишем в файл"""
        data = self.prepare_data_gals(data_p, data_a, data_l, num)
        # print(data)
        with open(filename, "a", newline="") as f:
            f_csv = csv.writer(f)
            f_csv.writerow(data)

    def prepare_data_gals(self, data_p: array.array, data_a: array.array, data_l: array.array, num: bool) -> list:
        """Подготовить данные для записи галса
        (формат, глубина, амплитуда, длительность, объект дата время,
         широта, долгота, скорость, курс, скорость звука, осадка, порог,
         диап. глубин, режим, частота, число стопов, число кор. стопов,
         ручн. метка, цвет ручн. метки , авто метка.)
        """
        format_ = config.get("System", "fmt")
        # vz = config.getint('System', 'vz')
        vz = self._vz
        zg = self._zg
        dt = self.data_upr_50 if num else self.data_upr_25
        send_data = self.send_data_50 if num else self.send_data_25
        freq = "50" if num else "25"
        depth, ku, cnt, m, ampl, lenth, glub = (
            dt.depth,
            dt.ku,
            dt.cnt,
            dt.m,
            dt.ampl,
            dt.len,
            dt.distance,
        )
        rej = send_data.rej
        try:
            # gps_t, gps_s, gps_d, gps_v, gps_k = self.gps_manager.get_data_gps()
            raise TypeError
        except TypeError:
            gps_t, gps_s, gps_d, gps_v, gps_k = "", "", "", "", ""
        if not gps_t:
            gps_t = time.strftime("%d.%m.%y %H:%M:%S")
        mark_ = self.data_deq_50[0][-1] if num else self.data_deq_25[0][-1]
        m_man, m_avto, color_mm = "", "", ""
        if mark_[0]:
            if mark_[1] == "M":
                m_man = mark_[0]
                color_mm = "red"
            if mark_[1] == "A":
                m_avto = mark_[0]
        file_list = [
            format_,
            glub,
            ampl,
            # lenth,
            self.cal_len_(lenth, depth),
            gps_t,
            gps_s,
            gps_d,
            gps_v,
            gps_k,
            vz,
            zg,
            f"{int(ku, 16)}",
            depth,
            rej,
            freq,
            cnt,
            m,
            m_man,
            color_mm,
            m_avto,
        ]
        for gd, ad, ld in zip(data_p[1:], data_a[1:], data_l[1:]):
            file_list.extend([gd, ad, self.cal_len_(ld, depth)])
        return file_list

    def pref_form(self, d: str, z: float, vz: int, zona: float) -> None:
        """Возврат результата из формы 'DBT'.., z(заглубл.) если есть изменения и
        переписать config.ini"""
        self._zg = z  # изменение заглубл.
        self._vz = vz
        self._zona = zona
        s = vz.to_bytes(2, "big").decode("latin-1")
        self.send_data_50.sv = s
        self.send_data_25.sv = s
        self.r_frame.tools.update_(f"{z}", d, vz)
        self.head.set_utc()
        config.set("System", "zagl", f"{z}")
        config.set("System", "fmt", f"{d}")
        write_config()

    def change_app_mode(self, arg=None) -> None:
        self._change_appearance_mode("Light") if self.theme_mode else self._change_appearance_mode("Dark")
        self.close_help()
        geometry_str = self.geometry()
        tmp = geometry_str.split("x")
        width = tmp[0]
        tmp2 = tmp[-1].split("+")
        height = tmp2[0]
        x = tmp2[1]
        y = str(int(tmp2[2]) + 1)
        self.geometry(f"{width}x{height}+{x}+{y}")  # дергаем окно

    def _change_appearance_mode(self, new_appearance_mode: str) -> None:
        """Сменить тему"""
        if new_appearance_mode == "Dark":
            self.s.configure("TSizegrip", background="grey19")
            self.theme_mode = 1
            # self.app_mode.set(0)
        else:
            self.s.configure("TSizegrip", background="grey82")
            self.theme_mode = 0
            # self.app_mode.set(1)
        ctk.set_appearance_mode(new_appearance_mode)
        config.set("Font", "app_mode", f"{self.theme_mode}")
        write_config()

    @staticmethod
    def _check_project(st_bar: Footer) -> None:
        """Проверка существования поекта"""
        if not Path(config.get("Dir", "dirprj")).exists():
            config.set("Dir", "dirprj", "")
            write_config()
            st_bar.set_info_project("")

    def edit_config(self, arg=None):
        """Редактировать файл config.ini"""
        window_ = CTkTop(
            title="Config.ini",
            icon="config",
            font=self.font,
            border_width=2,
            width=1100,
            height=800,
        )  # btn_close=False,
        frame = ctk.CTkFrame(window_.w_get)
        frame.grid(sticky="nsew")

        SimpleEditor(window_, frame)
        self.close_help()
        # self.after(300, lambda: self.top.close_help())

    def create_toplevel_help(self, arg=None) -> None:
        """Окно подсказок для привязок"""
        self.top = ToplevelHelp(self)

    def close_help(self, arg=None) -> None:
        """Убрать окно"""
        # self.top.close_help()
        self.after(300, lambda: self.top.close_help())

    def _on_closing(self) -> None:
        """Выход"""
        if self.btn_start.cget("text") == self.STOP:
            self.btn_start_()  # Перейти в ожидание если излучение
        self.ser_50.stop()
        self.ser_25.stop()
        self.g_ser.stop()
        # sys.stdout.flush()
        raise SystemExit()


class GpsManager:
    """Класс работы с НСП(GPS)"""

    def __init__(self, g_ser: PortThread, root):
        self.g_ser = g_ser
        self.root = root
        self.head = self.root.head
        self.crashes_gps = 5
        self.data_gps = None
        self._zona = config.getfloat("System", "vzona")

    # def _set_local_time(self) -> None:
    #     """Установка машинного времени в head"""
    #     t = time.strftime('%d.%m.%y %H:%M:%S')
    #     arg = ('', '', '', '', t, False)
    #     self.head.set_(*arg)

    def gps_read_data(self, data: bytes) -> None:
        """Приём из НСП в потоке
        '$GPRMC,123519.xxx,A,4807.038x,N,01131.000x,E,x22.4,084.4,230394,003.1,W*6A\n'
        123419 – UTC время 12:34:19, А – статус, 4807.038,N – Широта, 01131.000,Е – Долгота,
        022.4 – Скорость, 084.4 – Направление движения, 230394 – Дата, 003.1,W – Магнитные вариации
        """
        # print(f'<< {data}')
        self.root.gps_receive = 2
        # if data.startswith(b'$') and data.endswith(b'\r\n'):
        #     self.tmp = self.tmp2 = b''
        # else:
        #     if data.startswith(b'$'):
        #         self.tmp = data
        #     elif data.endswith(b'\r\n'):
        #         self.tmp2 = data
        #     if self.tmp and self.tmp2:
        #         data = self.tmp + self.tmp2
        #         self.tmp = self.tmp2 = b''
        #     else:
        #         data = b''
        # print(f'< {data}')
        if data:
            self.crashes_gps = 0
            data = data.decode("latin-1").split(",")[1:10]  # list[str...]
            if len(data) == 9:
                self._parse_data_gps(data)
            else:
                self.crashes_gps += 1
        else:
            self.crashes_gps += 1
        if self.crashes_gps > 3:
            self.crashes_gps = 3
            self.root.set_local_time()

    def _parse_data_gps(self, data: list) -> None:
        """Разбор данных gps"""
        # print('+')
        try:
            s_ = data[2].split(".")
            d_ = data[4].split(".")
            sh = f"{s_[0][:-2]} {s_[0][-2:]}.{s_[1][:3]} {data[3]}"  # {0xB0:c} °
            d = f"{d_[0][:-2]} {d_[0][-2:]}.{d_[1][:3]} {data[5]}"
        except IndexError:
            # print(f'e > {er}')
            sh = d = ""
        try:
            str_struct = time.strptime(data[0].split(".")[0] + data[8], "%H%M%S%d%m%y")
            t_sec = time.mktime(str_struct)
            t_sec += self._zona * 3600
            str_struct = time.localtime(t_sec)
            t = time.strftime("%d.%m.%y %H:%M:%S", str_struct)
        except (IndexError, ValueError):
            # print(f't > {er}')
            t = ""
        try:
            vs = f"{float(data[6]):=04.1f}"  # ! 05.1f
            k = f"{float(data[7]):=05.1f}"
        except (IndexError, ValueError):
            # print(f'v > {er}')
            vs = k = ""
        self.head.set_(sh, d, vs, k, t, True)  # только если излучение
        self.data_gps = (t, sh, d, vs, k)

    def get_data_gps(self) -> tuple:
        """Вернуть данные GPS"""
        return self.data_gps


if __name__ == "__main__":
    app = App()
    # app.attributes("-fullscreen", True)       # во весь экран без кнопок
    # app.state('zoomed')                       # развернутое окно


    app.mainloop()
