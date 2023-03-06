export JACKSON_VERSION=2.13.2 # MATCH the version used by geoserver
export JACKSON_DATABIND_VERSION=2.13.4.1 # MATCH the version used by geoserver
export CLASSPATH=${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/commons-logging-1.1.1.jar:${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/jackson-annotations-${JACKSON_VERSION}.jar:${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/jackson-core-${JACKSON_VERSION}.jar:${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/jackson-databind-${JACKSON_DATABIND_VERSION}.jar:${CATALINA_HOME}/webapps/geoserver/WEB-INF/lib/jul-jsonformatter-1.0.1.jar
export CATALINA_LOGGING_CONFIG="-Djava.util.logging.config.file=${CATALINA_HOME}/conf/logging.properties"
export TOMCAT_POST_INIT_SCRIPT='/usr/local/pulldata/push_geoserver_settings.py'
