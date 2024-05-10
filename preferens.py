#!/usr/bin/env python

import tkinter as tk
import customtkinter as ctk
from floatspinbox import FloatSpinbox as Spinbox
from common import config, write_config
from common import family, font_size
from top_widget import CTkTop


class Window:
    """Форма ввода настроек заглубления"""

    def __init__(self, master):
        self.root = master
        self.t = config.getfloat('Preferens', 't')
        self.h = config.getfloat('Preferens', 'h')
        self.chosen = ('DBT', 'DBK', 'DBS')
        self.d = config.getint('Preferens', 'd')
        self.v = config.getint('System', 'vz')
        self.z = config.getfloat('System', 'vzona')
        # Создание формы
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        pad_we = dict(sticky='we', padx=8, pady=4)                  # "0.5m"
        self.w = CTkTop(border_width=2, width=1100, height=800, font=font)
        self.frame = ctk.CTkFrame(self.w.w_get)
        self.frame.grid(sticky="nsew")
        ctk.CTkLabel(self.frame, text="Формат глубины",
                     font=font).grid(column=0, row=0, padx=8, sticky='e')
        format_chosen = ctk.CTkComboBox(self.frame, values=['DBT', 'DBK', 'DBS'],
                                        # text_color='gray10',
                                        font=font,
                                        dropdown_font=font)      # state='readonly'
        # format_chosen.set('DBT')
        format_chosen.grid(column=1, row=0, padx=8, pady=4, sticky="w")
        # format_chosen.bind('<FocusIn>', self.ch_format)
        format_chosen.set(self.chosen[self.d])                       # int
        self.format_chosen = format_chosen
        format_chosen.configure(command=self.ch_format)
        validate_cmd_t = (self.w.register(self.is_okay_t), '%P')           # , '%S'
        validate_cmd_h = (self.w.register(self.is_okay_h), '%P')
        validate_cmd_v = (self.w.register(self.is_okay_v), '%P')          # self.root
        validate_cmd = (self.w.register(self.is_okay_vz), '%P')
        # invcmd = (self.root.register(self.is_not_okay), '%S')
        ctk.CTkLabel(self.frame, text="Параметры судна", font=font).grid(
            column=1, row=1)
        ctk.CTkLabel(self.frame, text=' T, м', font=font).grid(
            column=0, row=2, sticky='e', padx=8)
        self.in_t = ctk.CTkEntry(self.frame, validate='key', font=font,
                                 validatecommand=validate_cmd_t)       # , invalidcommand=invcmd
        self.in_t.grid(column=1, row=2, **pad_we)
        ctk.CTkLabel(self.frame, text=' h, м', font=font).grid(
            column=0, row=3, sticky='e', padx=8)
        self.in_h = ctk.CTkEntry(self.frame, validate='key', font=font,
                                 validatecommand=validate_cmd_h)       # , invalidcommand=invcmd
        self.in_h.grid(column=1, row=3, **pad_we)
        ctk.CTkLabel(self.frame, text=" Поправка", font=font).grid(
            column=1, row=4)
        ctk.CTkLabel(self.frame, text='ΔZᵦ, м', font=font).grid(
            column=0, row=5, sticky='e', padx=8)
        self.in_popr = ctk.CTkLabel(self.frame, text='', font=font,
                                    corner_radius=6)
        self.in_popr.grid(column=1, row=5, **pad_we)

        ctk.CTkLabel(self.frame, text='Скорость звука', font=font).grid(
            column=0, row=6, sticky='e', padx=8)
        self.in_v = ctk.CTkEntry(self.frame, validate='key', font=font,
                                 validatecommand=validate_cmd_v)  # , invalidcommand=invcmd
        self.in_v.grid(column=1, row=6, **pad_we)
        self.in_v.delete(0, tk.END)
        self.in_v.insert(0, f'{self.v}')
        
        ctk.CTkLabel(self.frame, text='Временная зона', font=font).grid(
            column=0, row=7, sticky='e', padx=8)
        self.in_z = Spinbox(self.frame, width=150, step_size=0.5,
                            from_=-12, to=12,
                            validatecommand=validate_cmd
                            # textvariable=self.v_zona
                            )
        self.in_z.grid(column=1, row=7, **pad_we)
        
        f = ctk.CTkFrame(self.frame, corner_radius=0, fg_color='transparent')
        f.grid(column=0, row=8, columnspan=2, pady=7, sticky="we")
        self.btn_ok = ctk.CTkButton(f, text='Применить', text_color=('gray10', 'gray90'),
                                    border_width=2, border_color="#1f6aa5",
                                    fg_color='transparent', font=font, command=self.ok)
        self.btn_close = ctk.CTkButton(f, text='Отмена', text_color=('gray10', 'gray90'),
                                       border_width=2, border_color="#1f6aa5",
                                       fg_color='transparent', font=font, command=self.close)
        self.btn_close.pack(side='right', padx=10)
        self.btn_ok.pack(side='right', padx=10)
        self.valid = [-12.5+0.5*i for i in range(1, 50)]
        self.in_z.set(self.z)
        self.bind_()
        self.ch_format()
        
    def is_okay_vz(self, par: str) -> bool:
        """Если возвращает False, то значение временной зоны не изменить"""
        # print(f'p = {par}')
        if par == '':
            return True
        else:
            try:
                p = float(par)
            except ValueError:
                return False
        if float(p) in self.valid:
            return True
        return False

    def okay(self, par: str, arg: int) -> bool | None:
        if not par:
            return True
        try:
            res = float(par)
            _l = len(f"{res}".split('.')[-1]) > 1
            if res >= arg or _l:
                raise ValueError
        except ValueError:
            self.w.bell()
            return False
        return True

    def is_okay_t(self, par: str) -> bool:  # ,S
        """Если возвращает False, то значение в поле не изменить (T)"""
        return self.okay(par, 50)

    def is_okay_h(self, par: str) -> bool:
        """Если возвращает False, то значение в поле не изменить (h)"""
        return self.okay(par, 10)

    @staticmethod
    def is_okay_v(par: str) -> bool:
        """Если возвращает False, то значение скорости звука не изменить"""
        try:
            par = int(par)
            if par < 1 or par > 1600:
                raise ValueError
        except ValueError:
            return False
        return True

    def key_(self, event=None) -> None:
        self.root.after(100, self.calculate)

    def calculate(self, arg=None) -> None:
        """Считаем заглубление"""
        _t = self.in_t.get()
        _h = self.in_h.get()
        try:
            _z = round(float(_t) - float(_h), 2)
            self.in_popr.configure(text=f'{_z}')
        except ValueError:
            self.in_popr.configure(text='')

    def ch_format(self, arg=None) -> None:
        """Обработка comboboxa формата"""
        _format = self.format_chosen.get()       # text
        self.in_t.delete(0, tk.END)
        self.in_h.delete(0, tk.END)
        if _format == 'DBT':                     # match case TODO:
            self.in_t.insert(0, '0')
            self.in_h.insert(0, '0')
            self.in_t.configure(state='disabled')
            self.in_h.configure(state='disabled')
        elif _format == 'DBK':
            self.in_h.configure(state='normal')
            self.in_h.insert(0, f'{self.h}')
            self.in_t.insert(0, '0')
            self.in_t.configure(state='disabled')
        elif _format == 'DBS':
            self.in_t.configure(state='normal')
            self.in_h.configure(state='normal')
            self.in_t.insert(0, f'{self.t}')
            self.in_h.insert(0, f'{self.h}')
        self.calculate()

    def close(self, arg=None) -> None:
        """Обработка кнопки отмена"""
        self.unbind_()
        # self.withdraw()
        self.w.destroy()
        # self.root.win = None
        # self.root.tools.win_ = None       #
        # self.root.bind_()
        # self.root.focus()
        # self.root.bag()

    def ok(self, arg=None) -> None:
        """Обработка кнопки применить"""
        _t = float(self.in_t.get())
        _h = float(self.in_h.get())
        _z = round(_t - _h, 2)
        _dt = self.format_chosen.get()
        _vz = int(self.in_v.get())
        # _zona = float(self.v_zona.get())
        _zona = float(self.in_z.get())
        if _dt not in ('DBT', 'DBK', 'DBS'):
            self.close()
        _d = 1
        for i, j in enumerate(self.chosen):
            if _dt == j:
                _d = i
        if (_t, _h, _d, _vz, _zona) != (self.t, self.h, self.d, self.z):
            self.save_(_t, _h, _d, _vz, _zona)
            self.root.pref_form(_dt, _z, _vz, _zona)
        self.close()

    @staticmethod
    def save_(*arg) -> None:
        """Сохранить настройки в конфиге"""
        config.set('Preferens', 'T', f'{arg[0]}')
        config.set('Preferens', 'h', f'{arg[1]}')
        config.set('Preferens', 'D', f'{arg[2]}')
        config.set('System', 'vz', f'{arg[3]}')
        config.set('System', 'vzona', f'{arg[4]}')
        write_config()

    def bind_(self) -> None:
        self.in_h.bind('<Key>', self.key_)
        self.in_t.bind('<Key>', self.key_)
        self.w.bind("<Return>", self.ok)
        self.w.bind("<Escape>", self.close)

    def unbind_(self) -> None:
        self.w.unbind("<Return>")
        self.w.unbind("<Escape>")


if __name__ == "__main__":
    application = tk.Tk()
    window = Window(application)
    application.bind("<Control-q>", lambda *args: application.quit())
    # window.bind("<Control-q>", lambda *args: application.quit())
    application.mainloop()
