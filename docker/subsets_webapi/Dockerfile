FROM python:3.8

# Create app directory
WORKDIR /var/www/app

# Install app dependencies
COPY ../../src/subsets_api/requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY ../../src/subsets_api/ /var/www/app

EXPOSE 8080
#CMD [ "python", "server.py" ]