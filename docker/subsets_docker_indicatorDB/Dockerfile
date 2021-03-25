FROM mongo:latest
LABEL maintainer="j.camilo.garcia@hotmail.com"

#Environment folder
ENV FOLDER_APP=/src/

#copy resources
COPY ./indicator/ /database/indicator/
#COPY ./entrypoint.sh /docker-entrypoint-initdb.d/

#Script shared dictory
VOLUME ./data
VOLUME ./configuration
VOLUME ./backup
VOLUME ./logs

# docker build -t juancode528/subsets_indicators_database .
# or
# docker pull juancode528/subsets_indicators_database:latest
# docker run -d --name indicators_db -p 27017:27017 -v path/from/data:/data/indicator juancode528/subsets_indicators_database:latest
# docker exec -it indicators_db bash
# mongorestore --db=indicator --verbose /data/indicator/