Песочница для разработки моего персонального сайта.

Запуск проекта возможен на Debian trixie, в старших версиях не тестировалось.
Последовательность запуска в терминале следующая:

```
$ mkdir ~/workspace
$ cd ~/workspace
$ git clone https://github.com/jazz4web/sandbox.git
$ cd sandbox
$ sudo apt install $(cat deploy/packages)
$ ln -s -T /usr/share/fonts/truetype/crosextra/Caladea-Regular.ttf ~/workspace/sandbox/sandbox/captcha/picturize/Caladea-Regular.ttf
$ ln -s -T /usr/share/fonts/truetype/freefont/FreeSerif.ttf ~/workspace/sandbox/sandbox/captcha/picturize/FreeSerif.ttf
$ ln -s -T /usr/share/fonts/truetype/gentium/Gentium-R.ttf ~/workspace/sandbox/sandbox/captcha/picturize/Gentium-R.ttf
$ createdb sandboxdev
$ psql -d sandboxdev -f sql/db.sql
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install --upgrade wheel
$ pip install -r requirements.txt
$ tar xvaf deploy/vendor.tar.gz -C sandbox/static
$ mkdir sandbox/static/generic
$ ln -s -T ~/workspace/sandbox/sandbox/static/vendor/bootstrap/fonts sandbox/static/generic/fonts
$ python insert_captchas.py -n 100
$ python create_root.py
$ python runserver.py
```
В браузере по адресу localhost:5000 на текущий момент можно увидеть следующее:

![screen](https://codej.ru/picture/RD45UYZGuw.png)

Дополнительная информация о проекте на [CodeJ](https://codej.ru/blogs/jazz).
Жалуйтесь..! :)
