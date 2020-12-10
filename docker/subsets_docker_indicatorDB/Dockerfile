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

# docker pull juancode528/subsets_indicators_database:latest