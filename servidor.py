from flask import Flask, request, jsonify
import utils
app = Flask(__name__)


@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    imoveis = utils.listar_imoveis()
    return imoveis, 200


@app.route('/imoveis/<int:id>', methods=['GET'])
def listar_imovel_por_id(id):
    imovel = utils.listar_imovel_por_id(id)
    if imovel:
        return jsonify(imovel), 200
    else:
        return jsonify({"error": "Imóvel não encontrado"}), 404


if __name__ == '__main__':
    app.run(debug=True)