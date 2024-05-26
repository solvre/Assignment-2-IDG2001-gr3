FROM python:3.6

EXPOSE 8000

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY app.py /app
COPY Templates /app/Templates
CMD ["python", "app.py"]