import pytest
from application.app import app  # importera din Flask-app

@pytest.fixture # skapa en testklient för Flask-appen
def client():
    app.config["TESTING"] = True # Aktivera testläge
    with app.test_client() as client: # Skapa en testklient
        yield client # Ge testklienten till testfunktionerna

def test_index_loads(client):
    """Startsidan ska ladda korrekt"""
    response = client.get("/")
    assert response.status_code == 200 # Kontrollera att svaret är 200 OK
    assert b"Dagens elpriser" in response.data # Kontrollera att texten finns på sidan

def test_priser_sets_cookies(client):
    """En sökning ska sätta cookies"""
    response = client.post("/priser", data={
        "year": "2025",
        "month": "10",
        "day": "01",
        "area": "SE3"
    })
    assert response.status_code == 200 # Kontrollera att svaret är 200 OK

    # hämta alla Set-Cookie headers
    cookies = response.headers.getlist("Set-Cookie") # Hämta alla Set-Cookie headers
    all_cookies = " ".join(cookies) # Kombinera dem till en sträng för enklare sökning

    assert "last_year" in all_cookies
    assert "last_month" in all_cookies
    assert "last_day" in all_cookies
    assert "last_area" in all_cookies


def test_priser_cookie_values_used(client):
    """Cookies ska kunna läsas på startsidan"""
    # först gör en sökning som sätter cookies
    client.post("/priser", data={
        "year": "2025",
        "month": "10",
        "day": "01",
        "area": "SE2"
    })
    # sedan gå till startsidan
    response = client.get("/")
    assert response.status_code == 200
    # kontrollera att area från cookie används i HTML
    assert b"SE2" in response.data

def test_404_response(client):
    """Testar 404 felhantering"""
    response = client.get("/abc")  # en icke-existerande sida
    assert response.status_code == 404 # Kontrollera att svaret är 404 Not Found
