from flask import Flask, request, jsonify
from client import AuthClient
import mysql.connector
from mysql.connector import errorcode


app = Flask(__name__)

auth_client = AuthClient(base_url='http://localhost:3005')

db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'generaldbs'
}


def connect_to_db(config):
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Usuário ou senha do banco de dados incorretos")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("O banco de dados não existe")
        else:
            print(err)
    return None


def insert_product(cursor, product):
    add_product = ("INSERT INTO products "
                   "(name, description, company, price, amount) "
                   "VALUES (%s, %s, %s, %s, %s)")
    data_product = (product['name'], product['description'], product['company'], product['price'], product['amount'])
    cursor.execute(add_product, data_product)


def get_all_products(cursor):
    query = "SELECT * FROM products"
    cursor.execute(query)
    return cursor.fetchall()


@app.route('/postprodutosusuarioautenticado', methods=['POST'])
def process():
    payload = request.json
    email = payload.get('user')
    password = payload.get('password')

    auth_token = auth_client.login(email, password)
    if auth_token:

        products = payload.get('products', [])
        db_connection = connect_to_db(db_config)
        if db_connection is None:
            return jsonify({"message": "Falha ao conectar com o banco de dados."}), 500

        # É usado para executar instruções para se comunicar com o banco de dados MySQL.
        cursor = db_connection.cursor()

        try:
            for product in products:
                insert_product(cursor, product)
            db_connection.commit()

            all_products = get_all_products(cursor)

        except mysql.connector.Error as err:
            print(f"Erro ao inserir os produtos: {err}")
            # Reverte as mudanças por causa do error
            db_connection.rollback()
            return jsonify({"message": "Falha ao inserir os produtos"}), 500
        finally:
            cursor.close()
            db_connection.close()

        products_list = [
                {"amount": row[5], "price": row[4],"company": row[3],"description": row[2], "name": row[1]} for row in
                all_products]

        return jsonify({"message": "Produtos inseridos com sucesso", "products": products_list}), 200
    else:
        print(auth_token)
        return jsonify({"message": "Falha na autenticação! Verifique Email e/ou Senha INCORRETOS"}), 401


if __name__ == '__main__':
    app.run(debug=True)

