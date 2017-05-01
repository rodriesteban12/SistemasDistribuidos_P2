FROM httpd
ARG ARG1
ADD index.html /usr/local/apache2/htdocs/index.html
RUN echo "$ARG1" >> /usr/local/apache2/htdocs/index.html
