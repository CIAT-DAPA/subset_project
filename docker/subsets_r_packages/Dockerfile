FROM debian:stretch
LABEL maintainer="j.camilo.garcia@hotmail.com"

ENV FOLDER_APP=/var/www/html/

COPY ./src/ ${FOLDER_APP}
COPY ./entrypoint.sh /entrypoint.sh

# Install Dependences
# More info https://cran.r-project.org/bin/linux/debian/
RUN apt-get update \ 
	&& apt-get install -y --no-install-recommends \
		apt-utils \		
		wget \		
		dirmngr \
		gnupg \		
	&& echo "deb http://cloud.r-project.org/bin/linux/debian stretch-cran35/" >> /etc/apt/sources.list \
	&& apt-key adv --keyserver hkp://keys.gnupg.net:80 --recv-key 'E19F5F87128899B192B1A2C2AD5F960A256A04AF' \
	&& apt-get update \ 
	&& apt-get install -y --no-install-recommends \	
	&& apt-get install -y r-base \
	&& apt-get install -y r-base-dev \
    && apt-get install -y gdal-bin proj-bin libgdal-dev libproj-dev \
	&& apt-get install -y libcurl4-gnutls-dev \
    && chmod +x /entrypoint.sh \
    && /entrypoint.sh \
    && rm /entrypoint.sh 

#Script shared dictory
VOLUME ./var/script/
VOLUME ./var/input/
VOLUME ./var/output/
VOLUME ./var/logs/



# docker build -t juangarcia/r-dependencies:latest .
# docker run -it --rm juangarcia/r-dependencies:latest bash