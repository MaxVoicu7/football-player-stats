from typing import Dict, List
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class StatCategory:
    name: str
    stats: List[str]
    weight: float

class PlayerAnalyzer:
    def __init__(self):
        # Define stat categories with weights
        self.categories = {
            "attacking": StatCategory(
                name="Attacking",
                stats=[
                    "Non-Penalty Goals",
                    "npxG: Non-Penalty xG",
                    "Shots Total",
                    "Assists",
                    "xAG: Exp. Assisted Goals",
                    "Shot-Creating Actions"
                ],
                weight=0.3
            ),
            "possession": StatCategory(
                name="Possession",
                stats=[
                    "Passes Attempted",
                    "Pass Completion %",
                    "Progressive Passes",
                    "Progressive Carries",
                    "Successful Take-Ons",
                    "Progressive Passes Rec"
                ],
                weight=0.35
            ),
            "defensive": StatCategory(
                name="Defensive",
                stats=[
                    "Tackles",
                    "Interceptions",
                    "Blocks",
                    "Clearances",
                    "Aerials Won"
                ],
                weight=0.35
            )
        }

        # Updated position weights
        self.position_weights = {
            "FW": {"attacking": 0.5, "possession": 0.35, "defensive": 0.15},
            "MF": {"attacking": 0.35, "possession": 0.45, "defensive": 0.20},
            "DF": {"attacking": 0.15, "possession": 0.40, "defensive": 0.45},
            "GK": {"attacking": 0.05, "possession": 0.35, "defensive": 0.60}
        }

    def analyze_player(self, player_data: Dict) -> Dict:
        """Generate complete player analysis"""
        try:
            position = player_data['general_info']['position']
            age = player_data['general_info']['age']
            scouting_report = player_data['scouting_report']

            # Get position base (FW, MF, DF, GK)
            position_base = self._get_position_base(position)

            # Calculate category scores
            category_scores = self._calculate_category_scores(scouting_report, position_base)

            # Identify strengths and weaknesses with context
            strengths, weaknesses = self._identify_strengths_weaknesses(scouting_report, position_base)

            # Calculate detailed overall rating
            overall_rating = self._calculate_overall_rating(category_scores, position_base)

            # Analyze playing style in detail
            playing_style = self._analyze_playing_style(scouting_report, position, category_scores)

            # Generate development analysis
            development_analysis = self._analyze_development_needs(
                age, 
                weaknesses, 
                category_scores,
                position_base
            )

            return {
                "player_overview": {
                    "overall_rating": overall_rating,
                    "summary": self._generate_detailed_summary(
                        player_data['general_info']['name'],
                        position,
                        age,
                        overall_rating,
                        category_scores,
                        playing_style
                    ),
                    "performance_profile": {
                        "category_scores": category_scores,
                        "key_strengths": strengths[:3],  # Top 3 strengths
                        "areas_for_improvement": weaknesses[:3],  # Top 3 weaknesses
                        "playing_style": playing_style
                    },
                    "development_analysis": development_analysis,
                    "potential": {
                        "current_rating": overall_rating,
                        "potential_rating": self._estimate_potential(age, overall_rating, category_scores),
                        "development_timeframe": self._estimate_development_timeframe(age),
                        "key_development_areas": development_analysis['priority_areas']
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error analyzing player: {str(e)}")
            return {"error": "Could not analyze player"}

    def _get_position_base(self, position: str) -> str:
        """Extract base position from detailed position string"""
        position = position.upper()
        if any(pos in position for pos in ['FW', 'ST', 'CF', 'LW', 'RW']):
            return 'FW'
        elif any(pos in position for pos in ['MF', 'CM', 'DM', 'AM']):
            return 'MF'
        elif any(pos in position for pos in ['DF', 'CB', 'LB', 'RB']):
            return 'DF'
        elif 'GK' in position:
            return 'GK'
        return 'MF'  # Default to MF if unclear

    def _calculate_category_scores(self, scouting_report: List, position: str) -> Dict:
        """Calculate detailed scores for each category with adjusted weights"""
        category_scores = {}
        
        # Define key stats that should have higher weight
        key_stats = {
            "Pass Completion %": 1.3,
            "Progressive Passes": 1.3,
            "Progressive Carries": 1.2,
            "Shot-Creating Actions": 1.2,
            "Assists": 1.2,
            "Non-Penalty Goals": 1.2,
            "Tackles": 1.1,
            "Interceptions": 1.1,
            "Aerials Won": 1.1
        }
        
        for category, config in self.categories.items():
            relevant_stats = []
            weighted_sum = 0
            total_weight = 0
            
            for stat in scouting_report:
                if stat['stat'] in config.stats:
                    # Apply individual stat weight
                    stat_weight = key_stats.get(stat['stat'], 1.0)
                    weighted_sum += stat['percentile'] * stat_weight
                    total_weight += stat_weight
                    relevant_stats.append(stat)
            
            if relevant_stats:
                # Calculate weighted average
                score = weighted_sum / total_weight if total_weight > 0 else 0
                
                # Position-specific weight
                weight = self.position_weights[position][category]
                
                category_scores[category] = {
                    "score": round(score),
                    "weight": weight,
                    "contribution": round(score * weight, 2)
                }
        
        return category_scores

    def _identify_strengths_weaknesses(self, scouting_report: List, position: str) -> tuple:
        """Identify strengths and weaknesses with position context"""
        position_weights = self.position_weights[position]
        
        rated_stats = []
        for stat in scouting_report:
            # Determine which category this stat belongs to
            for category, config in self.categories.items():
                if stat['stat'] in config.stats:
                    # Apply position-specific weight to the stat's importance
                    weight = position_weights[category]
                    rated_stats.append({
                        "stat": stat['stat'],
                        "percentile": stat['percentile'],
                        "value": stat['per_90'],
                        "weighted_score": stat['percentile'] * weight,
                        "category": category
                    })
                    break
        
        # Sort by weighted score
        rated_stats.sort(key=lambda x: x['weighted_score'], reverse=True)
        
        strengths = [stat for stat in rated_stats if stat['percentile'] >= 75]
        weaknesses = [stat for stat in rated_stats if stat['percentile'] <= 35]
        
        return strengths, weaknesses

    def _analyze_playing_style(self, scouting_report: List, position: str, category_scores: Dict) -> Dict:
        """Detailed analysis of playing style"""
        # Calculate style characteristics
        characteristics = {
            "possession_play": self._calculate_style_characteristic(
                scouting_report,
                ["Pass Completion %", "Progressive Passes", "Progressive Carries"]
            ),
            "attacking_threat": self._calculate_style_characteristic(
                scouting_report,
                ["Non-Penalty Goals", "Shot-Creating Actions", "xAG: Exp. Assisted Goals"]
            ),
            "defensive_contribution": self._calculate_style_characteristic(
                scouting_report,
                ["Tackles", "Interceptions", "Blocks"]
            )
        }

        # Determine primary and secondary styles
        styles = sorted(characteristics.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "primary_style": styles[0][0].replace('_', ' ').title(),
            "secondary_style": styles[1][0].replace('_', ' ').title(),
            "style_characteristics": characteristics,
            "position_specific_traits": self._identify_position_specific_traits(
                scouting_report,
                position
            )
        }

    def _calculate_style_characteristic(self, scouting_report: List, relevant_stats: List) -> float:
        """Calculate score for a specific style characteristic"""
        relevant_values = [
            stat['percentile'] for stat in scouting_report 
            if stat['stat'] in relevant_stats
        ]
        return sum(relevant_values) / len(relevant_values) if relevant_values else 0

    def _analyze_development_needs(self, age: int, weaknesses: List, 
                                 category_scores: Dict, position: str) -> Dict:
        """Detailed development needs analysis"""
        development_timeframe = self._estimate_development_timeframe(age)
        
        # Prioritize development areas based on position and age
        priority_areas = {
            "critical": [],
            "important": [],
            "supplementary": []
        }

        for weakness in weaknesses:
            if weakness['percentile'] < 20:
                priority_areas["critical"].append(weakness)
            elif weakness['percentile'] < 30:
                priority_areas["important"].append(weakness)
            else:
                priority_areas["supplementary"].append(weakness)

        return {
            "priority_areas": priority_areas,
            "development_timeframe": development_timeframe,
            "training_recommendations": self._generate_training_recommendations(
                priority_areas,
                age,
                position
            )
        }

    def _estimate_development_timeframe(self, age: int) -> str:
        """Estimate development timeframe based on age"""
        if age <= 19:
            return "Long-term (3-5 years for full potential)"
        elif age <= 23:
            return "Medium-term (2-3 years for peak performance)"
        elif age <= 27:
            return "Short-term (1-2 years for refinements)"
        else:
            return "Maintenance phase"

    def _generate_training_recommendations(self, priority_areas: Dict, 
                                        age: int, position: str) -> List[Dict]:
        """Generate specific training recommendations"""
        recommendations = []
        
        for priority, weaknesses in priority_areas.items():
            for weakness in weaknesses:
                recommendations.append({
                    "focus_area": weakness['stat'],
                    "priority": priority,
                    "current_level": weakness['percentile'],
                    "target_level": min(weakness['percentile'] + 20, 90),
                    "timeframe": "Short-term" if priority == "critical" else "Medium-term"
                })
        
        return recommendations

    def _generate_detailed_summary(self, name: str, position: str, age: int,
                                 rating: int, category_scores: Dict, 
                                 playing_style: Dict) -> str:
        """Generate detailed natural language summary"""
        age_description = (
            "promising young" if age <= 20
            else "developing" if age <= 23
            else "peak-age" if age <= 28
            else "experienced"
        )

        best_category = max(category_scores.items(), key=lambda x: x[1]['score'])
        
        return (
            f"{name} is a {age_description} {position} currently rated at {rating}/100. "
            f"Their strongest aspect is {best_category[0]} ({best_category[1]['score']}/100), "
            f"with a playing style primarily focused on {playing_style['primary_style'].lower()}. "
            f"They also show good capabilities in {playing_style['secondary_style'].lower()}."
        )

    def _estimate_potential(self, age: int, current_rating: int, 
                          category_scores: Dict) -> int:
        """Estimate potential rating with more sophisticated logic"""
        # Base potential increase based on age
        if age <= 19:
            potential_increase = 15
        elif age <= 21:
            potential_increase = 12
        elif age <= 23:
            potential_increase = 8
        elif age <= 25:
            potential_increase = 5
        elif age <= 27:
            potential_increase = 3
        else:
            potential_increase = 0

        # Adjust based on current performance level
        if current_rating >= 85:
            potential_increase *= 0.5  # Harder to improve when already excellent
        elif current_rating <= 65:
            potential_increase *= 1.2  # More room for improvement

        # Consider category scores
        highest_category_score = max(
            score['score'] for score in category_scores.values()
        )
        if highest_category_score >= 85:
            potential_increase += 2  # Bonus for exceptional ability in any area

        return min(99, round(current_rating + potential_increase))

    def _calculate_overall_rating(self, category_scores: Dict, position: str) -> int:
        """Calculate overall rating with improved weighting and passing bonus"""
        try:
            total_weighted_score = 0
            total_weight = 0

            # Get position-specific weights
            position_weights = self.position_weights[position]

            # Calculate weighted score for each category
            for category, scores in category_scores.items():
                category_score = scores['score']
                # Combine base category weight with position-specific weight
                weight = scores['weight'] * position_weights[category]
                
                total_weighted_score += category_score * weight
                total_weight += weight

            # Calculate base rating
            base_rating = total_weighted_score / total_weight if total_weight > 0 else 70

            # Add passing bonus based on key passing stats
            passing_bonus = self._calculate_passing_bonus(category_scores)
            
            # Find exceptional stats (85+ percentile)
            exceptional_categories = sum(
                1 for scores in category_scores.values()
                if scores['score'] >= 85  # Lowered threshold from 90
            )

            # Calculate final rating with bonuses
            rating = base_rating + passing_bonus + (exceptional_categories * 2) + 5  # Added flat +5 bonus

            # Ensure rating stays within bounds
            return min(99, max(50, round(rating)))  # Increased minimum rating to 50

        except Exception as e:
            logger.error(f"Error calculating overall rating: {str(e)}")
            return 75  # Increased default rating

    def _calculate_passing_bonus(self, category_scores: Dict) -> float:
        """Calculate bonus points for good passing abilities"""
        possession_score = category_scores.get('possession', {}).get('score', 0)
        
        # Progressive passing bonus
        if possession_score >= 85:
            return 8
        elif possession_score >= 75:
            return 6
        elif possession_score >= 65:
            return 4
        return 0

    def _identify_position_specific_traits(self, scouting_report: List, position: str) -> Dict:
        """Identify position-specific traits and their levels"""
        
        # Define traits to look for based on position
        position_traits = {
            "FW": {
                "finishing": ["Non-Penalty Goals", "npxG: Non-Penalty xG"],
                "creativity": ["Assists", "xAG: Exp. Assisted Goals", "Shot-Creating Actions"],
                "movement": ["Progressive Passes Rec"]
            },
            "MF": {
                "playmaking": ["Progressive Passes", "Assists", "xAG: Exp. Assisted Goals"],
                "ball_control": ["Pass Completion %", "Progressive Carries", "Successful Take-Ons"],
                "work_rate": ["Shot-Creating Actions", "Tackles", "Interceptions"]
            },
            "DF": {
                "defending": ["Tackles", "Interceptions", "Blocks"],
                "aerial_ability": ["Aerials Won", "Clearances"],
                "build_up": ["Progressive Passes", "Pass Completion %"]
            },
            "GK": {
                "shot_stopping": ["Save Percentage", "Goals Against"],
                "distribution": ["Pass Completion %", "Passes Attempted"],
                "commanding": ["Crosses Stopped", "Clearances"]
            }
        }

        # Get base position
        base_position = self._get_position_base(position)
        relevant_traits = position_traits.get(base_position, position_traits["MF"])
        
        traits_analysis = {}
        
        # Analyze each trait
        for trait_name, relevant_stats in relevant_traits.items():
            trait_scores = []
            
            for stat in scouting_report:
                if stat['stat'] in relevant_stats:
                    trait_scores.append(stat['percentile'])
            
            if trait_scores:
                avg_score = sum(trait_scores) / len(trait_scores)
                traits_analysis[trait_name] = {
                    "score": round(avg_score),
                    "level": self._get_trait_level(avg_score),
                    "percentile": round(avg_score)
                }
        
        return {
            "position_role": self._determine_specific_role(traits_analysis, position),
            "key_traits": traits_analysis
        }

    def _get_trait_level(self, score: float) -> str:
        """Convert numerical score to descriptive level"""
        if score >= 90:
            return "Elite"
        elif score >= 80:
            return "Excellent"
        elif score >= 70:
            return "Very Good"
        elif score >= 60:
            return "Good"
        elif score >= 50:
            return "Above Average"
        elif score >= 40:
            return "Average"
        elif score >= 30:
            return "Below Average"
        else:
            return "Developing"

    def _determine_specific_role(self, traits_analysis: Dict, position: str) -> str:
        """Determine specific role based on traits and position"""
        base_position = self._get_position_base(position)
        
        # Get the strongest traits
        sorted_traits = sorted(
            traits_analysis.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )
        
        # Role definitions based on trait combinations
        role_definitions = {
            "FW": {
                "finishing": "Goal Poacher",
                "creativity": "Creative Forward",
                "movement": "Mobile Striker"
            },
            "MF": {
                "playmaking": "Playmaker",
                "ball_control": "Technical Midfielder",
                "work_rate": "Box-to-Box Midfielder"
            },
            "DF": {
                "defending": "No-Nonsense Defender",
                "aerial_ability": "Aerial Specialist",
                "build_up": "Ball-Playing Defender"
            },
            "GK": {
                "shot_stopping": "Shot Stopper",
                "distribution": "Sweeper Keeper",
                "commanding": "Traditional Keeper"
            }
        }
        
        if sorted_traits:
            # Get the primary trait
            primary_trait = sorted_traits[0][0]
            return role_definitions.get(base_position, {}).get(primary_trait, "Complete Player")
        
        return "Versatile Player"