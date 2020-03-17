# HTTP based RESTful API for managing customers/certificates

Code for a creating dockerized Flask REST API with MySQL and Flask-SQLAlchemy

## Requirements

- Docker
- Docker Compose

## Getting Started

- git clone -b nginx https://github.com/mahyadeh/rest-api-test.git
- cd rest-api
- docker-compose up --build
- docker-compose down (to stop containers)

To access:
  From your broswer open:
  https://localhost:8443/api/v1/
  or
  curl https://localhost:8443/api/v1/

## Data persistence
- Uses local volume (db-data) to persist database info from the mysql container.
- Data will be persisted in local folder after application is stopped 
- Application uses host port 6000 ( can change as needed in the docker-compose file)

## Assumptions
- customer name and email are unique
- Passwords must be at least 5 chars long and must contain at least 1 capital letter and 1 number
- Passwords are not directly stored in the database, hashing function is used(from werkzeug.security import generate_password_hash)
- In order to create a certificate for a customer, the customer must already exist first.
- Certificate status can only be  "active" or "deactive"
- Certificate private keys for certificates can be passed as string to the API call. It will be encoded to bytes before being stored in the database (type is BLOB)


## API USGAE
There are 2 main types(tables):

# 
    Customer: { customername: String,
                email: String,
                password: String,
                certificates: [Certificate],
                cust_id (PRIMARY KEY)
               }

            
    Certificate: { status: String (active|deactive),
                   privKey: String,
                   body: String,
                   cust_id (FOREIGN KEY)
                 }
               
# API Methods:
 ### 1. Create customer:
       curl  -H "Content-Type: application/json"   -X POST  -d '{"email":"user1@mail.com", "username":"user1", "password":"randomPass1","certs":""}' https://localhost:8443/api/v1/customer


 ### 2. Get customer:
       curl  -X GET https://localhost:8443/api/v1/customer/<customername>
       
 ### 3. View all customers
     curl  https://localhost:8443/api/v1/customers

 ### 4. Delete customer
     curl  -X DELETE https://localhost:8443/api/v1/customer/<customername>


 ### 5. Update customer info (only email and password)
    curl -H "Content-Type: application/json" -d '{"email":"newemail@mail.com", "password":"Newpassword1"}'   -X PUT https://localhost:8443/api/v1/customer/<customername>


 ### 6. Create certificate (customer must already exist)
    curl -H "Content-Type: application/json"   -X POST  -d '{"status":"active", "privKey":"randomKey", "body":"randomBody"}' https://localhost:8443/api/v1/customer/<customername>/cert

 ### 7.  Get all customer certificates (active and deactive)
    curl  https://localhost:8443/api/v1/customer/<customername>/certs

 ### 8. Get all customer ACTIVE certificates
    curl  https://localhost:8443/api/v1/customer/<customername>/certs/active

 ### 9. Activate csutomer certificate
    curl -X PUT https://localhost:8443/api/v1/customer/<customername>/certs/activate/<certID>

 ### 10. Deactivate customer certificae
    curl -X PUT https://localhost:8443/api/v1/customer/<customername>/certs/deactivate/<certID>            


### Repository Contents

- `app/routes.py` - Define  endpoints
- `app/models.py` - Defines database schema
- `app/__init__.py` - initially ran when application starts
- `config.py` - Provides database configuration
- `app.py` - main entry point to start the flask app
- `docker-compose.yaml` - docker-compose to start all services (flask, mysql db, nginx)
- `Dockerfile` - Dockerfile to build  flask app
- `requirements.txt` - list of python package dependencies the application requires
- `README.md` - README file
- `db-data/` - local volume (mounted to mysql container) for data persistence
- `nginx/Dockerfile` - Dockefile for nginx service
- `nginx/nginx.conf` - config file for nginx
- `nginx/nginx.cert` - self signed certificate 
- `nginx/nginx.key` - key for self signed certificate 

