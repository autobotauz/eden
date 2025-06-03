
import json
import glob
import os
from collections import defaultdict
from datetime import datetime
import numpy as np

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

def process_files(directory_path):
    """Process JSON files and aggregate metrics by class and date."""
    class_metrics = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                match_data = json.load(f)
            
            # Extract date from timestamp in 's' key
            timestamp_str = match_data.get('s', '1970-01-01T00:00:00Z')
            try:
                date = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
            except ValueError as e:
                print(f"Error parsing timestamp {timestamp_str} in file {file_path}: {e}")
                continue
            
            # Combine players from both teams
            all_players = match_data['a']['p'] + match_data['b']['p']
            
            for player in all_players:
                class_id = player.get('c')
                class_info = CLASS_TO_ROLE.get(class_id, None)
                if not class_info:
                    print(f"Warning: Unknown class ID {class_id} for player {player['n']} in file {file_path}")
                    continue
                
                class_name = class_info['name']
                stats = player.get('s', {})
                
                # Collect metrics
                metrics = {
                    'Damage': stats.get('dd', 0),
                    'Healing': stats.get('hd', 0),
                    'Interrupts': stats.get('ti', 0),
                    'Mez': stats.get('tm', 0),
                    'Shears': stats.get('ts', 0),
                    'Roots': stats.get('tr', 0),
                    'Disease': sum(stats.get('di', [])) if stats.get('di') else 0
                }
                
                # Store metrics by class and date
                for metric, value in metrics.items():
                    class_metrics[class_name][date][metric].append(value)
        
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    # Aggregate metrics (average per class per day)
    aggregated_metrics = defaultdict(lambda: defaultdict(dict))
    for class_name in class_metrics:
        for date in class_metrics[class_name]:
            for metric in class_metrics[class_name][date]:
                values = class_metrics[class_name][date][metric]
                aggregated_metrics[class_name][date][metric] = np.mean(values) if values else 0
    
    return aggregated_metrics

