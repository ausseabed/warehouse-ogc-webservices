export JACKSON_VERSION=2.10.1 # MATCH the version used by geoserver
export CLASSPATH=${CATALINA_HOME}/lib/jackson-annotations-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jackson-core-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jackson-databind-${JACKSON_VERSION}.jar:${CATALINA_HOME}/lib/jul-jsonformatter-1.0.1.jar
