FROM arm32v7/python:3.9.15-slim-bullseye
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /base
RUN apt-get update && apt-get -y install gcc
COPY . .
RUN pip install -U -i https://www.piwheels.org/simple --no-cache-dir -r requirements.txt
RUN addgroup --system base && adduser --system --group base
USER base
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]