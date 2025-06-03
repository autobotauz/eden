import numpy as np
from collections import defaultdict
import json
import glob
import os

# Class ID to name and role mapping
CLASS_TO_ROLE = {
    1: {'name': 'Paladin', 'role': 'Tank'},
    2: {'name': 'Armsman', 'role': 'Tank'},
    3: {'name': 'Scout', 'role': 'DPS'},
    4: {'name': 'Minstrel', 'role': 'DPS'},
    5: {'name': 'Theurgist', 'role': 'DPS'},
    6: {'name': 'Cleric', 'role': 'Healer'},
    7: {'name': 'Wizard', 'role': 'DPS'},
    8: {'name': 'Sorcerer', 'role': 'DPS'},
    9: {'name': 'Infiltrator', 'role': 'DPS'},
    10: {'name': 'Friar', 'role': 'Healer'},
    11: {'name': 'Mercenary', 'role': 'DPS'},
    12: {'name': 'Necromancer', 'role': 'DPS'},
    13: {'name': 'Cabalist', 'role': 'DPS'},
    19: {'name': 'Reaver', 'role': 'DPS'},
    21: {'name': 'Thane', 'role': 'DPS'},
    22: {'name': 'Warrior', 'role': 'Tank'},
    23: {'name': 'Shadowblade', 'role': 'DPS'},
    24: {'name': 'Skald', 'role': 'DPS'},
    25: {'name': 'Hunter', 'role': 'DPS'},
    26: {'name': 'Healer', 'role': 'Healer'},
    27: {'name': 'Spiritmaster', 'role': 'DPS'},
    28: {'name': 'Shaman', 'role': 'Healer'},
    29: {'name': 'Runemaster', 'role': 'DPS'},
    30: {'name': 'Bonedancer', 'role': 'DPS'},
    31: {'name': 'Berserker', 'role': 'DPS'},
    32: {'name': 'Savage', 'role': 'DPS'},
    33: {'name': 'Heretic', 'role': 'Healer'},
    34: {'name': 'Valkyrie', 'role': 'DPS'},
    39: {'name': 'Bainshee', 'role': 'DPS'},
    40: {'name': 'Eldritch', 'role': 'DPS'},
    41: {'name': 'Enchanter', 'role': 'DPS'},
    42: {'name': 'Mentalist', 'role': 'DPS'},
    43: {'name': 'Blademaster', 'role': 'DPS'},
    44: {'name': 'Hero', 'role': 'DPS'},
    45: {'name': 'Champion', 'role': 'DPS'},
    46: {'name': 'Warden', 'role': 'Healer'},
    47: {'name': 'Druid', 'role': 'Healer'},
    48: {'name': 'Bard', 'role': 'Healer'},
    49: {'name': 'Nightshade', 'role': 'DPS'},
    50: {'name': 'Ranger', 'role': 'DPS'},
    55: {'name': 'Animist', 'role': 'DPS'},
    56: {'name': 'Valewalker', 'role': 'DPS'},
    58: {'name': 'Vampiir', 'role': 'DPS'},
    59: {'name': 'Warlock', 'role': 'DPS'},
    63: {'name': 'Occultist', 'role': 'DPS'}
}

# Class-specific weights for MMR calculation
WEIGHTS = {
    'Healer': {
        'Win': 0.2,  # Reduced for 1v1 to balance performance
        'DD': 0.1,
        'HD': 0.4,  # Emphasize healing
        'DT': 0.15,
        'HT': 0.1,
        'ID': 0.025,
        'DiD': 0.025,
        'SD': 0.0   # Less relevant in 1v1
    },
    'DPS': {
        'Win': 0.2,
        'DD': 0.4,  # Emphasize damage
        'HD': 0.0,
        'DT': 0.2,
        'HT': 0.0,
        'ID': 0.1,
        'DiD': 0.05,
        'SD': 0.05
    },
    'Tank': {
        'Win': 0.2,
        'DD': 0.15,
        'HD': 0.0,
        'DT': 0.4,  # Emphasize damage taken
        'HT': 0.15,
        'ID': 0.05,
        'DiD': 0.025,
        'SD': 0.025
    }
}

# Fixed maximum values for 1v1 normalization (adjust based on DAoC 1v1 data)
MAX_VALUES_1V1 = {
    'DD': 10000,   # Typical max damage dealt
    'HD': 5000,    # Typical max healing dealt
    'DT': 10000,   # Typical max damage taken
    'HT': 5000,    # Typical max healing taken
    'ID': 10,      # Typical max interrupts
    'SD': 5,       # Typical max stuns
    'DiD': 1000    # Typical max disease damage
}

