#!/usr/bin/env python

import tkinter as tk
import customtkinter as ctk
from common import family, font_size


class ScrolledTxt(ctk.CTkFrame):
    """Текстовый редактор"""

    def __init__(self, parent=None, text='', file=None):
        super().__init__(parent)
        self.pack(expand=tk.YES, fill=tk.BOTH)
        self.text = ctk.CTkTextbox(self, corner_radius=0,
                                   border_width=2, width=400, height=400)
        self.text.pack(side=tk.TOP, expand=tk.YES, fill=tk.BOTH)       # LEFT
        if file:
            self.settext(text, file)

    def settext(self, text: str = '', file: str = None) -> None:
        """Вставить текст в редактор"""
        if file:
            text = open(file, 'r', encoding='utf-8').read()
        self.text.delete('1.0', tk.END)
        self.text.insert('1.0', text)
        # self.text.mark_set(tk.INSERT, '1.0')
        # self.text.focus()

    def gettext(self) -> str:
        """Получить весь текст из редактора"""
        return self.text.get('1.0', tk.END+'-1c')

    def deltext(self) -> None:
        """Очистить окно редактора"""
        self.text.delete('1.0', tk.END)


class SimpleEditor(ctk.CTkFrame):
    """Класс редактора конфига"""

    def __init__(self, master=None, parent=None):
        super().__init__(parent)
        font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.pack()
        self.master = master
        frm = ctk.CTkFrame(self, corner_radius=0)
        ctk.CTkButton(frm, text='Отмена', border_width=2, border_color="#1f6aa5",
                      fg_color='transparent', font=font, text_color=('gray10', 'gray90'),
                      command=self._exit).pack(side=tk.RIGHT, padx=(1, 1))
        ctk.CTkButton(frm, text='Сохранить',  border_width=2, border_color="#1f6aa5",
                      fg_color='transparent', font=font, text_color=('gray10', 'gray90'),
                      command=self.on_save).pack(side=tk.RIGHT, padx=(1, 1))
        self.filename = 'config.ini'
        self.st = ScrolledTxt(self, file=self.filename)
        self.st.text.configure(font=font)
        frm.pack(fill=tk.X, pady=(5, 0))
        self.focus()

    def on_save(self) -> None:
        """Сохранить изменения"""
        if self.filename:
            all_text = self.st.gettext()
            open(self.filename, 'w', encoding='utf-8').write(all_text)
        self._exit()

    def on_cut(self) -> None:
        """Вырезать текст"""
        text = self.st.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        self.st.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        self.clipboard_clear()
        self.clipboard_append(text)

    def on_paste(self) -> None:
        """Вставить текст"""
        try:
            text = self.selection_get(selection='CLIPBOARD')
            self.st.text.insert(tk.INSERT, text)
        except tk.TclError:
            pass

    def _exit(self) -> None:
        """Выйти без сохранения"""
        if self.master:
            self.master.destroy()
        else:
            self.quit()


if __name__ == '__main__':
    SimpleEditor().mainloop()
