FROM python:3.4

WORKDIR /app

#Agregar codigo y dependencias de python:
ADD files/app.py /app/app.py
ADD files/requirements.txt /app/requirements.txt

#Instalar y ubicar Confd:
ADD https://github.com/kelseyhightower/confd/releases/download/v0.10.0/confd-0.10.0-linux-amd64 /usr/local/bin/confd
ADD files/start.sh /app/start.sh
RUN chmod +x /usr/local/bin/confd /app/start.sh
ADD files/confd /etc/confd

RUN pip install -r requirements.txt

CMD ["/app/start.sh"]
