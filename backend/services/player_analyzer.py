from typing import Dict, List, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PlayerAnalysis:
    """Data class for complete player analysis"""
    overall_rating: int
    analysis_confidence: float
    detailed_analysis: Dict[str, Any]
    recommendations: Dict[str, Any]

class PlayerAnalyzer:
    def __init__(self):
        # Initialize all the components we created earlier
        self.position_weights = {
            "FW": {
                "attacking": 0.35,
                "playmaking": 0.25,
                "technical": 0.20,
                "defensive": 0.10,
                "physical": 0.10
            },
            "MF": {
                "attacking": 0.20,
                "playmaking": 0.35,
                "technical": 0.25,
                "defensive": 0.15,
                "physical": 0.05
            },
            "DF": {
                "attacking": 0.05,
                "playmaking": 0.15,
                "technical": 0.25,
                "defensive": 0.40,
                "physical": 0.15
            }
        }

        # Stat groupings
        self.stat_groups = {
            "attacking": [
                "Non-Penalty Goals",
                "npxG: Non-Penalty xG",
                "Shots Total"
            ],
            "playmaking": [
                "Assists",
                "xAG: Exp. Assisted Goals",
                "Shot-Creating Actions",
                "Progressive Passes",
                "Progressive Passes Rec"
            ],
            "technical": [
                "Pass Completion %",
                "Successful Take-Ons",
                "Progressive Carries",
                "Touches (Att Pen)"
            ],
            "defensive": [
                "Tackles",
                "Interceptions",
                "Blocks",
                "Clearances"
            ],
            "physical": [
                "Aerials Won"
            ]
        }

        # Define role requirements and their stat weightings
        self.role_definitions = {
            "Advanced Playmaker": {
                "key_stats": {
                    "Progressive Passes": 0.20,
                    "xAG: Exp. Assisted Goals": 0.20,
                    "Shot-Creating Actions": 0.15,
                    "Progressive Carries": 0.15,
                    "Pass Completion %": 0.15,
                    "Successful Take-Ons": 0.15
                },
                "suitable_positions": ["MF", "FW-MF"],
                "description": "Creates chances and progresses play from advanced positions"
            },
            "Inside Forward": {
                "key_stats": {
                    "Non-Penalty Goals": 0.20,
                    "npxG: Non-Penalty xG": 0.20,
                    "Shots Total": 0.15,
                    "Progressive Carries": 0.15,
                    "Successful Take-Ons": 0.15,
                    "Touches (Att Pen)": 0.15
                },
                "suitable_positions": ["FW", "FW-MF"],
                "description": "Cuts inside to create and score goals"
            },
            "Complete Forward": {
                "key_stats": {
                    "Non-Penalty Goals": 0.15,
                    "npxG: Non-Penalty xG": 0.15,
                    "Assists": 0.15,
                    "xAG: Exp. Assisted Goals": 0.15,
                    "Shot-Creating Actions": 0.10,
                    "Aerials Won": 0.15,
                    "Progressive Passes Rec": 0.15
                },
                "suitable_positions": ["FW"],
                "description": "All-round striker combining scoring and creating"
            },
            "Box-to-Box Midfielder": {
                "key_stats": {
                    "Progressive Passes": 0.15,
                    "Progressive Carries": 0.15,
                    "Tackles": 0.15,
                    "Interceptions": 0.15,
                    "Shot-Creating Actions": 0.10,
                    "Pass Completion %": 0.15,
                    "Progressive Passes Rec": 0.15
                },
                "suitable_positions": ["MF"],
                "description": "Dynamic midfielder contributing in both attack and defense"
            },
            "Pressing Forward": {
                "key_stats": {
                    "Tackles": 0.20,
                    "Interceptions": 0.15,
                    "Non-Penalty Goals": 0.15,
                    "npxG: Non-Penalty xG": 0.15,
                    "Progressive Passes Rec": 0.15,
                    "Shot-Creating Actions": 0.20
                },
                "suitable_positions": ["FW", "FW-MF"],
                "description": "Forward who excels in pressing and defensive contribution"
            }
        }

    def generate_complete_analysis(self, player_data: Dict) -> PlayerAnalysis:
        """
        Generate complete player analysis from scraped data
        """
        try:
            logger.info(f"Starting analysis for player: {player_data['general_info']['name']}")
            
            # Calculate base rating directly here instead of separate method
            scouting_report = player_data['scouting_report']
            position = self._get_primary_position(player_data['general_info']['position'])
            age = player_data['general_info']['age']

            # Generate analysis components
            playing_style = self._analyze_playing_style(scouting_report)
            strengths_weaknesses = self._analyze_strengths_weaknesses(scouting_report)
            role_suitability = self._analyze_role_suitability(scouting_report, position)
            development_analysis = self._analyze_development_areas(scouting_report, age)

            # Calculate overall rating inline
            try:
                base_rating = sum(stat['percentile'] for stat in scouting_report) / len(scouting_report)
                best_role_score = max(
                    role['score'] for role in role_suitability['role_scores'].values()
                ) if role_suitability['role_scores'] else 70
                exceptional_bonus = len(strengths_weaknesses.get('exceptional_abilities', [])) * 2
                
                overall_rating = min(99, round(
                    base_rating * 0.5 +
                    best_role_score * 0.3 +
                    exceptional_bonus
                ))
            except Exception as e:
                logger.error(f"Error calculating rating: {e}")
                overall_rating = 70

            # Calculate confidence score
            confidence_score = self._calculate_analysis_confidence(player_data)

            # Compile detailed analysis
            detailed_analysis = {
                "player_info": {
                    "name": player_data['general_info']['name'],
                    "age": age,
                    "position": position,
                    "club": player_data['general_info']['club']
                },
                "performance_profile": {
                    "playing_style": playing_style,
                    "strengths_weaknesses": strengths_weaknesses,
                    "role_suitability": role_suitability
                },
                "development": development_analysis,
                "current_season_performance": self._analyze_current_season_stats(
                    player_data['current_season_stats']
                )
            }

            # Generate recommendations
            recommendations = self._generate_recommendations(
                detailed_analysis,
                development_analysis,
                role_suitability
            )

            return PlayerAnalysis(
                overall_rating=overall_rating,
                analysis_confidence=confidence_score,
                detailed_analysis=detailed_analysis,
                recommendations=recommendations
            )

        except Exception as e:
            logger.error(f"Error generating analysis: {str(e)}")
            raise

    def _calculate_analysis_confidence(self, player_data: Dict) -> float:
        """Calculate confidence score for the analysis"""
        
        factors = {
            "data_completeness": self._check_data_completeness(player_data),
            "sample_size": self._check_sample_size(player_data),
            "data_recency": self._check_data_recency(player_data)
        }
        
        return sum(factors.values()) / len(factors)

    def _generate_recommendations(self, detailed_analysis: Dict, development_analysis: Dict, role_suitability: Dict) -> Dict:
        """Generate complete set of recommendations for the player"""
        try:
            return {
                "role_recommendations": {
                    "primary_role": role_suitability.get('primary_role', ''),
                    "alternative_roles": role_suitability.get('secondary_role', ''),
                    "role_specific_improvements": self._get_role_specific_improvements(role_suitability),
                },
                "development_focus": development_analysis.get('training_recommendations', []),
                "tactical_recommendations": self._generate_tactical_recommendations(
                    detailed_analysis,
                    role_suitability
                ),
                "training_priorities": self._prioritize_training_areas(
                    development_analysis,
                    role_suitability
                )
            }
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {
                "role_recommendations": {},
                "development_focus": [],
                "tactical_recommendations": {},
                "training_priorities": []
            }

    def _get_role_specific_improvements(self, role_suitability: Dict) -> List[Dict]:
        """Get specific improvements needed for optimal role performance"""
        improvements = []
        
        if not role_suitability or 'role_scores' not in role_suitability:
            return improvements

        primary_role = max(
            role_suitability['role_scores'].items(),
            key=lambda x: x[1]['score']
        )

        role_data = primary_role[1]
        if 'key_attributes' in role_data:
            for attr in role_data['key_attributes']:
                if attr['percentile'] < 85:
                    improvements.append({
                        "attribute": attr['stat'],
                        "current_level": attr['percentile'],
                        "target_level": min(attr['percentile'] + 15, 99),
                        "priority": "High" if attr['percentile'] < 70 else "Medium"
                    })

        return improvements

    def _prioritize_training_areas(self, development_analysis: Dict, role_suitability: Dict) -> List[Dict]:
        """Prioritize training areas based on development needs and role requirements"""
        priorities = []
        
        # Add critical development areas
        if 'priority_areas' in development_analysis:
            for area in development_analysis['priority_areas'].get('critical', []):
                priorities.append({
                    "area": area['stat'],
                    "priority": "High",
                    "current_level": area['current_percentile'],
                    "target_level": area['target_percentile'],
                    "focus": "Development"
                })

        # Add role-specific training needs
        if role_suitability and 'role_scores' in role_suitability:
            primary_role = max(
                role_suitability['role_scores'].items(),
                key=lambda x: x[1]['score']
            )
            
            if 'key_attributes' in primary_role[1]:
                for attr in primary_role[1]['key_attributes']:
                    if attr['percentile'] < 75:
                        priorities.append({
                            "area": attr['stat'],
                            "priority": "Medium",
                            "current_level": attr['percentile'],
                            "target_level": min(attr['percentile'] + 15, 99),
                            "focus": "Role Optimization"
                        })

        return sorted(priorities, key=lambda x: x['priority'] == 'High', reverse=True)

    def _get_primary_position(self, position_str: str) -> str:
        """Extract primary position category (FW, MF, DF)"""
        if 'FW' in position_str:
            return 'FW'
        elif 'MF' in position_str:
            return 'MF'
        elif 'DF' in position_str:
            return 'DF'
        return 'MF'  # default to midfielder if unclear

    def _calculate_component_scores(self, scouting_report: List, position: str) -> Dict[str, float]:
        """Calculate scores for each component based on percentiles"""
        scores = {}
        for group, stats in self.stat_groups.items():
            relevant_stats = [
                stat for stat in scouting_report 
                if stat['stat'] in stats
            ]
            if relevant_stats:
                scores[group] = sum(stat['percentile'] for stat in relevant_stats) / len(relevant_stats)
            else:
                scores[group] = 50  # default to average if no data
        return scores

    def _calculate_overall_rating(self, component_scores: Dict[str, float], position: str, age: int) -> int:
        """Calculate overall rating with position-specific weights and age factor"""
        weights = self.position_weights[position]
        
        # Calculate base rating
        base_rating = sum(
            component_scores[component] * weight 
            for component, weight in weights.items()
        ) / 100
        
        # Apply age factor (bonus for young players with high scores)
        age_factor = self._calculate_age_factor(age, base_rating)
        
        return round(base_rating * age_factor)

    def _calculate_age_factor(self, age: int, base_rating: float) -> float:
        """Calculate age-based adjustment factor"""
        if age <= 21:
            return 1.1  # bonus for very young players
        elif age <= 23:
            return 1.05
        elif age <= 27:
            return 1.0  # prime age
        elif age <= 30:
            return 0.95
        else:
            return 0.9  # penalty for older players

    def _analyze_playing_style(self, scouting_report: List) -> Dict:
        """
        Analyze player's playing style based on statistical tendencies
        Returns both primary and secondary play style characteristics
        """
        # Style indicators with their relevant stats and thresholds
        style_indicators = {
            "Playmaker": {
                "stats": [
                    "Progressive Passes",
                    "xAG: Exp. Assisted Goals",
                    "Shot-Creating Actions"
                ],
                "threshold": 75  # 75th percentile or higher
            },
            "Goal Scorer": {
                "stats": [
                    "Non-Penalty Goals",
                    "npxG: Non-Penalty xG",
                    "Shots Total"
                ],
                "threshold": 70
            },
            "Dribbler": {
                "stats": [
                    "Successful Take-Ons",
                    "Progressive Carries"
                ],
                "threshold": 75
            },
            "Box Presence": {
                "stats": [
                    "Touches (Att Pen)",
                    "Aerials Won"
                ],
                "threshold": 70
            },
            "Defensive Forward": {
                "stats": [
                    "Tackles",
                    "Interceptions",
                    "Blocks"
                ],
                "threshold": 70
            }
        }

        # Calculate style scores
        style_scores = {}
        for style, criteria in style_indicators.items():
            relevant_stats = [
                stat for stat in scouting_report 
                if stat['stat'] in criteria['stats']
            ]
            
            if relevant_stats:
                avg_percentile = sum(stat['percentile'] for stat in relevant_stats) / len(relevant_stats)
                style_scores[style] = {
                    "score": avg_percentile,
                    "is_characteristic": avg_percentile >= criteria['threshold']
                }

        # Identify primary and secondary styles
        sorted_styles = sorted(
            style_scores.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )

        # Get specific statistical highlights
        highlights = []
        for stat in scouting_report:
            if stat['percentile'] >= 90:  # Exceptional stats
                highlights.append({
                    "stat": stat['stat'],
                    "percentile": stat['percentile'],
                    "value": stat['per_90']
                })

        return {
            "primary_style": sorted_styles[0][0] if sorted_styles else None,
            "secondary_style": sorted_styles[1][0] if len(sorted_styles) > 1 else None,
            "style_scores": style_scores,
            "statistical_highlights": highlights,
            "play_style_summary": self._generate_style_summary(style_scores),
        }

    def _generate_style_summary(self, style_scores: Dict) -> str:
        """Generate a narrative summary of the player's style"""
        characteristic_styles = [
            style for style, data in style_scores.items() 
            if data["is_characteristic"]
        ]
        
        if not characteristic_styles:
            return "Balanced player without strongly pronounced stylistic tendencies"
        
        if len(characteristic_styles) == 1:
            return f"Specialized {characteristic_styles[0]} with clear tactical profile"
        
        return f"Versatile player combining {' and '.join(characteristic_styles)} characteristics"

    def _analyze_strengths_weaknesses(self, scouting_report: List) -> Dict:
        """
        Identify player's strengths and weaknesses based on percentile rankings
        Categorizes abilities and provides detailed analysis
        """
        # Categorize stats into skill groups
        skill_groups = {
            "Finishing": {
                "stats": ["Non-Penalty Goals", "npxG: Non-Penalty xG", "Shots Total"],
                "importance": "high"
            },
            "Creativity": {
                "stats": ["Assists", "xAG: Exp. Assisted Goals", "Shot-Creating Actions"],
                "importance": "high"
            },
            "Ball Progression": {
                "stats": ["Progressive Passes", "Progressive Carries", "Progressive Passes Rec"],
                "importance": "high"
            },
            "Technical Ability": {
                "stats": ["Pass Completion %", "Successful Take-Ons"],
                "importance": "medium"
            },
            "Defensive Contribution": {
                "stats": ["Tackles", "Interceptions", "Blocks"],
                "importance": "medium"
            },
            "Aerial Ability": {
                "stats": ["Aerials Won"],
                "importance": "low"
            }
        }

        # Analysis thresholds
        EXCEPTIONAL = 90
        STRENGTH = 75
        WEAKNESS = 40
        SEVERE_WEAKNESS = 25

        analysis = {
            "strengths": [],
            "weaknesses": [],
            "skill_groups": {},
            "exceptional_abilities": [],
            "areas_of_concern": []
        }

        # Analyze each skill group
        for group_name, group_info in skill_groups.items():
            relevant_stats = [
                stat for stat in scouting_report 
                if stat['stat'] in group_info['stats']
            ]
            
            if relevant_stats:
                avg_percentile = sum(stat['percentile'] for stat in relevant_stats) / len(relevant_stats)
                
                group_analysis = {
                    "average_percentile": avg_percentile,
                    "importance": group_info["importance"],
                    "rating": self._get_rating_label(avg_percentile),
                    "constituent_stats": [
                        {
                            "name": stat["stat"],
                            "percentile": stat["percentile"],
                            "value": stat["per_90"]
                        } for stat in relevant_stats
                    ]
                }
                
                analysis["skill_groups"][group_name] = group_analysis

                # Categorize as strength or weakness
                if avg_percentile >= EXCEPTIONAL:
                    analysis["exceptional_abilities"].append({
                        "category": group_name,
                        "percentile": avg_percentile,
                        "importance": group_info["importance"]
                    })
                elif avg_percentile >= STRENGTH:
                    analysis["strengths"].append({
                        "category": group_name,
                        "percentile": avg_percentile,
                        "importance": group_info["importance"]
                    })
                elif avg_percentile <= SEVERE_WEAKNESS:
                    analysis["areas_of_concern"].append({
                        "category": group_name,
                        "percentile": avg_percentile,
                        "importance": group_info["importance"]
                    })
                elif avg_percentile <= WEAKNESS:
                    analysis["weaknesses"].append({
                        "category": group_name,
                        "percentile": avg_percentile,
                        "importance": group_info["importance"]
                    })

        # Add individual exceptional stats
        for stat in scouting_report:
            if stat['percentile'] >= EXCEPTIONAL:
                analysis["exceptional_abilities"].append({
                    "stat": stat["stat"],
                    "percentile": stat["percentile"],
                    "value": stat["per_90"],
                    "type": "individual_stat"
                })

        # Generate summary
        analysis["summary"] = self._generate_strength_weakness_summary(analysis)
        
        return analysis

    def _get_rating_label(self, percentile: float) -> str:
        """Convert percentile to descriptive rating"""
        if percentile >= 90:
            return "Exceptional"
        elif percentile >= 75:
            return "Strong"
        elif percentile >= 60:
            return "Above Average"
        elif percentile >= 40:
            return "Average"
        elif percentile >= 25:
            return "Below Average"
        else:
            return "Poor"

    def _generate_strength_weakness_summary(self, analysis: Dict) -> str:
        """Generate a narrative summary of strengths and weaknesses"""
        summary_parts = []
        
        # Exceptional abilities
        if analysis["exceptional_abilities"]:
            exceptional = [item["category"] for item in analysis["exceptional_abilities"] 
                          if "category" in item]
            if exceptional:
                summary_parts.append(f"Exceptionally strong in {', '.join(exceptional)}")
        
        # Key strengths
        high_importance_strengths = [
            item["category"] for item in analysis["strengths"] 
            if item["importance"] == "high"
        ]
        if high_importance_strengths:
            summary_parts.append(f"Shows strong capability in {', '.join(high_importance_strengths)}")
        
        # Key weaknesses
        high_importance_weaknesses = [
            item["category"] for item in analysis["areas_of_concern"] 
            if item["importance"] == "high"
        ]
        if high_importance_weaknesses:
            summary_parts.append(f"Needs improvement in {', '.join(high_importance_weaknesses)}")
        
        return " | ".join(summary_parts)

    def _analyze_role_suitability(self, scouting_report: List, position: str) -> Dict:
        """
        Analyze player's suitability for different tactical roles
        based on their statistical profile
        """
        # Define role requirements and their stat weightings
        role_definitions = {
            "Advanced Playmaker": {
                "key_stats": {
                    "Progressive Passes": 0.20,
                    "xAG: Exp. Assisted Goals": 0.20,
                    "Shot-Creating Actions": 0.15,
                    "Progressive Carries": 0.15,
                    "Pass Completion %": 0.15,
                    "Successful Take-Ons": 0.15
                },
                "suitable_positions": ["MF", "FW-MF"],
                "description": "Creates chances and progresses play from advanced positions"
            },
            "Inside Forward": {
                "key_stats": {
                    "Non-Penalty Goals": 0.20,
                    "npxG: Non-Penalty xG": 0.20,
                    "Shots Total": 0.15,
                    "Progressive Carries": 0.15,
                    "Successful Take-Ons": 0.15,
                    "Touches (Att Pen)": 0.15
                },
                "suitable_positions": ["FW", "FW-MF"],
                "description": "Cuts inside to create and score goals"
            },
            "Complete Forward": {
                "key_stats": {
                    "Non-Penalty Goals": 0.15,
                    "npxG: Non-Penalty xG": 0.15,
                    "Assists": 0.15,
                    "xAG: Exp. Assisted Goals": 0.15,
                    "Shot-Creating Actions": 0.10,
                    "Aerials Won": 0.15,
                    "Progressive Passes Rec": 0.15
                },
                "suitable_positions": ["FW"],
                "description": "All-round striker combining scoring and creating"
            },
            "Box-to-Box Midfielder": {
                "key_stats": {
                    "Progressive Passes": 0.15,
                    "Progressive Carries": 0.15,
                    "Tackles": 0.15,
                    "Interceptions": 0.15,
                    "Shot-Creating Actions": 0.10,
                    "Pass Completion %": 0.15,
                    "Progressive Passes Rec": 0.15
                },
                "suitable_positions": ["MF"],
                "description": "Dynamic midfielder contributing in both attack and defense"
            },
            "Pressing Forward": {
                "key_stats": {
                    "Tackles": 0.20,
                    "Interceptions": 0.15,
                    "Non-Penalty Goals": 0.15,
                    "npxG: Non-Penalty xG": 0.15,
                    "Progressive Passes Rec": 0.15,
                    "Shot-Creating Actions": 0.20
                },
                "suitable_positions": ["FW", "FW-MF"],
                "description": "Forward who excels in pressing and defensive contribution"
            }
        }

        # Calculate role suitability scores
        role_scores = {}
        stat_dict = {stat['stat']: stat for stat in scouting_report}

        for role, definition in role_definitions.items():
            # Check position suitability first
            if not any(pos in position for pos in definition["suitable_positions"]):
                continue

            # Calculate weighted score
            total_weight = 0
            weighted_score = 0

            for stat, weight in definition["key_stats"].items():
                if stat in stat_dict:
                    weighted_score += stat_dict[stat]["percentile"] * weight
                    total_weight += weight

            if total_weight > 0:
                final_score = round(weighted_score / total_weight, 2)
                role_scores[role] = {
                    "score": final_score,
                    "rating": self._get_role_suitability_rating(final_score),
                    "key_attributes": self._get_key_attributes_for_role(stat_dict, definition["key_stats"]),
                    "description": definition["description"]
                }

        # Sort roles by suitability
        sorted_roles = sorted(role_scores.items(), key=lambda x: x[1]["score"], reverse=True)

        return {
            "primary_role": sorted_roles[0][0] if sorted_roles else None,
            "secondary_role": sorted_roles[1][0] if len(sorted_roles) > 1 else None,
            "role_scores": role_scores,
            "detailed_analysis": self._generate_role_analysis(sorted_roles, role_scores),
            "development_suggestions": self._generate_role_development_suggestions(sorted_roles, stat_dict)
        }

    def _get_role_suitability_rating(self, score: float) -> str:
        """Convert numerical score to descriptive rating"""
        if score >= 85:
            return "Perfect Fit"
        elif score >= 75:
            return "Strong Fit"
        elif score >= 65:
            return "Good Fit"
        elif score >= 55:
            return "Decent Fit"
        else:
            return "Poor Fit"

    def _get_key_attributes_for_role(self, stat_dict: Dict, key_stats: Dict) -> List[Dict]:
        """Identify key attributes that make player suitable/unsuitable for role"""
        attributes = []
        for stat, weight in key_stats.items():
            if stat in stat_dict:
                percentile = stat_dict[stat]["percentile"]
                attributes.append({
                    "stat": stat,
                    "percentile": percentile,
                    "value": stat_dict[stat]["per_90"],
                    "is_strength": percentile >= 70
                })
        return sorted(attributes, key=lambda x: x["percentile"], reverse=True)

    def _generate_role_analysis(self, sorted_roles: List, role_scores: Dict) -> str:
        """Generate detailed analysis of role suitability"""
        if not sorted_roles:
            return "Insufficient data for role analysis"

        primary_role = sorted_roles[0]
        analysis_parts = [
            f"Best suited as a {primary_role[0]} ({primary_role[1]['rating']}, {primary_role[1]['score']}%)"
        ]

        if len(sorted_roles) > 1:
            secondary_role = sorted_roles[1]
            analysis_parts.append(
                f"Can also perform as a {secondary_role[0]} ({secondary_role[1]['score']}%)"
            )

        return " | ".join(analysis_parts)

    def _generate_role_development_suggestions(self, sorted_roles: List, stat_dict: Dict) -> List[Dict]:
        """Generate suggestions for improving role suitability"""
        if not sorted_roles:
            return []

        primary_role = sorted_roles[0][0]
        role_stats = self.role_definitions[primary_role]["key_stats"]
        
        suggestions = []
        for stat, weight in role_stats.items():
            if stat in stat_dict and stat_dict[stat]["percentile"] < 70:
                suggestions.append({
                    "attribute": stat,
                    "current_percentile": stat_dict[stat]["percentile"],
                    "importance": "high" if weight >= 0.15 else "medium",
                    "target_percentile": 70
                })

        return sorted(suggestions, key=lambda x: x["importance"], reverse=True)

    def _analyze_development_areas(self, scouting_report: List, age: int) -> Dict:
        """
        Identify areas for development based on age, position, and current performance levels.
        Provides prioritized recommendations and development trajectory.
        """
        
        # Age-based development categories
        AGE_CATEGORIES = {
            "Young Prospect": (17, 21),
            "Developing Player": (22, 24),
            "Peak Years": (25, 29),
            "Experienced Pro": (30, 33),
            "Veteran": (34, 100)
        }

        # Development priority thresholds
        THRESHOLDS = {
            "Young Prospect": {
                "critical": 60,    # Below this needs urgent attention
                "important": 70,   # Below this needs improvement
                "polish": 85      # Below this could be enhanced
            },
            "Developing Player": {
                "critical": 65,
                "important": 75,
                "polish": 85
            },
            "Peak Years": {
                "critical": 70,
                "important": 80,
                "polish": 90
            },
            "Experienced Pro": {
                "critical": 65,
                "important": 75,
                "polish": 85
            },
            "Veteran": {
                "critical": 60,
                "important": 70,
                "polish": 80
            }
        }

        # Determine player's development category
        age_category = next(
            (cat for cat, (min_age, max_age) in AGE_CATEGORIES.items()
             if min_age <= age <= max_age),
            "Peak Years"
        )

        thresholds = THRESHOLDS[age_category]

        development_analysis = {
            "age_category": age_category,
            "development_stage": self._determine_development_stage(age, scouting_report),
            "priority_areas": {
                "critical": [],
                "important": [],
                "polish": []
            },
            "strengths_to_maintain": [],
            "development_trajectory": self._calculate_development_trajectory(age, scouting_report),
            "training_recommendations": []
        }

        # Analyze each stat for development needs
        for stat in scouting_report:
            percentile = stat['percentile']
            stat_info = {
                "stat": stat['stat'],
                "current_percentile": percentile,
                "current_value": stat['per_90'],
                "target_percentile": self._calculate_target_percentile(percentile, age_category)
            }

            if percentile < thresholds["critical"]:
                development_analysis["priority_areas"]["critical"].append(stat_info)
            elif percentile < thresholds["important"]:
                development_analysis["priority_areas"]["important"].append(stat_info)
            elif percentile < thresholds["polish"]:
                development_analysis["priority_areas"]["polish"].append(stat_info)
            elif percentile >= 85:
                development_analysis["strengths_to_maintain"].append(stat_info)

        # Generate training recommendations
        development_analysis["training_recommendations"] = self._generate_training_recommendations(
            development_analysis["priority_areas"],
            age_category
        )

        # Add development summary
        development_analysis["summary"] = self._generate_development_summary(development_analysis)

        return development_analysis

    def _determine_development_stage(self, age: int, scouting_report: List) -> Dict:
        """Determine player's current development stage and potential"""
        
        avg_percentile = sum(stat['percentile'] for stat in scouting_report) / len(scouting_report)
        
        return {
            "current_level": self._get_development_level(avg_percentile),
            "potential_level": self._estimate_potential_level(age, avg_percentile),
            "years_to_peak": max(0, 27 - age),  # Assuming 27 is typical peak age
            "development_phase": self._get_development_phase(age, avg_percentile)
        }

    def _calculate_development_trajectory(self, age: int, scouting_report: List) -> Dict:
        """Calculate expected development trajectory"""
        
        avg_percentile = sum(stat['percentile'] for stat in scouting_report) / len(scouting_report)
        
        trajectory = {
            "current_level": avg_percentile,
            "projected_peak": min(99, self._project_peak_level(age, avg_percentile)),
            "development_potential": self._calculate_potential_rating(age, avg_percentile),
            "time_to_peak": self._estimate_time_to_peak(age),
            "development_speed": self._estimate_development_speed(age)
        }
        
        return trajectory

    def _generate_training_recommendations(self, priority_areas: Dict, age_category: str) -> List[Dict]:
        """Generate specific training recommendations based on priority areas"""
        
        recommendations = []
        
        # Training focus areas based on stat categories
        training_areas = {
            "Non-Penalty Goals": ["Finishing drills", "Shooting practice", "Positioning exercises"],
            "Progressive Passes": ["Pass accuracy drills", "Vision training", "Decision making exercises"],
            "Successful Take-Ons": ["Dribbling drills", "1v1 situations", "Close control exercises"],
            "Tackles": ["Defensive positioning", "Tackling technique", "Defensive awareness"],
            # Add more training areas as needed
        }
        
        # Generate recommendations for critical areas first
        for priority_level in ["critical", "important", "polish"]:
            for stat_info in priority_areas[priority_level]:
                stat_name = stat_info["stat"]
                if stat_name in training_areas:
                    recommendations.append({
                        "area": stat_name,
                        "priority": priority_level,
                        "current_level": stat_info["current_percentile"],
                        "target_level": stat_info["target_percentile"],
                        "exercises": training_areas[stat_name],
                        "focus_level": "High" if priority_level == "critical" else "Medium"
                    })

        return recommendations

    def _generate_development_summary(self, analysis: Dict) -> str:
        """Generate a narrative summary of development needs"""
        
        summary_parts = []
        
        # Add age category context
        summary_parts.append(f"Player is in {analysis['age_category']} phase")
        
        # Add critical priorities if any
        if analysis['priority_areas']['critical']:
            critical_stats = [item['stat'] for item in analysis['priority_areas']['critical']]
            summary_parts.append(f"Urgent development needed in: {', '.join(critical_stats)}")
        
        # Add development trajectory
        trajectory = analysis['development_trajectory']
        summary_parts.append(
            f"Projected to peak at {trajectory['projected_peak']:.1f} percentile "
            f"in {trajectory['time_to_peak']} years"
        )
        
        return " | ".join(summary_parts)

    def _calculate_target_percentile(self, current_percentile: float, age_category: str) -> float:
        """Calculate target percentile based on current level and age category"""
        if age_category in ["Young Prospect", "Developing Player"]:
            return min(95, current_percentile + 15)
        elif age_category == "Peak Years":
            return min(95, current_percentile + 10)
        else:
            return min(95, current_percentile + 5)

    def _get_development_level(self, percentile: float) -> str:
        """Determine player's current development level based on percentile"""
        if percentile >= 90:
            return "World Class"
        elif percentile >= 80:
            return "Elite"
        elif percentile >= 70:
            return "Advanced"
        elif percentile >= 60:
            return "Established"
        elif percentile >= 50:
            return "Developing"
        else:
            return "Basic"

    def _estimate_potential_level(self, age: int, current_percentile: float) -> str:
        """Estimate player's potential level based on age and current performance"""
        potential_increase = {
            # age: maximum potential percentile increase
            17: 30,
            18: 28,
            19: 26,
            20: 24,
            21: 22,
            22: 20,
            23: 15,
            24: 10,
            25: 5,
            26: 3,
        }
        
        # Get potential increase based on age
        max_increase = potential_increase.get(age, 0)
        if age > 26:
            max_increase = max(0, 3 - (age - 26))  # Decreasing potential after 26
            
        projected_percentile = min(99, current_percentile + max_increase)
        return self._get_development_level(projected_percentile)

    def _get_development_phase(self, age: int, percentile: float) -> str:
        """Determine player's development phase"""
        if age <= 20:
            return "Early Development"
        elif age <= 23:
            return "Rapid Development"
        elif age <= 26:
            return "Peak Development"
        elif age <= 29:
            return "Prime"
        elif age <= 32:
            return "Experienced"
        else:
            return "Veteran"

    def _project_peak_level(self, age: int, current_percentile: float) -> float:
        """Project player's peak level"""
        potential_increase = self._calculate_potential_increase(age)
        return min(99, current_percentile + potential_increase)

    def _calculate_potential_increase(self, age: int) -> float:
        """Calculate potential percentile increase based on age"""
        if age <= 20:
            return 25.0
        elif age <= 23:
            return 20.0 - (age - 20) * 3
        elif age <= 26:
            return 10.0 - (age - 23) * 2
        elif age <= 29:
            return 5.0 - (age - 26)
        else:
            return 0.0

    def _calculate_potential_rating(self, age: int, current_percentile: float) -> str:
        """Calculate potential rating category"""
        potential_percentile = self._project_peak_level(age, current_percentile)
        
        if potential_percentile >= 90:
            return "World Class Potential"
        elif potential_percentile >= 80:
            return "Elite Potential"
        elif potential_percentile >= 70:
            return "High Potential"
        elif potential_percentile >= 60:
            return "Good Potential"
        else:
            return "Limited Potential"

    def _estimate_time_to_peak(self, age: int) -> int:
        """Estimate years until player reaches peak"""
        typical_peak_age = 27
        years_to_peak = typical_peak_age - age
        return max(0, years_to_peak)

    def _estimate_development_speed(self, age: int) -> str:
        """Estimate the speed of development based on age"""
        if age <= 20:
            return "Rapid"
        elif age <= 23:
            return "Fast"
        elif age <= 26:
            return "Normal"
        elif age <= 29:
            return "Gradual"
        else:
            return "Limited"

    def _check_data_completeness(self, player_data: Dict) -> float:
        """Check how complete the player data is"""
        required_fields = [
            'general_info',
            'current_season_stats',
            'scouting_report'
        ]
        
        completeness = sum(1 for field in required_fields if field in player_data)
        return completeness / len(required_fields)

    def _check_sample_size(self, player_data: Dict) -> float:
        """Check if there's enough data for reliable analysis"""
        try:
            total_minutes = sum(
                int(stats['minutes']) 
                for competition in player_data['current_season_stats'].values()
                for stats in [competition]
            )
            # Consider anything over 900 minutes (10 full games) as good sample size
            return min(1.0, total_minutes / 900)
        except:
            return 0.5

    def _check_data_recency(self, player_data: Dict) -> float:
        """Check how recent the data is"""
        # For now, return 1.0 as we're using current season data
        return 1.0

    def _analyze_current_season_stats(self, season_stats: Dict) -> Dict:
        """Analyze current season statistics across competitions"""
        try:
            analysis = {
                "by_competition": {},
                "overall": {
                    "total_minutes": 0,
                    "total_matches": 0,
                    "goals_per_90": 0,
                    "assists_per_90": 0,
                    "goal_contributions": 0,
                    "minutes_per_match": 0
                },
                "performance_trends": {}
            }

            total_minutes = 0
            total_matches = 0
            total_goals = 0
            total_assists = 0

            # Analyze each competition
            for competition, stats in season_stats.items():
                minutes = float(stats.get('minutes', 0))
                matches = int(stats.get('matches', 0))
                goals = int(stats.get('goals', 0))
                assists = int(stats.get('assists', 0))
                
                # Calculate per-90 stats
                minutes_per_match = minutes / matches if matches > 0 else 0
                goals_per_90 = (goals * 90) / minutes if minutes > 0 else 0
                assists_per_90 = (assists * 90) / minutes if minutes > 0 else 0
                
                analysis["by_competition"][competition] = {
                    "minutes_played": minutes,
                    "matches_played": matches,
                    "goals": goals,
                    "assists": assists,
                    "goals_per_90": round(goals_per_90, 2),
                    "assists_per_90": round(assists_per_90, 2),
                    "minutes_per_match": round(minutes_per_match, 2),
                    "goal_contributions": goals + assists,
                    "expected_stats": {
                        "xG": float(stats.get('expected_goals', 0)),
                        "xA": float(stats.get('expected_assists', 0)),
                        "npxG": float(stats.get('non_penalty_xg', 0))
                    }
                }

                # Accumulate totals
                total_minutes += minutes
                total_matches += matches
                total_goals += goals
                total_assists += assists

            # Calculate overall stats
            if total_minutes > 0:
                analysis["overall"] = {
                    "total_minutes": total_minutes,
                    "total_matches": total_matches,
                    "goals_per_90": round((total_goals * 90) / total_minutes, 2),
                    "assists_per_90": round((total_assists * 90) / total_minutes, 2),
                    "goal_contributions": total_goals + total_assists,
                    "minutes_per_match": round(total_minutes / total_matches, 2) if total_matches > 0 else 0
                }

            # Add performance assessment
            analysis["performance_assessment"] = self._assess_performance_level(
                analysis["overall"],
                analysis["by_competition"]
            )

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing season stats: {str(e)}")
            return {
                "error": "Could not analyze season stats",
                "by_competition": {},
                "overall": {},
                "performance_trends": {}
            }

    def _assess_performance_level(self, overall_stats: Dict, competition_stats: Dict) -> Dict:
        """Assess the player's performance level based on stats"""
        assessment = {
            "scoring_efficiency": "Average",
            "playing_time": "Regular",
            "contribution_level": "Medium",
            "performance_consistency": "Stable"
        }

        # Assess playing time
        if overall_stats["total_minutes"] > 1800:  # 20 full matches
            assessment["playing_time"] = "Key Player"
        elif overall_stats["total_minutes"] > 900:  # 10 full matches
            assessment["playing_time"] = "Regular"
        else:
            assessment["playing_time"] = "Rotation"

        # Assess scoring efficiency
        goals_per_90 = overall_stats["goals_per_90"]
        if goals_per_90 > 0.7:
            assessment["scoring_efficiency"] = "Excellent"
        elif goals_per_90 > 0.4:
            assessment["scoring_efficiency"] = "Good"
        elif goals_per_90 > 0.2:
            assessment["scoring_efficiency"] = "Average"
        else:
            assessment["scoring_efficiency"] = "Below Average"

        # Assess overall contribution
        contributions = overall_stats["goal_contributions"]
        if contributions > 15:
            assessment["contribution_level"] = "High"
        elif contributions > 8:
            assessment["contribution_level"] = "Medium"
        else:
            assessment["contribution_level"] = "Low"

        return assessment

    def _generate_tactical_recommendations(self, detailed_analysis: Dict, role_suitability: Dict) -> Dict:
        """Generate tactical recommendations based on player profile"""
        try:
            # Extract key information
            playing_style = detailed_analysis['performance_profile']['playing_style']
            strengths = detailed_analysis['performance_profile']['strengths_weaknesses']
            position = detailed_analysis['player_info']['position']

            recommendations = {
                "optimal_roles": [],
                "formation_fit": [],
                "tactical_instructions": [],
                "team_role": "",
                "attacking_recommendations": {},
                "defensive_recommendations": {},
                "positional_recommendations": {}
            }

            # Determine optimal roles based on role suitability
            sorted_roles = sorted(
                role_suitability['role_scores'].items(),
                key=lambda x: x[1]['score'],
                reverse=True
            )
            recommendations["optimal_roles"] = [
                {
                    "role": role,
                    "score": data['score'],
                    "description": data.get('description', '')
                }
                for role, data in sorted_roles[:3]  # Top 3 roles
            ]

            # Formation recommendations based on position and playing style
            formations = self._get_suitable_formations(position, playing_style)
            recommendations["formation_fit"] = formations

            # Generate attacking recommendations
            recommendations["attacking_recommendations"] = {
                "primary_role": self._get_attacking_role(playing_style, strengths),
                "movement_type": self._get_movement_recommendations(playing_style),
                "key_actions": self._get_key_attacking_actions(strengths),
                "positioning": self._get_positioning_recommendations(position, playing_style)
            }

            # Generate defensive recommendations
            recommendations["defensive_recommendations"] = {
                "pressing_intensity": self._get_pressing_intensity(strengths),
                "defensive_position": self._get_defensive_position(position),
                "marking_style": self._get_marking_style(strengths),
                "transition_role": self._get_transition_role(playing_style, position)
            }

            # Generate positional recommendations
            recommendations["positional_recommendations"] = {
                "average_position": self._get_average_position(position, playing_style),
                "movement_range": self._get_movement_range(playing_style),
                "defensive_responsibility": self._get_defensive_responsibility(position)
            }

            # Generate tactical instructions
            recommendations["tactical_instructions"] = self._generate_tactical_instructions(
                playing_style,
                strengths,
                position
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error generating tactical recommendations: {str(e)}")
            return {
                "error": "Could not generate tactical recommendations",
                "optimal_roles": [],
                "formation_fit": [],
                "tactical_instructions": []
            }

    def _get_suitable_formations(self, position: str, playing_style: Dict) -> List[Dict]:
        """Determine suitable formations based on position and playing style"""
        formations = []
        
        if "FW" in position:
            formations.extend([
                {"formation": "4-3-3", "role": "Wide Forward", "suitability": "High"},
                {"formation": "4-2-3-1", "role": "Winger", "suitability": "High"},
                {"formation": "3-5-2", "role": "Forward", "suitability": "Medium"}
            ])
        elif "MF" in position:
            formations.extend([
                {"formation": "4-3-3", "role": "Midfielder", "suitability": "High"},
                {"formation": "4-2-3-1", "role": "Attacking Midfielder", "suitability": "High"},
                {"formation": "3-5-2", "role": "Central Midfielder", "suitability": "Medium"}
            ])
        
        return formations

    def _get_attacking_role(self, playing_style: Dict, strengths: Dict) -> str:
        """Determine primary attacking role"""
        if playing_style.get('primary_style') == "Playmaker":
            return "Creative Hub"
        elif playing_style.get('primary_style') == "Goal Scorer":
            return "Primary Scorer"
        return "Supporting Attacker"

    def _get_movement_recommendations(self, playing_style: Dict) -> List[str]:
        """Generate movement recommendations based on playing style"""
        movements = []
        primary_style = playing_style.get('primary_style', '')
        
        if "Dribbler" in primary_style:
            movements.extend(["Cut inside", "Take on defenders", "Progressive carries"])
        elif "Playmaker" in primary_style:
            movements.extend(["Find space between lines", "Support build-up", "Late runs into box"])
        
        return movements

    def _get_key_attacking_actions(self, strengths: Dict) -> List[str]:
        """Determine key attacking actions based on strengths"""
        actions = []
        for strength in strengths.get('strengths', []):
            if "Finishing" in strength['category']:
                actions.append("Shoot on sight")
            elif "Creativity" in strength['category']:
                actions.append("Look for through balls")
        return actions

    def _get_positioning_recommendations(self, position: str, playing_style: Dict) -> Dict:
        """Generate positioning recommendations"""
        return {
            "attacking_position": "Advanced" if "FW" in position else "Supporting",
            "defensive_position": "Press high" if "FW" in position else "Track back",
            "width": "Wide" if "Dribbler" in str(playing_style.get('primary_style')) else "Narrow"
        }

    def _get_pressing_intensity(self, strengths: Dict) -> str:
        """Determine recommended pressing intensity"""
        defensive_stats = next(
            (s for s in strengths.get('skill_groups', {}).items() 
            if 'Defensive' in s[0]),
            None
        )
        
        if defensive_stats and defensive_stats[1]['average_percentile'] > 75:
            return "High"
        elif defensive_stats and defensive_stats[1]['average_percentile'] > 50:
            return "Medium"
        return "Low"

    def _get_defensive_position(self, position: str) -> str:
        """Determine defensive positioning"""
        if "FW" in position:
            return "First line of press"
        elif "MF" in position:
            return "Screen opposition midfield"
        return "Maintain defensive shape"

    def _get_marking_style(self, strengths: Dict) -> str:
        """Determine appropriate marking style"""
        return "Tight marking" if any(
            s['category'] == "Defensive Contribution" and s['percentile'] > 70
            for s in strengths.get('strengths', [])
        ) else "Zonal marking"

    def _get_transition_role(self, playing_style: Dict, position: str) -> str:
        """Determine role in transitions"""
        if "FW" in position:
            return "Counter-attacking outlet"
        return "Support counter-attacks"

    def _get_average_position(self, position: str, playing_style: Dict) -> str:
        """Determine recommended average position"""
        if "FW" in position:
            return "High and wide"
        return "Central midfield"

    def _get_movement_range(self, playing_style: Dict) -> str:
        """Determine recommended movement range"""
        if "Box Presence" in str(playing_style.get('primary_style')):
            return "Stay central"
        return "Roam from position"

    def _get_defensive_responsibility(self, position: str) -> str:
        """Determine defensive responsibilities"""
        if "FW" in position:
            return "Press opposition defense"
        return "Track back and defend"

    def _generate_tactical_instructions(self, playing_style: Dict, strengths: Dict, position: str) -> List[str]:
        """Generate specific tactical instructions"""
        instructions = []
        
        # Add position-specific instructions
        if "FW" in position:
            instructions.extend([
                "Stay forward for counter-attacks",
                "Look for through balls"
            ])
        elif "MF" in position:
            instructions.extend([
                "Support attacks",
                "Track back when possession is lost"
            ])
        
        return instructions