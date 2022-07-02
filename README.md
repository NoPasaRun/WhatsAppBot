<h1>Документация</h1>

<p>Проект "WhatsApp Bot" для приема и отправки сообщений в мессенджер WhatsApp</p>
<i>Приложение реализовано при помощи сервиса Green API</i>

<h2>Деплой</h2>

<p>Проект находится на сервере платформы heroku</p>
<strong>Данные аккаунта</strong>
<ul>
    <li>Почта: darkweberty@mail.ru</li>
    <li>Пароль: eAY$aIYyiy11</li><br>
    <i>Такие же данные для аккаунта почты</i>
</ul>

<h2>Конфигурация приложения</h2>
<p>В файле ./.env есть переменные для конфигурации приложения</p>
<ul>
    <li>DATABASE_URL - url для подключения к базе данных</li>
    <li>IdInstance - идентификатор приложения Green API</li>
    <li>apiTokenInstance - токен приложения Green API</li>
    <li>username - имя пользователя-администратора</li>
    <li>password - пароль пользователя-администратора</li>
    <li>text - сообщение-заглушка для отправки в мессенджер</li><br>
    <i>Не меняйте именование переменных! Сконфигурировать их значения можно через интерфейс или напрямую в файле.</i><br><br>
    <i>Чтобы узнать, как перезапустить приложение, смотрите следующий пункт</i>
</ul>

<h2>Перезапуск приложения</h2>

<h4>1. Установка heroku</h4>

<p>
Windows

Скачиваем .exe файл (<a href="https://cli-assets.heroku.com/heroku-x64.exe">x64</a> / <a href="https://cli-assets.heroku.com/heroku-x86.exe">x32</a>)
и устанавливаем heroku
</p>
<p>
mac OS

Вводим команду <code>rew tap heroku/brew && brew install heroku</code> и устанавливаем heroku

</p>
<p>
Linux

Вводим команду <code>sudo apt-get install heroku</code> и устанавливаем heroku

</p>

<h4>2. Логинимся</h4>

<p>
Пишем команду в cmd / терминале <code>heroku login</code>; программа запросит данные для аутентификации
- вводим логин и пароль, указанные в разделе Деплой
</p>

<h4>3. Перезапуск приложения</h4>

<p>
Если ничего до этого момента не сломалось, осталось только ввести следующую команду
<code>heroku restart --app fastapi-whatsappbot</code>, где fastapi-whatsappbot наше приложение
</p>

<i><code>heroku logs --tail --app fastapi-whatsappbot</code> для отслеживания логов</i><br>
<i><a href="https://devcenter.heroku.com/articles/heroku-cli#download-and-install">Если что-то пойдет не так, переходите на оф сайт с документацией</a></i>

<h2>Сведения о приложении</h2>

<ul>
    <li><a href="https://fastapi-whatsappbot.herokuapp.com/">Основной url веб-сервиса</a></li>
    <li><a href="https://fastapi-whatsappbot.herokuapp.com/admin">Админка</a></li>
    <li><a href="https://fastapi-whatsappbot.herokuapp.com/bot_config">Конфигурация бота</a></li>
    <li><a href="https://fastapi-whatsappbot.herokuapp.com/app_config">Конфигурация приложения</a></li>
</ul>
<p>Приложение написано на фрэймворке FastAPI</p>

<p>Спасибо за внмание!</p>
