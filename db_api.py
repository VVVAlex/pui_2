#!/usr/bin/env python

import sqlite3
from common import LookupDict

req = LookupDict({'num': 0, 'timedata': '', 'shirota': '', 'dolgota': '', 'glubina': 0, 'coment': ''})


def execute_db_query(dbname, query, parameters=()) -> sqlite3.Cursor:
    """Создание и подключение к базе"""
    dbname = str(dbname)
    with sqlite3.connect(dbname) as conn:
        cursor = conn.cursor()
        query_result = cursor.execute(query, parameters)
        # conn.commit()
    return query_result


def create_table(dbname, tbname) -> None:
    """Создание таблицы"""
    _SQL = f"create table {tbname} (num integer, \
            timedata text, shirota text, dolgota text, glubina integer, coment text)"
    execute_db_query(dbname, _SQL)


def insert_table(dbname, tbname, req) -> None:
    """Добавление данных в таблицу"""
    _SQL = f"insert into {tbname} values (?,?,?,?,?,?)"
    value = (req.num, req.timedata, req.shirota, req.dolgota, req.glubina, req.coment)
    execute_db_query(dbname, _SQL, value)


def update_table(dbname, tbname, num, txt) -> None:
    """Обновить коментарий с номером num текстом txt"""
    _SQL = f"update {tbname} set coment=? where num=?"
    value = (txt, num)
    execute_db_query(dbname, _SQL, value)


def request_data_all(dbname, tbname) -> iter:
    """Получение всех данных из таблицы"""
    _SQL = f"select * from {tbname}"
    result = execute_db_query(dbname, _SQL)
    return result.fetchall()


def request_data_coment(dbname, tbname, num) -> list:
    """Получение коментария из таблицы с номером num"""
    _SQL = f"select coment from {tbname} where num=?"
    value = (num, )
    result = execute_db_query(dbname, _SQL, value)
    return result.fetchone()


def del_table(dbname, tbname) -> None:
    """Удаление таблицы"""
    # 'delete from {tbname}' удаляет только содержимое таблицы
    # 'alter table {tbname} rename to {newtbname}' переименование таблицы
    # 'drop table {tbname}' удаление таблицы
    _SQL = f"delete from {tbname}"
    execute_db_query(dbname, _SQL)

# 'select * from sqlite_master' просмотр всех таблиц в базе
