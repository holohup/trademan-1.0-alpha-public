FROM python:3.12-bullseye
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /base
# RUN apt-get update && apt-get -y install gcc
COPY . .
RUN pip install --no-cache-dir setuptools && \
    pip install --no-cache-dir -r requirements.txt
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]