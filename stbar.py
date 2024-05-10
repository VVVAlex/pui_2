#!/usr/bin/env python

import os
import tkinter as tk
from tkinter import StringVar, ttk
import customtkinter as ctk
from common import config, family, font_size, load_image

MAX_LEN_TXT = 34


class Footer(ctk.CTkFrame):
    """Cтрока состояния"""

    def __init__(self, root):
        super().__init__(root, corner_radius=0, border_width=0, border_color="grey75")
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.im_tel = load_image("win_net.png", "win_net2.png")

        self.port_info = StringVar()
        self.project_info = StringVar()
        self.gals_info = StringVar()
        self.mod_info = StringVar()
        self.delay_info = StringVar()

        ctk.CTkLabel(self,
                     textvariable=self.port_info,
                     image=self.im_tel,
                     compound=tk.LEFT,
                     font=font,
                     padx=10,
                     pady=0
                     ).pack(side=tk.LEFT, fill=tk.X)         # expand=True
        ctk.CTkLabel(
            self, textvariable=self.project_info, font=font, padx=30, pady=0
        ).pack(side=tk.LEFT, fill=tk.X)
        ctk.CTkLabel(
            self, textvariable=self.gals_info, font=font, padx=10, pady=0
        ).pack(side=tk.LEFT, fill=tk.X)
        ttk.Sizegrip(self).pack(side=tk.RIGHT, padx=3)
        ctk.CTkLabel(
            self, textvariable=self.mod_info, font=font, padx=5, pady=0
        ).pack(side=tk.RIGHT, fill=tk.X)
        ctk.CTkLabel(
            self, textvariable=self.delay_info, font=font, padx=10, pady=0
        ).pack(side=tk.RIGHT)

        self.set_info_project(config.get("Dir", "dirprj"))

    def set_device(self, txt: str) -> None:
        """Информация о портах"""
        self.port_info.set(txt)

    def set_info_gals(self, txt: str) -> None:  # Path
        """Информация о галсе"""
        txt = str(txt)
        if not txt:
            txt = "Не выбран"
        if len(txt) > MAX_LEN_TXT:
            txt = txt[len(txt) - MAX_LEN_TXT:]
            txt = "..." + txt[txt.find(os.sep):]
        self.gals_info.set("Галс:    " + str(txt))

    def set_info_project(self, txt: str) -> None:
        """Информация о проекте"""
        if not txt:
            txt = "Не создан"
        self.project_info.set("Проект:    " + txt.split(os.sep)[-1])

    def set_mod(self, mod: str) -> None:
        """Информация о режиме работы"""
        self.mod_info.set(f"Режим:   {mod}")

    def set_delay(self, delay: float) -> None:
        """Информация об интервале запуска"""
        self.delay_info.set(f"t = {delay}с")
