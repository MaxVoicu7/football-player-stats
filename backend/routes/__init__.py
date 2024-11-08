from flask import jsonify

def register_routes(app):
  @app.route('/health', methods=['GET'])
  def health_check():
    return jsonify({"status": "healthy", "message": "Server is running"})
    
  @app.route('/', methods=['GET'])
  def home():
    return jsonify({
      "message": "Welcome to Flask Backend API",
      "version": "1.0.0"
    }) 