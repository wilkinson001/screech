# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory to /app
WORKDIR /app

COPY ./app /app
COPY ./requirements_dev.txt /app/.
COPY ./requirements.txt /app/.

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements_dev.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["flask", "run"]