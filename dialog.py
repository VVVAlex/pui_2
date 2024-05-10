#!/usr/bin/env python3

import sys
import tkinter as tk
import customtkinter as ctk
from floatspinbox import FloatSpinbox as Spinbox
from common import family, font_size
from top_widget import CTkTop

OK_BUTTON = 0b0001
CANCEL_BUTTON = 0b0010
# YES_BUTTON =    0b0100
# NO_BUTTON =     0b1000

PAD = "1.75m"
d = None
i_ = None


class Dialog:
    def __init__(self, master=None, title=None, buttons=OK_BUTTON, calback=None, default=OK_BUTTON):
        self.master = master  # or ctk._default_root
        self.font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.w = CTkTop(border_width=2, width=1100, height=800, font=self.font)             # btn_close=False,
        self.frame = ctk.CTkFrame(self.w.w_get)
        self.frame.grid(sticky="nsew")
        self.buttons = buttons
        self.default = default
        self.calback = calback           #
        self.acceptButton = None
        self.__create_ui()
        self.ok = None
        self.initialize()
        self.initialFocusWidget.focus()    # сосредоточиться на первом виджете
        self.w.wait_visibility()
        if calback is None:
            self.w.wait_window(self)

    def __create_ui(self) -> None:
        widget = self.body(self.frame)
        if isinstance(widget, (tuple, list)):
            body, focus_widget = widget
        else:
            body = focus_widget = widget
        self.initialFocusWidget = focus_widget
        buttons = self.button_box(self.frame)
        body.grid(row=0, column=0, sticky="nsew")
        buttons.grid(row=1, column=0, sticky="we")

        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)

    def __ok(self, *arg) -> None:
        # if not self.validate():
        #     self.initialFocusWidget.focus()
        #     return
        self.w.withdraw()
        # self.destroy()
        self.w.update_idletasks()
        try:
            self.ok = True
            self.apply(self.calback)
        finally:
            self.__canceled()

    def __cancel(self, *arg) -> None:
        global d, i_
        if self.ok is None:
            self.ok = False
        self.initialFocusWidget = None
        if self.master is not None:
            self.master.focus()
        self.w.destroy()
        d = None
        i_ = None
        self.apply(self.calback)

    def __canceled(self, *arg) -> None:
        global d, i_
        if self.ok is None:
            self.ok = False
        self.initialFocusWidget = None
        if self.master is not None:
            self.master.focus()
        self.w.destroy()
        d = None
        i_ = None

    def initialize(self) -> None:
        """Переопределите, чтобы выполнить все, что нужно сделать в конце"""
        pass

    def add_button(self, master, text, command, default=False) -> ctk.CTkButton:
        button = ctk.CTkButton(master, text=text,
                               text_color=('gray10', 'gray90'),
                               border_width=2,
                               fg_color='transparent', font=self.font,
                               border_color="#1f6aa5", command=command)
        # if default:
        #     # button.configure(default=tk.ACTIVE)
        #     button.configure(state=tk.ACTIVE)
        button.pack(side=tk.RIGHT, padx=PAD, pady=PAD)
        return button

    def button_box(self, master) -> ctk.CTkFrame:
        """Кнопки диалога"""
        _frame = ctk.CTkFrame(master, corner_radius=0, fg_color='transparent')      # черный фон
        if self.buttons & CANCEL_BUTTON:
            self.add_button(_frame, "Отмена", self.__cancel,
                            self.default == CANCEL_BUTTON)
        if self.buttons & OK_BUTTON:
            self.acceptButton = self.add_button(_frame, "Применить", self.__ok,
                                                self.default == OK_BUTTON)
        # if self.buttons & YES_BUTTON:
        #     self.acceptButton = self.add_button(frame, "Yes", self.__ok,
        #                                         self.default == YES_BUTTON)
        # if self.buttons & NO_BUTTON:
        #     self.add_button(frame, "No", self.__cancel,
        #                     self.default == NO_BUTTON)
        self.w.bind("<Return>", self.__ok, "+")
        self.w.bind("<Escape>", self.__cancel, "+")
        return _frame

    def body(self, master) -> ctk.CTkLabel:
        """Переопределить, чтобы создать тело диалога"""
        label = ctk.CTkLabel(master, text="[Override Dialog.body()]")
        return label

    @staticmethod
    def validate() -> bool:
        """Переопределить выполнение всей проверки диалога"""
        return True

    def apply(self, calback=None) -> None:
        """Переопределить выполнение действия OK"""
        pass


class Result:

    def __init__(self, value=None):
        self.value = value
        self.ok = False

    def __str__(self):
        return f"'{self.value}' {self.ok}"


class _StrDialog(Dialog):

    def __init__(self, master, title, prompt, result, calback):
        """Результатом должен быть объект Result,
           значение будет содержать str,
           ok будет содержать True, если пользователь нажал OK или
           False если пользователь нажал Cancel."""
        self.prompt = prompt
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        super().__init__(master, title, OK_BUTTON | CANCEL_BUTTON, calback)

    def body(self, master) -> (ctk.CTkFrame, ctk.CTkEntry):
        frame = ctk.CTkFrame(master, corner_radius=0, fg_color='transparent')       # черный фон
        label = ctk.CTkLabel(frame, text=self.prompt, font=self.font)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        entry = ctk.CTkEntry(frame, textvariable=self.value, font=self.font)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=PAD, pady=PAD)
        # entry.focus_force()
        return frame, entry

    def apply(self, calback=None) -> None:
        if self.ok:
            self.result.value = self.value.get()
            self.result.ok = True
        else:
            self.result.value = ''
        if calback:
            calback(self.result.value)


