def test_home_page_opens(client):
    response = client.get("/")

    assert response.status_code == 200


def test_home_page_shows_welcome(client):
    response = client.get("/")

    page = response.get_data(as_text=True)
    assert "Καλώς ήρθατε" in page