def generate_html_charts(aggregated_metrics):
    """Generate HTML with two Chart.js charts for the metrics."""
    # Prepare data for charts
    dates = sorted(set(date for class_name in aggregated_metrics for date in aggregated_metrics[class_name]))
    classes = sorted(aggregated_metrics.keys())
    
    # Data for damage and healing chart
    damage_data = {cls: [aggregated_metrics[cls][date].get('Damage', 0) for date in dates] for cls in classes}
    healing_data = {cls: [aggregated_metrics[cls][date].get('Healing', 0) for date in dates] for cls in classes}
    
    # Data for other metrics chart
    interrupts_data = {cls: [aggregated_metrics[cls][date].get('Interrupts', 0) for date in dates] for cls in classes}
    mez_data = {cls: [aggregated_metrics[cls][date].get('Mez', 0) for date in dates] for cls in classes}
    shears_data = {cls: [aggregated_metrics[cls][date].get('Shears', 0) for date in dates] for cls in classes}
    roots_data = {cls: [aggregated_metrics[cls][date].get('Roots', 0) for date in dates] for cls in classes}
    disease_data = {cls: [aggregated_metrics[cls][date].get('Disease', 0) for date in dates] for cls in classes}
    
    # Colors for classes
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#C9C9C9', '#535353', '#FF6384CC', '#36A2EBCC', '#FFCE56CC', '#4BC0C0CC'
    ]
    
    # Chart.js configurations
    damage_healing_chart = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": (
                [
                    {
                        "label": f"{cls} Damage",
                        "data": damage_data[cls],
                        "borderColor": colors[i % len(colors)],
                        "backgroundColor": colors[i % len(colors)],
                        "fill": False
                    } for i, cls in enumerate(classes)
                ] +
                [
                    {
                        "label": f"{cls} Healing",
                        "data": healing_data[cls],
                        "borderColor": colors[(i + len(classes)) % len(colors)],
                        "backgroundColor": colors[(i + len(classes)) % len(colors)],
                        "fill": False,
                        "borderDash": [5, 5]
                    } for i, cls in enumerate(classes)
                ]
            )
        },
        "options": {
            "responsive": True,
            "scales": {
                "x": {"title": {"display": True, "text": "Date"}},
                "y": {"title": {"display": True, "text": "Value"}, "beginAtZero": True}
            },
            "plugins": {
                "legend": {"display": True}
            }
        }
    }
    
    other_metrics_chart = {
        "type": "line",
        "data": {
            "labels": dates,
            "datasets": (
                [
                    {
                        "label": f"{cls} Interrupts",
                        "data": interrupts_data[cls],
                        "borderColor": colors[i % len(colors)],
                        "backgroundColor": colors[i % len(colors)],
                        "fill": False
                    } for i, cls in enumerate(classes)
                ] +
                [
                    {
                        "label": f"{cls} Mez",
                        "data": mez_data[cls],
                        "borderColor": colors[(i + len(classes)) % len(colors)],
                        "backgroundColor": colors[(i + len(classes)) % len(colors)],
                        "fill": False,
                        "borderDash": [5, 5]
                    } for i, cls in enumerate(classes)
                ] +
                [
                    {
                        "label": f"{cls} Shears",
                        "data": shears_data[cls],
                        "borderColor": colors[(i + 2 * len(classes)) % len(colors)],
                        "backgroundColor": colors[(i + 2 * len(classes)) % len(colors)],
                        "fill": False,
                        "borderDash": [10, 5]
                    } for i, cls in enumerate(classes)
                ] +
                [
                    {
                        "label": f"{cls} Roots",
                        "data": roots_data[cls],
                        "borderColor": colors[(i + 3 * len(classes)) % len(colors)],
                        "backgroundColor": colors[(i + 3 * len(classes)) % len(colors)],
                        "fill": False,
                        "borderDash": [15, 5]
                    } for i, cls in enumerate(classes)
                ] +
                [
                    {
                        "label": f"{cls} Disease",
                        "data": disease_data[cls],
                        "borderColor": colors[(i + 4 * len(classes)) % len(colors)],
                        "backgroundColor": colors[(i + 4 * len(classes)) % len(colors)],
                        "fill": False,
                        "borderDash": [20, 5]
                    } for i, cls in enumerate(classes)
                ]
            )
        },
        "options": {
            "responsive": True,
            "scales": {
                "x": {"title": {"display": True, "text": "Date"}},
                "y": {"title": {"display": True, "text": "Value"}, "beginAtZero": True}
            },
            "plugins": {
                "legend": {"display": True}
            }
        }
    }
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Class Metrics Time Series</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        canvas {{ margin-bottom: 40px; max-width: 100%; }}
        h2 {{ text-align: center; }}
    </style>
</head>
<body>
    <h2>Damage and Healing by Class</h2>
    <canvas id="damageHealingChart" width="800" height="400"></canvas>
    <h2>Interrupts, Mez, Shears, Roots, and Disease by Class</h2>
    <canvas id="otherMetricsChart" width="800" height="400"></canvas>

    <script>
        try {{
            const damageHealingCtx = document.getElementById('damageHealingChart').getContext('2d');
            new Chart(damageHealingCtx, {json.dumps(damage_healing_chart)});
            
            const otherMetricsCtx = document.getElementById('otherMetricsChart').getContext('2d');
            new Chart(otherMetricsCtx, {json.dumps(other_metrics_chart)});
        }} catch (error) {{
            console.error('Chart rendering error:', error);
            document.body.innerHTML += '<p style="color: red;">Error rendering charts: ' + error.message + '</p>';
        }}
    </script>
</body>
</html>
"""
    with open('class_metrics_charts.html', 'w') as f:
        f.write(html_content)

    # For debugging: Save raw data to a JSON file
    debug_data = {
        'dates': dates,
        'damage': damage_data,
        'healing': healing_data,
        'interrupts': interrupts_data,
        'mez': mez_data,
        'shears': shears_data,
        'roots': roots_data,
        'disease': disease_data
    }
    with open('debug_data.json', 'w') as f:
        json.dump(debug_data, f, indent=4)

if __name__ == '__main__':
    directory_path = "../fights_1"
    print(f"Processing JSON files in {directory_path}...")
    aggregated_metrics = process_files(directory_path)
    generate_html_charts(aggregated_metrics)
    print("Charts generated in 'class_metrics_charts.html'")
    print("Debug data saved in 'debug_data.json'")
