from flask import request, render_template, make_response, jsonify
from datetime import datetime as dt
import requests
from .models import db, User, Certificate
from app import app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError, InterfaceError


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
    
@app.errorhandler(500)
def internal_error(error):
    return make_response(jsonify({'An unexpected error has occurred'}), 500)    
@app.errorhandler(Exception)
def exception_error(error):
    return make_response(jsonify({'An exception has occurred'}), 404)    

#homepage
@app.route('/', methods=['GET'])
@app.route('/api/v1/', methods=['GET'])
@app.route('/api/v1', methods=['GET'])
def homepage():
    return "Welcome to the customer managemenet API"


#get info for all customers in database (password field is hidden)
@app.route("/api/v1/customers", methods=['GET'])
@app.errorhandler(404)
def get_customers():
    
    all_customers = User.query.all()
    customers_info=[]
    for cust in all_customers:
       customers_info.append({
                  'customername': cust.username,
                  'email': cust.email,
                  'certificates': [ c.id for c in cust.certs ]
                  }
                  )
    return make_response(f"All existing customers: {customers_info} ")

#get customer info
@app.route('/api/v1/customer/<string:customername>', methods=['GET'])
@app.errorhandler(404)
def get_customer(customername):
   try:
    cust = User.query.filter_by(username=customername).first_or_404(description='There is no record for user:  {}'.format(customername))
   
    
    return make_response(f"info for {cust.username}: email: {cust.email}, password: {cust.password},  certs: {[c.id for c in cust.certs]} ")
   except Exception as e:
     reason=str(e)
     return jsonify(msg='Error: {}. '.format(reason)), 404
     

#create new record for customer in database
@app.route('/api/v1/customer', methods=['POST'])
def create_customer():
    
    #extract info from request
    data = request.get_json()
    c_username = data['username']
    c_email = data['email']
    c_password = data['password']
    c_certs = data['certs']
    
    #create customer entry
    cust = User(username=c_username, email=c_email )
    cust.password=cust.set_password(c_password)

  
    try:
      db.session.add(cust)
      db.session.commit()
      cust_info ={
                  'customername': cust.username,
                  'email': cust.email,
                  'certificates': [ c.id for c in cust.certs ]
                  }
                  
      return make_response(f"User successfully created: {cust_info} ")
    except AssertionError as exception_message: 
      return jsonify(msg='Error: {}. '.format(exception_message)), 400

    except IntegrityError as e:
      db.session.rollback()
      return jsonify(msg='Error: One or more fields are not unique {}. '.format(e)), 400


#delete customer from database
@app.route('/api/v1/customer/<string:customername>', methods=['DELETE'])
@app.errorhandler(404)
def delete_customer(customername):
        try:
          cust = User.query.filter_by(username=customername).first_or_404()
          db.session.delete(cust)
          db.session.commit()
          return make_response(f" customer {cust.username} was successfully deleted ")
        except InterfaceError as e: 
           return jsonify(msg='Error: {}. '.format(e)), 400
        except Exception as e:
          reason=str(e)
          return jsonify(msg='Error: {}. '.format(reason)), 404           




#Updates customer info (email, password)
@app.route('/api/v1/customer/<string:customername>', methods=['PUT'])
def update_customer(customername):
    #extract info from request
    data = request.get_json()
    
    #check if customer exists
    cust = User.query.filter_by(username=customername).first_or_404()
    
    #get info from request
    c_email =  request.json.get('email', cust.email)
    c_password =  request.json.get('password', cust.password)
    c_certs =  request.json.get('certs', cust.certs)
    
    #update cust ino
    cust.email=c_email
    cust.password=cust.set_password(c_password)
    cust.certs=c_certs
    
    try: 
     db.session.add(cust)
     db.session.commit()
     return make_response(f" Updated info for {cust.username}: 'email': {cust.email}, 'password': {cust.password}, 'certs': {cust.certs} ")
    except AssertionError as exception_message: 
      return jsonify(msg='Error: {}. '.format(exception_message)), 400
   

#Creates a new certificate for customer
#Customer must already exist before you can create certificate
@app.route('/api/v1/customer/<string:customername>/cert', methods=['POST'])
@app.errorhandler(404)
def create_cert(customername):
  #extract info from request
  data = request.get_json()
  c_status = data['status']
  c_privKey = data['privKey']
  c_body = data['body']

  try:
    #make sure customer exists first
    cust = User.query.filter_by(username=customername).first_or_404(description='There is no record for user {}'.format(customername))
    
    cert = Certificate(body=c_body, status=c_status,user=cust)
    #encode private key (storage type is BLOB)
    cert.key_bytes=cert.encode_key(c_privKey)
    
    #assign certificate to customer
    cust.certs.append(cert)
    cert_info ={
                  'status': cert.status,
                  'privKey': cert.key_bytes,
                  'body': cert.body
                }
    


    db.session.add(cust)
    db.session.commit()
    return make_response(f" Created certificate for {cust.username}: {cert_info} ")
  except AssertionError as exception_message: 
     return jsonify(msg='Error: {}. '.format(exception_message)), 400
  except Exception as e:
     reason=str(e)
     return jsonify(msg='Error: {}. '.format(reason)), 404



