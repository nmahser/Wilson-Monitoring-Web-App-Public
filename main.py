import func
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('login.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.name)


@main.route('/overallstatus')
@login_required
def overall_status():
    #Query for filtering battery, energy, system status and disk usage aliases
    filter = """select sensor_metadata.location_id, sensor_metadata.id, sensor_metadata.devid, sensor_metadata.model, sensor_metadata.install_room, sensor_metadata.alias, sensor_metadata.current_status, 
                sensor_metadata.last_processed_event_time, current_value.value, current_value.event_time
                from sensor_metadata
                left join current_value
                on sensor_metadata.id = current_value.sensor_id
                where sensor_metadata.current_status = "Installed" and location_id IN (Select id from location where is_active=1) 
                AND (alias LIKE "%Battery%" OR alias LIKE "%Energy%" OR alias LIKE "%DISK%" OR alias LIKE "%sYSTEM%")
                order by location_id desc, devid desc, event_time desc"""

    #Data wranling for overallStatus page
    overallStatusFinal = func.overallStatusParser(filter)

    return render_template('overallStatus.html', overallStatusFinal=overallStatusFinal)

@main.route('/housestatus', methods=['POST'])
@login_required
def house_status():

    filter = """select sensor_metadata.location_id, sensor_metadata.id, sensor_metadata.devid, sensor_metadata.model, sensor_metadata.install_room, sensor_metadata.alias, sensor_metadata.current_status, 
                sensor_metadata.last_processed_event_time, current_value.value, current_value.event_time
                from sensor_metadata
                left join current_value
                on sensor_metadata.id = current_value.sensor_id
                where sensor_metadata.current_status = "Installed" and location_id IN (Select id from location where is_active=1) 
                AND (alias LIKE "%Battery%" OR alias LIKE "%Energy%" OR alias LIKE "%DISK%" OR alias LIKE "%sYSTEM%")
                order by location_id desc, devid desc, event_time desc"""

    #Data wranling for houseStatus page
    houseStatus = func.houseStatusParser(filter)


    if request.method == 'POST':
        locationId = request.form['houseNumber']    

    locationTable = [element for element in houseStatus if element['location_id'] == int(locationId)]

    return render_template('houseStatus.html', locationId=locationId, locationTable=locationTable, houseStatus=houseStatus)

