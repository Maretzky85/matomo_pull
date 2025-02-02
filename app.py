from datetime import datetime

from flask import Flask, jsonify, request
from functools import wraps
from matomo_pull.utils import DatabaseAlreadyUpdatedError
import jwt
import os

import main

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ['JWT_SECRET_KEY']


def check_for_token(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Missing token'}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], 'HS256')
        except jwt.exceptions.ExpiredSignatureError:
            return jsonify({'message': 'Token expired'}), 403
        except jwt.exceptions.InvalidSignatureError:
            return jsonify({'message': 'Invalid token'}), 403
        except Exception as e:
            return jsonify({'message': f"{type(e).__name__}:  {str(e)}"})
        return func(*args, **kwargs)
    return wrapped


def check_data(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        try:
            [
                request.args['base_url'],
                request.args['id_site'],
                request.args['start_date'],
                request.args['token_auth'],
                request.args['db_name']
            ]
        except Exception:
            return jsonify({'message': 'Invalid data'}), 403
        return func(*args, **kwargs)
    return wrapped


@app.route('/')
# @check_for_token
@check_data
def index():
    print(datetime.now())
    data = request.args
    try:
        main.exec(data)
    except DatabaseAlreadyUpdatedError:
        return jsonify(
            {'message': 'Database already updated'}
        ), 200
    except Exception as e:
        print(e)
        return jsonify(
            {'message': 'Error executing script: recheck database variables'}
        ), 403
    return jsonify(
        {'message': 'Database successfully imported'}
    ), 200


if __name__ == "__main__":
    app.run()
