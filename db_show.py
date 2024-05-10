#!/usr/bin/env python

# import os.path
# import pathlib
import tkinter as tk
import tkinter.ttk as ttk

import customtkinter as ctk

from common import font, font_size, load_image, load_image_tk  # create_images,

# from db_pdf import go_pdf
from top_widget import CTkTop

# list_images = ("open", "delete3", "print", "pdf")


class Editor:
    """Окно для ввода комментариев"""

    def __init__(self, master=None, parent=None):
        self.parent = parent  # ViewMetka
        self.master = master  # Frame
        # self.img = create_images(list_images)
        im_open = load_image("open2.png", "open.png")
        im_cancel = load_image("delete2.png", "delete3.png")
        im_save = load_image("saveas2.png", "saveas.png")
        # font = ("Roboto Medium", -16)
        font_ = ctk.CTkFont(family=f"{font}", size=font_size)
        font_textbox = ctk.CTkFont(family="Helvetica", size=18)
        self.st = ctk.CTkTextbox(
            master,
            font=font_textbox,
            corner_radius=0,
            height=115,
            fg_color="transparent",
            # fg_color=bg_color,  text_color='white'
        )
        self.st.focus_set()
        # ttk.Separator(root).pack(fill=tk.X, expand=True)
        self.dir_info = tk.StringVar()

        f = ctk.CTkFrame(
            master,
            corner_radius=0,
            # fg_color=bg_color,
            border_width=0,
            border_color="grey75",
            fg_color="transparent",
        )
        f.pack(side=tk.BOTTOM, fill=tk.X, expand=True, pady=(2, 3))
        self.st.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        name_dir = ctk.CTkFrame(f, corner_radius=0, fg_color="transparent")
        name_dir.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ctk.CTkLabel(
            name_dir,
            image=im_open,  # self.img.open,
            compound=tk.LEFT,
            padx=10,
            font=font_,
            textvariable=self.dir_info,
            fg_color="transparent",
        ).pack(side=tk.LEFT, fill=tk.X, expand=False)
        # ttk.Separator(f, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y)

        # s = ttk.Style()
        # s.configure('TSizegrip', background='grey19')

        # ttk.Sizegrip(f).pack(side=tk.RIGHT, padx=3)           #

        f_btn = ctk.CTkFrame(f, corner_radius=0, fg_color="transparent")
        f_btn.pack(side=tk.RIGHT, fill=tk.X, expand=False)
        btn_cancel = ctk.CTkButton(
            f_btn,
            text="Отмена",
            image=im_cancel,  # self.img.delete3,
            text_color=("gray10", "gray90"),
            width=115,
            height=30,
            border_width=2,
            font=font_,
            border_color="#1f6aa5",
            fg_color="transparent",
            cursor="hand2",
            command=self.cancel_,
        )
        self.btn_save = ctk.CTkButton(
            f_btn,
            text="Сохранить",
            image=im_save,  # self.img.pdf,
            text_color=("gray10", "gray90"),
            width=115,
            height=30,
            border_width=2,
            font=font_,
            border_color="#1f6aa5",
            fg_color="transparent",
            cursor="hand2",
            command=self.save_,
        )
        self.btn_save.pack(side=tk.RIGHT, fill=tk.X, expand=False, padx=(5, 5))
        btn_cancel.pack(side=tk.RIGHT, fill=tk.X, expand=False, padx=5, pady=0)

    def _gettext(self):
        """Получить текст из редактора"""
        return self.st.get("1.0", tk.END + "-1c")

    def clr_text(self):
        """Очистить редактор"""
        self.st.delete("1.0", tk.END)

    def set_info(self, msg):
        """Вывести msg в правый лабель"""
        return self.dir_info.set(msg)

    def cancel_(self, arg=None):
        """Скрыть редактор"""
        self.st.delete(1.0, tk.END)
        self.parent.ed_frame.grid_remove()
        # geom = self.parent.geometry().split("+")
        # self.parent.geometry(f"1051x300+{geom[1]}+{geom[-1]}")

    def save_(self, arg=None):
        """Сохранить комментарий"""
        text = self._gettext()
        self.parent.save_comment(text)


