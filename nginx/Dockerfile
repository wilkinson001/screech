FROM nginx:latest
RUN rm /etc/nginx/conf.d/default.conf
RUN rm -rf /etc/nginx/sites-enabled/default
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/setup.conf /etc/nginx/conf.d/
COPY app/static/ /static