import pytest
from app import create_app, db, Event, Participant

@pytest.fixture
def client():
    # Create a fresh app instance for this test
    app = create_app({
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'TESTING': True
    })
    
    with app.test_client() as client:
        # Authenticate as ADMIN by default for full flow
        client.set_cookie('roaster_auth', 'opendooradmin')
        
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_full_flow(client):
    # 1. Create Event
    response = client.post('/event/create', data=dict(name="Tennis 101"), follow_redirects=True)
    assert response.status_code == 200
    assert b'Tennis 101' in response.data

    with client.application.app_context():
        event = Event.query.first()
        assert event is not None
        event_id = event.id

    # 2. Register Participants
    participants = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
    for name in participants:
        client.post(f'/event/{event_id}/register', data=dict(name=name), follow_redirects=True)

    with client.application.app_context():
        count = Participant.query.filter_by(event_id=event_id).count()
        assert count == 5

    # 3. Move to Roster (Alice, Bob, Charlie, Dave)
    with client.application.app_context():
        ps = Participant.query.filter_by(event_id=event_id).all()
        p_map = {p.name: p.id for p in ps}
    
    for name in ['Alice', 'Bob', 'Charlie', 'Dave']:
        pid = p_map[name]
        client.post(f'/participant/{pid}/move', follow_redirects=True)

    with client.application.app_context():
        roster_count = Participant.query.filter_by(event_id=event_id, status='roster').count()
        assert roster_count == 4

    # 4. Shuffle (Form Teams)
    response = client.post(f'/event/{event_id}/shuffle', follow_redirects=True)
    assert b'Team Assignments' in response.data

    with client.application.app_context():
        # Verify teams
        roster = Participant.query.filter_by(event_id=event_id, status='roster').all()
        teams = [p.team_id for p in roster if p.team_id]
        assert len(teams) == 4

def test_permissions(client):
    # Logout/Reset to User
    client.set_cookie('roaster_auth', 'opendoor')
    
    # Try Create Event as User -> Should Fail (403)
    response = client.post('/event/create', data=dict(name="Restricted Event"), follow_redirects=True)
    assert response.status_code == 403

    # Switch to Admin to Create Event
    client.set_cookie('roaster_auth', 'opendooradmin')
    client.post('/event/create', data=dict(name="Restricted Event"), follow_redirects=True)
    
    # Switch back to User
    client.set_cookie('roaster_auth', 'opendoor')

    with client.application.app_context():
        event = Event.query.first()
        event_id = event.id
        # Add 2 participants to roster
        p1 = Participant(event_id=event_id, name="P1", status='roster')
        p2 = Participant(event_id=event_id, name="P2", status='roster')
        db.session.add_all([p1, p2])
        db.session.commit()

    # Try Shuffle as User -> Should Fail (403)
    response = client.post(f'/event/{event_id}/shuffle')
    assert response.status_code == 403

    # Unlock with Password
    response = client.post('/verify-admin', data=dict(admin_password='opendooradmin', event_id=event_id))
    assert b'admin_token' in response.data
    assert b'value="opendooradmin"' in response.data

    # Try Shuffle with Token
    response = client.post(f'/event/{event_id}/shuffle', data=dict(admin_token='opendooradmin'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Team Assignments' in response.data

    # Test Delete Permissions
    # User cannot delete
    client.set_cookie('roaster_auth', 'opendoor')
    response = client.delete(f'/event/{event_id}')
    assert response.status_code == 403

    # Admin can delete
    client.set_cookie('roaster_auth', 'opendooradmin')
    response = client.delete(f'/event/{event_id}')
    assert response.status_code == 200
    
    with client.application.app_context():
        assert Event.query.get(event_id) is None
