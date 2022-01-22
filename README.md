#Тестовое задание для конпании HuntFlow
###Задача:
    Есть файл с кандидатами `Тестовая база.xslx` с колонками.
    Необходимо добавить в Хантфлоу кандидатов из этого файла в базу и на вакансию 
    на соответствующий этап с комментарием (вакансии уже созданы в Хантфлоу).

    Кроме этого, в папках с названием вакансии находятся резюме кандидатов, их
    также необходимо прикрепить к кандидату из Excel.
###Дополнительные задачи:
    Скрипт должен уметь принимать параметры командной строки (токен и 
    путь к папке с базой).

    Плюсом будет умение скрипта запускать заливку с места последнего 
    запуска (на случай сетевых проблем или прерывании выполнения),например,
    с определенной строки.

##Описание решения
Для работы скрипта необходимо установить зависимости и запустить файл main.py в корне проекта.
    
    pip3 install -r requirements.txt
    python3 main.py

В скрипте реализованы все основные и дополнительные фичи.

Так же:

    - Реалиализована валидация токена и пути к базе.
    - Добавлен ассинхронный клиент на aiohttp для обращению к API 
      паттерном Singleton.
    - Зазрузка кандидатов из базы реализована ассинхронно, скорость 
      работы определяется константой STEP.
    - В проекте присутвует логгер, пишущий в консоль и файл.