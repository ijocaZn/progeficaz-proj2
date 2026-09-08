import pytest
from unittest.mock import patch, MagicMock
from servidor import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("utils.conectar_banco")
def test_banco_vazio(mock_conectar_banco, client):
    """GET /imoveis - lista vazia."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == []

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("utils.conectar_banco")
def test_listar_contatos_com_dados(mock_conectar_banco, client):
    """GET /imoveis - lista com dados."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        (1, "Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
        (2, "Price Prairie", "Travessa", "Colonton", "North Garyville", "93354", "Casa", 500000.0, "2023-02-20"),
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis")

    assert response.status_code == 200
    assert response.get_json() == [
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth","cep": "85184","tipo": "casa em condominio","valor": 488423.52,"data_aquisicao": "2017-07-29"},
        {"id": 2, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville","cep": "93354","tipo": "Casa","valor": 500000.0,"data_aquisicao": "2023-02-20"},
    ]

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis"
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()