FROM arm32v7/python:3.9.15-slim-bullseye as base
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
RUN apt-get update && apt-get -y install gcc
COPY requirements.txt .
RUN pip install --index-url=https://www.piwheels.org/simple --no-cache-dir -r requirements.txt

FROM arm32v7/python:3.9.15-slim-bullseye
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
COPY --from=base /usr/local/lib/python3.9/site-packages/ /usr/local/lib/python3.9/site-packages/
COPY --from=base /usr/local/bin/ /usr/local/bin/
WORKDIR /bot
RUN apt-get update && apt-get install libatomic1 -y
COPY . .
CMD ["python3", "main.py"]