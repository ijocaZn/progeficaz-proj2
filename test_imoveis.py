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
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"},
        {"id": 2, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep": "93354", "tipo": "Casa", "valor": 500000.0, "data_aquisicao": "2023-02-20"},
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


@patch("utils.conectar_banco")
def test_listar_contato_id_200(mock_conectar_banco, client):
    """GET /imoveis - lista com dados."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"}

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"}
    

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (1,)
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_listar_contato_id_404(mock_conectar_banco, client):
    """GET /imoveis - lista com dados."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchone.return_value = None

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis/3")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Imóvel não encontrado"
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE id = %s", (3,),
    )
    mock_cursor.fetchone.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_criar_imovel_ok(mock_conectar_banco, client):
    """POST /imoveis - cria imovel com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simula ID gerado pelo banco
    mock_cursor.lastrowid = 10

    mock_conectar_banco.return_value = mock_conn

    payload = {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"}
    response = client.post("/imoveis", json=payload)

    assert response.status_code == 201
    assert response.get_json() == {"id": 10}

    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO imoveis (logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        ("Nicole Common", "Travessa", "Lake Danielle", "Judymouth", "85184", "casa em condominio", 488423.52, "2017-07-29"),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_criar_imovel_erro_validacao(mock_conectar_banco, client):
    """POST /imoveis - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.post("/imoveis", json={"cidade": "Judymouth"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()


@patch("utils.conectar_banco")
def test_atualizar_imovel_ok(mock_conectar_banco, client):
    """PUT /imoveis/<id> - atualiza com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    payload = {"logradouro": "Novo logradouro", "tipo_logradouro": "nova tipo", "bairro": "novo bairro", "cidade": "Nova Cidade", "cep": "00001", "tipo": "apartamento", "valor": 235531.1, "data_aquisicao": "2017-07-29"}
    response = client.put("/imoveis/1", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "imovel atualizado com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("Novo logradouro", "nova tipo", "novo bairro", "Nova Cidade", "00001", "apartamento", 235531.1, "2017-07-29", 1),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_atualizar_imovel_not_found(mock_conectar_banco, client):
    """PUT /imoveis/<id> - imóvel não encontrado (rowcount=0)."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    payload = {"logradouro": "Novo logradouro", "tipo_logradouro": "nova tipo", "bairro": "novo bairro", "cidade": "Nova Cidade", "cep": "00001", "tipo": "apartamento", "valor": 235531.1, "data_aquisicao": "2017-07-29"}
    response = client.put("/imoveis/999", json=payload)

    assert response.status_code == 404
    assert response.get_json() == {"erro": "imovel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "UPDATE imoveis SET logradouro = %s, tipo_logradouro = %s, bairro = %s, cidade = %s, cep = %s, tipo = %s, valor = %s, data_aquisicao = %s WHERE id = %s",
        ("Novo logradouro", "nova tipo", "novo bairro", "Nova Cidade", "00001", "apartamento", 235531.1, "2017-07-29", 999),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_atualizar_contato_erro_validacao(mock_conectar_banco, client):
    """PUT /imoveis/<id> - falta campo obrigatório -> 400. Não deve acessar o banco."""
    response = client.put("/imoveis/1", json={"logradouro": "Novo logradouro"})

    assert response.status_code == 400
    assert response.get_json() == {"erro": "Campos obrigatórios: logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao"}

    mock_conectar_banco.assert_not_called()

@patch("utils.conectar_banco")
def test_deletar_imovel_ok(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - deleta com sucesso."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 1
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/1")

    assert response.status_code == 200
    assert response.get_json() == {"mensagem": "imovel excluído com sucesso"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = %s",
        (1,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_deletar_imovel_not_found(mock_conectar_banco, client):
    """DELETE /imoveis/<id> - imovel não encontrado."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_cursor.rowcount = 0
    mock_conectar_banco.return_value = mock_conn

    response = client.delete("/imoveis/999")

    assert response.status_code == 404
    assert response.get_json() == {"erro": "imovel não encontrado"}

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM imoveis WHERE id = %s",
        (999,),
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()