# https://hub.docker.com/_/python

FROM python:3.12-slim-bullseye

# Set work directory
WORKDIR /app

# Copy only requirements to cache them in docker layer
COPY requirements.txt ./
COPY entrypoint.sh ./

RUN pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

ENTRYPOINT ["/entrypoint.sh"]
