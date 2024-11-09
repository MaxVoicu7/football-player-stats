from flask import jsonify
from routes.player_routes import player_bp

def register_routes(app):
  app.register_blueprint(player_bp, url_prefix='/api/player')

  @app.route('/health', methods=['GET'])
  def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})
    
  @app.route('/', methods=['GET'])
  def home():
    return jsonify({
      "message": "Welcome to Flask Backend API",
      "version": "1.0.0"
    })
    