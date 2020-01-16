# Wilson-Monitoring-Web-Application
Web app to monitor overall system health for each house. Provides information about sd card usage, system status, battery level, device connectivity and last process event time for each sensor. 

![wilsonMonitor](https://user-images.githubusercontent.com/20258893/72489921-a5fac380-37e3-11ea-9316-ddeb1cb290d8.gif)

## Installation / Preparation
`git clone https://github.com/CreateHealth/Wilson-Monitoring-Web-Application.git` <br>
Request `connect.py` and `credentials.py` files from admin. For local deployment, use `localConnect.py` <br>
Create a virtual environment and install the necessary libraries:
```
cd Wilson-Monitoring-Web-Application
python3 -m venvy myvenvy
source myvenv/bin/activate
pip install -r requirements.txt
```
Generate a SECRET_KEY for the app: <br>
```
import secrets
secrets.token_urlsafe(16)
```
Paste the output into `app.config['SECRET_KEY'] = output` under `app.py`

### User Authentication 
Seperate database (SQLite) is being used to handle user authentication. Follow the steps to add a user:
```
python3
```
```
from app import dbLite, create_app
app = create_app()
app.app_context().push()
from models import User
from werkzeug.security import generate_password_hash
newuser = User(username="username",password=generate_password_hash("password"))
dbLite.session.add(newuser)
dbLite.session.commit()
```
### Run It Locally
Make sure virtualenv is activated. If not, `source myvenv/bin/activate`. <br>
```
export FLASK_APP=app.py
export FLASK_DEBUG=1 (do not use it for production!)
flask run
```
