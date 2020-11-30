FROM mongo:latest
LABEL maintainer="j.camilo.garcia@hotmail.com"

#Environment folder
ENV FOLDER_APP=/src/

#copy resources
COPY ./indicator/ /database/indicator/
COPY ./entrypoint.sh /docker-entrypoint-initdb.d/

#Script shared dictory
VOLUME [ ${FOLDER_APP}, "/mnt", "/src/data/" ]
VOLUME [ ${FOLDER_APP}, "/mnt", "/src/logs/" ]
VOLUME [ ${FOLDER_APP}, "/mnt", "/src/configuration/" ]
VOLUME [ ${FOLDER_APP}, "/mnt", "/src/backup/" ]

# docker build -t juangarcia/subsets_indicator_database:latest .
# docker run --name indicator_db -d subsets_indicators_database:latest