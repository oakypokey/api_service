FROM python:latest

# set the working directory
WORKDIR /api_service

# install dependencies
COPY ./requirements.txt /api_service
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy the scripts to the folder
COPY . /api_service

# Expose port
EXPOSE 8080

# start the server
CMD ["python", "-m", "src"]