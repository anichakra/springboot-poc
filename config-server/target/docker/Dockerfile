FROM openjdk:8-jdk-alpine
ADD /config-server-0.0.1-SNAPSHOT.jar //
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar", "/config-server-0.0.1-SNAPSHOT.jar"]
