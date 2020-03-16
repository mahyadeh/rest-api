from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from os import environ
from config import Config


     
app = Flask(__name__)

app.config.from_object(Config)
db = SQLAlchemy(app) 

#create all db tables based on models.py
@app.before_first_request
def create_tables(): 
  db.create_all()

from app import models, routes
