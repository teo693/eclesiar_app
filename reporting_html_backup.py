import os
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from db import get_item_price_series, get_item_price_avg


def get_country_flag(country_name: str) -> str:
    """Zwraca flagę emoji dla danego kraju"""
    if not country_name:
        return "🏳️"
    
    country_lower = country_name.lower().strip()
    
    # Mapowanie krajów na flagi (podstawowe)
    flag_map = {
        'poland': '🇵🇱',
        'polska': '🇵🇱',
        'germany': '🇩🇪',
        'niemcy': '🇩🇪',
        'france': '🇫🇷',
        'francja': '🇫🇷',
        'spain': '🇪🇸',
        'hiszpania': '🇪🇸',
        'italy': '🇮🇹',
        'włochy': '🇮🇹',
        'united kingdom': '🇬🇧',
        'wielka brytania': '🇬🇧',
        'united states': '🇺🇸',
        'stany zjednoczone': '🇺🇸',
        'usa': '🇺🇸',
        'russia': '🇷🇺',
        'rosja': '🇷🇺',
        'china': '🇨🇳',
        'chiny': '🇨🇳',
        'japan': '🇯🇵',
        'japonia': '🇯🇵',
        'brazil': '🇧🇷',
        'brazylia': '🇧🇷',
        'canada': '🇨🇦',
        'kanada': '🇨🇦',
        'australia': '🇦🇺',
        'australia': '🇦🇺',
        'india': '🇮🇳',
        'indie': '🇮🇳',
        'south korea': '🇰🇷',
        'korea południowa': '🇰🇷',
        'mexico': '🇲🇽',
        'meksyk': '🇲🇽',
        'argentina': '🇦🇷',
        'argentyna': '🇦🇷',
        'south africa': '🇿🇦',
        'południowa afryka': '🇿🇦',
        'egypt': '🇪🇬',
        'egipt': '🇪🇬',
        'turkey': '🇹🇷',
        'turcja': '🇹🇷',
        'saudi arabia': '🇸🇦',
        'arabia saudyjska': '🇸🇦',
        'israel': '🇮🇱',
        'izrael': '🇮🇱',
        'sweden': '🇸🇪',
        'szwecja': '🇸🇪',
        'norway': '🇳🇴',
        'norwegia': '🇳🇴',
        'denmark': '🇩🇰',
        'dania': '🇩🇰',
        'finland': '🇫🇮',
        'finlandia': '🇫🇮',
        'netherlands': '🇳🇱',
        'holandia': '🇳🇱',
        'belgium': '🇧🇪',
        'belgia': '🇧🇪',
        'switzerland': '🇨🇭',
        'szwajcaria': '🇨🇭',
        'austria': '🇦🇹',
        'austria': '🇦🇹',
        'czech republic': '🇨🇿',
        'czechy': '🇨🇿',
        'slovakia': '🇸🇰',
        'słowacja': '🇸🇰',
        'hungary': '🇭🇺',
        'węgry': '🇭🇺',
        'romania': '🇷🇴',
        'rumunia': '🇷🇴',
        'bulgaria': '🇧🇬',
        'bułgaria': '🇧🇬',
        'croatia': '🇭🇷',
        'chorwacja': '🇭🇷',
        'serbia': '🇷🇸',
        'serbia': '🇷🇸',
        'slovenia': '🇸🇮',
        'słowenia': '🇸🇮',
        'lithuania': '🇱🇹',
        'litwa': '🇱🇹',
        'latvia': '🇱🇻',
        'łotwa': '🇱🇻',
        'estonia': '🇪🇪',
        'estonia': '🇪🇪',
        'ukraine': '🇺🇦',
        'ukraina': '🇺🇦',
        'belarus': '🇧🇾',
        'białoruś': '🇧🇾',
        'greece': '🇬🇷',
        'grecja': '🇬🇷',
        'portugal': '🇵🇹',
        'portugalia': '🇵🇹',
        'ireland': '🇮🇪',
        'irlandia': '🇮🇪',
        'iceland': '🇮🇸',
        'islandia': '🇮🇸',
        'luxembourg': '🇱🇺',
        'luksemburg': '🇱🇺',
        'malta': '🇲🇹',
        'malta': '🇲🇹',
        'cyprus': '🇨🇾',
        'cypr': '🇨🇾',
        'european union': '🇪🇺',
        'unia europejska': '🇪🇺',
        'global': '🌍',
    }
    
    # Sprawdź dokładne dopasowanie
    if country_lower in flag_map:
        return flag_map[country_lower]
    
    # Sprawdź częściowe dopasowanie
    for key, flag in flag_map.items():
        if key in country_lower or country_lower in key:
            return flag
    
    # Domyślna flaga
    return "🏳️"


