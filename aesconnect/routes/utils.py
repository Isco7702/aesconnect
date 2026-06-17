from flask import jsonify
from flask_smorest import Blueprint

utils_bp = Blueprint('utils', __name__, url_prefix='/utils')


@utils_bp.route('/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'status': 'ok'})
