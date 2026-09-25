FROM python:3.12

WORKDIR /Course_project_ustudy

# Копируем зависимости
COPY requirements.txt .
RUN pip install -r requirements.txt

# Копируем весь исходный код проекта
COPY . .

# Команда запуска (например, gunicorn или manage.py runserver)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]