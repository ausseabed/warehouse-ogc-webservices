# Mirror of kartoza/geoserver:2.22.2
FROM 288871573946.dkr.ecr.ap-southeast-2.amazonaws.com/ausseabed-kartoza-geoserver:9-jdk11-openjdk-slim-buster-2.22.2
USER root

WORKDIR /usr/src/app

RUN apt-get update \
  && apt-get install -y git python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN pip3 install pyOpenSSL==23.0.0 --upgrade

RUN apt-get update -y && \
apt-get install -y unzip curl && \
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
unzip awscliv2.zip && \
./aws/install 

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

RUN mkdir -p /usr/local/pulldata/styles
RUN mkdir -p /usr/local/pulldata/vector_config
RUN chmod +rx /usr/local/pulldata

COPY geoserverpush/styles/*.sld /usr/local/pulldata/styles/
COPY geoserverpush/vector_config/ /usr/local/pulldata/vector_config/
COPY geoserverpush/*.py /usr/local/pulldata/
COPY geoserverpush/*.sh /usr/local/pulldata/
RUN chmod +r /usr/local/pulldata/styles/*.sld
RUN chmod -R +r /usr/local/pulldata/vector_config/
RUN chmod +rx /usr/local/pulldata/*.py
RUN chmod +rx /usr/local/pulldata/*.sh
# COPY /usr/local/pulldata/entrypoint.sh .
COPY geoserverpush/entrypoint.sh ./
RUN chmod +rx entrypoint.sh

COPY ausseabed.pipeline/target/*.jar ${CATALINA_HOME}/lib/
COPY ausseabed.pipeline/target/lib/*.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/

# Oracle support
COPY ./gt-jdbc-oracle-28.2.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/
COPY ./ojdbc8-19.10.0.0.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/

# fix for s3-geotiff plugin
COPY ./gt-s3-geotiff-30-SNAPSHOT.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/

# ehcache issue; see https://github.com/kartoza/docker-geoserver/issues/340
# manually copying as the above fix was later removed
# package builders for s3-geotiff might've also removed causing the issue to come back
COPY ./ehcache-2.10.9.2.jar ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/

RUN chmod +r ${CATALINA_HOME}/lib/*
RUN chmod +r ${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/*

COPY tomcat/conf/server.xml /usr/local/tomcat/conf 
RUN chmod +r /usr/local/tomcat/conf/*

COPY tomcat/index.html /usr/local/tomcat/webapps/ROOT/index.html
RUN chmod +r /usr/local/tomcat/webapps/ROOT/index.html

RUN ln -s /usr/lib/jni/libgdalalljni /usr/lib/jni/libgdaljni

ENV \
    GEOSERVER_ADMIN_USER="admin" \
    GEOSERVER_CSRF_WHITELIST="ausseabed.gov.au" \
    # Disable Geoserver X-Frame-Options header
    XFRAME_OPTIONS="false" \
    S3_SERVER_URL='' \
    S3_USERNAME='' \
    S3_PASSWORD='' \
    GEOSERVER_URL='http://localhost:8080/geoserver' \
    LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/usr/local/apr/lib:/opt/libjpeg-turbo/lib64:/usr/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/jni" \
    JAVA_OPTS="-Dpost.init.script=/usr/local/pulldata/push_geoserver_settings.py \
    -Ds3.caching.chunkSizeBytes=524288 \
    -DGT2_LOGGING_REDIRECTION=JavaLogging \
    -DRELINQUISH_LOG4J_CONTROL=true \
    -Djava.util.logging.config.file=${CATALINA_HOME}/webapps/geoserver/WEB-INF/classes/logging.properties"

# \"-Djava.util.logging.config.file=${CATALINA_HOME}/conf/logging.properties" \
#    -Djavax.xml.stream.XMLOutputFactory=com.bea.xml.stream.XMLOutputFactoryBase \
    
# defaults for Cache config that could also be tailored:
# -Ds3.caching.diskCacheSize= 524288000 # 500 MB
# -Ds3.caching.diskPath= Files.createTempDirectory("s3Cachine")

# CMD ["/usr/local/pulldata/decode_aws_json.sh","geoserverpush/entrypoint.sh"]
# ENTRYPOINT ["/usr/local/pulldata/decode_aws_json.sh"]
# CMD ["entrypoint.sh"]
ENTRYPOINT ["/usr/local/pulldata/decode_aws_json.sh","./entrypoint.sh"]
