from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates 
import re 


from app import app


#Handles Customer Objects    
class User(db.Model):

    def set_password(self, password):
      #Ensure password field is provided
      if not password:
        raise AssertionError('Password not provided')
      
      #Ensure password contains at least 1 captial letter and 1  number
      if not re.match('.*\d.*[A-Z]|.*[A-Z].*\d', password):
        raise AssertionError('Password must contain at least 1 capital letter and 1 number')
      
      #Ensure password is at least 5 characters
      if len(password) < 5:
        raise AssertionError('Password must be at least 5 characters')
      
      #Store password hash in database
      self.password = generate_password_hash(password)
      return self.password

    #to verify password
    def check_password(self, password):
        return check_password_hash(self.password, password)

    @validates('email') 
    def validate_email(self, key, email):
      #Ensure email field is provided
      if not email:
        raise AssertionError('No email provided')
      
      #Ensure proper email format
      if not re.match("[^@]+@[^@]+\.[^@]+", email):
        raise AssertionError('Provided email is not valid format') 
      return email

    #__tablename__ = 'user'
    id = db.Column(db.Integer,
                   primary_key=True)
    username = db.Column(db.String(64),
                         index=False,
                         unique=True,
                         nullable=False)
    email = db.Column(db.String(64),
                         index=False,
                         unique=True,
                         nullable=False)    
    
    password = db.Column(db.String(120),
                         index=False,
                         unique=False,
                         nullable=False)                         
    certs = db.relationship('Certificate',
        backref=db.backref('user', lazy=True))

class Certificate(db.Model):
    @validates('status') 
    def validate_status(self, key, status):
      #Ensure status field is provided
      if not status:
        raise AssertionError('No status provided')
      
      #Ensure status field is only "active" or "deactive"
      if "active" == status or "deactive" == status: # or not re.match("deactive", status):
        return status
      else:
        raise AssertionError(' status must only be: active|deactive')
    
    #Encode priv_key from String to bytes to store as BLOB type
    def encode_key(self, privKey):

      self.key_bytes = privKey.encode('utf-8')
      return self.key_bytes


    #__tablename__ = 'certificates'
    id = db.Column(db.Integer,
                   primary_key=True)
    status = db.Column(db.String(64),
                         index=False,
                         unique=False,
                         nullable=False)
    #Use type BLOB for storing bytes                     
    key_bytes = db.Column(db.BLOB,
                         index=False,
                         unique=False,
                         nullable=False) 
    body = db.Column(db.String(64),
                         index=False,
                         unique=True,
                         nullable=False)                          
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),
        nullable=False)              

    #def __repr__(self):
    #    return '<User %r>' % self.user_id
        
