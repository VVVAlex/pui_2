#!/usr/bin/env python

import serial
import threading

port_exc = serial.SerialException


def thread_read_port(port_inst) -> None:
    """Поточная функция"""
    while port_inst.started:
        port_inst.read_data_port()


class PortThread:
    """Класс работы с портами"""

    def __init__(self, on_receive_func):
        self.tty = serial.Serial(timeout=0.2)
        self.tty.write_timeout = 0              # !!
        self.started = False
        self.on_receive_func = on_receive_func
        self.thread = threading.Thread(target=thread_read_port, args=(self,), daemon=True)
        self.max_message_len = 1

    def start(self) -> None:
        """start"""
        if self.tty.is_open:
            self.started = True
            self.thread.start()

    def stop(self) -> None:
        """stop"""
        if self.started:
            self.started = False
            # self.thread.join()
            self.tty.close()

    def send(self, data: bytes) -> None:
        """Посылка данных без потока"""
        if self.started:
            # arr = bytearray(data)
            # print(f'> {data}')
            self.tty.write(data)

    def send_thread(self, data: bytes) -> None:
        """Посылка данных в потоке"""
        if self.started:
            thread_ds = threading.Thread(target=self.tty.write, args=(data,), daemon=True)
            thread_ds.start()

    def read_data_port(self) -> None:
        """Чтение порта"""
        if self.started and self.tty.in_waiting:
            data = self.tty.read(self.max_message_len)
            if len(data) > 0:
                self.on_receive_func(data)
                # print(f'< {data}')

    def open_port(self, port: str) -> None:
        """Открывает выбранный порт"""
        self.tty.port = port
        self.tty.open()
        self.tty.reset_input_buffer()

    def clear_port(self) -> None:
        """Очистка порта"""
        self.tty.reset_input_buffer()

    def is_open(self) -> bool:
        """Tue если порт открыт и False если нет"""
        return self.tty.is_open

    def close_port(self) -> None:
        """Закрываем порт"""
        self.tty.close()
