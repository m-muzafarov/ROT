Thrift Client-Server
====================

thrift
------

Описывает две функции: ping и подсчёт количества тэгов.    

server
------

Python для парсинга страниц на количество тэгов.
Принимает на вход текст страницы и искомый тэг.
На выходе возвращает количество таких тэгов на странице.

client
------

С++. Принимает на вход URL и тэг.
Скачивает страницу, отправляет текст серверу, возвращает количество искомых тегов.


Компиляция и зависимости
========================

Требует установленного thrift, libcurl, g++

Для С++ thrift успешно собирается по инструкции с сайта.
Python у меня его не увидел (возможно недособрал) - решается установкой python-thrift:

    pip install thrift

Сборка происходит с помощью утилиты make.

На выходе будет доступно два исполняемых файла: server.py и client.elf
