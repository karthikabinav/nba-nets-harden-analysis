import urllib.request
import urllib.parse
import json
import sys

def fetch_nba_games(team_id, season_year):
    """Fetch NBA games for a team in a specific season"""
    # Using the balldontlie API
    base_url = "https://www.balldontlie.io/api/v1/games"
    
    all_games = []
    page = 1
    per_page = 100
    
    while True:
        params = {
            'team_ids[]': team_id,
            'seasons[]': season_year,
            'per_page': per_page,
            'page': page
        }
        
        url = f"{base_url}?{urllib.parse.urlencode(params)}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode())
                games = data.get('data', [])
                
                if not games:
                    break
                    
                all_games.extend(games)
                
                meta = data.get('meta', {})
                if not meta.get('next_cursor'):
                    break
                    
                page += 1
                
                # Safety limit
                if page > 10:
                    break
                    
        except Exception as e:
            print(f"Error fetching data for season {season_year}: {e}")
            break
    
    return all_games

def find_first_game_of_season(games):
    """Find the first game of a season (chronologically)"""
    if not games:
        return None
    
    # Filter for regular season games only
    regular_season_games = [g for g in games if not g.get('postseason', False)]
    
    if not regular_season_games:
        return None
    
    # Sort by date
    sorted_games = sorted(regular_season_games, key=lambda x: x.get('date', ''))
    return sorted_games[0]

def find_harden_first_game_with_nets(games):
    """Find James Harden's first game with the Nets (after trade in Jan 2021)"""
    if not games:
        return None
    
    # Filter for games after January 1, 2021 (when trade happened)
    # The trade was on Jan 13, 2021, so we look for games after that date
    filtered_games = [
        g for g in games 
        if g.get('date', '') > '2021-01-13' and not g.get('postseason', False)
    ]
    
    if not filtered_games:
        return None
    
    # Sort by date and get the first one
    sorted_games = sorted(filtered_games, key=lambda x: x.get('date', ''))
    return sorted_games[0]

def main():
    print("=" * 70)
    print("Brooklyn Nets - James Harden Trade Analysis")
    print("=" * 70)
    
    nets_team_id = 3  # Brooklyn Nets
    
    # 1. Get Nets' first game with James Harden (2020-21 season)
    print("\n1. Fetching Nets' first game with James Harden (2020-21 season)...")
    games_2020_21 = fetch_nba_games(nets_team_id, 2020)
    harden_first_game = find_harden_first_game_with_nets(games_2020_21)
    
    if harden_first_game:
        nets_score_harden = harden_first_game.get('home_team', {}).get('id') == nets_team_id
        if nets_score_harden:
            nets_points_harden = harden_first_game.get('home_team_score', 0)
        else:
            nets_points_harden = harden_first_game.get('visitor_team_score', 0)
        
        opponent_harden = (
            harden_first_game.get('visitor_team', {}).get('abbreviation')
            if nets_score_harden
            else harden_first_game.get('home_team', {}).get('abbreviation')
        )
        
        print(f"   Date: {harden_first_game.get('date', '')[:10]}")
        print(f"   Opponent: {opponent_harden}")
        print(f"   Nets Points: {nets_points_harden}")
        print(f"   Game: Brooklyn Nets vs {opponent_harden}")
    else:
        print("   ERROR: Could not find Harden's first game")
        # Fallback to known data
        nets_points_harden = 122
        print(f"   Using known value: Nets scored {nets_points_harden} points")
    
    # 2. Get Nets' first game of the previous season (2019-20 season)
    print("\n2. Fetching Nets' first game of the 2019-20 season...")
    games_2019_20 = fetch_nba_games(nets_team_id, 2019)
    first_game_2019 = find_first_game_of_season(games_2019_20)
    
    if first_game_2019:
        nets_score_first_2019 = first_game_2019.get('home_team', {}).get('id') == nets_team_id
        if nets_score_first_2019:
            nets_points_2019 = first_game_2019.get('home_team_score', 0)
        else:
            nets_points_2019 = first_game_2019.get('visitor_team_score', 0)
        
        opponent_2019 = (
            first_game_2019.get('visitor_team', {}).get('abbreviation')
            if nets_score_first_2019
            else first_game_2019.get('home_team', {}).get('abbreviation')
        )
        
        print(f"   Date: {first_game_2019.get('date', '')[:10]}")
        print(f"   Opponent: {opponent_2019}")
        print(f"   Nets Points: {nets_points_2019}")
        print(f"   Game: Brooklyn Nets vs {opponent_2019}")
    else:
        print("   ERROR: Could not find first game of 2019-20 season")
        # Fallback to known data
        nets_points_2019 = 126
        print(f"   Using known value: Nets scored {nets_points_2019} points")
    
    # 3. Comparison
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    
    print(f"\nNets points in first game WITH Harden (2020-21): {nets_points_harden}")
    print(f"Nets points in first game of PREVIOUS season (2019-20): {nets_points_2019}")
    
    if nets_points_harden > nets_points_2019:
        print(f"\n✓ YES, the Nets scored MORE points with Harden!")
        diff = nets_points_harden - nets_points_2019
        print(f"  Difference: +{diff} points")
    elif nets_points_harden < nets_points_2019:
        print(f"\n✗ NO, the Nets scored FEWER points with Harden")
        diff = nets_points_2019 - nets_points_harden
        print(f"  Difference: -{diff} points (Nets scored {diff} fewer points)")
    else:
        print(f"\n= The Nets scored the SAME number of points")
        print(f"  Difference: 0 points")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    main()