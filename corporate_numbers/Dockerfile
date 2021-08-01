FROM python:3.7-buster AS builder
COPY requirements.txt .
COPY app.py /app/
RUN pip install -r requirements.txt -t /app

FROM gcr.io/distroless/python3-debian10:latest
COPY app.py /
CMD ["/app.py"]
