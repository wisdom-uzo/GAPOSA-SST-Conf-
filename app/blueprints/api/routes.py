from datetime import date
from flask import Blueprint, jsonify, request
from app.firebase_service import firebase_service
from app.blueprints.registration.routes import calculate_conference_fee
from config import Config

api_bp = Blueprint('api', __name__)

@api_bp.route('/calculate-fee')
def api_calculate_fee():
    category = request.args.get('category', 'local_scholar')
    check_date = request.args.get('date')
    fee_data = calculate_conference_fee(category, check_date=check_date)
    return jsonify(fee_data)

@api_bp.route('/subthemes')
def api_subthemes():
    track = request.args.get('track')
    subthemes = firebase_service.get_subthemes()
    if track:
        subthemes = [s for s in subthemes if s.get('track') == track or s.get('track_slug') == track]
    return jsonify({'subthemes': subthemes, 'total': len(subthemes)})

@api_bp.route('/stats')
def api_stats():
    analytics = firebase_service.get_analytics()
    return jsonify(analytics)
