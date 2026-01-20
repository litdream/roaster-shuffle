import pytest
from app import app, db, Event, Participant

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()

def test_full_flow(client):
    # 1. Create Event
    response = client.post('/event/create', data=dict(name="Tennis 101"), follow_redirects=True)
    assert response.status_code == 200
    assert b'Tennis 101' in response.data
    
    with app.app_context():
        event = Event.query.first()
        assert event is not None
        event_id = event.id

    # 2. Register Participants
    participants = ['Alice', 'Bob', 'Charlie', 'Dave', 'Eve']
    for name in participants:
        client.post(f'/event/{event_id}/register', data=dict(name=name), follow_redirects=True)

    with app.app_context():
        count = Participant.query.filter_by(event_id=event_id).count()
        assert count == 5

    # 3. Move to Roster (Alice, Bob, Charlie, Dave)
    with app.app_context():
        ps = Participant.query.filter_by(event_id=event_id).all()
        p_map = {p.name: p.id for p in ps}
    
    for name in ['Alice', 'Bob', 'Charlie', 'Dave']:
        pid = p_map[name]
        client.post(f'/participant/{pid}/move', follow_redirects=True)

    with app.app_context():
        roster_count = Participant.query.filter_by(event_id=event_id, status='roster').count()
        assert roster_count == 4

    # 4. Shuffle (Form Teams)
    client.post(f'/event/{event_id}/shuffle', follow_redirects=True)

    with app.app_context():
        # Verify teams
        roster = Participant.query.filter_by(event_id=event_id, status='roster').all()
        teams = [p.team_id for p in roster if p.team_id]
        assert len(teams) == 4, "All roster members should have a team"
        assert teams.count(1) == 2, "Team 1 should have 2 members"
        assert teams.count(2) == 2, "Team 2 should have 2 members"

    # 5. Move back to Pool (Alice)
    alice_id = p_map['Alice']
    client.post(f'/participant/{alice_id}/move', follow_redirects=True)

    with app.app_context():
        p = Participant.query.get(alice_id)
        assert p.status == 'pool'
        assert p.team_id is None, "Team ID should be cleared when moving back to pool"
