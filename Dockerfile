# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory to /app
WORKDIR /app

COPY ./requirements_dev.txt /app/.
COPY ./requirements.txt /app/.

# Install any needed packages specified in requirements.txt
RUN echo "http://dl-8.alpinelinux.org/alpine/edge/community" >> /etc/apk/repositories
RUN apk --no-cache --update-cache add gcc gfortran python python-dev py-pip build-base wget freetype-dev libpng-dev openblas-dev
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install --trusted-host pypi.python.org numpy
RUN pip install --trusted-host pypi.python.org -r requirements_dev.txt

COPY ./app /app

RUN addgroup -g 1000 appuser
RUN adduser -u 1000 -D appuser -G appuser
RUN mkdir /uploads/
RUN chmod 777 /uploads/

# Make port 80 available to the world outside this container
EXPOSE 5001

ENV FLASK_APP=hello_fl.py
ENV FLASK_ENV=development
# Run app.py when the container launches
CMD ["gunicorn", "-b", "0.0.0.0:5001", "app.hello_fl:app", "--chdir", "/"]