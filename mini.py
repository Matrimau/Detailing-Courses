from flask import Blueprint, jsonify
import requests
import hashlib
import json

mini = Blueprint('mini', __name__)

@mini.route('/api/about', methods=['GET'])
def about():
    try:
        with open('about.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception:
        return jsonify({"error": "Файл не найден"}), 404

@mini.route('/api/hash/<text>', methods=['GET'])
def hash_text(text):
    result = hashlib.sha256(text.encode()).hexdigest()
    return jsonify({
        "request": text,
        "result": result
    }), 200

@mini.route('/api/analytics', methods=['GET'])
def analytics_proxy():
    try:
        resp = requests.get('http://127.0.0.1:5001/api/analytics', timeout=3)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException:
        return jsonify({"error": "Supporting сервис недоступен"}), 503

@mini.route('/api/notifications', methods=['GET'])
def notifications_proxy():
    try:
        resp = requests.get('http://127.0.0.1:5001/api/notifications', timeout=3)
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException:
        return jsonify({"notifications": []}), 200