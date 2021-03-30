FROM python:3.8

# Create app directory
WORKDIR /var/www/app

ENV PYTHONUNBUFFERED=1

# Install app dependencies
COPY ./src/subsets_api/requirements.txt ./

RUN pip install -r requirements.txt

# Bundle app source
COPY ./src/subsets_api/ /var/www/app

CMD python3 manage.py runserver 0.0.0.0:8000

# cd ..\..\
# docker build -t juancode528/subsets_api_python -f docker/subsets_webapi/Dockerfile .
# or 
# docker pull juancode528/subsets_api_python
# docker run -d --name subsets_api -p 8000:8000 --link indicators_db:mongo --env-file path/to/env juancode528/subsets_api_python:latest
