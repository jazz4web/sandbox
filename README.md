Sandbox - это песочница для разработки моего персонального web-сайта.
На текущий момент все функциональные возможности сайта реализованы в
соответствии с моими предпочтениями и первоначальным замыслом. Вероятно, что
в процессе работы над сайтом, наполнении его контентом и активном использовании
этого web-интерфейса мне захочется что-нибудь доработать и исправить мелкие,
досадные проблемы - такова перспектива. А пока я доволен как сытый слон.

Запуск проекта возможен на Debian trixie, на [CodeJ](https://codej.ru/) проект
в текущем состоянии развёрнут и удовлетворительно работает на базе Debian
bookworm. В сущности, любой желающий может использовать это приложение в
соответствии с GNU GPLv.3 для своего сайта. Последовательность запуска
приложения в терминале следующая:

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
$ cp env_template .env
$ mkdir sandbox/static/generic
$ ln -s -T ~/workspace/sandbox/sandbox/static/vendor/bootstrap/fonts sandbox/static/generic/fonts
$ python insert_captchas.py -n 100
$ python create_root.py
$ python runserver.py
```
После выполнения всех команд можно обнаружить приложение в браузере по адресу
localhost:5000.

Дополнительную информацию о проекте можно найти на
[CodeJ](https://codej.ru/8ffdIqY4). Донат проекту можно перевести
[сюда](https://yoomoney.ru/to/410015590807463) - перевод на 5 рублей лучше,
чем никакого перевода, а ваш донат гарантирует, что я не закрою проект уже в
ближайшее время. И да, процесс развёртывания этого приложения на сервер тоже
могу продемонстрировать по запросу конечного пользователя, все контакты на
[главной](https://codej.ru/).