class ViewMetka:
    """Окно показа меток"""

    def __init__(self, parent, root, result):
        # super().__init__(parent)
        self.parent = parent  # fild
        self.result = result
        self.root = root
        bg_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkFrame"]["border_color"]
        )
        text_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        )
        selected_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )
        font_tree = ctk.CTkFont(family="Roboto Thin", size=16)
        font_tree_head = ctk.CTkFont(family="Roboto Medium", size=23)

        self.book3 = load_image_tk("./comment.png")
        self.im16 = load_image_tk("./im16.png")
        self.a_1 = load_image_tk("./metka_a.png")
        self.marker3 = load_image_tk("./metki_on.png")

        self.top_w = CTkTop(
            title="Просмотр логов",
            font=("Roboto Medium", -16),
            border_width=2,
            width=1100,
            height=800,
            icon="db",  # ,title_color='red'
        )
        self.frame = ctk.CTkFrame(self.top_w.w_get)
        self.frame.grid(sticky="nsew")
        self.ed_frame = ctk.CTkFrame(self.frame, fg_color="transparent")  # self
        self.ed = Editor(self.ed_frame, self)
        self.frame.focus()

        # self.withdraw()
        # self.protocol("WM_DELETE_WINDOW", self.parent.state_db_norm)
        # self.title("")
        # if geom:
        #     self.geometry(f"1051x300+{geom[1]}+{geom[-1]}")
        # else:
        #     self.geometry("1051x300+100+100")
        # self.deiconify()  #
        # self.bind("<Escape>", self.parent.state_db_norm)

        # self.overrideredirect(True)                     # убрать заголовок окна
        # self.overrideredirect(0)                        # macOS

        # self.lift()
        # self.attributes("-topmost", True)
        # self.focus_force()  # !

        # self.resizable(0, 0)                            # не менять размер
        # self.transient(self.parent)                     # сделать зависимым от окна parent
        # self.protocol("WM_DELETE_WINDOW", self.parent.state_db_norm)

        # bg_color = self.top_w._apply_appearance_mode(                     # self
        #     ctk.ThemeManager.theme["CTkFrame"]["fg_color"]
        # )
        # text_color = self.top_w._apply_appearance_mode(                   # self
        #     ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        # )
        # selected_color = self.top_w._apply_appearance_mode(               # self
        #     ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        # )

        # print(bg_color, text_color, selected_color)

        # style = ttk.Style()
        style = root.s
        # style.theme_use('default')
        # style.configure("Treeview.Heading", font=font_tree_head,
        #                 background='gray25', foreground='red')
        # style.map("Treeview.Heading", background='gray25', foreground='red'

        style.configure(
            "Treeview.Heading",
            font=font_tree_head,
            background="gray25",  # bg_color
            foreground="DodgerBlue2",  # "red",
            borderwidth=0,  # !!
        )
        # style.map('Treeview.Heading', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
        # style.theme_use('vista')
        style.configure(
            "Treeview",
            background=bg_color,
            foreground=text_color,
            fieldbackground=bg_color,
            borderwidth=0,
            font=font_tree,
        )
        style.map(
            "Treeview",
            background=[("selected", bg_color)],
            foreground=[("selected", selected_color)],
        )
        style.map(
            "Treeview.Heading",
            background=[("selected", "gray25")],
        )
        # style.configure("Treeview", foreground='#555',
        #                 font=font_tree, background='#eee')  #
        # style.configure("Treeview.Heading", background=bg_color, foreground=text_color,
        # fieldbackground=bg_color, borderwidth=0, font=font_tree)

        # style.configure('TSizegrip', background='grey19')

        columns = ("#1", "#2", "#3", "#4")
        self.tree = ttk.Treeview(
            self.frame, height=18, columns=columns, selectmode="browse"
        )  # self
        self.tree.heading("#0", text="Метка", image=self.marker3)
        self.tree.column("#1", width=200, anchor=tk.CENTER)
        self.tree.column("#2", width=200, anchor=tk.CENTER)
        self.tree.column("#3", width=200, anchor=tk.CENTER)
        self.tree.column("#4", width=200, anchor=tk.CENTER)
        self.tree.column("#0", width=120, anchor=tk.W)
        self.tree.heading("#1", text="Дата и время")
        self.tree.heading("#2", text="Широта")
        self.tree.heading("#3", text="Долгота")
        self.tree.heading("#4", text="Глубина")
        self.ysb = ctk.CTkScrollbar(
            self.frame,  # self
            button_color="grey55",
            button_hover_color="grey55",
            command=self.tree.yview,
        )
        self.tree.configure(yscrollcommand=self.ysb.set)
        # self.tree.focus_force
        self.image_ = self.im16

    def show_tree(self) -> None:
        """Показать метки"""
        tags = ("dbl-click",)
        for res in self.result:
            row = list(res)
            self.image_ = self.im16
            if row[5]:  # есть комментарий
                self.image_ = self.book3
                if row[5].startswith("A"):
                    self.image_ = self.a_1
            self.tree.insert(
                "",
                tk.END,
                text=f"  {row[0]}",
                image=self.image_,
                values=tuple(row)[1:-1],
                tags=tags,
            )
        # self.tree.tag_bind("dbl-click", "<Double-Button-1>", self.edit_db)  #
        self.tree.bind("<<TreeviewSelect>>", self._comment_selection)

        self.tree.grid(row=0, column=0, sticky="nsew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.ed_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # self.rowconfigure(0, weight=10)                     # self
        # self.rowconfigure(1, weight=1)                      # self
        # self.columnconfigure(0, weight=1)                   # self

        self.ed_frame.grid_remove()

    def _comment_selection(self, event) -> None:
        """Вывести комментарий в редактор"""
        for selection in self.tree.selection():
            item = self.tree.item(selection)
            self.number = item["text"]  # type -> str
            data = self.parent.data_comment(self.number)[0]
            if data == "A":
                self.ed.clr_text()
                self.ed.cancel_()
                return
            # geom = self.top_w.geometry().split("+")                           # self
            # self.top_w.geometry(f"1051x554+{geom[1]}+{geom[-1]}")             # self
            self.ed.st.configure(state="normal")
            self.ed.st.delete(1.0, tk.END)
            self.ed.st.insert(tk.END, data)
            self.ed_frame.grid()

    def save_comment(self, comment: str) -> None:
        """Сохранить комментарий в базе"""
        self.parent.save_new_coment(self.number, comment)
        self.ed_frame.grid_remove()
        # geom = self.parent.geometry().split("+")
        # self.parent.review_db()             # сразу закрыть окно и вывести новое

    def set_name_db(self, msg: str) -> None:
        """Путь в строку состояния"""
        self.ed.set_info(msg)
