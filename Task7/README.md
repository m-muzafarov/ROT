AMQP
====

master.py
---------

Отправляет в RabbitMQ (порт 5672) выражение - сумму двух чисел.

Запуск:
  
  python master.py [a [b]]

Если какие-то аргументы не указаны - генерируется случайное число от MinINT64 до MaxINT64.

slave.py
--------

Слушает RabbitMQ очередь.

Если получает сообщение с темой 'calc' - пытается его посчитать.

Если получилось - выводит результат.