def normalize_metrics(match_data, is_1v1=False):
    """Normalize metrics across all players in a match."""
    all_players = match_data['a']['p'] + match_data['b']['p']
    metrics = ['DD', 'DT', 'HD', 'HT', 'ID', 'SD', 'DiD']
    
    if is_1v1:
        # Absolute normalization for 1v1
        normalized_data = {'winning_team': [], 'losing_team': []}
        for team_key, players in [('winning_team', match_data['a']['p']), ('losing_team', match_data['b']['p'])]:
            for player in players:
                norm_player = player.copy()
                stats = player['s']
                norm_stats = {}
                for m in metrics:
                    raw_value = stats.get('dd' if m == 'DD' else 'hr' if m == 'HT' else 'ti' if m == 'ID' else 'ts' if m == 'SD' else m.lower(), 0)
                    if m == 'DiD':
                        raw_value = sum(stats.get('di', [])) if stats.get('di') else 0
                    # Normalize by fixed max, cap at 1
                    norm_stats[m + '_norm'] = min(raw_value / MAX_VALUES_1V1[m], 1.0)
                norm_player['s_norm'] = norm_stats
                normalized_data[team_key].append(norm_player)
        return normalized_data
    else:
        # Original min-max normalization for group matches
        metric_values = {m: [] for m in metrics}
        for player in all_players:
            stats = player['s']
            metric_values['DD'].append(stats.get('dd', 0))
            metric_values['DT'].append(stats.get('dt', 0))
            metric_values['HD'].append(stats.get('hd', 0))
            metric_values['HT'].append(stats.get('hr', 0))
            metric_values['ID'].append(stats.get('ti', 0))
            metric_values['SD'].append(stats.get('ts', 0))
            metric_values['DiD'].append(sum(stats.get('di', [])) if stats.get('di') else 0)
        
        min_values = {m: min(values) for m, values in metric_values.items()}
        max_values = {m: max(values) for m, values in metric_values.items()}
        
        normalized_data = {'winning_team': [], 'losing_team': []}
        for team_key, players in [('winning_team', match_data['a']['p']), ('losing_team', match_data['b']['p'])]:
            for player in players:
                norm_player = player.copy()
                stats = player['s']
                norm_stats = {}
                for m in metrics:
                    raw_value = stats.get('dd' if m == 'DD' else 'hr' if m == 'HT' else 'ti' if m == 'ID' else 'ts' if m == 'SD' else m.lower(), 0)
                    if m == 'DiD':
                        raw_value = sum(stats.get('di', [])) if stats.get('di') else 0
                    if max_values[m] > min_values[m]:
                        norm_stats[m + '_norm'] = (raw_value - min_values[m]) / (max_values[m] - min_values[m])
                    else:
                        norm_stats[m + '_norm'] = 0.0
                norm_player['s_norm'] = norm_stats
                normalized_data[team_key].append(norm_player)
        return normalized_data

def calculate_match_score(player, class_weights):
    """Calculate per-match score for a player based on normalized metrics and weights."""
    score = class_weights['Win'] * player['Win']
    metrics = ['DD', 'DT', 'HD', 'HT', 'ID', 'SD', 'DiD']
    for m in metrics:
        score += class_weights[m] * player['s_norm'].get(m + '_norm', 0.0)
    return score * 1000  # Scale to 0-1000

def calculate_mmr(directory_path):
    """Calculate MMR for each player and class type across all JSON files in the directory."""
    player_scores = defaultdict(list)
    class_scores = defaultdict(list)
    match_count = 0

    # Iterate through all JSON files in the directory
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                match_data = json.load(f)
            
            # Detect 1v1 match
            is_1v1 = len(match_data['a']['p']) == 1 and len(match_data['b']['p']) == 1
            
            norm_match = normalize_metrics(match_data, is_1v1)
            
            for team_key, win_status in [('winning_team', 1), ('losing_team', 0)]:
                for player in norm_match[team_key]:
                    player['Win'] = win_status
                    class_id = player['c']
                    class_info = CLASS_TO_ROLE.get(class_id, None)
                    if not class_info:
                        print(f"Warning: Unknown class ID {class_id} for player {player['n']} in file {file_path}")
                        continue
                    
                    class_name = class_info['name']
                    role = class_info['role']
                    
                    score = calculate_match_score(player, WEIGHTS[role])
                    player_scores[player['n']].append(score)
                    class_scores[class_name].append(score)
            
            match_count += 1
            if match_count % 100 == 0:
                print(f"Processed {match_count} files...")
        
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    # Calculate final MMRs
    player_mmr = {name: np.mean(scores) for name, scores in player_scores.items()}
    class_mmr = {class_name: np.mean(scores) for class_name, scores in class_scores.items()}
    
    return player_mmr, class_mmr, match_count

def save_mmr_results(player_mmr, class_mmr, output_file):
    """Save MMR results to a JSON file."""
    results = {
        'player_mmr': {name: float(mmr) for name, mmr in player_mmr.items()},
        'class_mmr': {class_name: float(mmr) for class_name, class_mmr in class_mmr.items()}
    }
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == '__main__':
    # Directory containing JSON files
    directory_path = "../fights_1"
    output_file = "mmr_results_1v1.json"
    
    print(f"Processing JSON files in {directory_path}...")
    player_mmr, class_mmr, match_count = calculate_mmr(directory_path)
    
    print(f"\nProcessed {match_count} matches.")
    print("\nIndividual Player MMR:")
    for name, mmr in sorted(player_mmr.items()):
        print(f"{name}: {mmr:.2f}")
    
    print("\nClass Type MMR:")
    for class_name, mmr in sorted(class_mmr.items()):
        print(f"{class_name}: {mmr:.2f}")
    
    # Save results to JSON
    save_mmr_results(player_mmr, class_mmr, output_file)
    print(f"\nMMR results saved to {output_file}")