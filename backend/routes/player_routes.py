from flask import Blueprint, request, jsonify
from services.player_scraper import PlayerScraper
from models.player import Player
from database import db

player_bp = Blueprint('player', __name__)
player_scraper = PlayerScraper()

@player_bp.route('/search')
def search_player():
  try:
    name = request.args.get('name')
    if not name:
      return jsonify({"success": False, "error": "No name provided"}), 400

    player = Player.query.filter_by(name=name).first()
    if player:
      return jsonify(player.to_dict())

    result = player_scraper.search_player(name)
        
    if result['success']:
      new_player = Player(
        name=name,
        general_info=result['data']['general_info'],
        current_season_stats=result['data'].get('current_season_stats'),
        scouting_report=result['data'].get('scouting_report'),
        player_overview=result['data'].get('player_overview')
      )
      db.session.add(new_player)
      db.session.commit()

    return jsonify(result)
        
  except Exception as e:
    return jsonify({"success": False, "error": str(e)}), 500