#Get all (active,deactive) certificates for customer
@app.route('/api/v1/customer/<string:customername>/certs', methods=['GET'])
@app.errorhandler(404)
def get_certs(customername):
    
    try:
     #find customer in database
     cust =  User.query.filter_by(username=customername).first_or_404()
      
     all_certs =[]
     for c in cust.certs:
      all_certs.append({
          'id': c.id,
          'status': c.status,
          'privKey': c.key_bytes,
          'body': c.body
          }
         )
     

     return make_response(f" all certificates for customer {cust.username} : {all_certs} ")
    except Exception as e:
      reason=str(e)
      return jsonify(msg='Error: {}. '.format(reason)), 404 



#get all active certificates for customer
@app.route('/api/v1/customer/<string:customername>/certs/active', methods=['GET'])
@app.errorhandler(404)
def get_certs_active(customername):
  try:
    cust =  User.query.filter_by(username=customername).first_or_404()
    
    #get all active certificates
    all_active_certs=[ { "id": c.id, "privKey": c.key_bytes, "status": c.status, "body":c.body} for c in cust.certs if c.status=="active"]   

    return make_response(f" all active certificates for customer: {cust.username} : {all_active_certs} ")
  except Exception as e:
      reason=str(e)
      return jsonify(msg='Error: {}. '.format(reason)), 404 
      

#get all deactive certificates for customer
@app.route('/api/v1/customer/<string:customername>/certs/deactive', methods=['GET'])
@app.errorhandler(404)
def get_certs_deactive(customername):
  try:
    #find customer in database
    cust =  User.query.filter_by(username=customername).first_or_404()
    
    #get all deactive certificates
    all_deactive_certs=[ { "id": c.id, "privKey": c.key_bytes, "status": c.status, "body":c.body} for c in cust.certs if c.status=="deactive"]  

    return make_response(f" all deactive certificates for customer: {cust.username} : {all_deactive_certs} ")
  except Exception as e:
      reason=str(e)
      return jsonify(msg='Error: {}. '.format(reason)), 404     
 

#Notify external system, tested with http://httpbin.org
def notify_external_system(msg):
          #notify
          notification_url = 'http://httpbin.org/post'
          notification_testdata={'msg':msg}
          r = requests.post(notification_url, json=notification_testdata)
          return r.status_code  
 

#Activates a certificate that is deactive. 
#Notifies external system  about this event
@app.route('/api/v1/customer/<string:customername>/certs/activate/<int:certid>', methods=['PUT'])
@app.errorhandler(404)
def activate_cert(customername,certid):
    
       #verify customer exists
       cust = User.query.filter_by(username=customername).first_or_404()
       
       #find certificate for customer
       cert_for_cust = Certificate.query.get_or_404(certid)
       
       #only activate certificates that are currently "deactive"
       if cert_for_cust.status == "deactive":
          cert_for_cust.status = "active"
          
          db.session.add(cert_for_cust)
          db.session.add(cust)
          db.session.commit()
          
          #Notify exterenal system about certificate activation
          status_code = notify_external_system(msg="Certificate was just activated")
          if status_code == 200:
             msg="External system notified successfully"
          else:
             msg="External system not notified"
          
          return make_response(f" cert {cert_for_cust.id} for {cust.username} was actived. {msg} ")

       #No action needed if certificate is already active
       else:
           return make_response(f" cert {cert_for_cust.id} for {cust.username} was already active! ")      
    
    



#Deactivates a certificate that is active
#Notifies external system  about this event
@app.route('/api/v1/customer/<string:customername>/certs/deactivate/<int:certid>', methods=['PUT'])
def deactivate_cert(customername,certid):
       #verify customer exists
       cust = User.query.filter_by(username=customername).first_or_404()
       
       #find certificate for customer
       cert_for_cust = Certificate.query.get_or_404(certid)
       
       #only deactivate certificates that are currently "active"       
       if cert_for_cust.status == "active":
          cert_for_cust.status = "deactive"
          
          db.session.add(cert_for_cust)
          db.session.add(cust)
          db.session.commit()
          
          #Notify exterenal system about certificate deactivation
          status_code = notify_external_system(msg="Certificate was just deactivated")
          
          if status_code == 200:
             msg="External system notified successfully"
          else:
             msg="External system not notified"
          
          return make_response(f" cert {cert_for_cust.id} for {cust.username} was deactived. {msg} ")          
 
       #No action needed if certificate is already deactive
       else:
           return make_response(f" cert {cert_for_cust.id} for {cust.username} was already deactive! ")      
