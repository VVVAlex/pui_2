#!/usr/bin/env python
import csv
import os
import pathlib
import time
import tkinter as tk
from tkinter import ttk
import customtkinter as ctk
import dialog as dlg_
from common import (
    config,
    family,
    font_size,
    load_image,
    write_config,
)
from ctkmessagebox import CTkMessagebox as Box
from preferens import Window

list_images = ("coment", "info", "kol", "handle", "avto")


class Tools(ctk.CTkFrame):
    """Управление видимостью"""

    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.root = master.root
        vz = config.getint("System", "vz")
        zagl = config.getfloat("System", "zagl")
        fmt = config.get("System", "fmt")
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        # self.root.app_mode.trace('w', self.reconfig_image)
        self.font = font
        self.path = pathlib.Path(os.path.abspath("."))
        path_ = self.path.joinpath("Проекты")  # каталог для файлов проектов
        if not path_.exists():
            os.mkdir(path_)

        self.old_sec = 0
        self.tgals_minut = 0
        self.tgals_hour = 0
        self.id_g = None
        self.id_rec = None
        self.flag_rec_color = False
        self.flag_rec = False
        self.time_gl = tk.StringVar()
        self.time_gl.set("00 : 00")
        self.file_gals = ""
        # self.win_ = None  # нет окна заглубления

        k_image = load_image(
            "kol.png",
        )
        i_image = load_image(
            "info.png",
        )
        handle_image = load_image(
            "handle.png",
        )
        coment_image = load_image(
            "coment.png",
        )
        avto_image = load_image(
            "avto.png",
        )
        self.img_records = load_image(
            "record1.png",
        )
        self.img_pause = load_image(
            "pause1.png",
        )

        row = 0
        pad_x = 10
        pdx_l = (10, 0)
        pdx_r = (0, 10)

        row += 1
        # row_ = 0
        self.btn_record = ctk.CTkButton(
            master=self,
            text="Запись",
            width=140,
            font=font,
            text_color=("gray10", "gray90"),
            image=self.img_records,
            height=40,
            border_width=2,
            corner_radius=10,
            compound="right",
            border_color="green",
            fg_color=("gray84", "gray25"),
            hover_color="SeaGreen3",
            command=self.record,
        )
        self.btn_record.grid(row=row, column=0, padx=pdx_l, pady=(5, 2), sticky="w")
        self.lab_time_gals = ctk.CTkLabel(
            master=self,
            textvariable=self.time_gl,
            font=font,
            anchor="w",
            width=70,
        )
        self.lab_time_gals.grid(row=row, column=1, padx=pdx_r, pady=(2, 2), sticky="e")
        row += 1
        ttk.Separator(self).grid(
            pady=4, row=row, column=0, columnspan=2, padx=5, sticky="ew"
        )
        row += 1
        self.btn_pr_name = ctk.CTkButton(
            master=self,
            text="Проект",
            font=font,
            text_color=("gray10", "gray90"),
            width=90,
            height=30,
            border_width=2,
            border_color="#1f6aa5",
            fg_color="transparent",
            # fg_color="gray40", hover_color="gray25",
            command=self.new_project,
        )
        self.btn_pr_name.grid(row=row, column=0, padx=pdx_l, pady=(2, 2), sticky="w")
        self.btn_gals_name = ctk.CTkButton(
            master=self,
            text="Галс",
            font=font,
            text_color=("gray10", "gray90"),
            width=90,
            height=30,
            border_width=2,
            border_color="#1f6aa5",
            fg_color="transparent",
            # fg_color="gray40", hover_color="gray25",
            command=self.new_gals,
        )
        self.btn_gals_name.grid(row=row, column=1, padx=pdx_r, pady=(2, 2), sticky="e")
        row += 1
        ttk.Separator(self).grid(
            pady=2, row=row, column=0, columnspan=2, padx=5, sticky="ew"
        )
        row += 1
        ctk.CTkLabel(master=self, text="Вид", font=font, anchor="w").grid(
            row=row,
            column=0,
            padx=pdx_l,
            pady=(2, 2),
            sticky="w",
        )
        self.lab_vid = ctk.CTkButton(
            master=self,
            image=k_image,
            text="",
            width=40,
            height=30,
            border_width=2,
            # fg_color='transparent',
            # fg_color="gray40", hover_color="gray25",
            command=self.root.create_toplevel_help,
        )
        self.lab_vid.grid(row=row, column=1, padx=pdx_r, pady=(2, 2), sticky="e")
        row += 1
        ctk.CTkLabel(master=self, text="Скорость звука", font=font, anchor="w").grid(
            row=row, column=0, padx=pdx_l, sticky="w"
        )
        self.lab_vid = ctk.CTkLabel(
            master=self, text=f"{vz}", font=font, anchor="e", width=70
        )
        self.lab_vid.grid(row=row, column=1, padx=pdx_r, sticky="e")
        row += 1
        ctk.CTkLabel(master=self, text="Заглубление", font=font, anchor="w").grid(
            row=row,
            column=0,
            padx=pdx_l,
            pady=(0, 0),
            sticky="w",
        )
        self.lab_zagl = ctk.CTkLabel(
            master=self, text=f"{zagl}", anchor="e", font=font, width=70
        )
        self.lab_zagl.grid(row=row, column=1, padx=pdx_r, sticky="e")
        row += 1
        self.lab_format = ctk.CTkLabel(
            master=self, text=f"{fmt}", font=font, anchor="w"
        )
        self.lab_format.grid(row=row, column=0, padx=pdx_l, pady=(2, 2), sticky="w")
        self.btn_fon = ctk.CTkButton(
            master=self,
            image=i_image,
            text="",
            width=40,
            height=30,
            border_width=2,
            # fg_color='transparent',
            # fg_color="gray40", hover_color="gray25",
            command=self._deepening,
        )
        self.btn_fon.grid(row=row, column=1, padx=pdx_r, pady=(2, 2), sticky="e")
        row += 1
        ttk.Separator(self).grid(
            pady=2, row=row, column=0, columnspan=2, padx=5, sticky="ew"
        )
        row += 1
        ctk.CTkLabel(
            master=self,
            text="Метки",
            corner_radius=9,
            font=font,
            padx=1,
            pady=1,
        ).grid(row=row, column=0, columnspan=2, padx=pad_x, pady=(0, 1), sticky="ew")
        row += 1
        self.btn_mark_a = ctk.CTkButton(
            master=self,
            image=avto_image,
            text="Авто".center(10),
            height=30,
            font=font,
            border_width=2,
            # fg_color='transparent',
            command=self._press_avto,
        )
        # ToolTip(self.btn_osadka, msg='Осадка', fg="white", bg="gray25")
        self.btn_mark_a.grid(
            row=row, column=0, columnspan=2, padx=pad_x, pady=(0, 5), sticky="ew"
        )
        row += 1
        self.btn_mark_r = ctk.CTkButton(
            master=self,
            image=handle_image,
            text="Ручная".center(10),
            height=30,
            font=font,
            border_width=2,
            # fg_color='transparent',
            command=self._press_manual,
        )
        self.btn_mark_r.grid(
            row=row, column=0, columnspan=2, padx=pad_x, pady=(0, 5), sticky="ew"
        )
        row += 1
        self.btn_book = ctk.CTkButton(
            master=self,
            image=coment_image,
            text="Заметки",
            height=28,
            border_width=2,
            font=font,
            command=self._db_show,
        )
        self.btn_book.grid(
            row=row, column=0, columnspan=2, padx=pad_x, pady=(0, 10), sticky="ew"
        )
        row += 1
        ttk.Separator(self).grid(
            pady=(10, 10), row=row, column=0, columnspan=2, padx=5, sticky="ew"
        )

        # Separator
        # row += 1
        # ctk.CTkFrame(root.frame_tools, height=2, border_width=1,
        #              fg_color=('grey95', 'grey45')).grid(
        #     pady=5, row=row, column=0, columnspan=2, padx=5, sticky="ew")

        # self.reconfig_image(None, None, None)

    def record(self) -> None:
        """Обработчик кнопки записи"""
        if (
            self.btn_record.cget("text") == "Запись"
            and self.root.start_work
            and self.file_gals
        ):
            self.btn_record.configure(text="Пауза", image=self.img_pause)
            self.flag_rec = True
            self._write_file()
            self.tick_gals()
            self.blink_rec()
        else:
            self.btn_record.configure(text="Запись", image=self.img_records)
            self.flag_rec = False
            self._stop_write_file()
            try:
                self.root.after_cancel(self.id_g)
                self.root.after_cancel(self.id_rec)
            except ValueError:
                pass

    def tick_gals(self) -> None:
        """Время записи галса"""
        secs = time.time()
        if secs - self.old_sec >= 60.0:  # 1 мин
            self.old_sec = secs
            if self.tgals_minut >= 60:
                self.tgals_minut = 0
                self.tgals_hour += 1
            self.time_gl.set(f"{self.tgals_hour:02d} : {self.tgals_minut:02d}")
            self.tgals_minut += 1
        self.id_g = self.root.after(5000, self.tick_gals)

    def blink_rec(self, arg=None) -> None:
        """Мигнуть рамкой кнопки"""
        color = "green" if self.flag_rec_color else "red"
        self.btn_record.configure(border_color=color)
        self.flag_rec_color = not self.flag_rec_color
        self.id_rec = self.root.after(500, self.blink_rec)

    def _write_file(self) -> None:
        """Запись в файл"""
        self.root.records = True

    def _stop_write_file(self) -> None:
        """Остановить запись в файл"""
        self.root.records = False
        if self.id_rec:
            self.root.after_cancel(self.id_rec)
            self.btn_record.configure(border_color="#499c54")  # стоп
            self.id_rec = None
        if self.id_g:
            self.root.after_cancel(self.id_g)

    def config_avto(self, msg: str) -> None:
        """Установить значение интервала на кнопке Авто"""
        self.btn_mark_a.configure(text=msg.center(15))

    def _press_manual(self, arg=None) -> None:
        """Обработчик кнопки ручных меток"""
        if self.root.start_work:
            if self.root.adr == "$":
                self.root.board_50.op_manual()  # !!
            else:
                self.root.board_25.op_manual()

    def _press_avto(self, arg=None) -> None:
        """Обработчик кнопки авто меток"""
        if self.root.start_work:
            if self.root.adr == "$":
                self.root.board_50.op_avto()  # !!
            else:
                self.root.board_25.op_avto()

    def _db_show(self, arg=None) -> None:
        """Обработчик кнопки заметок"""
        if self.file_gals:
            if self.root.adr == "$":
                self.root.board_50.op_mark_bd()  # Просмотр базы !!
            else:
                self.root.board_25.op_mark_bd()

    def _deepening(self, event=None) -> None:
        """Обработчик кнопки формата глубины и заглубления"""
        self.win = Window(self.root)
        self.root.bind("<Escape>", self.close_win)
        # if self.win_ is None:
        # self.win_ = True
        # self.win = Window(self.root)
        # self.win.bind("<Escape>", self.close_win)
        # else:
        # self.win.lift()
        # self.win.focus()

    def close_win(self, arg=None) -> None:
        """Свернуть окно глубины и заглубления"""
        self.win.w.destroy()
        self.root.unbind("<Escape>")
        self.root.bind_()
        # self.win_ = None
        # self.win.unbind("<Escape>")
        # # self.root.bind_()
        # self.root.focus()
        # self.win.withdraw()

    def update_(self, msg=None, fmt=None, vz=None) -> None:
        """Обновить заглубление, формат глубины и скорость звука"""
        self.lab_zagl.configure(text=msg)
        self.lab_format.configure(text=fmt)
        self.lab_vid.configure(text=vz)

    def new_project(self) -> None:
        """Обработчик кнопки проект"""
        dlg_.get_str(
            self.root,
            "Ввод имени проекта",
            "Введите имя проекта",
            "",
            self._new_project,
        )

    def _new_project(self, arg=None) -> None:
        """Создать новый проект и сохранить путь в config"""
        # print(f'..{arg}')
        if arg:
            path = pathlib.Path(arg)
            prj_name = path.name
            prj_path = path.joinpath(os.path.abspath("."), "Проекты")
            path_prj = path.joinpath(prj_path, prj_name)
            if prj_name in os.listdir(prj_path):
                # box.showwarning("", "Проект с таким именем\n уже существует!")
                Box(
                    title="",
                    message="Проект с таким именем\n уже существует!",
                    font=self.font,
                    icon="warning",
                )
                return
            config.set("Dir", "dirprj", f"{path_prj}")
            write_config()
            self.root.st_bar.set_info_project(prj_name)
            try:
                os.mkdir(path_prj)
            except OSError:
                # box.showerror("", "Ошибка создания проекта!")
                Box(
                    title="",
                    message="Ошибка создания проекта!",
                    font=self.font,
                    icon="cancel",
                )

    def new_gals(self) -> None:
        """ "Обработчик кнопки галс"""
        if config.get("Dir", "dirprj"):
            dlg_.get_str(
                self.root, "Выбор галса", "Введите имя галса", "", self._new_gals
            )
        else:
            # box.showwarning("", "Проект не создан!")
            Box(title="", message="Проект не создан!", font=self.font, icon="cancel")

    def _new_gals(self, arg=None) -> None:
        """Смена галса"""
        if arg:
            self._stop_write_file()
            path = pathlib.Path(arg)
            gals_name_ = path.name
            prj_name = pathlib.Path(config.get("Dir", "dirprj"))
            # prj_name_25 = f'{prj_name}_25'
            # print(prj_name, prj_name_25)
            file_gals = pathlib.Path.joinpath(prj_name, gals_name_)
            gals_name = f"{gals_name_}.csv"
            gals_name_25 = f"{gals_name_}_25.csv"
            if gals_name in os.listdir(prj_name):
                # if not box.askyesno("", "Файл существует!\n" "Переписать файл?\n"):
                #     return
                response = Box(
                    title="",
                    message="Файл существует!\nПереписать файл?\n",
                    font=self.font,
                    icon="question",
                    option_2="Cancel",
                ).get()
                if response != "OK":
                    return
            self.time_gl.set("00 : 00")
            self.tgals_minut = 0
            self.tgals_hour = 0
            self.root.adr = "$"
            self.root.board_50.create_db_tb(prj_name, gals_name)
            self.root.adr = "%"
            self.root.board_25.create_db_tb(prj_name, gals_name_25)
            # print('new_gals', prj_name, gals_name, gals_name_25)
            self.root.adr = "$"
            self.root.st_bar.set_info_gals(file_gals)
            self.file_gals = f"{file_gals}.csv"
            self.file_gals_25 = f"{file_gals}_25.csv"
            if self.root.mod == 1:
                self._create_csv_head(self.file_gals)
            elif self.root.mod == 2:
                self._create_csv_head(self.file_gals_25)
            else:
                self._create_csv_head(self.file_gals)
                self._create_csv_head(self.file_gals_25)
            self.root.init_fild()  # Очистка поля
            self.root.board_50.new_avtom_()  # Остановить автометки
            self.root.board_25.new_avtom_()
            self.root.choose_gals = True

    @staticmethod
    def _create_csv_head(file) -> None:
        """Создание csv файла с заголовком head"""
        head = [
            "format_",
            "glub",
            "ampl",
            "lenth",
            "timdata",
            "shir",
            "dolg",
            "vs",
            "kurs",
            "vz",
            "zg",
            "ku",
            "depth",
            "rej",
            "frek",
            "cnt",
            "m",
            "m_man",
            "color_mm",
            "m_avto",
        ]
        for i in range(20):
            head.extend([f"g{i}", f"a{i}", f"l{i}"])
        with open(file, "w", newline="") as f:  # пишем в файл шапку
            f_csv = csv.writer(f)
            f_csv.writerow(head)
