#!/usr/bin/env python

from tkinter import ttk
import customtkinter as ctk
from common import family, font_size
from top_widget import CTkTop


class ToplevelHelp:
    """Форма ввода настроек"""

    def __init__(self, root):
        self.root = root
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.w = CTkTop(border_width=2, width=1100, height=800, font=font)
        frame = ctk.CTkFrame(self.w.w_get)
        frame.grid(sticky="nsew")
        frame_ = ctk.CTkFrame(
            frame,
            # fg_color="transparent",
            bg_color="transparent",  # transparent_color
            corner_radius=8,
            # border_width=2,
            # border_color=('grey25', "#1f6aa5")
        )
        frame_.grid(sticky="nsew")
        var_row = 0
        data = (
            ("Видимость целей", "<Control - P>", self.root.board.all_one_echo),
            (
                "Показать длительность",
                "<Control - L>",
                self.root.board.show_duration_echo,
            ),
            ("Сменить фон", "<Control - B>", self.root.brd_fon_color_ch),
            # ('Сменить фон', '<Control - B>', self.root.board.fon_color_ch),
            ("Сменить тему", "<Control - O>", self.root.change_app_mode),
            ("Шкала авто", "<Control - M>", self.root.board.off_scale),
            ("Скрыть метки", "<Control - W>", self.root.board.hide_metki),
            ("Скрыть время меток", "<Control - T>", self.root.board.time_metka_on),
            ("Показать версию", "<Control - V>", self.root.get_version),
            ("Вывести шум", "<Control - N>", self.root.get_noise),
            # ('Обновить режим', '<Control - R>', self.get_mod),
            ("Редактор конфига", "<Control - E>", self.root.edit_config),
        )

        for i, j in enumerate(data):
            text_l1, text_l2, command = j
            col_, row_ = 0, i
            ctk.CTkLabel(frame_, text=text_l1, font=font, anchor="w").grid(
                row=row_, column=col_, padx=(30, 1), pady=(5, 0), sticky="w"
            )
            col_ += 1
            ctk.CTkButton(
                frame_,
                corner_radius=6,
                border_spacing=4,
                text=text_l2,
                font=font,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                # hover_color=("gray70", "gray30")
                hover_color="#1f6aa5",
                command=command,
            ).grid(row=row_, column=col_, sticky="ew", padx=10)
            var_row = row_
        var_row += 1
        ttk.Separator(frame_).grid(
            pady=(5, 0), row=var_row, column=0, columnspan=3, padx=20, sticky="ew"
        )
        var_row += 1
        ctk.CTkButton(
            frame_,
            text="Закрыть",
            text_color=("gray10", "gray90"),
            font=font,
            border_width=2,
            border_color="#1f6aa5",
            fg_color="transparent",
            command=self.w.destroy,
        ).grid(row=var_row, column=1, pady=5, padx=16, sticky="se")

    def close_help(self) -> None:
        """Убрать окно"""
        self.w.destroy()
