from datetime import datetime
from database import db

class Player(db.Model):
  __tablename__ = 'players'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), unique=True, nullable=False)
  general_info = db.Column(db.JSON, nullable=False)
  current_season_stats = db.Column(db.JSON)
  scouting_report = db.Column(db.JSON)
  player_overview = db.Column(db.JSON)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

  def to_dict(self):
    return {
      'success': True,
      'data': {
          'general_info': self.general_info,
          'current_season_stats': self.current_season_stats,
          'scouting_report': self.scouting_report,
        'player_overview': self.player_overview
      }
    } 