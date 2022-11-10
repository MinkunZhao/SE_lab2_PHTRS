import os
# import pandas as pd
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
# from sqlalchemy import create_engine
from os import path
from dotenv import load_dotenv
# from config import Config, DevConfig

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '../.env'))

# init SQL Alchemy so we can use it later in our models
# the class is used to control the SQLAlchemy integration to one or more Flask applications
db = SQLAlchemy()

# the __init__.py contains the application factory and tells Python that the "project" directory should be treated as a package
# create_app is the application factory function


def create_app(config=None):
    # __name__ is the name of the current Python module.
    # The app needs to know where it's located to set up some paths, and it uses name to do this
    # instance_relative_config=True tells the app that configuration files are relative to the instance folder.
    # The "instance folder" is located outside the "project" package and can hold local data that should not be commited to version control
    app = Flask(__name__, instance_relative_config=True)
    
    # app.config.from_mapping sets default configuration that the app will use
    # the secret_key is used to keep data safe
    # it's set to 'dev' to provide a convenient value during development, but should be overridden with a random value when deploying
    # DATABASE is the path where the SQLite database file will be saved
    # it's under app.instance_path, which is the path that Flask has chosen for the instance folder
    app.config.from_object('config.DevConfig')
    
    #app.config['SECRET_KEY'] = '\xd5c\xad\x07\x8bv\x0cd\x9f\xc6\xfb\xf8xM\x08S'
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pothole.sqlite'
    

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Configure the application to support the SQLAlchemy object
    # A flask.Flask.app_context() has to exist to issue create_all and drop_all statements
    db.init_app(app)
    
    # the login manager contains the code that lets your application and Flask-Login work together
    login_manager = LoginManager()
    
    #sets the name of the login view
    login_manager.login_view = 'auth.login'
    
    #Once the actual application object has been created, configure it for login:
    login_manager.init_app(app)
    
    # import the user model
    from .models import User
    
    # you need to provide a user_loader callback
    # the callback is used to reload the user object from the user ID stored in the session
    # it should take the unicode  ID of a user, and return the corresponding user object
    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))
    
    #blueprint for auth routes in our app
    #blueprints organize groups of related views and other code
    #Rather than registering views and code directly with an application, they are registered with a blueprint
    #The blueprint is registered with the application when it is available in the factor function
    # import and register the blueprint from the factory using app.register_blueprint()
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    #blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
  
    # with app.app_context():
    #     from .models import Equipment
    #     from .models import RepairCrew
    #     db.create_all()
    #     db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    #
    #     engine = create_engine(db_uri, echo=True)
    #
    #     file = ".\\project\\street_centerline.csv"
    #     #file = ".\\street_centerline.csv"
    #
    #     data = pd.read_csv(file)
    #
    #     data.to_sql('DenverStreets', con=engine, if_exists='replace')
    #
    #     if not db.session.query(Equipment).first() or not db.session.query(RepairCrew).first():
    #
    #         newEquipment1 = Equipment(equipment="Bobcat", costPerHour = 31.25)
    #         newEquipment2 = Equipment(equipment="Steam Roller", costPerHour = 23.75)
    #         newEquipment3 = Equipment(equipment="Patch Hand Roller", costPerHour = 10.00)
    #         newEquipment4 = Equipment(equipment="Bull Dozer", costPerHour = 25.00)
    #         newEquipment5 = Equipment(equipment="Dump Truck", costPerHour = 45.50)
    #         newEquipment6 = Equipment(equipment="Power Tamper", costPerHour = 15.00)
    #         newEquipment7 = Equipment(equipment="Pro-Patch Asphalt Patcher", costPerHour = 33.25)
    #         newEquipment8 = Equipment(equipment="Spray-Injection Machine", costPerHour = 28.75)
    #         db.session.add_all([newEquipment1, newEquipment2, newEquipment3, newEquipment4, newEquipment5,
    #                         newEquipment6, newEquipment7, newEquipment8])
    #         newRepair1 = RepairCrew(people=5, HRpay=20.00)
    #         newRepair2 = RepairCrew(people=10, HRpay=20.00)
    #         newRepair3 = RepairCrew(people=15, HRpay=20.00)
    #         newRepair4 = RepairCrew(people=20, HRpay=20.00)
    #         newRepair5 = RepairCrew(people=2, HRpay=20.00)
    #         newRepair6 = RepairCrew(people=3, HRpay=20.00)
    #         newRepair7 = RepairCrew(people=1, HRpay=20.00)
    #         db.session.add_all([newRepair1,
    #                             newRepair2,
    #                             newRepair3,
    #                             newRepair4,
    #                             newRepair5,
    #                             newRepair6,
    #                             newRepair7])
    #         db.session.commit()

    return app


#app = create_app()

