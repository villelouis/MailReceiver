Перед запуском поместить credentials.json в корень проекта 

#### первый запуск:
0. перейти по ссылке, авторизоваться через gmail почту и нажать `Enable the GMAIL API`
    https://developers.google.com/gmail/api/quickstart/python \
    в появившемся окне нажать `DOWNLOAD CLIENT CONFIGURATION` и поместить файл в корень проекта
1. выполнить через терминал (linux, в windows команды могут отличаться):
    ```bash
    python3 -m venv venv && \
    . venv/bin/activate && \
    pip install -r req.txt && \
    python main.py 
    ```
2. пройти авторизацию через браузер

#### последующий запуск (при активном окружении):
```
python main.py
```