#!/usr/bin/env python
from tkinter import StringVar
import customtkinter as ctk
from common import family, font_size, get_color, load_image


class Uprav(ctk.CTkFrame):
    """Управление режимами"""

    def __init__(self, master):
        super().__init__(master, corner_radius=0)
        self.root = master.root
        self.im_korabl = load_image("korab.png", im_2=None, size=(48, 24))
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.radio_var = StringVar(value="L")  # 'МГ'
        self.enable_collback = False
        row = 0

        self.lb_dist = ctk.CTkLabel(
            master=self,
            text="Глубина",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="w",
        )
        self.lb_dist.grid(row=row, column=0, sticky="nw", padx=3, pady=0)
        self.lb_glub = ctk.CTkLabel(
            master=self,
            text="0",
            width=100,
            font=font,
            padx=10,
            pady=2,
            anchor="e",
        )
        self.lb_glub.grid(row=row, column=1, sticky="e", padx=3, pady=0)
        row += 1
        self.lb_ut = ctk.CTkLabel(
            master=self,
            text="Уровень",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="w",
        )
        self.lb_ut.grid(row=row, column=0, sticky="w", padx=3, pady=0)
        self.lb_uv = ctk.CTkLabel(
            master=self,
            text="",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="e",
        )
        self.lb_uv.grid(row=row, column=1, sticky="ew", padx=3, pady=0)
        row += 1
        self.lb_lt = ctk.CTkLabel(
            master=self,
            text="Длит.",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="w",
        )
        self.lb_lt.grid(row=row, column=0, sticky="w", padx=3, pady=0)
        self.lb_lv = ctk.CTkLabel(
            master=self,
            text="",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="e",
        )
        self.lb_lv.grid(row=row, column=1, sticky="ew", padx=3, pady=0)
        row += 1
        self.lb_et = ctk.CTkLabel(
            master=self,
            text="Эхо",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="w",
        )
        self.lb_et.grid(row=row, column=0, sticky="w", padx=3, pady=0)
        self.lb_ev = ctk.CTkLabel(
            master=self,
            text="",
            width=100,
            font=font,
            padx=10,
            pady=1,
            anchor="e",
        )
        self.lb_ev.grid(row=row, column=1, sticky="ew", padx=3, pady=0)
        self.lb_rgb = ctk.CTkLabel(
            master=self,
            width=15,
            corner_radius=8,
            height=15,
            text="",
            padx=0,
            pady=0,
            anchor="e",
        )
        self.lb_rgb.grid(row=0, column=2, sticky="ens", rowspan=3, padx=10, pady=30)
        row += 1
        self.lb_upr = ctk.CTkLabel(
            master=self,
            text="Порог",
            width=100,
            anchor="w",
            font=font,
            padx=10,
            pady=1,
        )
        row += 1
        self.lb_upr.grid(row=row, column=0, sticky="w", padx=3, pady=0)
        self.lb_uprg = ctk.CTkLabel(
            master=self, text="", width=100, font=font, padx=10, pady=1
        )
        self.lb_uprg.grid(row=row, column=1, sticky="e", padx=3, pady=0)
        row += 1
        self.mg = ctk.CTkRadioButton(
            master=self,
            text="МГ",
            font=font,
            variable=self.radio_var,
            value="L",
            command=self._get_data,
        )
        self.mg.grid(row=row, column=0, pady=4, padx=10, sticky="w")
        self.sg = ctk.CTkRadioButton(
            master=self,
            text="СГ",
            font=font,
            variable=self.radio_var,
            value="M",
            command=self._get_data,
        )
        row += 1
        self.sg.grid(row=row, column=0, pady=4, padx=10, sticky="w")
        self.bg = ctk.CTkRadioButton(
            master=self,
            text="БГ",
            font=font,
            variable=self.radio_var,
            value="H",
            command=self._get_data,
        )
        row += 1
        self.bg.grid(row=row, column=0, pady=4, padx=10, sticky="w")

        self.b6 = ctk.CTkRadioButton(
            master=self,
            text="Б6",
            font=font,
            variable=self.radio_var,
            value="B",
            command=self._get_data,
        )
        row += 1
        self.b6.grid(row=row, column=0, pady=1, padx=10, sticky="w")

        self.sw_avto = ctk.CTkSwitch(
            master=self,
            text="Авто",
            onvalue="S",
            offvalue="R",
            font=font,
            command=self._get_data,
        )
        self.sw_avto.grid(
            row=row, column=1, columnspan=2, pady=1, padx=(50, 0), sticky="w"
        )
        self.slider_gain = ctk.CTkSlider(
            master=self,
            from_=15,
            to=1,
            height=60,
            number_of_steps=14,
            orientation="vertical",
            command=self._get_data,
        )
        self.slider_gain.grid(
            row=row - 3, column=1, rowspan=3, pady=1, padx=1, sticky="ns"
        )

        self.sw_avto.select()  # Avto
        if self.root.xk1:
            self.bg.configure(state="disabled")
            # self.bg.grid_forget()
        # self.b6.configure(state='disabled')
        self.b6.grid_forget()

    @staticmethod
    def cal_ampl(cod: int) -> float:
        """Вычислить амплитуды эхо в мв."""
        return round(1000 * cod * 2.5 / 255, 2)

    def update_upr(self, dat_upr) -> None:
        """Обнавить виджета по dat_upr=NamedTuple(depth: int, ku: int,
        cnt: int, m: int, ampl: int, dlit: int, rgb: int)
           вызывается из root"""
        self.enable_collback = False
        if self.sw_avto.get() == "S" or self.root.set_flag:
            self.radio_var.set(dat_upr.depth)
            self.slider_gain.set(int(dat_upr.ku, 16))
            self.lb_uprg.configure(text=f"{int(dat_upr.ku, 16)}")
        self.lb_ev.configure(text=f"{dat_upr.cnt} / {dat_upr.m}")
        level = self.cal_ampl(dat_upr.ampl)
        self.lb_uv.configure(
            text=f"{level:4.0f}  мВ"
        ) if level else self.lb_uv.configure(text="")
        # self.lb_uv.configure(text=f"{dat_upr.ampl}")
        # print(f"upr> {dat_upr.depth}")
        len_ = self.root.cal_len_(dat_upr.len, dat_upr.depth)
        self.lb_lv.configure(
            text=f"{len_:0.2f} м"
        ) if dat_upr.len else self.lb_lv.configure(text="")
        color = get_color(dat_upr.ampl)
        self.lb_rgb.configure(fg_color=color)
        self.lb_glub.configure(
            text=f"{dat_upr.distance / 10:4.1f} м"
        ) if dat_upr.distance else self.lb_glub.configure(text="")
        self.enable_collback = True

    def _get_data(self, event=None) -> None:
        """Передать данные в root если были изменения"""
        if self.enable_collback:
            # print("get")
            rej = self.sw_avto.get()
            depth = self.radio_var.get()
            ku = "{0:X}".format(int(self.slider_gain.get()))
            self.root.change_data_upr(rej, depth, ku)  # update DataRequest
            v = int(self.slider_gain.get())
            self.lb_uprg.configure(text=f"{v}")
        if self.sw_avto.get() == "R":
            self.sw_avto.configure(text="Ручн.")
        elif self.sw_avto.get() == "S":
            self.sw_avto.configure(text="Авто")
