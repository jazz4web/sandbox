Песочница для разработки моего персонального сайта.

Запуск проекта возможен на Debian trixie, в старших версиях не тестировалось.
Последовательность запуска в терминале следующая:

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone https://github.com/jazz4web/sandbox.git
$ cd sandbox
$ sudo apt install $(cat deploy/packages)
$ createdb sandboxdev
$ psql -d sandboxdev -f sql/db.sql
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade wheel
$ pip install -r requirements.txt
$ tar xvaf deploy/vendor.tar.gz -C sandbox/static
$ python runserver.py
```
В браузере по адресу localhost:5000 на текущий момент можно увидеть следующее:

![screen](https://codej.ru/picture/RD45UYZGuw.png)

Дополнительная информация о проекте на [CodeJ](https://codej.ru/blogs/jazz).
Жалуйтесь..! :)