# SistemasDistribuidos_P2

#### Nombre Estudiante: Andrés Felipe Piñeros
#### Código Estudiante: A00273344
#### Repositorio: https://github.com/AndresPineros/SistemasDistribuidos_P2

### Descripción
Aprovisionamiento	de	un	ambiente	compuesto	por	los	siguientes	elementos:	un servidor	encargado de	realizar balanceo de	carga,	tres	servidores	web	con páginas estáticas. Se	debe probar	el	funcionamiento	del balanceador	realizando peticiones y mostrando servidores distintos atendiendo las peticiones.

<p align="center">
  <img src="images/01_diagrama_despliegue.png" width="650"/>
</p>

### Actividades
En un documento en formato PDF cuyo nombre de
archivo debe ser examen2_codigoestudiante.pdf debe incluir lo siguiente:

1. Documento en formato PDF:  
  * Formato PDF (5%)
  * Nombre y código de los integrantes del grupo (5%)
  * Ortografía y redacción (5%)
2. Consigne los comandos de linux necesarios para el aprovisionamiento de los servicios solicitados. En este punto no debe incluir archivos tipo Dockerfile solo se requiere que usted identifique los comandos o acciones que debe automatizar (15%)
3. Escriba los archivos Dockerfile para cada uno de los servicios solicitados junto con los archivos fuente necesarios. Tenga en cuenta consultar buenas prácticas para la elaboración de archivos Dockerfile. (20%)
4. Escriba el archivo docker-compose.yml necesario para el despliegue de la infraestructura (10%)
5. Publicar en un repositorio de github los archivos para el aprovisionamiento junto con un archivo de extensión .md donde explique brevemente como realizar el aprovisionamiento (15%)
6. Incluya evidencias que muestran el funcionamiento de lo solicitado (15%)
7. Documente algunos de los problemas encontrados y las acciones efectuadas para su solución al aprovisionar la infraestructura y aplicaciones (10%)


## 1. Acciones y Comandos de Linux para el Aprovisionamiento de las Máquinas

### 1.1 Load Balancer

La máquina de balanceo de cargas se encargará de recibir las peticiones por el puerto 8080 y de redireccionar dichas peticiones (equitativamente) hacia las máquinas web. Para esto se usará el servicio de balanceo de cargas de Nginx.

Las acciones a realizar para configurar efectivamente el balanceador de cargas son:
- Abrir el puerto 8080 con el servicio de iptables.

``` sh
iptables -I INPUT 5 -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT
service iptables save
```

- Instalar Nginx

``` sh
apt-get update nginx
apt-get install nginx -y
```
- Configurar el archivo de Nginx para balancear las cargas (`/etc/nginx/nginx.conf`)

Actualmente el archivo tiene contenido. Este se debe reemplazar completamente por la siguiente configuración:

``` sh
worker_processes 4;
 
events { worker_connections 1024; }
 
http {
    sendfile on;
 
    upstream app_servers {
        server app_1:80;
        server app_2:80;
        server app_3:80;
    }
 
    server {
        listen 80;
 
        location / {
            proxy_pass         http://app_servers;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }
}
```
En este archivo se definen los servidores a los que el balanceador de carga apuntará. También se define el puerto de escucha del balanceador de cargas. En este caso, ya que el puerto 80 se encuentra actualmente en uso, se usará el puerto 8080.

- Reiniciar servicio de Nginx

``` sh
service nginx restart
```

### 1.2 Máquinas Web

- Instalar dependencias de tecnologías
``` sh
yum install httpd -y
```
- Abrir puerto 80 para recibir peticiones http
``` sh
iptables -I INPUT 5 -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
service iptables save
```
- Agregar el archivo de index que se entregara por el puerto 80


# 2. Soluciones
Realizar templates en Docker no es tan sencillo como en Vagrant. También es complicado simular estrategias para realizar templates sin romper las buenas prácticas de Docker. Por ejemplo, si se usan variables del entorno del contenedor para posteriormente modificar los archivos con el comando sed (simulando templates), tocaría ejecutar en el ENTRYPOINT todos los comandos para reemplazar los parámetros por los argumentos de building y además el comando de ejecución del servicio.

### 2.1 Solución base

Para servir la página web utilizaré Apache2 (httpd) ya que tiene una configuración muy básica, aunque es un poco pesado.

Descargamos el contenedor que viene con httpd versión 2.4
```
sudo docker pull httpd:2.4
```
Creamos el archivo Dockerfile para hacer build al nuevo contenedor que contendrá el archivo HTML de la página web.

#### 2.1.1 Contenedores web
```
#Dockerfile del httpd con archivo dinámico
FROM httpd
#Recibe el argumento de build llamado ARG1
ARG ARG1
#Agrega el index.html base al contenedor
ADD index.html /usr/local/apache2/htdocs/index.html
#Modifica el archivo index agregando el argumento al final
RUN echo "$ARG1" >> /usr/local/apache2/htdocs/index.html
```

