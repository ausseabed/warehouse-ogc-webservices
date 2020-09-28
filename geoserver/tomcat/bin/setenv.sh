export JACKSON_VERSION=2.10.1 # MATCH the version used by geoserver
export CLASSPATH=${CATALINA_HOME}/lib/jackson-annotations-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jackson-core-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jackson-databind-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jul-jsonformatter-1.0.1.jar:${CATALINA_HOME}/conf
export CATALINA_LOGGING_CONFIG="-Djava.util.logging.config.file=${CATALINA_HOME}/conf/logging.properties"
