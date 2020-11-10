#--------- Generic stuff all our Dockerfiles should start with so we get caching ------------
# ARG IMAGE_VERSION=9.0.7-jre8

## The Geoserver version
ARG GS_VERSION=2.17.1

FROM 288871573946.dkr.ecr.ap-southeast-2.amazonaws.com/ausseabed-kartoza-geoserver:9-jdk11-openjdk-slim-buster-2.18.0
USER root

WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y git python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get update -y && \ 
apt-get install -y unzip curl && \
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && \
./aws/install 

## Why all the chmod - why don't we change the USER that is executing the script?
RUN rm ${CATALINA_HOME}/log4j.properties

## Logging for Tomcat
COPY logs/catalina_logging.properties ${CATALINA_HOME}/conf/logging.properties
RUN chmod +r ${CATALINA_HOME}/conf/logging.properties

## Logging for Geoserver
COPY logs/logging.properties ${CATALINA_HOME}/webapps/geoserver/WEB-INF/classes/ 
RUN chmod +r ${CATALINA_HOME}/webapps/geoserver/WEB-INF/classes/logging.properties 

# This adds to the class path
COPY tomcat/bin/setenv.sh ${CATALINA_HOME}/bin/ 
RUN chmod +rx ${CATALINA_HOME}/bin/setenv.sh

# This is the logging that geoserver will use for log4j
COPY logs/log4j.properties ${CATALINA_HOME}
RUN chmod +r ${CATALINA_HOME}/log4j.properties
COPY logs/logging.xml /opt/geoserver/data_dir/logging.xml
RUN chmod +r /opt/geoserver/data_dir/logging.xml
COPY logs /opt/geoserver/data_dir/logs
RUN chmod +rx /opt/geoserver/data_dir/logs
RUN chmod +r /opt/geoserver/data_dir/logs/*

COPY geoserverpush/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir /usr/local/pulldata
RUN chmod +rx /usr/local/pulldata

COPY geoserverpush/*.sld /usr/local/pulldata/
COPY geoserverpush/*.py /usr/local/pulldata/
COPY geoserverpush/*.sh /usr/local/pulldata/
RUN chmod +r /usr/local/pulldata/*.sld
RUN chmod +rx /usr/local/pulldata/*.py
RUN chmod +rx /usr/local/pulldata/*.sh

COPY ausseabed.pipeline/target/*.jar ${CATALINA_HOME}/lib/
RUN chmod +r ${CATALINA_HOME}/lib/*

COPY ausseabed.pipeline/target/lib/*.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/
RUN chmod +r ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/*

COPY tomcat/conf/server.xml /usr/local/tomcat/conf 
RUN chmod +r /usr/local/tomcat/conf/*

COPY tomcat/index.html /usr/local/tomcat/webapps/ROOT/index.html
RUN chmod +r /usr/local/tomcat/webapps/ROOT/index.html

RUN ln -s /usr/lib/jni/libgdalalljni /usr/lib/jni/libgdaljni

# 3 environmental variables are required for running
# GEOSERVER_URL = "http://ec2-54-153-228-148.ap-southeast-2.compute.amazonaws.com/geoserver"
# GEOSERVER_ADMIN_PASSWORD = 
# LIST_PATH = "https://bathymetry-survey-288871573946.s3-ap-southeast-2.amazonaws.com/registered_files.json"
#  the file at the end of the path is a json encoded list of dictionary entries indexed by filename - e.g.,
#  [{"filename": "s3://bathymetry-survey-288871573946-beagle-grid0/GA-0364_BlueFin_MB/BlueFin_2018-172_1m_coloured.tif"}]

ENV \
    ## Initial Memory that Java can allocate
    INITIAL_MEMORY="500M" \
    ## Maximum Memory that Java can allocate
    MAXIMUM_MEMORY="1000M" \
    S3_SERVER_URL='' \
    S3_USERNAME='' \
    S3_PASSWORD='' \
    GEOSERVER_URL='http://localhost:8080/geoserver' \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/apr/lib:/opt/libjpeg-turbo/lib64:/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/jni;/usr/local/openjdk-14/bin/java" \
    JAVA_OPTS="-Dpost.init.script=/usr/local/pulldata/push_geoserver_settings.py \
    -Ds3.caching.chunkSizeBytes=524288 \
    -DGT2_LOGGING_REDIRECTION=JavaLogging \
    -DRELINQUISH_LOG4J_CONTROL=true \
    -Djava.util.logging.config.file=${CATALINA_HOME}/webapps/geoserver/WEB-INF/classes/logging.properties"

# \"-Djava.util.logging.config.file=${CATALINA_HOME}/conf/logging.properties" \
    
# defaults for Cache config that could also be tailored:
# -Ds3.caching.diskCacheSize= 524288000 # 500 MB
# -Ds3.caching.diskPath= Files.createTempDirectory("s3Cachine")

CMD ["/usr/local/pulldata/decode_aws_json.sh","/scripts/entrypoint.sh"]
