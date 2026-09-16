# Progeficaz Projeto 2 - Joaquim Aguiar e Carlos de Carli

API Flask para cadastro e consulta de imoveis usando MySQL.

## Requisitos

- Python
- MySQL configurado
- Variaveis de ambiente no arquivo `.env`

O arquivo `.env` deve conter:

```env
DB_HOST=seu_host
DB_PORT=sua_porta
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_NAME=seu_banco
DB_SSL_CA=ca.pem
```

## Executar o projeto

Instale as dependencias:

```powershell
.\env\Scripts\python.exe -m pip install flask mysql-connector-python python-dotenv
```

Inicie o servidor:

```powershell
.\env\Scripts\python.exe servidor.py
```

A API fica disponivel em `http://127.0.0.1:5000`.

## Testes

Execute todos os testes com:

```powershell
.\env\Scripts\python.exe -m pytest .\test_imoveis.py -v
```

## Rotas

### Listar imoveis

```http
GET /imoveis
```

Filtros opcionais:

```http
GET /imoveis?tipo=casa%20em%20condominio
GET /imoveis?cidade=Goiania
```

Resposta `200`:

```json
{
	"items": [
		{
			"id": 1,
			"logradouro": "Rua A",
			"tipo_logradouro": "Rua",
			"bairro": "Centro",
			"cidade": "Goiania",
			"cep": "74000000",
			"tipo": "Casa",
			"valor": 250000.0,
			"data_aquisicao": "2024-01-10",
			"_links": {
				"self": {"href": "/imoveis/1", "method": "GET"},
				"update": {"href": "/imoveis/1", "method": "PUT"},
				"delete": {"href": "/imoveis/1", "method": "DELETE"}
			}
		}
	],
	"_links": {
		"self": {"href": "/imoveis", "method": "GET"},
		"create": {"href": "/imoveis", "method": "POST"}
	}
}
```

Se o filtro `tipo` ou `cidade` nao encontrar resultados, a API retorna `404`.

### Consultar imovel por ID

```http
GET /imoveis/<id>
```

Retorna `200` com os dados do imovel e links para consultar, atualizar, excluir e voltar para a colecao. Se o ID nao existir, retorna `404`.

### Criar imovel

```http
POST /imoveis
Content-Type: application/json
```

Corpo obrigatorio:

```json
{
	"logradouro": "Rua A",
	"tipo_logradouro": "Rua",
	"bairro": "Centro",
	"cidade": "Goiania",
	"cep": "74000000",
	"tipo": "Casa",
	"valor": 250000.0,
	"data_aquisicao": "2024-01-10"
}
```

Retorna `201` com o ID criado e links para o imovel e para a colecao. Se faltar algum campo obrigatorio, retorna `400`.

### Atualizar imovel

```http
PUT /imoveis/<id>
Content-Type: application/json
```

Recebe o mesmo corpo da rota de criacao. Retorna `200` com a mensagem e os links do imovel. Se o ID nao existir, retorna `404`; se faltar campo obrigatorio, retorna `400`.

### Excluir imovel

```http
DELETE /imoveis/<id>
```

Retorna `200` com uma mensagem e um link para a colecao. Se o ID nao existir, retorna `404`.

## Nivel de maturidade

A API usa os niveis 1 e 2 do modelo de Richardson por meio de recursos e verbos HTTP (`GET`, `POST`, `PUT` e `DELETE`). Tambem implementa o nivel 3 com HATEOAS: as respostas informam links para as proximas operacoes possiveis.