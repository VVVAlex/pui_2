#!/usr/bin/env python

import customtkinter as ctk
from tkinter import ttk
from typing import Union, Callable
from common import family, font_size

# family = "Roboto Medium"
# font_size = -16


class FloatSpinbox(ctk.CTkFrame, ttk.Spinbox):
    """Виджет спинбокс"""
    def __init__(self, *args,
                 width: int = 100,
                 height: int = 32,
                 from_: int = 1,
                 to: int = 10,
                 textvariable=None,
                 validate='key',
                 validatecommand=None,
                 step_size: Union[int, float] = 0.5,
                 command: Callable = None,
                 **kwargs):

        super().__init__(*args, width=width, height=height, **kwargs) 
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.step_size = step_size
        self.command = command
        self.from_ = from_
        self.to = to
        self.text_var = textvariable
        self.validate = validate
        self.validatecommand = validatecommand

        self.grid_columnconfigure(1, weight=1)       # entry expands

        self.subtract_button = ctk.CTkButton(self, text="-", width=height-6, height=height-6,
                                             command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)
        self.entry = ctk.CTkEntry(self, width=width-(2*height), height=height-6,
                                  textvariable=self.text_var,
                                  justify="right",
                                  font=font, validate=self.validate,
                                  validatecommand=self.validatecommand)
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")
        self.add_button = ctk.CTkButton(self, text="+", width=height-6, height=height-6,
                                        command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.bind("<MouseWheel>", self.on_mouse_wheel)
        self.entry.bind("<Enter>", self.on_enter)
        self.entry.bind("<Leave>", self.on_leave)

    @staticmethod
    def on_enter(event=None) -> None:
        """Курсор над полем ввода"""
        event.widget.configure(cursor='hand2')

    @staticmethod
    def on_leave(event=None) -> None:
        """Курсор покинул поле ввода"""
        event.widget.configure(cursor='xterm')

    def add_button_callback(self) -> None:
        """Обработчик кнопки +"""
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) + self.step_size
            if value <= self.to:
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
        except ValueError:
            pass

    def subtract_button_callback(self) -> None:
        """Обработчик кнопки -"""
        if self.command is not None:
            self.command()
        try:
            value = float(self.entry.get()) - self.step_size
            if value >= self.from_:
                self.entry.delete(0, "end")
                self.entry.insert(0, value)
        except ValueError:
            pass

    def get(self) -> Union[float, None]:
        """Получить данные"""
        try:
            return float(self.entry.get())
        except ValueError:
            return None
            
    def on_mouse_wheel(self, event):
        """Изменять значение колесом мыши"""
        if event.delta > 0:
            self.add_button_callback()
        else:
            self.subtract_button_callback()

    def set(self, value: float) -> None:
        """Установить данные"""
        self.entry.delete(0, "end")
        self.entry.insert(0, str(float(value)))

    def clr_(self, arg=None) -> None:
        """Очистить поле ввода"""
        self.entry.delete(0, "end")
        self.entry.insert(0, f"{self.from_}")


if __name__ == "__main__":
    app = ctk.CTk()
    spinbox_1 = FloatSpinbox(app, width=150, step_size=0.5, from_=1, to=10)
    spinbox_1.pack(padx=20, pady=20)
    spinbox_1.set(9)
    print(spinbox_1.get())
    app.mainloop()
