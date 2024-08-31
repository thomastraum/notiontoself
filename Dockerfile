# Use an official Python runtime as a base image
FROM python:3.10

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app
COPY .env /app/.env

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

ARG NOTION_DATABASE_ID
ENV NOTION_DATABASE_ID=${NOTION_DATABASE_ID}

# Run app.py when the container launches
CMD ["python", "main.py"]
