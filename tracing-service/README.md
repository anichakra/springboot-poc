# springboot-poc
This contains a microservice demo with springboot and docker..

# Pre-requisite
1) Install Postgre (9.6.6) : https://www.enterprisedb.com/downloads/postgres-postgresql-downloads

2) Install Node JS : https://nodejs.org/download/release/v8.9.3/node-v8.9.3-x64.msi

3) Install Rabbit MQ : https://www.rabbitmq.com/download.html

4) Install Kafka : https://dzone.com/articles/running-apache-kafka-on-windows-os


# After installing Postgre create database by using following steps
1) Go to postgre bin path : usually path is C:\Program Files\PostgreSQL\9.6\bin

2) Open CMD with this location and run pg_ctl -D "data path" start ...... usually data path is C:\Program Files\PostgreSQL\9.6\data

3) Now open new cmd window with same bin path and run psql -U postgre

4) You are now in postgre consol. Create DB by this command "create database authsystem"

5) Verify DB creation by running command \list.

#Config-Server
Under config server project open application.yml and kindly add your creandentials to run the project in local

username: #Enter your user name

password: #Enter your password 

url : enter git URL



