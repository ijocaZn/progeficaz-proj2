from flask import Flask, request, jsonify
import utils
app = Flask(__name__)

campos_obrigatorios = ["logradouro", "tipo_logradouro", "bairro", "cidade", "cep", "tipo", "valor", "data_aquisicao"]


@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    tipo = request.args.get("tipo")
    cidade = request.args.get("cidade")
    imoveis = utils.listar_imoveis(tipo=tipo, cidade=cidade)
    if tipo and not imoveis:
        return jsonify({"error": "Tipo não encontrado"}), 404
    if cidade and not imoveis:
        return jsonify({"error": "Cidade não encontrada"}), 404
    return imoveis, 200


@app.route('/imoveis/<int:id>', methods=['GET'])
def listar_imovel_por_id(id):
    imovel = utils.listar_imovel_por_id(id)
    if imovel:
        return jsonify(imovel), 200
    else:
        return jsonify({"error": "Imóvel não encontrado"}), 404

@app.route('/imoveis', methods=['POST'])
def criar_imovel():
    imovel = request.get_json()
    if not all(campo in imovel for campo in campos_obrigatorios):
        return jsonify({"erro": "Campos obrigatórios: " + ", ".join(campos_obrigatorios)}), 400
    imovel_id = utils.criar_imovel(imovel)
    return jsonify({"id": imovel_id}), 201

@app.route('/imoveis/<int:id>', methods=['PUT'])
def atualizar_imovel(id):
    imovel = request.get_json()
    if not all(campo in imovel for campo in campos_obrigatorios):
        return jsonify({"erro": "Campos obrigatórios: " + ", ".join(campos_obrigatorios)}), 400
    updated_rows = utils.atualizar_imovel(id, imovel)
    if updated_rows == 0:
        return jsonify({"erro": "imovel não encontrado"}), 404
    return jsonify({"mensagem": "imovel atualizado com sucesso"}), 200

@app.route('/imoveis/<int:id>', methods=['DELETE'])
def deletar_imovel(id):
    deleted_rows = utils.deletar_imovel(id)
    if deleted_rows == 0:
        return jsonify({"erro": "imovel não encontrado"}), 404
    return jsonify({"mensagem": "imovel excluído com sucesso"}), 200

if __name__ == '__main__':
    app.run(debug=True)