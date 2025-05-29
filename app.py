from flask import Flask, render_template, redirect, url_for, request, flash
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate
from flask import current_app
from itsdangerous import URLSafeTimedSerializer as Serializer
from dotenv import load_dotenv
import random
import string
import os

app = Flask(__name__)

load_dotenv(dotenv_path.os.path.join(os.path.dirname)(__file__), 'LicensePlateGame.env'))  # Load environment variables from .env file

# Make sure to configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")    
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")  # Use a secure secret key from environment variables

mail = Mail(app)

# Configure the database URI and the secret key for sessions
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///license_plate_game.db'
app.secret_key = 'your_secret_key_here'  # Change this to a secure secret key
db = SQLAlchemy(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'    # This will redirect to login if the user isn't autheticated
login_manager.login_message = "You must be logged in to access this page."  # Custom login message
login_manager.init_app(app)

# Define the User model for user authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    reset_token = db.Column(db.String(100), nullable=True)  # Added for password reset token

    def get_reset_token(self, expires_sec=1800):
        """
        Generates a password reset token that expires after a given time period (default 30 minutes).
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        """
        Verifies the password reset token and returns the associated user.
        If the token is invalid or expired, returns None.
        """
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception as e:
            return None  # Token is invalid or expired
        user = User.query.get(data['user_id'])
        return user


# Define the StateProvince model for tracking US states, Canadian provinces, and Mexican states
class StateProvince(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100), nullable=False)  # 'US', 'Canada', 'Mexico'
    name = db.Column(db.String(100), nullable=False)  # State or province name
    category = db.Column(db.String(50), nullable=False)  # 'US', 'Canada', or 'Mexico'

# Define the UserTracking model to track the states/provinces a user has seen
class UserTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    state_province_id = db.Column(db.Integer, db.ForeignKey('state_province.id'))
    user = db.relationship('User', back_populates='tracked_states')
    state_province = db.relationship('StateProvince', back_populates='users')

User.tracked_states = db.relationship('UserTracking', back_populates='user')
StateProvince.users = db.relationship('UserTracking', back_populates='state_province')

# Function to create the database tables within the app context
def create_db():
    with app.app_context():
        db.create_all()

# Initialize the database and create tables
create_db()


# initialize the migration manager
migrate = Migrate(app, db)



# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('user_page'))  # Redirect to user page if already logged in

    # Process the form submission
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = 'remember' in request.form  # For a "Remember Me" checkbox

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            if user.is_approved:   # Check if the user is approved
                login_user(user, remember=remember)
                flash("Login successful!", "success")
                next_page = request.args.get('next')  # Get the 'next' parameter from the URL
                if next_page:
                    return redirect(next_page)  # Redirect to next page if available
                else:
                    return redirect(url_for('user_page'))   # Redirect to user page if no next_url
            else:
                flash("Your account is not approved yet.  Please wait for approval.", "danger")
                return redirect(url_for('login'))  # Redirect back to login page
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
            return redirect(url_for('login'))  # Redirect back to login page

    # render the login page for non-authenticated users
    return render_template('login.html', title='Login')



# Route for user registration (signup)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        print(f"Received signup request for username: {username}, email: {email}")  # Debugging

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match. Please try again.')
            return redirect(url_for('signup'))

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email address already registered. Please use a different email.')
            return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user with 'is_approved' set to False
        new_user = User(username=username, email=email, password=hashed_password, is_approved=False)
        
        print("Attempting to add user to database...")  # Debugging
        try:
            db.session.add(new_user)
            db.session.commit()
            print("New user added to the database.")  # Debugging
        except Exception as e:
            flash(f'Error creating user: {str(e)}')
            print(f"Error adding user: {str(e)}")  # Debugging
            return redirect(url_for('signup'))

        # Send email to mreetz@gmail.com to notify about the new user
        approval_link = url_for('approve_user', user_id=new_user.id, _external=True)
        msg = Message('New User Sign-Up Awaiting Approval', recipients=['mreetz@gmail.com'])
        msg.body = f'A new user has signed up and is awaiting approval.\n\n' \
                   f'Username: {new_user.username}\n' \
                   f'Email: {new_user.email}\n\n' \
                   f'Click the link to approve or disapprove the user:\n{approval_link}'

        try:
            mail.send(msg)
            print("Approval email sent to mreetz@gmail.com.")  # Debugging
            flash('Your account has been created and is awaiting approval. The admin will approve it shortly.')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error sending approval email: {str(e)}')
            print(f"Error sending approval email: {str(e)}")  # Debugging
            return redirect(url_for('signup'))

    return render_template('signup.html')



# Route for user page (requires login)
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_page():
    # Query all states, provinces, and regions
    us_states = StateProvince.query.filter_by(category='US').all()
    canadian_provinces = StateProvince.query.filter_by(category='Canada').all()
    mexican_states = StateProvince.query.filter_by(category='Mexico').all()

    # Get the list of states the user has tracked
    user_states = [state.state_province_id for state in current_user.tracked_states]

    # Handle form submission (saving the user's selections)
    if request.method == 'POST':
        # Get the selected states, provinces, and regions from the form
        selected_us_states = request.form.getlist('us_states')
        selected_canadian_provinces = request.form.getlist('canadian_provinces')
        selected_mexican_states = request.form.getlist('mexican_states')

        # Convert selected plates to integer lists
        selected_states = set(
            map(int, selected_us_states + selected_canadian_provinces + selected_mexican_states)
        )

        # Remove unchecked plates
        current_user_states_ids = set(user_states)
        states_to_remove = current_user_states_ids - selected_states

        # Remove states no longer selected
        for state_id in states_to_remove:
            user_tracking = UserTracking.query.filter_by(user_id=current_user.id, state_province_id=state_id).first()
            if user_tracking:
                db.session.delete(user_tracking)

        # Add newly selected states
        for state_id in selected_states:
            if state_id not in current_user_states_ids:
                state = StateProvince.query.get(state_id)
                user_tracking = UserTracking(user_id=current_user.id, state_province=state)
                db.session.add(user_tracking)

        db.session.commit()
        flash('Your updates have been saved to the database')

        # Re-fetch the user's updated tracked states after saving
        user_states = [state.state_province_id for state in current_user.tracked_states]

    return render_template('user_page.html', 
                           us_states=us_states, 
                           canadian_provinces=canadian_provinces, 
                           mexican_states=mexican_states,
                           user_states=user_states)


# Route for logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# Route for leaderboard (only US states)
@app.route('/leaderboard')
def leaderboard():
    # Query for US plates leaderboard
    us_leaderboard = db.session.query(User, db.func.count(UserTracking.id).label('plate_count'))\
                               .join(UserTracking, User.id == UserTracking.user_id)\
                               .join(StateProvince, StateProvince.id == UserTracking.state_province_id)\
                               .filter(StateProvince.category == 'US')\
                               .group_by(User.id)\
                               .order_by(db.desc('plate_count'))\
                               .all()

    # Query for Canadian plates leaderboard
    canada_leaderboard = db.session.query(User, db.func.count(UserTracking.id).label('plate_count'))\
                                   .join(UserTracking, User.id == UserTracking.user_id)\
                                   .join(StateProvince, StateProvince.id == UserTracking.state_province_id)\
                                   .filter(StateProvince.category == 'Canada')\
                                   .group_by(User.id)\
                                   .order_by(db.desc('plate_count'))\
                                   .all()

    # Query for Mexican plates leaderboard
    mexico_leaderboard = db.session.query(User, db.func.count(UserTracking.id).label('plate_count'))\
                                   .join(UserTracking, User.id == UserTracking.user_id)\
                                   .join(StateProvince, StateProvince.id == UserTracking.state_province_id)\
                                   .filter(StateProvince.category == 'Mexico')\
                                   .group_by(User.id)\
                                   .order_by(db.desc('plate_count'))\
                                   .all()

    return render_template('leaderboard.html', 
                           us_leaderboard=us_leaderboard, 
                           canada_leaderboard=canada_leaderboard, 
                           mexico_leaderboard=mexico_leaderboard)

# Route for forgot password
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username_or_email = request.form['username_or_email']
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user:
            # Generate a reset token (for example, use a random string or a cryptographic token)
            token = ''.join(random.choices(string.ascii_letters + string.digits, k=20))

            # Save the token to the user's record in the database (you can store it in a separate table for better security)
            user.reset_token = token
            db.session.commit()

            # Generate the reset URL using `url_for` to build the link
            reset_url = url_for('reset_password', token=token, _external=True)  # _external=True to generate absolute URL

            # Send the reset link to the user's email
            msg = Message('Password Reset Request', recipients=[user.email])
            msg.body = f'Click the link below to reset your password:\n{reset_url}'
            try:
                mail.send(msg)
                flash('An email has been sent with instructions to reset your password.')
                return redirect(url_for('login'))
            except Exception as e:
                flash(f'Error sending email: {str(e)}')
                return redirect(url_for('forgot_password'))

        else:
            flash('No user found with that username or email address.')

    return render_template('forgot_password.html')


# Route to enable a reset of a user's password
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    #user = db.session.get(User, token)  # Loop up user by token

    
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash('Invalid or expired token.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed_password = generate_password_hash(new_password)

        user.password = hashed_password
        user.reset_token = None  # Clear the token after resetting the password
        db.session.commit()

        flash('Your password has been updated.')
        return redirect(url_for('login'))

    return render_template('reset_password.html')

# Route for user feedback
from flask_mail import Message

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def feedback():
    if request.method == 'POST':
        title = request.form['title']
        comment = request.form['comment']

        # Send feedback email to mreetz@gmail.com
        msg = Message('LicensePlate Game feedback', recipients=['mreetz@gmail.com'])
        msg.body = f"Title: {title}\n\nComment:\n{comment}"
        try:
            mail.send(msg)
            flash('Your feedback has been sent!')
            return redirect(url_for('user_page'))  # Redirect back to user page after sending feedback
        except Exception as e:
            flash(f'Error sending feedback email: {str(e)}')

    return render_template('feedback.html')  # Render a simple feedback page for the form


# Route for administration of the data
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    # Ensure only admin can access this page (you can use a role-based check)
    if not current_user.is_admin:
        return redirect(url_for('home'))

    users = User.query.all()  # Get all users
    return render_template('admin.html', users=users)


# Route for admin of the States and Provinces
@app.route('/admin/states', methods=['GET', 'POST'])
@login_required
def manage_states():
    if not current_user.is_admin:
        return redirect(url_for('home'))

    states = StateProvince.query.all()

    if request.method == 'POST':
        action = request.form['action']
        state_id = request.form['state_id']

        if action == 'delete':
            state = StateProvince.query.get(state_id)
            db.session.delete(state)
            db.session.commit()
        elif action == 'update':
            state_name = request.form['state_name']
            state = StateProvince.query.get(state_id)
            state.name = state_name
            db.session.commit()

    return render_template('manage_states.html', states=states)


# Route to easily approve a new user by an Admin
@app.route('/approve_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def approve_user(user_id):
    print("user is not logged in, redirecting to login....")
    if not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))  # redirect to login, save the current URL

    # Ensure the user is an admin
    if not current_user.is_admin:
        flash('You are not authorized to access this page.')
        return redirect(url_for('home'))

    user = User.query.get(user_id)
    if user:
        if request.method == 'POST':
            # If the form is submitted (approve or disapprove)
            action = request.form['action']
            if action == 'approve':
                user.is_approved = True
            elif action == 'disapprove':
                user.is_approved = False

            db.session.commit()
            flash(f'User {user.username} has been {action}d.')
            return redirect(url_for('admin'))  # Redirect to the admin panel after the action

        # If it's a GET request, simply display the user info
        return render_template('approve_user.html', user=user)

    flash('User not found.')
    return redirect(url_for('admin'))  # Redirect to the admin panel if the user doesn't exist


# Route to test if sending email is working
@app.route('/send_test_email')
def send_test_email():
    msg = Message('Test Subject', recipients=['mreetz@gmail.com'])
    msg.body = 'This is a test email sent from Flask-Mail!'
    try:
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Error sending email: {str(e)}'


# Populate the database with US states, Canadian provinces, and Mexican states
def populate_data():
    us_states = [
        "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", 
        "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", 
        "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", 
        "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico", 
        "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", 
        "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", 
        "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "Washington D.C."
    ]

    canadian_provinces = [
        "Alberta", "British Columbia", "Manitoba", "New Brunswick", "Newfoundland and Labrador", 
        "Nova Scotia", "Ontario", "Prince Edward Island", "Quebec", "Saskatchewan"
    ]

    mexican_states = [
        "Aguascalientes", "Baja California", "Baja California Sur", "Campeche", "Chiapas", "Chihuahua", 
        "Coahuila", "Colima", "Durango", "Guanajuato", "Guerrero", "Hidalgo", "Jalisco", "Mexico City", 
        "Mexico State", "Michoacán", "Morelos", "Nayarit", "Nuevo León", "Oaxaca", "Puebla", "Querétaro", 
        "Quintana Roo", "San Luis Potosi", "Sinaloa", "Sonora", "Tabasco", "Tamaulipas", "Tlaxcala", 
        "Veracruz", "Yucatan", "Zacatecas"
    ]

    # Insert US States
    for state in us_states:
        db.session.add(StateProvince(country="US", name=state, category="US"))

    # Insert Canadian Provinces
    for province in canadian_provinces:
        db.session.add(StateProvince(country="Canada", name=province, category="Canada"))

    # Insert Mexican States
    for state in mexican_states:
        db.session.add(StateProvince(country="Mexico", name=state, category="Mexico"))

    db.session.commit()

# Uncomment this line to populate data when needed
# populate_data()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

