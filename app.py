import os
from flask import Flask, render_template, request, redirect, url_for, Blueprint, g
from extensions import db
from models import Event, Participant

main = Blueprint('main', __name__)

def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///roaster.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    if test_config:
        app.config.update(test_config)
    
    db.init_app(app)
    app.register_blueprint(main)
    
    # Only create tables if not in testing mode (or handle manually)
    if not test_config:
        with app.app_context():
            db.create_all()
        
    return app



# Simple Security
USER_PASSWORD = "opendoor"
ADMIN_PASSWORD = "opendooradmin"
AUTH_COOKIE_NAME = "roaster_auth"

@main.before_request
def require_login():
    if request.endpoint == 'static':
        return
    if request.endpoint == 'main.login':
        return
    
    auth_cookie = request.cookies.get(AUTH_COOKIE_NAME)
    
    # Check if logged in with either password
    if auth_cookie not in [USER_PASSWORD, ADMIN_PASSWORD]:
        return redirect(url_for('main.login'))

    # Set admin status in global context for templates
    g.is_admin = (auth_cookie == ADMIN_PASSWORD)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password in [USER_PASSWORD, ADMIN_PASSWORD]:
            response = redirect(url_for('main.index'))
            # Expire in 6 hours
            response.set_cookie(AUTH_COOKIE_NAME, password, max_age=6*60*60)
            return response
        else:
            return render_template('login.html', error="Invalid password")
    return render_template('login.html')

@main.route('/')
def index():
    events = Event.query.order_by(Event.created_at.desc()).all()
    return render_template('index.html', events=events)

@main.route('/event/create', methods=['POST'])
def create_event():
    if not g.is_admin:
        return "Unauthorized", 403
    name = request.form.get('name')
    if name:
        event = Event(name=name)
        db.session.add(event)
        db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/event/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    if not g.is_admin:
        return "Unauthorized", 403
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return ""  # HTTP 200 OK, empty content ensures row is removed from DOM

@main.route('/event/<int:event_id>')
def event_dashboard(event_id):
    event = Event.query.get_or_404(event_id)
    pool = [p for p in event.participants if p.status == 'pool']
    roster = [p for p in event.participants if p.status == 'roster']
    
    # Group by team_id
    teams = {}
    for p in roster:
        if p.team_id:
            if p.team_id not in teams:
                teams[p.team_id] = []
            teams[p.team_id].append(p)
            
    # Sort teams by team_id
    sorted_teams = dict(sorted(teams.items()))
    
    return render_template('event.html', event=event, pool=pool, roster=roster, teams=sorted_teams)

@main.route('/event/<int:event_id>/register', methods=['POST'])
def register_participant(event_id):
    event = Event.query.get_or_404(event_id)
    name = request.form.get('name')
    if name:
        p = Participant(event_id=event.id, name=name, status='pool')
        db.session.add(p)
        db.session.commit()
    return redirect(url_for('main.event_dashboard', event_id=event.id))

@main.route('/participant/<int:participant_id>/move', methods=['POST'])
def move_participant(participant_id):
    p = Participant.query.get_or_404(participant_id)
    if p.status == 'pool':
        p.status = 'roster'
    else:
        p.status = 'pool'
        p.team_id = None # Reset team if moved back to pool
    db.session.commit()
    # For simplicity, refreshing the whole page or part of it? 
    # HTMX can swap specific parts, but determining which list to remove from and add to is tricky with simple swaps.
    # Easiest is to redirect back to dashboard which will re-render everything.
    # Or use hx-target="body" to refresh page via AJAX (smoothish).
    return redirect(url_for('main.event_dashboard', event_id=p.event_id))

@main.route('/verify-admin', methods=['POST'])
def verify_admin():
    password = request.form.get('admin_password')
    event_id = request.form.get('event_id')
    
    if password == ADMIN_PASSWORD:
        # Success:
        # 1. Update the Shuffle Button (OOB Swap)
        # 2. Close the modal (Script)
        
        # New Enabled Shuffle Form
        new_shuffle_form = f'''
        <form id="shuffle-form" action="{url_for('main.shuffle_teams', event_id=event_id)}" method="POST" hx-swap-oob="true">
            <input type="hidden" name="admin_token" value="{ADMIN_PASSWORD}">
            <input type="submit" value="Shuffle Teams">
        </form>
        '''
        
        # Script to close modal
        close_script = '<script>document.getElementById("admin-dialog").close();</script>'
        
        return new_shuffle_form + close_script
    else:
        # Failure: return error message to the target (the error div)
        return '<div id="admin-error" style="color: red; margin-bottom: 1rem;">Invalid Password</div>'

@main.route('/event/<int:event_id>/shuffle', methods=['POST'])
def shuffle_teams(event_id):
    # Check Admin Access
    admin_token = request.form.get('admin_token')
    
    if not g.is_admin and admin_token != ADMIN_PASSWORD:
        return "Unauthorized", 403

    import random
    event = Event.query.get_or_404(event_id)
    roster = [p for p in event.participants if p.status == 'roster']
    
    # Shuffle logic (simple pairs)
    random.shuffle(roster)
    num_teams = len(roster) // 2
    
    for i in range(num_teams):
        team_id = i + 1
        roster[2*i].team_id = team_id
        roster[2*i+1].team_id = team_id
        
    db.session.commit()
    return redirect(url_for('main.event_dashboard', event_id=event.id))


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
