# aiohttp_crud

1. В директории проекта создать файл .env и заполнить его по образцу:

```python
PG_USER:postgres
PG_PASSWORD:12345
PG_DB:aiohttp_test
```
2. Подготовить окружение и установить зависимости: 
```python
python3 -m venv env

source env/bin/activate
```
```python
pip install -r requirements.txt
```
3. Запустить контейнер с базой данных:
```python
docker-compose up -d
```
4. Запустить приложение:
```python
cd app && python main.py
```