from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Pothole, Equipment, RepairCrew, WorkOrder, Bridge, Damage
from . import db
from re import sub
from decimal import Decimal
import sqlite3
from sqlalchemy import func
import sys

# this creates a blueprint named 'auth'
# like the application object, the blueprint needs to know where it's defined
# the name is passed as the second argument
# the url_prefix will be prepended to all the URLs associated with the blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')


def get_db_connection():
    conn = sqlite3.connect(".\\project\\pothole.sqlite")
    conn.row_factory = sqlite3.Row
    return conn

@auth.route('/signup')
def signup():
    return render_template('auth/signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    userType = request.form.get('loginType')
    
    user = User.query.filter_by(email=email).first() # if this returns a user, the the email is already in the db
    
    if user: # if a user is found, we want to redirect back to signup page so user can try again
        flash('Email address already exists')
        return redirect(url_for('auth.signup'))
    
    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), type=userType)
    
    # add the new user to the db
    db.session.add(new_user)
    db.session.commit()
    
    return redirect(url_for('auth.login'))

@auth.route('/login')
def login():
    return render_template('/auth/login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    
    email = request.form.get('email')
    password = request.form.get('password')
    formType = request.form.get('loginType')
    
    user = User.query.filter_by(email=email).first()
    
    # check if user exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
    
    if user.type != formType:
        flash('Please make sure you have the correct login type selected from the drop-down menu')
        return redirect(url_for('auth.login'))
    
    # if the above check passes, then we know the user has the right credentials
    if formType=='Citizen':
        login_user(user)
        return redirect(url_for('auth.citizen'))
    elif formType=='Employee':
        login_user(user)
        return redirect(url_for('auth.employee'))

@auth.route('/citizen')
@login_required
def citizen():
    conn = get_db_connection()
    
    #get init values
    rows = conn.execute("select FULLNAME, ZIPLEFT \
                                    from DenverStreets \
                                    where JURISID == 'DENVER' \
                                    group by fullname").fetchall()
    
    conn.close()
                                
    return render_template('auth/citizen.html', name=current_user.name, streetList=rows)

@auth.route('/citizen', methods=['POST'])
@login_required
def citizen_post():
    
    streetNumber = request.form.get('streetNumber')
    streetName = request.form.get('streetName')
    state = "CO"
    city = "DENVER"
    zipCode = request.form.get('zip')
    location = request.form.get('location')
    size = int(request.form['answer'])
    priority = None
    w_order = 0
    
    conn = get_db_connection()
    
    district = conn.execute('SELECT distinct addressquad \
                            FROM DenverStreets \
                            WHERE zipleft = ? \
                            AND fullname = ?  \
                            AND jurisid = ?', (zipCode, streetName, city)).fetchone()['addressquad']
    
    if district == 'N':
         district = 'North'
    elif district == 'E':
         district = 'East'
    elif district == 'S':
         district = 'South'
    elif district == 'W':
        district = 'West'
    elif district == 'NW':
        district = 'North West'
    elif district == 'NE':
        district = 'North East'
    elif district == 'SW':
        district = 'South West'
    elif district == 'SE':
        district = 'South East'
        
    if size == 1 or size == 2:
        priority = 'Very Low'
    elif size == 3 or size == 4:
        priority = 'Low'
    elif size == 5 or size == 6:
        priority = 'Medium'
    elif size == 7 or size == 8:
        priority = 'High'
    elif size == 9 or size == 10:
        priority = 'Urgent'

    conn.execute('INSERT INTO pothole (user_id, streetNumber, streetName, city, state, \
                 zip, location, district, size, priority, w_order) VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (current_user.id,streetNumber,streetName,city,state,zipCode,location,district,size,priority,w_order))
    
    conn.commit()
    conn.close()   

    return redirect(url_for('auth.citizen'))

@auth.route('/get_zip')
def update_dropdown():
    street = request.args.get('street', type=str)
    
    conn = get_db_connection()
    
    rows = conn.execute("select FULLNAME, ZIPLEFT \
                                from DenverStreets \
                                where JURISID == 'DENVER' \
                                and fullname = ? \
                                group by fullname", (street,)).fetchall()
    zipValues = ''
    for row in rows:
        zipValues += '<option values="{}">{}</option>'.format(row['zipleft'], row['zipleft'])
        
    return jsonify(zipValues=zipValues)

@auth.route('/employee')
@login_required
def employee():
    
    potholes = Pothole.query.filter_by(w_order=0).all()
    potholesCheck = Pothole.query.filter_by(w_order=0).first()
    equipmentList = Equipment.query.order_by(Equipment.equipment).all()
    crewList = RepairCrew.query.order_by(RepairCrew.id).all()
    
    if potholesCheck is not None:
        return render_template('auth/employee.html', name=current_user.name, potholes=potholes, equipment=equipmentList, crewList=crewList)
    else:
        # Update if potholes are empty
        return redirect(url_for('main.index'))

@auth.route('/employee', methods=['POST'])
@login_required
def employee_post():
    pothole_number = request.form.get('potholes', type=int)
    Pothole.query.filter(Pothole.id == pothole_number).\
        update({"w_order": (1)})
    db.session.commit()
    crew_number = request.form.get('crew', type=int)
    print(pothole_number, file=sys.stderr)
    hours = request.form.get('hours', type=int)
    status = request.form.get('status', type=str)
    filler = request.form.get('filler', type=int)
    equipmentList = request.form.getlist('equipment')
    print(equipmentList, file=sys.stderr)
    cost = request.form.get('cost', type=str)
    cost = Decimal(sub(r'[^\d.]', '', cost))
               
    # create a new work order
    new_work_order = WorkOrder(pothole_id=pothole_number,repair_crew_id=crew_number,hours=hours,
                              status=status,fillerAmount=filler,cost=cost)
    db.session.add(new_work_order)
    db.session.commit()
    
    equipmentResult = db.session.query(Equipment).filter(Equipment.equipment.in_(equipmentList))
    print(f'equipment = {equipmentResult}')
    
    for equipment in equipmentResult:
        db.session.add(Bridge(work_order_id = new_work_order.id,
                              equipment_id = equipment.id))
        
    db.session.commit()
    
    return redirect(url_for('auth.work_orders'))

@auth.route('/work_orders')
@login_required
def work_orders():
    
    equipConcat = func.group_concat(Equipment.equipment.distinct())
    
    workOrders = db.session.query(WorkOrder, Pothole, RepairCrew, Equipment, equipConcat).\
        join(Pothole, Pothole.id == WorkOrder.pothole_id).\
        join(RepairCrew, RepairCrew.id == WorkOrder.repair_crew_id).\
        join(Bridge, Bridge.work_order_id == WorkOrder.id).\
        join(Equipment, Equipment.id == Bridge.equipment_id).group_by(WorkOrder.id)
    
    return render_template('/auth/work_orders.html', workOrders=workOrders)


@auth.route('/update_pothole_info')
def update_pothole_info():
    pothole_number = request.args.get('pothole', type=str)
    pothole_number = pothole_number.split("#",1)[1]
    pothole_number = int(pothole_number[0])

    pothole = Pothole.query.get(pothole_number)
    
    streetNumber = pothole.streetNumber
    streetName = pothole.streetName
    zip = pothole.zip
    size = pothole.size
    district = pothole.district
    location = pothole.location
    priority = pothole.priority
    
    return jsonify(streetNumber = streetNumber, streetName = streetName, zip = zip,
                   size = size, district = district, location=location, priority = priority)
    
@auth.route('/calculate_cost')
def calculate_cost():
    
    # get form variables
    crew = request.args.get('crew', type=int)
    filler = request.args.get('filler', type=int)
    status = request.args.get('status', type=str)
    hours = request.args.get('hours', type=int)
    equipment = request.args.get('equipment')
    #split equipment on commas
    equipment = equipment.split(",")
    
    # return crew id
    crewResult = RepairCrew.query.get(crew)
    
    # get people in crew
    people = crewResult.people
    crewCost = crewResult.total
    
    #calculate cost
    cost = 0
    peopleCost = people * hours * 20
    fillerCost = filler * 12.50
    print(peopleCost)
    print(fillerCost)
    
    crewCost = f'{crewResult.people} crew members @ {crewResult.HRpay} / hr = ${crewResult.total}'
    hoursCost = f'${crewResult.total} x {hours} hours = ${crewResult.total * hours}'
    equipmentCost = f'${crewResult.total * hours}'
    
    equipmentResult = Equipment.query.filter(Equipment.equipment.in_(equipment))
    for row in equipment:
        print(row)
        
    runningTotal = crewResult.total * hours
    for row in equipmentResult:
        runningTotal += row.costPerHour * hours
        equipmentCost += f' + {row.equipment} @ (${row.costPerHour} x {hours} hours)'
        
    equipmentCost += f' = ${runningTotal}'
    
    fillerCost = f'${runningTotal} + ({filler} filler bag(s) @ 12.50 ea.) = '\
                f'${runningTotal + (filler * 12.50)}'
    
    cost=runningTotal + (filler * 12.50)
        
    cost = "${:,.2f}".format(cost)
    
    return jsonify(crewCost=crewCost, hoursCost=hoursCost, equipmentCost=equipmentCost,
                   fillerCost=fillerCost, cost=cost)

@auth.route('/damage')
def damage_post():
       
    potholes = Pothole.query.all()
    
    return render_template('auth/damage.html', potholes = potholes)

@auth.route('/damage', methods=['POST'])
def damage():
    pothole_number = request.form.get('potholes', type=int)
    name = request.form.get('name', type=str)
    address1 = request.form.get('address1', type=str)
    address2 = request.form.get('address2', type=str)
    city = request.form.get('city', type=str)
    state = request.form.get('state', type=str)
    zip = request.form.get('zip', type=str)
    phone = request.form.get('phone', type=str)
    dollar = request.form.get('dollar', type=str)
    damage = request.form.get('damage', type=str)
    dollar = Decimal(sub(r'[^\d.]', '', dollar))
    
    damageFile = Damage(pothole_id=pothole_number, name=name, address1=address1,
           address2 = address2, city=city, state=state, zip=zip,
           phone = phone, amount=dollar, damage=damage)
    
    db.session.add(damageFile)
    db.session.commit()
    
    return redirect(url_for('main.index'))

    
@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))