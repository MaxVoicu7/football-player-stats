import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
from datetime import datetime

class PlayerScraper:
    def extract_age(self, birth_date_text):
        try:
            if not birth_date_text:
                return None
                
            # First try to find age directly
            age_match = re.search(r'\(Age: (\d+)', birth_date_text)
            if age_match:
                return int(age_match.group(1))
                
            # If no direct age, calculate from birth date
            # Example format: "July 13, 2007"
            birth_date = datetime.strptime(birth_date_text.strip(), '%B %d, %Y')
            today = datetime.today()
            age = today.year - birth_date.year
            
            # Adjust age if birthday hasn't occurred this year
            if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
                age -= 1
                
            return age
            
        except Exception as e:
            print(f"Error extracting age: {e}")
            return None

    def search_player(self, name):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            search_url = f"https://fbref.com/search/search.fcgi?search={quote(name)}"
            response = requests.get(search_url, headers=headers)
            
            if '/players/' not in response.url:
                return {
                    'success': False,
                    'error': 'Player not found'
                }

            soup = BeautifulSoup(response.text, 'html.parser')
            meta_div = soup.find('div', id='meta')
            
            if not meta_div:
                return {
                    'success': False,
                    'error': 'Could not find player info'
                }

            # Get birth date text
            birth_date_element = meta_div.find('span', id='necro-birth')
            birth_date_text = birth_date_element.text.strip() if birth_date_element else None
            
            # Extract basic info
            player_info = {
                'general_info': {
                    'photo_url': meta_div.find('img')['src'] if meta_div.find('img') else None,
                    'name': meta_div.find('h1').text.strip() if meta_div.find('h1') else None,
                    'position': next((p.text.split('▪')[0].replace('Position:', '').strip() 
                                   for p in meta_div.find_all('p') if 'Position:' in p.text), None),
                    'age': self.extract_age(birth_date_text),
                    'national_team': next((p.find('a').text.strip() 
                                        for p in meta_div.find_all('p') if 'National Team:' in p.text), None),
                    'club': next((p.find('a').text.strip() 
                                for p in meta_div.find_all('p') if 'Club:' in p.text), None),
                }
            }

            # Get current season stats
            stats_div = soup.find('div', class_='stats_pullout')
            if stats_div:
                # Get competition names, filtering out the season header
                competition_elements = stats_div.select('div > div > p strong')
                competitions = [comp.text.strip() for comp in competition_elements 
                              if not comp.text.strip().startswith('20')]
                print(f"\nFound competitions: {competitions}")
                
                current_season_stats = {}
                
                # Get all stat values
                matches = [p.text.strip() for p in stats_div.select('div.p1 div:nth-child(1) p')]
                minutes = [p.text.strip() for p in stats_div.select('div.p1 div:nth-child(2) p')]
                goals = [p.text.strip() for p in stats_div.select('div.p1 div:nth-child(3) p')]
                assists = [p.text.strip() for p in stats_div.select('div.p1 div:nth-child(4) p')]
                xg = [p.text.strip() for p in stats_div.select('div.p2 div:nth-child(1) p')]
                npxg = [p.text.strip() for p in stats_div.select('div.p2 div:nth-child(2) p')]
                xa = [p.text.strip() for p in stats_div.select('div.p2 div:nth-child(3) p')]
                sca = [p.text.strip() for p in stats_div.select('div.p3 div:nth-child(1) p')]
                gca = [p.text.strip() for p in stats_div.select('div.p3 div:nth-child(2) p')]
                
                # For each competition
                for i, competition in enumerate(competitions):
                    print(f"\nProcessing {competition} (index {i}):")
                    
                    try:
                        stats = {
                            'matches': matches[i],
                            'minutes': minutes[i],
                            'goals': goals[i],
                            'assists': assists[i],
                            'expected_goals': xg[i],
                            'non_penalty_xg': npxg[i],
                            'expected_assists': xa[i],
                            'shot_creating_actions': sca[i],
                            'goal_creating_actions': gca[i]
                        }
                        print(f"Extracted stats: {stats}")
                        current_season_stats[competition] = stats
                        
                    except Exception as e:
                        print(f"Error extracting stats for {competition}: {e}")
                        current_season_stats[competition] = {
                            'matches': "0",
                            'minutes': "0",
                            'goals': "0",
                            'assists': "0",
                            'expected_goals': "0",
                            'non_penalty_xg': "0",
                            'expected_assists': "0",
                            'shot_creating_actions': "0",
                            'goal_creating_actions': "0"
                        }
                
                player_info['current_season_stats'] = current_season_stats

            # Get scouting report - using a more flexible approach
            scouting_report = []
            
            # Find all divs that start with 'div_scout_summary_'
            scouting_divs = soup.find_all('div', id=lambda x: x and x.startswith('div_scout_summary_'))
            print(f"Found {len(scouting_divs)} scouting report divs")
            
            if scouting_divs:
                # Use the first scouting div found (usually there's only one per player)
                scouting_div = scouting_divs[0]
                print(f"Using scouting div with ID: {scouting_div.get('id', 'unknown')}")
                
                # Get all stat rows
                stat_rows = scouting_div.select('tbody tr')
                print(f"Found {len(stat_rows)} stat rows")
                
                for row in stat_rows:
                    # Skip spacer rows
                    if 'spacer' in row.get('class', []):
                        continue
                        
                    try:
                        stat_name = row.find('th', {'data-stat': 'statistic'}).text.strip()
                        per90_value = row.find('td', {'data-stat': 'per90'}).text.strip()
                        percentile = row.find('td', {'data-stat': 'percentile'}).select_one('div').text.strip()
                        
                        scouting_report.append({
                            'stat': stat_name,
                            'per_90': per90_value,
                            'percentile': int(percentile)
                        })
                        print(f"Processed stat: {stat_name}")
                    except Exception as e:
                        print(f"Error processing stat row: {e}")
                        continue
            else:
                print("No scouting report div found")
            
            player_info['scouting_report'] = scouting_report

            return {
                'success': True,
                'data': player_info
            }
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e)
            }