El archivo de index.html es muy básico:
```
Hell yeah!
```

#### 2.1.2 Contenedor proxy

```
#Se usa el contenedor con nginx pre instalado
FROM nginx
#Se elimina el archivo de configuración default y su carpeta
RUN rm /etc/nginx/conf.d/default.conf && rm -r /etc/nginx/conf.d
#Se agrega el archivo de configuracion de nginx
ADD nginx.conf /etc/nginx/nginx.conf
#Se agrega esta linea para que el contenedor no termine su ejecucion.
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
CMD service nginx start
```
El archivo de configuración de Nginx que se agrega es el siguiente.
Se hace referencia a las aplicaciones por medio de los links del compose.
En el upstream se agrega el puerto 80 de los contenedores web ya que el servicio es el httpd, que por default se expone en el puerto 80.
```
worker_processes 4;
 
events { worker_connections 1024; }
 
http {
    sendfile on;
 
    upstream app_servers {
        server app_1:80;
        server app_2:80;
        server app_3:80;
    }
 
    server {
        listen 80;
 
        location / {
            proxy_pass         http://app_servers;
            proxy_redirect     off;
            proxy_set_header   Host $host;
            proxy_set_header   X-Real-IP $remote_addr;
            proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Host $server_name;
        }
    }
}
```
#### 2.1.3 Compose
En el compose se exponen los servicios de las tres aplicaciones. No me agrada tener que repetir el servicio por cada contenedor pues no es muy escalable. En todo caso, los servidores web exponen el puerto 80 del servicio HTTPD. Al exponerlos, únicamente otros contenedores del daemon de Docker podrán accederlo. Se parametrizan las diferencias de la página web por medio de la opción de args del build de la versión 3 del docker-compose.

Al final del archivo se crea el servicio de reverse-proxy de Nginx. Lo especial de este servicio es que para poder exponer el balanceo de cargas se hace el binding del puerto 80 de Nginx al puerto 8080 de la máquina host. También que se hace un link hacia las aplicaciones web. Por este link es que en el archivo de configuración de Nginx se puede hacer referencia a las IP's de los contenedores web por medio de su nombre.
```
version: '3'
 
services:
  app_1:
    build:
      context:  ./app
      dockerfile: Dockerfile
      args:
        - ARG1=App1
    expose:
      - "80"

  app_2:
    build:
      context:  ./app
      dockerfile: Dockerfile
      args:
        - ARG1=App2
    expose:
      - "80"

  app_3:
    build:
      context:  ./app
      dockerfile: Dockerfile
      args:
        - ARG1=App3
    expose:
      - "80"

  proxy:
    build:
      context:  ./nginx
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    links:
      - app_1
      - app_2
      - app_3
```

### 2.2 Otra posible solución

Es posible utilizar docker-compose para realizar una solución más elegante que permite realizar una mejor escalabilidad.

En el docker-compose.yml únicamente se agregan los tipos de contenedores que se desean una única vez. Esto tiene el problema de que no permitirá que los nodos tengan páginas web diferentes, pero cuando se intenta escalar horizontalmente servicio, la idea es que todos sean identicos.

La configuración de nginx es la misma y la aplicación web simplemente evitaría todo lo relacionado a los args de building.
```
version: '2'
 
services:
  app:
    build:
      context:  ./app
      dockerfile: Dockerfile
    expose:
      - "5000"
 
  proxy:
    build:
      context:  ./nginx
      dockerfile: Dockerfile
    ports:
      - "8080:80"
    links:
      - app

```
La configuración de nginx es la misma, únicamente se modifica el nombre de los contenedores web ya que tendrán como prefijo la carpeta en la que se encuentran. En este caso sol1 al ser la carpeta de la primera solución:
```
worker_processes 4;
 
events { worker_connections 1024; }
 
http {
    sendfile on;
 
    upstream app_servers {
        server sol1_app_1:80;
        server sol1_app_2:80;
            ....
            ....
            ....
```
y la aplicación web simplemente evitaría todo lo relacionado a los args de building.
```
#Dockerfile web del httpd con archivo dinámico
FROM httpd
ADD index.html /usr/local/apache2/htdocs/index.html
```

Se hace build de los contenedores. Esto es particularmente importante ya que no se repetirá la configuración de contenedores similares:
```
sudo docker-compose build
```

Ahora se escalarán los contenedores web a la cantidad necesaria. En este caso 3:
```
sudo docker-compose scale app=3
```
Que debe resultar en:
```
python_user@ubuntu1604:~/Documents/SistemasDistribuidos_P2/program/sol1$ sudo docker-compose scale app=3
Creating sol1_app_1 ... 
Creating sol1_app_2 ... 
Creating sol1_app_3 ... 
Creating sol1_app_1 ... done
Creating sol1_app_2 ... done
Creating sol1_app_3 ... done
```

Si se realiza un docker ps -a se oyedeb ver los 3 contenedores web:

