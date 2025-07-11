FROM python:3.8-slim

RUN mkdir -p /usr/src/app
COPY . /usrdeps275d6419b0ef/requirements.txt
WORKDIR /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80
CMD ["python", "./Flask_App.py"]