def create_infographic_html(title, data, labels, color, ax_title):
    """Tworzy wykres i zwraca go jako base64 string dla HTML"""
    if not data or not labels:
        return None
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    y_pos = np.arange(len(labels))
    ax.bar(y_pos, data, color=color, edgecolor='black', zorder=3)
    ax.set_xticks(y_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel(ax_title, fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for i, v in enumerate(data):
        ax.text(i, v + max(data) * 0.05, f'{v:,}', ha='center', fontweight='bold')
    plt.tight_layout()
    
    # Konwertuj do base64
    import io
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{image_base64}"


def generate_html_report(
    summary_data,
    historical_data,
    top_warriors,
    items_map,
    currencies_map,
    country_map=None,
    currency_codes_map=None,
    gold_id=None,
    output_dir="reports",
    sections=None
):
    """Generate daily report as an HTML file and return its path."""
    
    # Ustaw domyślne sekcje jeśli nie podano
    if sections is None:
        sections = {
            'military': True,
            'warriors': True, 
            'economic': True,
            'production': True
        }
    
    # Create reports directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # HTML template
    html_content = f"""
<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eclesiar's Pulse - Raport Dzienny</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #2c3e50;
            font-size: 2.5em;
            margin: 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }}
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 1.1em;
            margin-top: 10px;
        }}
        .section {{
            margin: 30px 0;
            padding: 20px;
            border-left: 4px solid #3498db;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .section h2 {{
            color: #2c3e50;
            font-size: 1.8em;
            margin-top: 0;
            margin-bottom: 15px;
        }}
        .section h3 {{
            color: #34495e;
            font-size: 1.4em;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .warrior-highlight {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            font-size: 1.2em;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        th {{
            background: #34495e;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}
        tr:hover {{
            background-color: #e8f4f8;
        }}
        .metric {{
            display: inline-block;
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            margin: 5px;
            font-weight: bold;
        }}
        .metric.positive {{
            background: #27ae60;
        }}
        .metric.negative {{
            background: #e74c3c;
        }}
        .metric.neutral {{
            background: #95a5a6;
        }}
        .change {{
            font-weight: bold;
        }}
        .change.positive {{
            color: #27ae60;
        }}
        .change.negative {{
            color: #e74c3c;
        }}
        .change.neutral {{
            color: #95a5a6;
        }}
        .chart {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #ecf0f1;
            color: #7f8c8d;
        }}
        .list-item {{
            margin: 8px 0;
            padding: 8px;
            background: white;
            border-radius: 5px;
            border-left: 3px solid #3498db;
        }}
        .category-section {{
            margin: 25px 0;
            padding: 20px;
            background: white;
            border-radius: 8px;
            border: 1px solid #ecf0f1;
        }}
        .category-title {{
            color: #2c3e50;
            font-size: 1.5em;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498db;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏛️ Eclesiar's Pulse</h1>
            <div class="subtitle">
                Raport wygenerowany: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
"""

    # Add data source info
    fetched_at = summary_data.get('fetched_at')
    if fetched_at:
        try:
            dt = datetime.fromisoformat(str(fetched_at).replace('Z', '+00:00'))
            ts = dt.astimezone().strftime("%Y-%m-%d %H:%M %Z") if dt.tzinfo else dt.strftime("%Y-%m-%d %H:%M")
            html_content += f'<div class="subtitle">Dane źródłowe pobrane: {ts}</div>'
        except Exception:
            html_content += f'<div class="subtitle">Dane źródłowe pobrane: {fetched_at}</div>'

    # Best warrior shoutout
    tw_local = summary_data.get('top_warriors') or []
    if isinstance(tw_local, list) and len(tw_local) > 0:
        best = tw_local[0]
        best_name = str(best.get('username', 'Unknown Warrior'))
        # Resolve country name
        best_country_raw = best.get('country')
        if not best_country_raw or str(best_country_raw).strip().lower() == 'nieznany kraj':
            cm = country_map or {}
            nat_id = best.get('nationality_id')
            reg_id = best.get('region_id')
            if nat_id in (cm or {}):
                best_country = cm.get(nat_id)
            elif reg_id in (cm or {}):
                best_country = cm.get(reg_id)
            else:
                best_country = 'Unknown Country'
        else:
            best_country = str(best_country_raw)
        
        html_content += f"""
        <div class="warrior-highlight">
            🏆 Gratulacje dla Najlepszego Wojownika: {best_name} ({best_country})!
        </div>
        """

    # Military section
    if sections.get('military', True):
        html_content += """
            <div class="section">
                <h2>⚔️ Pulse Pola Bitwy: Kluczowe Statystyki Wojenne</h2>
                <p>Obrażenia przypisane do kraju to suma obrażeń zadanych przez graczy tego kraju we wszystkich bitwach w ciągu ostatnich 24 godzin (niezależnie od tego, czy kraj był stroną konfliktu).</p>
        """

        # Define yesterday_key and today's war counts
        yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        wars_summary = summary_data.get('wars_summary', {}) or {}
        ongoing_wars = wars_summary.get('ongoing') or []
        finished_wars = wars_summary.get('finished') or []
        today_ongoing = len(ongoing_wars)
        today_finished = len(finished_wars)
        
        if ongoing_wars or finished_wars:
            html_content += '<h3>🗺️ Aktywność Wojskowa: trwające i zakończone wojny</h3>'
            
            if ongoing_wars:
                html_content += '<h4>Trwające bitwy:</h4><ul>'
            for line in ongoing_wars:
                txt = str(line)
                txt = txt.replace('wojna', 'war').replace('Wojna', 'War').replace('wynik', 'score').replace('Wynik', 'Score')
                html_content += f'<li class="list-item">{txt}</li>'
            html_content += '</ul>'
        else:
            html_content += '<p>Brak trwających bitew w tej chwili.</p>'
            
        if finished_wars:
            html_content += '<h4>Zakończone bitwy:</h4><ul>'
            for line in finished_wars:
                txt = str(line)
                txt = txt.replace('wojna', 'war').replace('Wojna', 'War').replace('wynik', 'score').replace('Wynik', 'Score')
                html_content += f'<li class="list-item">{txt}</li>'
            html_content += '</ul>'
        else:
            html_content += '<p>Brak zakończonych bitew do wyświetlenia.</p>'
        
        # Compare wars with yesterday if available
        if yesterday_key in historical_data and historical_data[yesterday_key].get('wars_summary'):
            yesterday_wars = historical_data[yesterday_key]['wars_summary']
            yesterday_ongoing = len(yesterday_wars.get('ongoing', []))
            yesterday_finished = len(yesterday_wars.get('finished', []))
            
            if today_ongoing != yesterday_ongoing or today_finished != yesterday_finished:
                html_content += '<h3>🗺️ Wojny: Zmiany w porównaniu z wczoraj</h3>'
                if today_ongoing != yesterday_ongoing:
                    change = today_ongoing - yesterday_ongoing
                    arrow = "▲" if change > 0 else "▼"
                    change_class = "positive" if change > 0 else "negative"
                    html_content += f'<p>Trwające wojny: <span class="change {change_class}">{arrow} {change:+d}</span> ({today_ongoing} vs {yesterday_ongoing})</p>'
                if today_finished != yesterday_finished:
                    change = today_finished - yesterday_finished
                    arrow = "▲" if change > 0 else "▼"
                    change_class = "positive" if change > 0 else "negative"
                    html_content += f'<p>Zakończone wojny: <span class="change {change_class}">{arrow} {change:+d}</span> ({today_finished} vs {yesterday_finished})</p>'

    military_summary = summary_data.get('military_summary', {})
    if not military_summary:
        html_content += '<p>Brak danych wojennych z ostatnich 24 godzin. Serwer był spokojny.</p>'
    else:
        # Normalize country names
        def normalize_country_name(name: str) -> str:
            if not name:
                return 'Unknown Country'
            n = str(name).strip()
            if n.lower() == 'nieznany kraj':
                return 'Unknown Country'
            return n

        sorted_countries = sorted(military_summary.keys(), key=lambda x: military_summary[x], reverse=True)
        top_countries = sorted_countries[:7]
        html_content += f'<p>W ciągu ostatnich 24 godzin aktywność wojskowa została odnotowana w {len(military_summary)} krajach.</p>'
        
        html_content += '<table><tr><th>Kraj</th><th>Obrażenia</th></tr>'
        for country in top_countries:
            dmg = military_summary[country]
            html_content += f'<tr><td>{normalize_country_name(country)}</td><td>{dmg:,}</td></tr>'
        html_content += '</table>'
        
        # Add executive summary of changes if historical data is available
        if yesterday_key in historical_data:
            html_content += '<h3>📊 Podsumowanie Wykonawcze: Kluczowe Zmiany</h3>'
            
            # Military changes summary
            if historical_data[yesterday_key].get('military_summary'):
                yesterday_military = historical_data[yesterday_key]['military_summary']
                total_today = sum(military_summary.values())
                total_yesterday = sum(yesterday_military.values())
                if total_yesterday > 0:
                    military_change_pct = (total_today - total_yesterday) / total_yesterday * 100.0
                    arrow = "▲" if military_change_pct > 0 else ("▼" if military_change_pct < 0 else "→")
                    change_class = "positive" if military_change_pct > 0 else ("negative" if military_change_pct < 0 else "neutral")
                    html_content += f'<p>⚔️ Całkowita aktywność wojskowa: <span class="change {change_class}">{arrow} {military_change_pct:+.1f}%</span> ({total_today:,} vs {total_yesterday:,})</p>'
            
            # Economic changes summary
            economic_data = summary_data.get('economic_summary', {})
            if historical_data[yesterday_key].get('economic_summary'):
                yesterday_economic = historical_data[yesterday_key]['economic_summary']
                today_rates = economic_data.get('currency_rates', {})
                yesterday_rates = yesterday_economic.get('currency_rates', {})
                
                if today_rates and yesterday_rates:
                    # Count currencies with significant changes
                    significant_changes = 0
                    for currency_id in today_rates:
                        if currency_id in yesterday_rates:
                            try:
                                today_val = float(today_rates[currency_id])
                                yesterday_val = float(yesterday_rates[currency_id])
                                if yesterday_val != 0:
                                    change_pct = abs((today_val - yesterday_val) / yesterday_val * 100.0)
                                    if change_pct > 1.0:
                                        significant_changes += 1
                            except (ValueError, TypeError):
                                continue
                    
                    if significant_changes > 0:
                        html_content += f'<p>💰 Zmienność walut: {significant_changes} walut zmieniło się o >1%</p>'
                    else:
                        html_content += '<p>💰 Rynki walutowe: Stabilne (brak znaczących zmian)</p>'
            
            html_content += '<p>Zobacz szczegółowe porównania poniżej dla konkretnych metryk.</p>'
            
        # Military comparison with yesterday
        if yesterday_key in historical_data and historical_data[yesterday_key].get('military_summary'):
            html_content += '<h3>⚖️ Wojskowość: W porównaniu z wczoraj</h3>'
            yesterday_data = historical_data[yesterday_key]['military_summary']
            
            # Show top 5 countries with biggest changes
            changes = []
            for country in set(list(military_summary.keys()) + list(yesterday_data.keys())):
                today_dmg = military_summary.get(country, 0)
                yesterday_dmg = yesterday_data.get(country, 0)
                change = today_dmg - yesterday_dmg
                if change != 0:  # Only show countries with changes
                    changes.append((abs(change), change, normalize_country_name(country)))
            
            if changes:
                # Sort by absolute change value
                changes.sort(key=lambda x: x[0], reverse=True)
                html_content += '<p>Największe zmiany w aktywności wojskowej:</p><ul>'
                for _, change, country in changes[:5]:
                    change_class = "positive" if change > 0 else "negative"
                    arrow = "▲" if change > 0 else "▼"
                    html_content += f'<li class="list-item">{country}: <span class="change {change_class}">{arrow} {change:,}</span></li>'
                html_content += '</ul>'
            else:
                html_content += '<p>Nie wykryto znaczących zmian w aktywności wojskowej.</p>'

        html_content += '</div>'  # End military section

    # Top warriors
    if sections.get('warriors', True):
        html_content += """
            <div class="section">
                <h2>🏆 Najlepsi z Najlepszych: Ranking Bohaterów</h2>
        """
    
    top_warriors_local = summary_data.get('top_warriors', [])
    if not top_warriors_local:
        html_content += '<p>Brak danych o najlepszych wojownikach z ostatniego dnia.</p>'
    else:
        html_content += '<p>Oto lista najpotężniejszych wojowników z ostatnich 24 godzin:</p>'
        html_content += '<table><tr><th>Pozycja</th><th>Wojownik</th><th>Kraj</th><th>Obrażenia</th></tr>'
        
        cm = country_map or {}
        for i, warrior in enumerate(top_warriors_local, 1):
            username = warrior.get('username', f"ID: {warrior.get('id', 'Unknown')}")
            damage = warrior.get('damage', 0)
            country = warrior.get('country')
            if not country or str(country).strip().lower() == 'nieznany kraj':
                nat_id = warrior.get('nationality_id')
                reg_id = warrior.get('region_id')
                if nat_id in cm:
                    country = cm.get(nat_id)
                elif reg_id in cm:
                    country = cm.get(reg_id)
                else:
                    country = 'Unknown Country'
            html_content += f'<tr><td>{i}</td><td>{username}</td><td>{country}</td><td>{damage:,}</td></tr>'
        
        html_content += '</table>'
        
        # Compare with yesterday's top warriors if available
        if yesterday_key in historical_data and historical_data[yesterday_key].get('top_warriors'):
            yesterday_warriors = historical_data[yesterday_key]['top_warriors']
            if yesterday_warriors:
                html_content += '<h3>🏆 Najlepsi Wojownicy: Zmiany w porównaniu z wczoraj</h3>'
                
                # Find warriors who appeared in both days
                today_usernames = {w.get('username', '').lower() for w in top_warriors_local}
                yesterday_usernames = {w.get('username', '').lower() for w in yesterday_warriors}
                
                # Warriors who maintained position
                maintained = today_usernames.intersection(yesterday_usernames)
                if maintained:
                    html_content += '<h4>Wojownicy, którzy utrzymali pozycje w czołówce:</h4><ul>'
                    for username in list(maintained)[:3]:  # Show top 3
                        today_warrior = next((w for w in top_warriors_local if w.get('username', '').lower() == username), None)
                        yesterday_warrior = next((w for w in yesterday_warriors if w.get('username', '').lower() == username), None)
                        if today_warrior and yesterday_warrior:
                            today_dmg = today_warrior.get('damage', 0)
                            yesterday_dmg = yesterday_warrior.get('damage', 0)
                            if yesterday_dmg > 0:
                                change_pct = (today_dmg - yesterday_dmg) / yesterday_dmg * 100.0
                                arrow = "▲" if change_pct > 0 else ("▼" if change_pct < 0 else "→")
                                change_class = "positive" if change_pct > 0 else ("negative" if change_pct < 0 else "neutral")
                                html_content += f'<li class="list-item">{username.title()}: <span class="change {change_class}">{arrow} {change_pct:+.1f}%</span> ({today_dmg:,} vs {yesterday_dmg:,})</li>'
                    html_content += '</ul>'
                
                # New warriors in top list
                new_warriors = today_usernames - yesterday_usernames
                if new_warriors:
                    html_content += '<h4>Nowi wojownicy w czołówce:</h4><ul>'
                    for username in list(new_warriors)[:3]:  # Show top 3
                        warrior = next((w for w in top_warriors_local if w.get('username', '').lower() == username), None)
                        if warrior:
                            damage = warrior.get('damage', 0)
                            country = warrior.get('country', 'Unknown')
                            html_content += f'<li class="list-item">{username.title()} ({country}): {damage:,} obrażeń</li>'
                    html_content += '</ul>'

        html_content += '</div>'  # End top warriors section

    # Economic summary
    if sections.get('economic', True):
        html_content += """
            <div class="section">
                <h2>💰 Pulse Ekonomiczny</h2>
        """
    
    economic_data = summary_data.get('economic_summary', {})
    if not economic_data:
        html_content += '<p>Brak danych ekonomicznych (endpoint może być niedostępny).</p>'
    else:
        # Top 5 best job offers worldwide
        best_jobs = economic_data.get('best_jobs', [])
        if best_jobs:
            html_content += '<h3>💼 Top 5 Najlepszych Ofert Pracy na Świecie</h3>'
            html_content += '<p>Najlepiej płatne oferty pracy we wszystkich krajach (wynagrodzenie w GOLD):</p>'
            html_content += '<table><tr><th>Kraj</th><th>Firma</th><th>ID Firmy</th><th>Wynagrodzenie (GOLD)</th></tr>'
            
            for job in best_jobs[:5]:
                country_name = job.get('country_name', 'Unknown')
                company_name = job.get('business_name') or job.get('company_name') or '—'
                business_id = job.get('business_id', 'N/A')
                salary_gold = job.get('salary_gold', 0) or 0
                note = "*" if isinstance(salary_gold, (int, float)) and salary_gold > 5 else ""
                html_content += f'<tr><td>{country_name}</td><td>{company_name}</td><td>{business_id}</td><td>{float(salary_gold):.6f}{note}</td></tr>'
            
            html_content += '</table>'
            html_content += '<p><small>* oznaczone jako potencjalnie anomalne (sprawdź ponownie konwersję)</small></p>'
        
        # Currency rates
        currency_rates = (economic_data.get('currency_rates') or {})
        codes_map = currency_codes_map or {}
        if currency_rates:
            html_content += '<h3>Kursy walut vs GOLD</h3>'
            try:
                # Try to compute yesterday diffs if available
                yesterday_rates = {}
                try:
                    if yesterday_key in historical_data:
                        yesterday_rates = (historical_data[yesterday_key].get('economic_summary') or {}).get('currency_rates') or {}
                except Exception:
                    yesterday_rates = {}
                has_diff = bool(yesterday_rates)
                
                html_content += '<table><tr><th>Waluta</th><th>Kurs (GOLD za 1)</th>'
                if has_diff:
                    html_content += '<th>Kurs wczoraj</th><th>Zmiana %</th>'
                html_content += '</tr>'
                
                # Build canonical rows with country info
                rows_list = []
                for k, rate in currency_rates.items():
                    try:
                        cid = int(k)
                    except Exception:
                        cid = k
                    
                    # Get currency name and country info
                    currency_name = None
                    country_name = None
                    country_flag = None
                    
                    # Try to get currency name from codes_map first
                    if codes_map:
                        currency_name = codes_map.get(cid)
                    
                    # Fall back to currencies_map
                    if not currency_name and isinstance(currencies_map, dict):
                        currency_name = currencies_map.get(cid)
                    
                    # If still no name, use ID
                    if not currency_name:
                        currency_name = str(cid)
                    
                    # Try to find country info for this currency
                    # Map currency names to countries (simplified approach)
                    currency_to_country = {
                        'PLN': 'Poland',
                        'EUR': 'European Union',
                        'USD': 'United States',
                        'GBP': 'United Kingdom',
                        'CHF': 'Switzerland',
                        'JPY': 'Japan',
                        'CAD': 'Canada',
                        'AUD': 'Australia',
                        'CNY': 'China',
                        'RUB': 'Russia',
                        'BRL': 'Brazil',
                        'INR': 'India',
                        'KRW': 'South Korea',
                        'MXN': 'Mexico',
                        'ARS': 'Argentina',
                        'ZAR': 'South Africa',
                        'EGP': 'Egypt',
                        'TRY': 'Turkey',
                        'SAR': 'Saudi Arabia',
                        'ILS': 'Israel',
                        'SEK': 'Sweden',
                        'NOK': 'Norway',
                        'DKK': 'Denmark',
                        'CZK': 'Czech Republic',
                        'HUF': 'Hungary',
                        'RON': 'Romania',
                        'BGN': 'Bulgaria',
                        'HRK': 'Croatia',
                        'RSD': 'Serbia',
                        'UAH': 'Ukraine',
                        'BYN': 'Belarus',
                        'GOLD': 'Global',
                    }
                    
                    # Try to find country name from currency code
                    if currency_name.upper() in currency_to_country:
                        country_name = currency_to_country[currency_name.upper()]
                        country_flag = get_country_flag(country_name)
                    else:
                        # Try to extract country from currency name
                        country_flag = get_country_flag(currency_name)
                    
                    try:
                        rate_val = float(rate)
                    except Exception:
                        rate_val = None
                    
                    rows_list.append((cid, currency_name, country_name, country_flag, rate_val))
                
                # Sort by currency name
                rows_list.sort(key=lambda r: (str(r[1]).lower()))
                
                for cid, currency_name, country_name, country_flag, rate_val in rows_list:
                    # Create display name with flag and country
                    display_name = currency_name
                    if country_flag and country_name:
                        display_name = f"{country_flag} {currency_name} ({country_name})"
                    elif country_flag:
                        display_name = f"{country_flag} {currency_name}"
                    elif country_name:
                        display_name = f"{currency_name} ({country_name})"
                    
                    rate_display = f"{rate_val:.6f}" if isinstance(rate_val, (int, float)) else "brak danych"
                    html_content += f'<tr><td>{display_name}</td><td>{rate_display}</td>'
                    if has_diff:
                        try:
                            prev = yesterday_rates.get(cid, yesterday_rates.get(str(cid)))
                            prev_val = float(prev) if prev is not None else None
                        except Exception:
                            prev_val = None
                        if isinstance(rate_val, (int, float)) and isinstance(prev_val, (int, float)) and prev_val != 0:
                            diff_pct = (rate_val - prev_val) / prev_val * 100.0
                            arrow = "▲" if diff_pct > 0 else ("▼" if diff_pct < 0 else "→")
                            change_class = "positive" if diff_pct > 0 else ("negative" if diff_pct < 0 else "neutral")
                            html_content += f'<td>{prev_val:.6f}</td><td><span class="change {change_class}">{arrow} {diff_pct:+.2f}%</span></td>'
                        else:
                            html_content += '<td>—</td><td>—</td>'
                    html_content += '</tr>'
                
                html_content += '</table>'
            except Exception as e:
                # Fallback to bullet list if table rendering fails
                print(f"DEBUG: Error in currency table generation: {e}")
                import traceback
                traceback.print_exc()
                html_content += '<ul>'
                for key, rate in currency_rates.items():
                    try:
                        rate_val = float(rate)
                        html_content += f'<li class="list-item">{key}: {rate_val:.6f} GOLD</li>'
                    except Exception:
                        html_content += f'<li class="list-item">{key}: brak danych</li>'
                html_content += '</ul>'

        # Cheapest items from all countries
        cheapest_items_all = economic_data.get('cheapest_items_all_countries', {})
        if cheapest_items_all:
            html_content += '<h3>🌍 Najtańsze towary ze wszystkich krajów</h3>'
            html_content += '<p>Najtańsze towary każdego typu ze wszystkich krajów:</p>'
            
            # Group items by category
            def categorize_item(name: str) -> str:
                name_lower = str(name).lower()
                if any(word in name_lower for word in ["grain", "iron", "titanium", "fuel", "raw"]):
                    return "Surowce"
                elif "weapon" in name_lower:
                    return "Broń"
                elif "food" in name_lower:
                    return "Żywność"
                elif "aircraft" in name_lower or ("airplane" in name_lower and "ticket" not in name_lower):
                    return "Samoloty"
                elif "ticket" in name_lower:
                    return "Bilety lotnicze"
                else:
                    return "Inne"
            
            # Group items by category
            categorized_items = {}
            for item_id, item_data in cheapest_items_all.items():
                try:
                    category = categorize_item(item_data.get('item_name', ''))
                    if category not in categorized_items:
                        categorized_items[category] = []
                    categorized_items[category].append(item_data)
                except Exception as e:
                    print(f"DEBUG: Error processing item {item_id}: {e}")
                    continue
            
            # Display each category in a separate section
            for category, items in categorized_items.items():
                if items:
                    html_content += f'<div class="category-section"><h4 class="category-title">{category}</h4>'
                    html_content += '<table><tr><th>Towar</th><th>Kraj</th><th>Cena (waluta)</th><th>Cena (GOLD)</th><th>Ilość</th><th>Średnia z 5 najtańszych (GOLD)</th></tr>'
                    
                    # Sort items within the category by GOLD price
                    sorted_items = sorted(items, key=lambda x: x.get('price_gold', 0))
                    
                    for item in sorted_items:
                        try:
                            item_name = str(item.get('item_name', 'Nieznany'))
                            country_name = str(item.get('country_name', 'Nieznany'))
                            price_original = item.get('price_original', 0)
                            currency_name = item.get('currency_name', '')
                            price_gold = item.get('price_gold', 0)
                            qty = item.get('amount_at_price')
                            avg5 = item.get('avg5_in_gold') or item.get('avg10_in_gold')
                            
                            
                            # Format values safely
                            try:
                                price_gold_formatted = f"{float(price_gold):.6f}"
                            except (ValueError, TypeError):
                                price_gold_formatted = "—"
                            
                            try:
                                avg5_formatted = f"{float(avg5):.6f}" if isinstance(avg5, (int, float)) else "—"
                            except (ValueError, TypeError):
                                avg5_formatted = "—"
                            
                            html_content += f'<tr>'
                            html_content += f'<td>{item_name}</td>'
                            html_content += f'<td>{country_name}</td>'
                            html_content += f'<td>{price_original} {currency_name}</td>'
                            html_content += f'<td>{price_gold_formatted}</td>'
                            html_content += f'<td>{int(qty) if isinstance(qty, (int, float)) else "—"}</td>'
                            html_content += f'<td>{avg5_formatted}</td>'
                            html_content += f'</tr>'
                        except Exception as e:
                            print(f"DEBUG: Error processing row for item {item}: {e}")
                            continue
                    
                    html_content += '</table></div>'
        else:
            # Add useful economic information instead of empty section
            html_content += '<h3>📊 Dodatkowe Informacje Ekonomiczne</h3>'
            
            # Show currency extremes
            currency_extremes = economic_data.get('currency_extremes')
            if currency_extremes:
                most_expensive, cheapest = currency_extremes
                html_content += '<div class="category-section">'
                html_content += '<h4 class="category-title">Skrajne Kursy Walut</h4>'
                html_content += f'<p><strong>💰 Najdroższa waluta:</strong> ID {most_expensive[0]} - {most_expensive[1]:.6f} GOLD za jednostkę</p>'
                html_content += f'<p><strong>🏷️ Najtańsza waluta:</strong> ID {cheapest[0]} - {cheapest[1]:.6f} GOLD za jednostkę</p>'
                html_content += '</div>'
            
            # Show lowest NPC wage countries
            lowest_npc_wage = economic_data.get('lowest_npc_wage', [])
            if lowest_npc_wage:
                html_content += '<div class="category-section">'
                html_content += '<h4 class="category-title">Kraje z Najniższymi Płacami NPC</h4>'
                html_content += '<table><tr><th>Kraj</th><th>Płaca NPC (GOLD)</th></tr>'
                for country in lowest_npc_wage[:10]:  # Show top 10
                    country_name = country.get('country_name', 'Unknown')
                    npc_wage = country.get('npc_wage_gold', 0)
                    html_content += f'<tr><td>{country_name}</td><td>{npc_wage:.4f}</td></tr>'
                html_content += '</table>'
                html_content += '</div>'
            
            # Show available data summary
            html_content += '<div class="category-section">'
            html_content += '<h4 class="category-title">Dostępne Dane w Systemie</h4>'
            html_content += '<ul>'
            data_descriptions = {
                'most_expensive_currency': 'Najdroższa waluta vs GOLD',
                'cheapest_currency': 'Najtańsza waluta vs GOLD',
                'currency_rates': f'Kursy {len(economic_data.get("currency_rates", {}))} walut vs GOLD',
                'lowest_npc_wage': f'Płace NPC w {len(lowest_npc_wage)} krajach',
                'regions_data': 'Dane o regionach z bonusami',
                'regions_summary': 'Podsumowanie statystyk regionów'
            }
            for key in economic_data.keys():
                description = data_descriptions.get(key, 'Dane ekonomiczne')
                html_content += f'<li class="list-item"><strong>{key}:</strong> {description}</li>'
            html_content += '</ul>'
            html_content += '<p><em>💡 Dane o najtańszych towarach są pobierane w tle i będą dostępne w kolejnych raportach.</em></p>'
            html_content += '</div>'

        html_content += '</div>'  # End economic section

    # Production analysis section
    production_data = summary_data.get('production_data', [])
    if sections.get('production', True) and production_data:
        html_content += """
            <div class="section">
                <h2>🏭 Analiza Produktywności Regionów</h2>
                <p>Analiza efektywności produkcji w różnych regionach dla różnych towarów.</p>
        """
        
        # Group by efficiency score ranges
        items_groups = {}
        for data in production_data:
            if data.efficiency_score > 0.8:
                group = "Bardzo wysoka efektywność"
            elif data.efficiency_score > 0.6:
                group = "Wysoka efektywność"
            elif data.efficiency_score > 0.4:
                group = "Średnia efektywność"
            else:
                group = "Niska efektywność"
            
            if group not in items_groups:
                items_groups[group] = []
            items_groups[group].append(data)
        
        for group_name, items in items_groups.items():
            if items:
                html_content += f'<div class="category-section"><h4 class="category-title">{group_name} (Score > {min(item.efficiency_score for item in items):.2f})</h4>'
                html_content += '<table><tr><th>Region</th><th>Kraj</th><th>Score</th><th>Bonus</th><th>Produkcja Q5</th><th>Płace NPC (GOLD)</th></tr>'
                
                # Show top 10 from each group
                for item in items[:10]:
                    html_content += f'<tr>'
                    html_content += f'<td>{item.region_name}</td>'
                    html_content += f'<td>{item.country_name}</td>'
                    html_content += f'<td>{item.efficiency_score:.2f}</td>'
                    html_content += f'<td>{item.total_bonus:.1%}</td>'
                    html_content += f'<td>{item.production_q5}</td>'
                    html_content += f'<td>{item.npc_wages:.2f}</td>'
                    html_content += f'</tr>'
                
                html_content += '</table></div>'
        
            html_content += '</div>'  # End production section

    # Footer
    html_content += f"""
        <div class="footer">
            <p>Raport wygenerowany przez aplikację Eclesiar</p>
            <p>Data generowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
    """
    
    # Save HTML file
    file_name = f"raport_dzienny_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.html"
    file_path = os.path.join(output_dir, file_name)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Raport HTML został pomyślnie wygenerowany jako '{file_path}'")
    return file_path
