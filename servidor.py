from flask import Flask, request, jsonify
import utils
app = Flask(__name__)


@app.route('/imoveis', methods=['GET'])
def listar_imoveis():
    imoveis = utils.listar_imoveis()
    return imoveis, 200



if __name__ == '__main__':
    app.run(debug=True)