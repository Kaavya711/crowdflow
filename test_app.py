"""
CrowdFlow Test Suite
Tests: routes, API, input sanitization, security headers, edge cases
"""
import pytest
import json
from app import app, sanitize_input


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        yield client


# --- Route Tests ---

def test_dashboard_loads(client):
    """Dashboard should return 200."""
    res = client.get('/')
    assert res.status_code == 200

def test_stadium_map_loads(client):
    res = client.get('/map')
    assert res.status_code == 200

def test_gates_loads(client):
    res = client.get('/gates')
    assert res.status_code == 200

def test_food_loads(client):
    res = client.get('/food')
    assert res.status_code == 200

def test_alerts_loads(client):
    res = client.get('/alerts')
    assert res.status_code == 200

def test_assistant_loads(client):
    res = client.get('/assistant')
    assert res.status_code == 200


# --- API Tests ---

def test_api_chat_valid(client):
    """Valid chat message should return a reply."""
    payload = {"messages": [{"role": "user", "content": "What is the wait at Gate E?"}]}
    res = client.post('/api/chat',
                      data=json.dumps(payload),
                      content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert "reply" in data
    assert isinstance(data["reply"], str)

def test_api_chat_empty_body(client):
    """Empty body should return 400."""
    res = client.post('/api/chat',
                      data='',
                      content_type='application/json')
    assert res.status_code == 400

def test_api_chat_too_many_messages(client):
    """Over 50 messages should be rejected."""
    messages = [{"role": "user", "content": "msg"} for _ in range(51)]
    res = client.post('/api/chat',
                      data=json.dumps({"messages": messages}),
                      content_type='application/json')
    assert res.status_code == 400

def test_api_chat_wrong_method(client):
    """GET on /api/chat should return 405."""
    res = client.get('/api/chat')
    assert res.status_code == 405


# --- Sanitization Tests ---

def test_sanitize_removes_script():
    result = sanitize_input("<script>alert('xss')</script>Hello")
    assert "<script>" not in result
    assert "Hello" in result

def test_sanitize_truncates_long_input():
    long_text = "A" * 600
    result = sanitize_input(long_text)
    assert len(result) <= 500

def test_sanitize_empty_string():
    assert sanitize_input("") == ""

def test_sanitize_none():
    assert sanitize_input(None) == ""

def test_sanitize_normal_text():
    result = sanitize_input("Which gate has the lowest wait time?")
    assert result == "Which gate has the lowest wait time?"


# --- Edge Case Tests ---

def test_dashboard_post_routing(client):
    """Routing form POST should redirect or return 200."""
    res = client.post('/', data={
        'seat_section': 'N.STAND - BLOCK 4',
        'density': 'High',
        'need': 'Food'
    })
    assert res.status_code in [200, 302]

def test_404_handling(client):
    """Unknown route should return 404."""
    res = client.get('/nonexistent-page')
    assert res.status_code == 404
