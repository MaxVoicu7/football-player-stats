from flask import Blueprint, request, jsonify
from services.player_scraper import PlayerScraper

player_bp = Blueprint('player', __name__)
player_scraper = PlayerScraper()

@player_bp.route('/search')
def search_player():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"success": False, "error": "No name provided"}), 400
   
        result = player_scraper.search_player(name)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500