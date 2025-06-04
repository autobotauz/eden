
import json
import glob
import os
from collections import defaultdict
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
    """Process JSON files and aggregate metrics by class."""
    class_metrics = defaultdict(lambda: defaultdict(list))
    json_files = glob.glob(os.path.join(directory_path, "*.json"))
    
    for file_path in json_files:
        try:
            with open(file_path, 'r') as f:
                match_data = json.load(f)
            
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
                    'Healing': stats.get('hd', 0)
                }
                
                # Store metrics by class
                for metric, value in metrics.items():
                    class_metrics[class_name][metric].append(value)
        
        except Exception as e:
            print(f"Error processing file {file_path}: {str(e)}")
    
    # Aggregate metrics (sum per class) and calculate percentages
    aggregated_metrics = defaultdict(dict)
    percentage_metrics = defaultdict(dict)
    totals = defaultdict(float)
    
    # Single pass: compute sums and totals
    for class_name in class_metrics:
        for metric in class_metrics[class_name]:
            values = class_metrics[class_name][metric]
            class_sum = sum(values) if values else 0
            aggregated_metrics[class_name][metric] = class_sum
            totals[metric] += class_sum
    
    # Calculate percentages
    for class_name in class_metrics:
        for metric in class_metrics[class_name]:
            total = totals[metric]
            value = aggregated_metrics[class_name][metric]
            percentage_metrics[class_name][metric] = round(value / total * 100, 2) if total > 0 else 0
    
    return percentage_metrics, aggregated_metrics

def generate_html_charts(percentage_metrics, aggregated_metrics):
    """Generate HTML with two Chart.js pie charts for damage and healing."""
    classes = sorted(percentage_metrics.keys())
    
    # Data for each pie chart (percentages)
    metrics = ['Damage', 'Healing']
    chart_data = {
        metric: [percentage_metrics[cls].get(metric, 0) for cls in classes]
        for metric in metrics
    }
    
    # Raw sums for tooltips
    raw_data = {
        metric: [aggregated_metrics[cls].get(metric, 0) for cls in classes]
        for metric in metrics
    }
    
    # Colors for classes
    colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40',
        '#C9C9C9', '#535353', '#FF6384CC', '#36A2EBCC', '#FFCE56CC', '#4BC0C0CC',
        '#FF6384AA', '#36A2EBAA', '#FFCE56AA', '#4BC0C0AA', '#9966FFAA', '#FF9F40AA'
    ]
    
    # Generate pie chart configurations
    pie_charts = {}
    for metric in metrics:
        pie_charts[metric] = {
            "type": "pie",
            "data": {
                "labels": [f"{cls} ({chart_data[metric][i]:.1f}%)" for i, cls in enumerate(classes)],
                "datasets": [{
                    "data": chart_data[metric],
                    "backgroundColor": colors[:len(classes)],
                    "borderColor": '#FFFFFF',
                    "borderWidth": 1
                }]
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "position": 'right',
                        "labels": {
                            "font": {
                                "size": 12
                            }
                        }
                    },
                    "title": {
                        "display": True,
                        "text": f"{metric} by Class (%)",
                        "font": {
                            "size": 16
                        }
                    },
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": """
                            function(context) {
                                const label = context.label.split(' (')[0];
                                const percentage = context.parsed.toFixed(1);
                                const rawValue = context.dataset.data[context.dataIndex];
                                return `${label}: ${percentage}% (${rawValue.toFixed(0)})`;
                            }
                            """
                        }
                    }
                }
            }
        }
    
    # Generate HTML
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Class Metrics Pie Charts</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .chart-container {{ 
            max-width: 450px; 
            height: 450px; 
            margin: 20px; 
            display: inline-block; 
            vertical-align: top; 
        }}
        h2 {{ text-align: center; }}
        .charts-row {{ text-align: center; white-space: nowrap; }}
    </style>
</head>
<body>
    <h2>Class Metrics Breakdown (Percentages)</h2>
    <div class="charts-row">
        <div class="chart-container"><canvas id="damageChart"></canvas></div>
        <div class="chart-container"><canvas id="healingChart"></canvas></div>
    </div>

    <script>
        try {{
            const charts = {{
                damageChart: {json.dumps(pie_charts['Damage'])},
                healingChart: {json.dumps(pie_charts['Healing'])}
            }};
            Object.keys(charts).forEach(chartId => {{
                const ctx = document.getElementById(chartId).getContext('2d');
                new Chart(ctx, charts[chartId]);
            }});
        }} catch (error) {{
            console.error('Chart rendering error:', error);
            document.body.innerHTML += '<p style="color: red;">Error rendering charts: ' + error.message + '</p>';
        }}
    </script>
</body>
</html>
"""
    with open('class_metrics_pie_charts.html', 'w') as f:
        f.write(html_content)

    # For debugging: Save raw and percentage data to a JSON file
    debug_data = {
        'classes': classes,
        'percentages': chart_data,
        'raw_sums': raw_data
    }
    with open('debug_data.json', 'w') as f:
        json.dump(debug_data, f, indent=4)

if __name__ == '__main__':
    directory_path = "../fights_1"
    print(f"Processing JSON files in {directory_path}...")
    percentage_metrics, aggregated_metrics = process_files(directory_path)
    generate_html_charts(percentage_metrics, aggregated_metrics)
    print("Pie charts generated in 'class_metrics_pie_charts.html'")
    print("Debug data saved in 'debug_data.json'")
