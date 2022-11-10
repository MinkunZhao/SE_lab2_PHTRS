from sqlalchemy import Table, Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) #primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    type = db.Column(db.String(100))
    
class Pothole(db.Model):
    __tablename__ = 'pothole'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    streetNumber = db.Column(db.Integer)
    streetName = db.Column(db.Text)
    state = db.Column(db.String(2))
    city = db.Column(db.String(10))
    zip = db.Column(db.Integer)
    size = db.Column(db.Integer)
    location = db.Column(db.String(100))
    district = db.Column(db.String(100))
    priority = db.Column(db.String(100))
    w_order = db.Column(db.Integer)
    
class RepairCrew(db.Model):
    __tablename__ = 'repair_crew'
    id = db.Column(db.Integer, primary_key=True)
    people = db.Column(db.Integer)
    HRpay = db.Column(db.Float)
    total = db.Column(db.Float)
    
    def __init__(self, people, HRpay):
        self.people = people
        self.HRpay = HRpay
        self.total = (self.people * self.HRpay)
    
class Equipment(db.Model):
    __tablename__ = 'equipment'
    id = db.Column(db.Integer, primary_key=True)
    equipment = db.Column(db.String(100))
    costPerHour = db.Column(db.Float)
    
    def __init__(self, equipment, costPerHour):
        self.equipment = equipment
        self.costPerHour = costPerHour
        
class WorkOrder(db.Model):
    __tablename__ = 'work_order'
    id = db.Column(db.Integer, primary_key=True)
    pothole_id = db.Column(db.Integer, ForeignKey('pothole.id'))
    repair_crew_id = db.Column(db.Integer, ForeignKey('repair_crew.id'))
    hours = db.Column(db.Integer)
    status = db.Column(db.String(100))
    fillerAmount = db.Column(db.Integer)
    cost=db.Column(db.Float)
    
    def __init__(self, pothole_id, repair_crew_id,
                 hours, status, fillerAmount, cost):
        self.pothole_id = pothole_id
        self.repair_crew_id = repair_crew_id
        self.hours = hours
        self.status = status
        self.fillerAmount = fillerAmount
        self.cost = cost
        
    
class Bridge(db.Model):
    __tablename__ = 'bridge'
    id = db.Column(db.Integer, primary_key=True)
    work_order_id = db.Column(db.Integer, ForeignKey('work_order.id'))
    equipment_id = db.Column(db.Integer, ForeignKey('equipment.id'))
    
    def __init__(self, work_order_id, equipment_id):
        self.work_order_id = work_order_id
        self.equipment_id = equipment_id
        
class Damage(db.Model):
    __tablename__ = 'damage'
    id = db.Column(db.Integer, primary_key=True)
    pothole_id = db.Column(db.Integer, ForeignKey('pothole.id'))
    name = db.Column(db.String(100))
    address1 = db.Column(db.String(100))
    address2 = db.Column(db.String(100))
    city = db.Column(db.String(100))
    state = db.Column(db.String(2))
    zip = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    damage = db.Column(db.Text)
    amount = db.Column(db.Float())
    
    def __init__(self, pothole_id, name, address1,
                 address2, city, state, zip,
                 phone, damage, amount):
        self.pothole_id = pothole_id
        self.name = name
        self.address1 = address1
        self.address2 = address2
        self.city = city
        self.state = state
        self.zip = zip
        self.phone = phone
        self.damage = damage
        self.amount = amount
