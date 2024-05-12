#!/usr/bin/env python
import array
import hashlib
import pathlib
import sqlite3
import time
import tkinter as tk
import customtkinter as ctk
import dialog as dlg_
from common import COLOR, dict_color, family, font_size
from ctkmessagebox import CTkMessagebox as Box
from db_api import (
    LookupDict,
    create_table,
    del_table,
    insert_table,
    request_data_all,
    request_data_coment,
    update_table,
)
from db_show import ViewMetka

req = LookupDict({})

# система координат x0, y0 верхний левый  угол x1, y1 правый нижний угол


class Fild(ctk.CTkFrame):
    """Поляна для эхосигналов"""

    def __init__(self, root, size_x, size_y, sel=None):
        super().__init__(root, corner_radius=0, border_width=0, border_color="grey75")
        self.root = root
        self.size_x = size_x
        self.size_y = size_y
        if sel:
            # frame_fild = self.root.frame_fild_25
            frame_fild = self.root.screen.frame_fild_25
            self.data_deq = self.root.data_deq_25
            self.num = False
        else:
            # frame_fild = self.root.frame_fild_50
            frame_fild = self.root.screen.frame_fild_50
            self.data_deq = self.root.data_deq_50
            self.num = True

        self.bg_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkFrame"]["border_color"]
        )
        self.text_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkLabel"]["text_color"]
        )
        self.selected_color = root._apply_appearance_mode(
            ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        )

        self.mark_type = (0, "", "")  # !!

        self.font_ppu = ctk.CTkFont(family="Helvetica", size=40)
        self.font_vers = ctk.CTkFont(family="Roboto Medium", size=28, slant="italic")
        self.font_dist = ctk.CTkFont(family="Roboto Medium", size=60, slant="italic")
        self.font_fild = ctk.CTkFont(family="Roboto Thin", size=18)
        self.font_opt = ctk.CTkFont(family="Helvetica", size=11)
        self.font = ctk.CTkFont(family=f"{family}", size=font_size)
        self.fil = "orange3"
        self.hide_ = False  # for hide mark
        self.y_top = 25
        self.x_right = 60  # 60
        self.x_start_fild = int(self.size_x - self.x_right - 2)
        self.px = 20  # число пикселов между штрихами
        self.x0 = 0

        self.color_bar = ctk.CTkFrame(frame_fild, border_width=1)
        for i in COLOR:
            ctk.CTkLabel(master=self.color_bar, text="", bg_color=i, width=16).pack(
                fill=tk.Y, expand=True
            )
        self.color_bar.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=3, pady=3)
        self.canv = tk.Canvas(
            frame_fild, background="gray22", border=2, relief=tk.SUNKEN
        )
        self.canv.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.canv.configure(width=self.size_x, height=self.size_y)
        self.canv.configure(highlightthickness=0)
        self.canv.bind("<Configure>", self.size_canv)

        self.scale = (
            1.0,
            2.0,
            5.0,
            10.0,
            20.0,
            40.0,
            50.0,
            100.0,
            200.0,
            300.0,
            400.0,
            500.0,
        )
        self.scroll = 8000
        self.n_ = 10  # 3(300) 4(600) 5(1200) 6(1500) 7(3000) 9(6000) 11
        self.k = 1.0
        self.i = 0
        self.scroll_reg_y = (
            self.scroll / self.k + self.y_top + 2
        )  # 200000 для 10 000 м (125000 для 6 000 м)
        self.old_glub = 0
        self.error = False
        self.y_scr = self.scroll_reg_y + 10
        self.x_scr = self.root.winfo_screenwidth() + 50
        # self.error_pui = True
        self.enable_scale = False  # нельзя менять шкалу автоматом
        self.color_ch = True
        self.visible = False  # Показать все точки
        self.visible_len = True  # Не показать длительность
        self.visible_time_mark_on = True  # Не показать время на метках
        self.hide_mark = False  # Показывать метки
        self.txt_op_metka_cnt = 0  # счётчик оперативных отметок ручн.
        self.y_mark = self.y_top
        self.y_old = 0.0  # для перемещен текста врем. меток  !!!!
        self.view_db = None
        self.fil_a_mark = "DodgerBlue2"
        self.last_sec = -1
        self.count_tmetka = 1
        self.ida_ = True  # при отсутствии данных в линии False
        self.ida = None
        self.db_name, self.tb_name = "", ""

    # def bind_(self):
    #     self.canv.bind("<Up>", self.up)
    #     self.canv.bind("<Down>", self.down)

    def create_db_tb(self, db: str, tb: str) -> None:
        """Создать таблицу и базу данных если не существует"""
        tb = tb.split(".")[0]
        md5 = hashlib.md5(tb.encode("utf-8")).hexdigest()
        self.tb_name = f"tb_{md5}"
        path = pathlib.Path(db)
        if self.root.adr == "$":
            self.db_name = path.joinpath(path.name + ".db")
        else:
            self.db_name = path.joinpath(f"{path.name}_25" + ".db")
        # print('create', self.tb_name, self.db_name)             # str, str
        try:
            create_table(self.db_name, self.tb_name)  # создать таблицу и если надо базу
        except sqlite3.OperationalError as err:
            self.root.st_bar.set_info_gals("Галс не выбран ...")
            if str(err) == f"table {self.tb_name} already exists":
                del_table(self.db_name, self.tb_name)
            else:
                Box(
                    title="",
                    message=f"Ошибка базы данных!\n{str(err)}",
                    font=self.font,
                    icon="cancel",
                )

    def create_error(self, tag: str) -> None:
        """Выводим на канвас сообщение 'Нет связи с ППУ'  или 'Нет данных'"""
        txt = "Нет связи с ППУ" if tag == "error" else "Нет данных!"
        self.canv.delete(tag)
        self.canv.delete("glub")
        self.error = True
        self.canv.create_text(
            20,
            self.canv.canvasy(self.size_y - 40),  # self.size_x / 2
            text=txt,
            font=self.font_ppu,
            anchor=tk.W,  # CENTER
            fill="red",
            tags=tag,
        )

    def clr_item(self, tag: tuple) -> None:
        """Удалить с холста надписи с переданным тегом"""
        for i in tag:
            self.canv.delete(i)

    def view_glub(self, glub_: int) -> None:
        """Отобразить глубину на холсте"""
        self.clr_item(("error",))  # убераем надпись 'Нет связи с ППУ'
        if glub_ != self.old_glub or self.error:
            self.error = False
            self.old_glub = glub_
            text = f"{glub_ / 10:>5.1f} м " if glub_ else ""
            self.canv.delete("glub")
            self.canv.create_text(
                20,
                self.canv.canvasy(self.size_y - 40),
                text=text,
                font=self.font_dist,
                anchor=tk.W,
                fill=self.fil,
                tags="glub",
            )

    def view_version(self, vers: str) -> None:
        """ "Отобразить версию на холсте"""
        self.clr_item(("error", "version", "noise", "not_data"))
        fill = "DodgerBlue2"
        text = vers
        self.canv.create_text(
            20,
            self.canv.canvasy(self.size_y - 40),
            text=text,
            font=self.font_vers,
            anchor=tk.W,
            fill=fill,
            tags="version",
        )

    def view_noise(self, data: bytes) -> None:
        """Отобразить шумы на холсте"""
        # 408x310 размер окна шума
        self.clr_item(("error", "version", "noise", "not_data"))
        w_ = 4
        self.canv.create_rectangle(
            100, 10, 508, 320, fill="#ccc", outline="#1e6aa5", width=w_, tags="noise"
        )
        if data:  # bytes
            # print(len(data))
            data = list(data)  # [int, int, ...]
            dat = [data[i] * 256 + data[i + 1] for i in range(0, len(data), 2)]
            for i in range(200):
                y = 319 - int(round(dat[i] / 8))
                self.canv.create_line(
                    (i * 2) + w_ + 100,
                    319,
                    (i * 2) + w_ + 100,
                    y,
                    width=2,
                    fill="gray25",
                    tags="noise",
                )
            average = 320 - int(round(dat[-1] / 8))
            if average < 0:
                average = 0
            self.canv.create_line(100, average, 508, average, fill="red", tags="noise")
            label = ctk.CTkLabel(
                self.canv,
                text=f"{dat[-1]:04d}",
                width=5,
                corner_radius=5,
                fg_color="gray65",
                bg_color="#ccc",
                text_color="#1e6aa5",
            )
            label.pack()
            y = average - 11 if average > 100 else average + 11
            self.canv.create_window(460, y - 10, window=label, tags="noise")

    def create_fild(self) -> None:
        """Рисуем поле"""
        lin_color = "gray50"
        font_color = self.fil
        x0 = self.size_x - self.x_right
        # self.x_start_fild = int(x0 - 2)
        n_line = int(self.scroll_reg_y / 20)
        line = self.canv.create_line
        text = self.canv.create_text
        self.canv.configure(scrollregion=(0, 0, self.size_y, self.scroll_reg_y))
        line(
            x0,
            self.y_top,
            x0,
            self.scroll_reg_y + 10,
            width="3",
            fill="brown",
            stipple="gray75",
            tags="fild",
        )  # y0
        line(
            x0,
            self.y_top,
            0,
            self.y_top,
            width="3",
            fill="brown",
            stipple="gray75",
            tags="fild",
        )  # x0
        text(
            x0 + 10,
            self.y_top,
            text=0,
            anchor=tk.W,
            font=self.font_fild,
            fill=font_color,
            tags="fild_t",
        )
        for i in range(0, n_line):
            stepy = self.y_top + i * self.px
            line(x0 + 5, stepy, x0, stepy, fill=lin_color, tags="fild")  # штрих
            if i % 5 == 0:  # not i % 5
                line(x0, stepy, 0, stepy, fill=lin_color, tags="fild_l")  # yn
                text(
                    x0 + 10,
                    stepy,
                    text=f"{int(i * self.k)}",
                    anchor=tk.W,
                    font=self.font_fild,
                    fill=font_color,
                    tags="fild_t",
                )
        self.x0 = x0

    # canv.create_rectangle(100,100,101,101,outline='red') fill='red' квадрат 2x2 px

    def _redrawing_fild(self, on_eco: bool = False) -> None:
        """Показ данных всего поля (перерисовка)"""
        deq = self.data_deq.copy()
        gen_data = zip(range(self.x_start_fild), deq)
        x = self.x0
        for _, dat in gen_data:
            glub_, ampl_, len_, mark_ = dat
            glub = [n * 10 for n in glub_]
            x -= 1
            y = -100 if self.visible_time_mark_on else 0
            self.show_point(glub, ampl_, len_, x)
            if not self.hide_ and not on_eco and mark_[0]:
                try:
                    y_g = self.y_top + glub_[0] * self.px / self.k + 1
                    if mark_[1] == "M":  # перерисовка ручн меток
                        self.canv.create_line(
                            x - 2, self.y_top + 1, x - 2, y_g, fill="red", tags="mmetka"
                        )
                        self.canv.create_text(
                            x - 2,
                            self.y_top - 7 + self.y_old,
                            text=mark_[0],
                            anchor="center",
                            font=self.font_opt,
                            fill="red",
                            tags="mman_t",
                        )
                    elif mark_[1] == "A":  # перерисовка авто меток
                        self.canv.create_line(
                            x - 2,
                            self.y_top + 1,
                            x - 2,
                            y_g,
                            fill="DodgerBlue2",
                            tags="ametka",
                        )
                        self.canv.create_text(
                            x - 2,
                            self.y_top - 7 + self.y_old,
                            text=mark_[0],
                            anchor=tk.CENTER,
                            font=self.font_opt,
                            fill=self.fil_a_mark,
                            tags="tametka",
                        )
                        id_ = self.canv.create_text(
                            x - 8,
                            self.y_top + 27 + self.y_old + y,
                            text=mark_[-1],
                            anchor=tk.CENTER,
                            font=self.font_opt,
                            fill=self.fil_a_mark,
                            tags="timeametka",
                        )
                        self.canv.itemconfigure(id_, angle=90)
                except IndexError:
                    # print('ex')
                    pass

    def move_metka(self, x: int = -1, y: int = 0) -> None:
        """Переместить метки на x, y"""
        for i in (
            "ametka",
            "tametka",
            "mmetka",
            "mman_t",
            "timeametka",
        ):  # 'mman_t_glub',
            self.canv.move(i, x, y)

    def _move_metkai_hide(self, hide: bool) -> None:
        """Переместить техт меткок для скрытия и удалить линии"""
        self.hide_ = hide
        # maxy = -self.root.winfo_screenheight()          # !!
        maxy = -100
        mov_list = (
            "mman_t",
            "timeametka",
            "tametka",
        )  # txt на р.м., time на а.м., txt на а.м.
        del_list = ("mmetka", "ametka")  # р.м., а.м.
        if hide:
            for i in mov_list:
                self.canv.move(i, 0, maxy)
            for i in del_list:
                self.canv.delete(i, 0, maxy)
                # self.canv.move(i, 0, maxy)
        else:
            for i in mov_list:
                self.canv.move(i, 0, -maxy)
            # for i in del_list:
            #     self.canv.move(i, 0, -maxy)
            self._reconfig()

    def move_grid(self, x: int, y: int = 0) -> None:
        """Переместить гор. разметку"""
        self.canv.move("fild_l", x, y)

    def del_width_canvas(self) -> None:
        """Удалить всё за пределами холста"""
        x = self.root.winfo_width() - self.x_scr
        # print(x, self.root.winfo_x())
        for id_ in self.canv.find_enclosed(
            x - 110, -110, x, self.y_scr
        ):  # canv.find_overlapping
            if id_:
                self.canv.delete(id_)
                # print(f'del {id_}')

    def show_point(self, point: iter, ampl: iter, duration: iter, x_draw=None) -> None:
        """Показ очередных целей в начале если x_draw=None или рисуем в точке x_draw"""
        if x_draw is None:
            self.canv.move("point_g", -1, 0)
            self.canv.move("point", -1, 0)
            self.move_metka()
            x = self.x0 - 2
        else:
            x = x_draw
        k = self.px / self.k
        data_point = [n / 10 for n in point]  # список 1 + cnt глубин
        # data_ampl = ampl                                        # список 1 + cnt амплитуд
        data_len = [
            self.root.cal_len_(n, self.root.depth) for n in duration
        ]  # список 1 + cnt длительностей
        if data_point[0] > 0:  # есть глубина
            y_g = self.y_top + data_point[0] * k + 1
            if self.visible:  # одна цель
                color_point = "white" if self.color_ch else "black"
                self.canv.create_line(
                    x, y_g, x, y_g + 2, fill=color_point, tags="point_g"
                )
            self.y_mark = self.y_top + data_point[0] * self.px / self.k + 1
        else:
            self.y_mark = self.y_top
        if not self.visible:  # все цели
            # for point, ampl, len_ in zip(data_point[1:], ampl[1:], duration[1:]):
            for point, ampl, len_ in zip(data_point[1:], ampl[1:], data_len[1:]):
                y = self.y_top + point * k + 1
                if point > 0:
                    color_point = dict_color.get(ampl, "gray55")
                    t = len_ * k
                    h = t if t > 2 else 2
                    hl = h if not self.visible_len else 2
                    self.canv.create_line(
                        x, y, x, y + hl, fill=color_point, tags="point"
                    )
        # print(len(self.root.data_deq), len(self.root.data_deq_50), len(self.root.data_deq_25))

    def show(self, data_point: array.array, data_ampl: array.array, data_len: array.array) -> None:
        """"""
        self._update_scale(data_point)
        self.show_point(data_point, data_ampl, data_len)
        self.del_width_canvas()  # удалить всё за холстом
        self.mark_type = (0, "", "")

    def _update_scale(self, data_p: array.array) -> None:
        """Установка шкалы по глубине"""
        if not data_p or not self.enable_scale:
            return
        x = data_p[0] / 10
        up = (20, 40, 100, 200, 400, 800, 1000, 2000, 4000, 4500)
        down = (0, 16, 35, 75, 190, 350, 750, 950, 1900, 3900)
        if x > up[self.i]:
            self.up()
        elif x < down[self.i]:
            self.down()

    def _reconfig(self, arg=None) -> None:
        """Обновить холст"""
        for i in (
            "point",
            "point_g",
            "fild",
            "fild_l",
            "fild_t",
            "mmetka",
            "ametka",
            "tametka",
            "timeametka",
            "mman_t",
        ):
            self.canv.delete(i)
        self.create_fild()
        self._redrawing_fild()
        self.view_glub(self.old_glub)
        if arg and self.visible:
            self.canv.delete("point")

    def all_one_echo(self, event=None) -> None:
        """Тригер показ всех точек или одна цель"""
        if self.visible:
            self._redrawing_fild(on_eco=True)
        else:
            self.canv.delete("point")
        # self._redrawing_fild(on_eco=True) if self.visible else self.canv.delete('point')
        self.visible = not self.visible
        self._reconfig()
        self.root.close_help()

    def show_duration_echo(self, event=None) -> None:
        """Тригер показ длительности целей"""
        if self.visible_len:
            self._redrawing_fild(on_eco=True)
        else:
            self.canv.delete("point")
        self.visible_len = not self.visible_len
        self._reconfig()
        self.root.close_help()

    def fon_color_ch(self, arg=None) -> None:
        """Обработчик ккнопки смены фона"""
        (bg, fil) = ("beige", "darkblue") if self.color_ch else ("gray22", "orange3")
        self.fil = fil
        self.color_ch = not self.color_ch
        self._reconfig()
        self.canv.config(background=bg)
        self.canv.itemconfigure("fild_t", fill=fil)
        self.canv.itemconfigure("ametka", fill=self.fil_a_mark)
        self.canv.itemconfigure("tametka", fill=self.fil_a_mark)
        self.root.close_help()

    def off_scale(self, event=None) -> None:
        """Шкала авто или мануал"""
        self.enable_scale = not self.enable_scale
        self.root.close_help()

    def time_metka_on(self, event=None) -> None:
        """Обработчик кнопки показа времени на автометке"""
        y = 100 if self.visible_time_mark_on else -100
        self.canv.move("timeametka", 0, y)  # время на авт. метке
        self.visible_time_mark_on = not self.visible_time_mark_on
        self.root.close_help()

    def hide_metki(self, event=None) -> None:
        """Показать, скрыть метки"""
        hide = False if self.hide_mark else True
        self._move_metkai_hide(hide=hide)
        self.hide_mark = not self.hide_mark
        self.root.close_help()

    def up(self, event=None) -> None:
        """Увеличить масштад"""
        if self.i < self.n_:
            self.i += 1
            self.k = self.scale[self.i]
            self._reconfig(1)

    def down(self, event=None) -> None:
        """Уменьшить масштад"""
        if self.i:
            self.i -= 1
            self.k = self.scale[self.i]
            self._reconfig(1)

    def home(self, event=None) -> None:
        """На начало"""
        self.k = 1.0
        self.i = 0
        self._reconfig(1)

    def en(self, event=None) -> None:
        """В конец (6250м)"""
        self.k = self.scale[-2]  # 500
        self.i = self.n_  # 11
        self._reconfig(1)

    def size_canv(self, event=None) -> None:
        """Даёт текущую ширину и высоту холста"""
        _, old_y = self.size_x, self.size_y
        self.size_x, self.size_y = self.canv.winfo_width(), self.canv.winfo_height()
        tag = ("glub", "error", "version", "not_data")
        for i in tag:
            self.canv.move(i, 0, self.size_y - old_y)
        self._reconfig()
        if self.visible:
            self.canv.delete("point")

    def decorate_metka(*d_arg):  # self, *d_arg
        """Декоратор функции"""

        def my_decorator(func):
            def wrapped(self, *f_arg):
                if self.hide_mark:
                    for tag in d_arg:
                        self.canv.move(tag, 0, 100)
                func(self, *f_arg)
                if self.hide_mark:
                    for tag in d_arg:
                        self.canv.move(tag, 0, -100)

            return wrapped

        return my_decorator

    @decorate_metka("mman_t")  # '', 'mman_td'
    def op_manual(self, arg=None) -> None:
        """Обработчик кнопки постановки ручной метки"""
        x = self.x0 - 3
        self.canv.create_line(
            x, self.y_top + 1, x, self.y_mark, fill="red", tags="mmetka"
        )
        self.txt_op_metka_cnt += 1
        self.canv.create_text(
            x,
            self.y_top - 7 + self.y_old,
            text=self.txt_op_metka_cnt,
            anchor="center",
            font=self.font_opt,
            fill="red",
            tags="mman_t",
        )
        self.mark_type = (self.txt_op_metka_cnt, "M", "")
        req.num = self.txt_op_metka_cnt
        req.coment = ""
        if self.root.choose_gals:
            self.get_data_db()
            insert_table(self.db_name, self.tb_name, req)  # !!! default
        # if self.view_db:
        #     # geom = self.view_db.geometry().split("+")
        #     self.review_db()
        if self.hide_mark:
            self.canv.delete("mmetka")

    def del_metka_man(self) -> None:
        """Удаление ручных и авто отметок при смене галса"""
        for tag in (
            "mmetka",
            "mman_t",
            "ametka",
            "tametka",
            "point",
            "point_g",
            "glub",
            "timeametka",
        ):
            self.canv.delete(tag)
        self.txt_op_metka_cnt = 0

    def get_data_db(self) -> None:
        """Получить данные для базы"""
        d_gps = self.root.gps_manager.get_data_gps()
        if d_gps is None:
            t, sh_, d_ = time.strftime("%d.%m.%y %H:%M:%S"), "", ""
        else:
            t, sh, d = d_gps[0], d_gps[1], d_gps[2]
            sh__ = sh.split()
            d__ = d.split()
            sh_ = f"{sh__[0]}{0xB0:c} {sh__[1]}{0xB4:c} {sh__[2]}"
            d_ = f"{d__[0]}{0xB0:c} {d__[1]}{0xB4:c} {d__[2]}"
        req.timedata, req.shirota, req.dolgota = t, sh_, d_
        # req.glubina = f'{round(self.root.data_point[0] / 10, 1)} м' if self.root.data_point else 0
        req.glubina = f"{round(self.data_deq[0][0][0], 1)} м"
        # print(self.root.data_point[0], self.data_deq[0][0][0])
        # req.coment = ''

    # def review_db(self) -> None:
    #     """Обновить окно меток"""
    #     # self.view_db.destroy()
    #     self.view_db.top_w.withdraw()
    #     self.op_mark_bd()

    def op_mark_bd(self) -> None:
        """ "Вывести просмотр базы и коментов"""
        try:
            result = request_data_all(self.db_name, self.tb_name)
        except sqlite3.Error:  # as er
            # print(er)
            return
        if self.view_db:
            self.view_db.top_w.destroy()
        self.view_db = ViewMetka(self, self.root, result)
        self.view_db.show_tree()
        self.view_db.set_name_db(self.db_name)

    def data_comment(self, num: int) -> iter:
        """Получить коментарий из базы"""
        return request_data_coment(self.db_name, self.tb_name, num)

    def save_new_coment(self, num: int, txt: str) -> None:
        """Сохранить коментарий в базе"""
        update_table(self.db_name, self.tb_name, num, txt)

    def state_db_norm(self, arg=None) -> None:
        """Удалить окно просмотра меток и разблокировать кнопку db"""
        self.view_db.top_w.destroy()  # withdraw()
        self.view_db = None  #

    def op_avto(self, arg=None) -> None:
        """Обработчик кнопки постановки авто. метки"""
        dlg_.get_float(
            self.root,
            "Автоинтервал",
            "Введите интервал в мин.",
            self.new_avtom_,
            initial=1.0,
            minimum=0.5,
            maximum=60,
        )

    def new_avtom_(self, arg=None) -> None:
        """Запуск автометок"""
        if self.ida:
            self.root.after_cancel(self.ida)  # остановить цикл
        if not arg:
            self.root.tools.config_avto(msg="Авто")
            return
        else:
            self.root.tools.config_avto(msg=f"{arg:0.1f} м")
            self.count_tmetka = 1
            self._timer_avto(arg)  # запустить цикл

    def _timer_avto(self, t: float) -> None:
        """Тик для автометок 1 секунда"""
        sec = time.localtime(time.time())[5]
        if sec != self.last_sec:
            self.last_sec = sec  # 1 сек
            self.count_tmetka -= 1
            if self.count_tmetka == 0:
                if self.ida_ and self.root.start_work:
                    self._draw_t()
                self.count_tmetka = t * 60
        self.ida = self.root.after(100, lambda: self._timer_avto(t))

    @decorate_metka("tametka", "timeametka")  # '', 'tametka', 'timeametka'
    def _draw_t(self, arg=None) -> None:
        """Рисуем временные автоматич. метки"""
        d_gps = self.root.gps_manager.get_data_gps()  # receive_data_gps
        x = self.x0 - 3
        text = time.strftime("%H:%M:%S") if d_gps is None else d_gps[0].split()[-1]
        self.txt_op_metka_cnt += 1
        y_ = -100 if self.visible_time_mark_on else 0
        if not self.hide_mark:
            self.canv.create_line(
                x, self.y_top, x, self.y_mark, fill=self.fil_a_mark, tags="ametka"
            )
        self.canv.create_text(
            x,
            self.y_top - 7 + self.y_old,
            text=self.txt_op_metka_cnt,
            anchor=tk.CENTER,
            font=self.font_opt,
            fill=self.fil_a_mark,
            tags="tametka",
        )
        id_ = self.canv.create_text(
            x - 6,
            self.y_top + 27 + self.y_old + y_,
            text=text,
            anchor=tk.CENTER,
            font=self.font_opt,
            fill=self.fil_a_mark,
            tags="timeametka",
        )
        self.canv.itemconfigure(id_, angle=90)
        self.mark_type = (self.txt_op_metka_cnt, "A", text)
        req.num = self.txt_op_metka_cnt
        req.coment = "A"
        if self.root.choose_gals:
            self.get_data_db()
            insert_table(self.db_name, self.tb_name, req)
        # if self.view_db:
        #     # geom = self.view_db.geometry().split("+")
        #     self.review_db()