class _NumberDialogBase(Dialog):    # Abstract base class

    def __init__(self, master, title, prompt, result, calback=None, minimum=None,
                 maximum=None, format_=None):
        """Результатом должен быть объект Result,
           значение будет содержать int или float,
           ok будет содержать True, если пользователь нажал OK или
           False если пользователь нажал Cancel."""
        self.prompt = prompt
        self.minimum = minimum
        self.maximum = maximum
        self.format = format_
        self.value = tk.StringVar()
        self.value.set(result.value)
        self.result = result
        self.valid = [0.5+i*0.5 for i in range(120)]
        super().__init__(master, title, OK_BUTTON | CANCEL_BUTTON, calback)


# class _IntDialog(_NumberDialogBase):
#
#     def body(self, root) -> (ctk.CTkFrame, ttk.Spinbox):
#         frame = ctk.CTkFrame(root, corner_radius=0)
#         label = ctk.CTkLabel(frame, text=self.prompt)
#         label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
#         self.spinbox = ttk.Spinbox(frame, from_=self.minimum, to=self.maximum,
#                                    textvariable=self.value, validate="all")
#         self.spinbox.config(validatecommand=(
#             self.spinbox.register(self.validate), "%P"))
#         self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
#         return frame, self.spinbox
#
#     @staticmethod
#     def validate_spinbox_int(spinbox, number=None) -> bool:
#         if number is None:
#             number = spinbox.get()
#         if number == "":
#             return True
#         try:
#             x = int(number)
#             if int(spinbox.cget("from")) <= x <= int(spinbox.cget("to")):
#                 return True
#         except ValueError:
#             pass
#         return False
#
#     def validate(self, number=None) -> bool:
#         return self.validate_spinbox_int(self.spinbox, number)
#
#     def apply(self, calback=None) -> None:
#         self.result.value = int(self.value.get())
#         self.result.ok = True
#         if calback:
#             calback(self.result.value)


class _FloatDialog(_NumberDialogBase):

    def body(self, master) -> (ctk.CTkFrame, Spinbox):
        validate_cmd = (master.register(self.is_okay), '%P')
        frame = ctk.CTkFrame(master, corner_radius=0)
        label = ctk.CTkLabel(frame, text=self.prompt, corner_radius=0, font=self.font)
        label.pack(side=tk.LEFT, fill=tk.X, padx=PAD, pady=PAD)
        self.spinbox = Spinbox(frame, width=150, step_size=0.5,
                               from_=self.minimum, to=self.maximum,
                               textvariable=self.value,
                               validatecommand=validate_cmd)
        self.spinbox.pack(side=tk.LEFT, padx=PAD, pady=PAD)
        return frame, self.spinbox

    def apply(self, calback=None) -> None:
        if self.ok:
            self.result.value = float(self.value.get())
            self.result.ok = True
        else:
            self.result.value = 0               # add
        # print(self.result.value)
        if calback:
            calback(self.result.value)
            
    def is_okay(self, par: str) -> bool:
        """Если возвращает False, то значение в поле не изменить"""
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


def get_str(master, title, prompt, initial="", calback=None) -> str:
    """Возвращает None, если отмена или строку"""
    result = Result(initial)
    _StrDialog(master, title, prompt, result, calback)
    return result.value if result.ok else None


# def get_int(root, title, prompt, calback=None, initial=0, minimum=None,
#             maximum=None) -> int:
#     """Возвращает None если отмена или int в заданном диапазоне"""
#     assert minimum is not None and maximum is not None
#     global i_, d
#     result = Result(initial)
#     if d:
#         d.destroy()
#         d = None
#     if not i_:
#         i_ = _IntDialog(root, title, prompt, result, calback, minimum, maximum)
#     else:
#         i_.focus()
#     return result.value if result.ok else None


def get_float(master, title, prompt, callback=None, initial=0.0, minimum=None,
              maximum=None, format_="%0.1f") -> float:
    """Возвращает None если отмена или float в заданном диапазоне"""
    assert minimum is not None and maximum is not None
    global d, i_
    result = Result(initial)
    # if i_:
    #     i_.destroy()
    #     i_ = None
    if not d:
        d = _FloatDialog(master, title, prompt, result, callback, minimum, maximum, format_)
    else:
        d.w.focus()
    return result.value if result.ok else None


if __name__ == "__main__":
    if sys.stdout.isatty():
        application = tk.Tk()
        Dialog(application, "Dialog")
        x = get_str(application, "Get Str", "Name", "test")
        print("str", x)
        # x = get_int(application, "Get Int", "Percent", None, 5, 0, 100)
        # print("int", x)
        x = get_float(application, "Get Float", "Angle", None, 90, 0, 90)
        print("float", x)
        application.bind("<Escape>", lambda *args: application.quit())
        application.mainloop()
    else:
        print("Loaded OK")
