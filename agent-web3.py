from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from web3 import Web3, HTTPProvider, IPCProvider
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
CORS(app, resources={r"/*": {"origins": "*"}})
db = SQLAlchemy(app)

# Web3 연결 설정
# 가나슈에 연결 시
w3 = Web3(HTTPProvider('http://localhost:7545'))
# 로컬 EVM 연결 시
# w3 = Web3(HTTPProvider('http://192.168.0.2:8545'))
w3.eth.enable_unaudited_features()

# ERC20 Smart Contract 설정
# contract_address = '0x743A82902b6C9bE5e11175a8816f01F2532404e9'
# with open('./abi.json') as f:
#     abi = json.loads(f.read())
# checksum_address = w3.toChecksumAddress(contract_address)
# base_contract = w3.eth.contract(checksum_address, abi=abi)
# ERC20 Smart Contract

# print('================')
# print('Base Contract')
# print(base_contract)
# print('================')


# models.py
class Wallet(db.Model):
    __tablename__ = 'wallets'
    # define schema
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.String(28), unique=True, nullable=False)
    password = db.Column(db.String(32), nullable=False)
    address = db.Column(db.String(40), unique=True, nullable=False)
    private_key = db.Column(db.String(152), unique=True, nullable=False)
    create_at = db.Column(
        db.DateTime,
        default=func.now(),
    )
    account = None

    def __init__(self, userid, password, address, private_key):
        # if address.startswith('0x'):
        #     address = address[2:]
        # if private_key.startswith('0x'):
        #     private_key = private_key[2:]
        self.userid = userid
        self.password = password
        self.address = address
        self.private_key = private_key

    # 계정 생성

    @staticmethod
    def create_account(userid, password, salt=None):
        if not salt:
            salt = os.urandom(16)

        userid = userid
        password = password
        account = w3.eth.account.create(salt)
        wallet = Wallet(
            userid=userid,
            password=password,
            address=account.address,
            private_key=account.privateKey.hex()
        )
        db.session.add(wallet)
        db.session.commit()
        return wallet

    # 로그인

    @staticmethod
    def find_account(userid, password):
        if not userid or not password:
            raise AssertionError

        account = Wallet.query.filter_by(
            userid=userid).filter_by(password=password).first()
        return account

    # 개인 잔고 확인

    @staticmethod
    def get_balance(address=None):
        if not address:
            raise ValueError

        balance = w3.fromWei(w3.eth.getBalance(address), 'ether')
        return balance

    # 이더 보내기

    @staticmethod
    def send_ether(sender, receiver, amount):
        if not sender or not receiver or not amount:
            raise ValueError

        result = w3.eth.sendTransaction(
            {'from': sender, 'to': receiver, 'value': w3.toWei(amount, 'ether')})
        return result


# view.py
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/keystore')
def list_keystore():

    output = ''
    for k in w3.personal.listAccounts:
        output += k
        output += ' '
        output += str(w3.eth.getBalance(k))  # to from wei

        output += '<br>'

    return output


@app.route('/signup', methods=['POST'])
def create_account():
    request_body = request.get_json()

    if request_body['userId'] is None or request_body['password'] is None:
        return "Invalid Parameter"

    wallet = Wallet.create_account(
        userid=request_body['userId'], password=request_body['password'], salt='test_salt')
    return jsonify({'address': wallet.address})


@app.route('/login', methods=['POST'])
@cross_origin()
def find_account():
    request_body = request.get_json()
    query_result = Wallet.find_account(
        request_body['userId'], request_body['password'])
    response = {'userId': query_result.userid, 'password': query_result.password,
                'address': query_result.address, 'privateKey': query_result.private_key}

    return jsonify(response)


@app.route('/wallets')
def list_wallet():
    wallets = Wallet.query.all()
    output = ''
    for w in wallets:
        output += w.address
        output += ' '
        output += w.private_key
        # balance
        output += '<br>'
    return output


@app.route('/get_balance', methods=['GET'])
def get_balances():
    account_list = w3.eth.accounts
    budget_list = []
    for user in account_list:
        budget_list.append(
            {'address': user, 'balance': round(Wallet.get_balance(user))})

    return jsonify(budget_list)


@app.route('/get_accounts', methods=['GET'])
def get_accounts():
    account_list = w3.eth.accounts
    response = []

    for account in account_list:
        response.append(
            {'address': account, 'balance': int(Wallet.get_balance(account))})

    return jsonify(response)


@app.route('/transfer', methods=['POST'])
def transfer():
    request_body = request.get_json()
    result = Wallet.send_ether(
        request_body['from'], request_body['to'], request_body['amount'])
    return str(result)


@app.route('/get_block', methods=['GET'])
def get_block():
    block = w3.eth.getBlock('latest')
    return str(block)


# manage.py
# Port 설정
if __name__ == '__main__':
    db.create_all()
    app.run(port=8000)
