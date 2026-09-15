import pytest
from unittest.mock import patch, MagicMock
from servidor import app


@pytest.fixture
def client():
    """Cria um cliente de teste para a API."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def assert_links_do_imovel(imovel, imovel_id):
    assert imovel["_links"]["self"] == {"href": f"/imoveis/{imovel_id}", "method": "GET"}
    assert imovel["_links"]["update"] == {"href": f"/imoveis/{imovel_id}", "method": "PUT"}
    assert imovel["_links"]["delete"] == {"href": f"/imoveis/{imovel_id}", "method": "DELETE"}

def dados_sem_links(imoveis):
    return [{chave: valor for chave, valor in imovel.items() if chave != "_links"} for imovel in imoveis]

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
    assert response.get_json()["items"] == []
    assert response.get_json()["_links"]["create"] == {"href": "/imoveis", "method": "POST"}

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
    body = response.get_json()
    assert dados_sem_links(body["items"]) == [
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth","cep": "85184","tipo": "casa em condominio","valor": 488423.52,"data_aquisicao": "2017-07-29"},
        {"id": 2, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville","cep": "93354","tipo": "Casa","valor": 500000.0,"data_aquisicao": "2023-02-20"},
    ]
    assert_links_do_imovel(body["items"][0], 1)
    assert_links_do_imovel(body["items"][1], 2)

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
    body = response.get_json()
    assert {chave: valor for chave, valor in body.items() if chave != "_links"} == {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"}
    assert_links_do_imovel(body, 1)
    assert body["_links"]["collection"] == {"href": "/imoveis", "method": "GET"}
    

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
    assert response.get_json() == {
        "id": 10,
        "_links": {
            "self": {"href": "/imoveis/10", "method": "GET"},
            "collection": {"href": "/imoveis", "method": "GET"},
        },
    }

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
    assert response.get_json() == {
        "mensagem": "imovel atualizado com sucesso",
        "_links": {
            "self": {"href": "/imoveis/1", "method": "GET"},
            "update": {"href": "/imoveis/1", "method": "PUT"},
            "delete": {"href": "/imoveis/1", "method": "DELETE"},
        },
    }

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
    assert response.get_json() == {
        "mensagem": "imovel excluído com sucesso",
        "_links": {
            "collection": {"href": "/imoveis", "method": "GET"},
        },
    }

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


@patch("utils.conectar_banco")
def test_listar_imovel_tipo_200(mock_conectar_banco, client):
    """GET /imoveis?tipo=<tipo> - tipo existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"},
        {"id": 3, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep": "34567", "tipo": "casa em condominio", "valor": 600000.0, "data_aquisicao": "2022-05-21"},
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis?tipo=casa em condominio")

    assert response.status_code == 200
    body = response.get_json()
    assert dados_sem_links(body["items"]) == [
            {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Judymouth","cep": "85184","tipo": "casa em condominio","valor": 488423.52,"data_aquisicao": "2017-07-29"},
            {"id": 3, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "North Garyville", "cep": "34567", "tipo": "casa em condominio", "valor": 600000.0, "data_aquisicao": "2022-05-21"},
        ]
    assert body["_links"]["create"] == {"href": "/imoveis", "method": "POST"}
    
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s", ("casa em condominio",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_listar_imovel_tipo_404(mock_conectar_banco, client):
    """GET /imoveis?tipo=<tipo> - tipo nao existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis?tipo=mansao")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Tipo não encontrado"
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE tipo = %s", ("mansao",),
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_listar_imovel_cidade_200(mock_conectar_banco, client):
    """GET /imoveis?cidade=<cidade> - cidade existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [
        {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Goiania", "cep": "85184", "tipo": "casa em condominio", "valor": 488423.52, "data_aquisicao": "2017-07-29"},
        {"id": 3, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "Goiania", "cep": "34567", "tipo": "Apartamento", "valor": 600000.0, "data_aquisicao": "2022-05-21"},
    ]

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis?cidade=Goiania")

    assert response.status_code == 200
    body = response.get_json()
    assert dados_sem_links(body["items"]) == [
            {"id": 1, "logradouro": "Nicole Common", "tipo_logradouro": "Travessa", "bairro": "Lake Danielle", "cidade": "Goiania","cep": "85184","tipo": "casa em condominio","valor": 488423.52,"data_aquisicao": "2017-07-29"},
            {"id": 3, "logradouro": "Price Prairie", "tipo_logradouro": "Travessa", "bairro": "Colonton", "cidade": "Goiania", "cep": "34567", "tipo": "Apartamento", "valor": 600000.0, "data_aquisicao": "2022-05-21"},
        ]
    assert body["_links"]["create"] == {"href": "/imoveis", "method": "POST"}
    
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s", ("Goiania",)
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

@patch("utils.conectar_banco")
def test_listar_imovel_cidade_404(mock_conectar_banco, client):
    """GET /imoveis?cidade=<cidade> - cidade nao existe."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = []

    mock_conectar_banco.return_value = mock_conn

    response = client.get("/imoveis?cidade=mogi das cruzes")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": "Cidade não encontrada"
    }

    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM imoveis WHERE cidade = %s", ("mogi das cruzes",),
    )
    mock_cursor.fetchall.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()