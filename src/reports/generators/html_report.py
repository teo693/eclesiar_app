import io
import os
import base64
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
from src.data.database.models import get_item_price_series, get_item_price_avg


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
        'ukraine': '🇺🇦',
        'ukraina': '🇺🇦',
        'belarus': '🇧🇾',
        'białoruś': '🇧🇾',
        'slovakia': '🇸🇰',
        'słowacja': '🇸🇰',
        'slovenia': '🇸🇮',
        'słowenia': '🇸🇮',
        'lithuania': '🇱🇹',
        'litwa': '🇱🇹',
        'latvia': '🇱🇻',
        'łotwa': '🇱🇻',
        'estonia': '🇪🇪',
        'estonia': '🇪🇪',
        'greece': '🇬🇷',
        'grecja': '🇬🇷',
        'portugal': '🇵🇹',
        'portugalia': '🇵🇹',
        'ireland': '🇮🇪',
        'irlandia': '🇮🇪',
        'colombia': '🇨🇴',
        'kolumbia': '🇨🇴',
        'peru': '🇵🇪',
        'peru': '🇵🇪',
        'chile': '🇨🇱',
        'chile': '🇨🇱',
        'iraq': '🇮🇶',
        'irak': '🇮🇶',
        'iran': '🇮🇷',
        'iran': '🇮🇷',
        'pakistan': '🇵🇰',
        'pakistan': '🇵🇰',
        'bangladesh': '🇧🇩',
        'bangladesz': '🇧🇩',
        'vietnam': '🇻🇳',
        'wietnam': '🇻🇳',
        'thailand': '🇹🇭',
        'tajlandia': '🇹🇭',
        'indonesia': '🇮🇩',
        'indonezja': '🇮🇩',
        'philippines': '🇵🇭',
        'filipiny': '🇵🇭',
        'malaysia': '🇲🇾',
        'malezja': '🇲🇾',
        'singapore': '🇸🇬',
        'singapur': '🇸🇬',
        'new zealand': '🇳🇿',
        'nowa zelandia': '🇳🇿',
        'south africa': '🇿🇦',
        'południowa afryka': '🇿🇦',
        'nigeria': '🇳🇬',
        'nigeria': '🇳🇬',
        'kenya': '🇰🇪',
        'kenia': '🇰🇪',
        'morocco': '🇲🇦',
        'maroko': '🇲🇦',
        'algeria': '🇩🇿',
        'algieria': '🇩🇿',
        'tunisia': '🇹🇳',
        'tunezja': '🇹🇳',
        'libya': '🇱🇾',
        'libia': '🇱🇾',
        'ethiopia': '🇪🇹',
        'etiopia': '🇪🇹',
        'ghana': '🇬🇭',
        'ghana': '🇬🇭',
        'ivory coast': '🇨🇮',
        'wybrzeże kości słoniowej': '🇨🇮',
        'senegal': '🇸🇳',
        'senegal': '🇸🇳',
        'mali': '🇲🇱',
        'mali': '🇲🇱',
        'burkina faso': '🇧🇫',
        'burkina faso': '🇧🇫',
        'niger': '🇳🇪',
        'niger': '🇳🇪',
        'chad': '🇹🇩',
        'czad': '🇹🇩',
        'sudan': '🇸🇩',
        'sudan': '🇸🇩',
        'south sudan': '🇸🇸',
        'południowy sudan': '🇸🇸',
        'central african republic': '🇨🇫',
        'republika środkowoafrykańska': '🇨🇫',
        'cameroon': '🇨🇲',
        'kamerun': '🇨🇲',
        'gabon': '🇬🇦',
        'gabon': '🇬🇦',
        'equatorial guinea': '🇬🇶',
        'gwinea równikowa': '🇬🇶',
        'congo': '🇨🇬',
        'kong': '🇨🇬',
        'democratic republic of the congo': '🇨🇩',
        'demokratyczna republika konga': '🇨🇩',
        'angola': '🇦🇴',
        'angola': '🇦🇴',
        'zambia': '🇿🇲',
        'zambia': '🇿🇲',
        'zimbabwe': '🇿🇼',
        'zimbabwe': '🇿🇼',
        'botswana': '🇧🇼',
        'botswana': '🇧🇼',
        'namibia': '🇳🇦',
        'namibia': '🇳🇦',
        'lesotho': '🇱🇸',
        'lesotho': '🇱🇸',
        'swaziland': '🇸🇿',
        'swaziland': '🇸🇿',
        'madagascar': '🇲🇬',
        'madagaskar': '🇲🇬',
        'mauritius': '🇲🇺',
        'mauritius': '🇲🇺',
        'seychelles': '🇸🇨',
        'seszele': '🇸🇨',
        'comoros': '🇰🇲',
        'komory': '🇰🇲',
        'djibouti': '🇩🇯',
        'dżibuti': '🇩🇯',
        'eritrea': '🇪🇷',
        'erytrea': '🇪🇷',
        'somalia': '🇸🇴',
        'somalia': '🇸🇴',
        'uganda': '🇺🇬',
        'uganda': '🇺🇬',
        'tanzania': '🇹🇿',
        'tanzania': '🇹🇿',
        'rwanda': '🇷🇼',
        'rwanda': '🇷🇼',
        'burundi': '🇧🇮',
        'burundi': '🇧🇮',
        'malawi': '🇲🇼',
        'malawi': '🇲🇼',
        'mozambique': '🇲🇿',
        'mozambik': '🇲🇿',
        'zambia': '🇿🇲',
        'zambia': '🇿🇲',
        'malawi': '🇲🇼',
        'malawi': '🇲🇼',
        'madagascar': '🇲🇬',
        'madagaskar': '🇲🇬',
        'mauritius': '🇲🇺',
        'mauritius': '🇲🇺',
        'seychelles': '🇸🇨',
        'seszele': '🇸🇨',
        'comoros': '🇰🇲',
        'komory': '🇰🇲',
        'djibouti': '🇩🇯',
        'dżibuti': '🇩🇯',
        'eritrea': '🇪🇷',
        'erytrea': '🇪🇷',
        'somalia': '🇸🇴',
        'somalia': '🇸🇴',
        'uganda': '🇺🇬',
        'uganda': '🇺🇬',
        'tanzania': '🇹🇿',
        'tanzania': '🇹🇿',
        'rwanda': '🇷🇼',
        'rwanda': '🇷🇼',
        'burundi': '🇧🇮',
        'burundi': '🇧🇮',
        'malawi': '🇲🇼',
        'malawi': '🇲🇼',
        'mozambique': '🇲🇿',
        'mozambik': '🇲🇿',
        # Dodatkowe kraje dla walut
        'albania': '🇦🇱',
        'venezuela': '🇻🇪',
        'uruguay': '🇺🇾',
        'paraguay': '🇵🇾',
        'bolivia': '🇧🇴',
        'chile': '🇨🇱',
        'georgia': '🇬🇪',
        'armenia': '🇦🇲',
        'azerbaijan': '🇦🇿',
        'kazakhstan': '🇰🇿',
        'uzbekistan': '🇺🇿',
        'turkmenistan': '🇹🇲',
        'kyrgyzstan': '🇰🇬',
        'tajikistan': '🇹🇯',
        'afghanistan': '🇦🇫',
        'sri lanka': '🇱🇰',
        'nepal': '🇳🇵',
        'bhutan': '🇧🇹',
        'myanmar': '🇲🇲',
        'laos': '🇱🇦',
        'cambodia': '🇰🇭',
        'mongolia': '🇲🇳',
        'north korea': '🇰🇵',
        'taiwan': '🇹🇼',
        'hong kong': '🇭🇰',
        'macau': '🇲🇴',
        'brunei': '🇧🇳',
        'european union': '🇪🇺',
        'global': '🌍',
    }
    
    return flag_map.get(country_lower, "🏳️")


def get_item_icon(item_name: str) -> str:
    """Zwraca ikonę emoji dla danego towaru"""
    if not item_name:
        return "📦"
    
    item_lower = item_name.lower().strip()
    
    # Mapowanie towarów na ikony
    if 'grain' in item_lower or 'zboże' in item_lower:
        return "🌾"
    elif 'food' in item_lower or 'żywność' in item_lower:
        return "🍞"
    elif 'iron' in item_lower or 'żelazo' in item_lower:
        return "⚙️"
    elif 'titanium' in item_lower or 'tytan' in item_lower:
        return "🔩"
    elif 'fuel' in item_lower or 'paliwo' in item_lower:
        return "⛽"
    elif 'weapon' in item_lower or 'broń' in item_lower:
        return "🔫"
    elif 'aircraft' in item_lower or 'samolot' in item_lower:
        return "✈️"
    elif 'airplane ticket' in item_lower or 'bilet' in item_lower:
        return "🎫"
    else:
        return "📦"


def get_currency_flag(currency_code: str, currency_name: str = "") -> str:
    """Zwraca flagę emoji dla danej waluty na podstawie kodu lub nazwy"""
    if not currency_code and not currency_name:
        return "🏳️"
    
    # Mapowanie kodów walut na kraje
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
        'IRR': 'Iran',
        'IQD': 'Iraq',
        'PKR': 'Pakistan',
        'BDT': 'Bangladesh',
        'VND': 'Vietnam',
        'THB': 'Thailand',
        'IDR': 'Indonesia',
        'PHP': 'Philippines',
        'MYR': 'Malaysia',
        'SGD': 'Singapore',
        'NZD': 'New Zealand',
        'NGN': 'Nigeria',
        'KES': 'Kenya',
        'MAD': 'Morocco',
        'DZD': 'Algeria',
        'TND': 'Tunisia',
        'LYD': 'Libya',
        'ETB': 'Ethiopia',
        'GHS': 'Ghana',
        'XOF': 'Ivory Coast',
        'XAF': 'Central African Republic',
        'AOA': 'Angola',
        'ZMW': 'Zambia',
        'ZWL': 'Zimbabwe',
        'BWP': 'Botswana',
        'NAD': 'Namibia',
        'LSL': 'Lesotho',
        'SZL': 'Swaziland',
        'MGA': 'Madagascar',
        'MUR': 'Mauritius',
        'SCR': 'Seychelles',
        'KMF': 'Comoros',
        'DJF': 'Djibouti',
        'ERN': 'Eritrea',
        'SOS': 'Somalia',
        'UGX': 'Uganda',
        'TZS': 'Tanzania',
        'RWF': 'Rwanda',
        'BIF': 'Burundi',
        'MWK': 'Malawi',
        'MZN': 'Mozambique',
        # Dodatkowe waluty widoczne w raportach
        'ALL': 'Albania',
        'LTL': 'Lithuania',
        'COP': 'Colombia',
        'VEF': 'Venezuela',
        'UYU': 'Uruguay',
        'PYG': 'Paraguay',
        'BOB': 'Bolivia',
        'PEN': 'Peru',
        'CLP': 'Chile',
        'GEL': 'Georgia',
        'AMD': 'Armenia',
        'AZN': 'Azerbaijan',
        'KZT': 'Kazakhstan',
        'UZS': 'Uzbekistan',
        'TMT': 'Turkmenistan',
        'KGS': 'Kyrgyzstan',
        'TJS': 'Tajikistan',
        'AFN': 'Afghanistan',
        'LKR': 'Sri Lanka',
        'NPR': 'Nepal',
        'BTN': 'Bhutan',
        'MMK': 'Myanmar',
        'LAK': 'Laos',
        'KHR': 'Cambodia',
        'MNT': 'Mongolia',
        'KPW': 'North Korea',
        'TWD': 'Taiwan',
        'HKD': 'Hong Kong',
        'MOP': 'Macau',
        'BND': 'Brunei',
    }
    
    # Spróbuj znaleźć kraj na podstawie kodu waluty
    if currency_code and currency_code.upper() in currency_to_country:
        country_name = currency_to_country[currency_code.upper()]
        return get_country_flag(country_name)
    
    # Spróbuj znaleźć kraj na podstawie nazwy waluty
    if currency_name:
        return get_country_flag(currency_name)
    
    return "🏳️"


def create_infographic_html(title, data, labels, color, ax_title):
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
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
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

    # Add source data timestamp
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
        # Resolve country name to English using provided maps if available
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
                <h2>⚔️ Battlefield Pulse: Key Military Statistics</h2>
                <p>Damage attributed to a country is the sum of damage dealt by players from that country in all battles within the last 24 hours (regardless of whether the country was a party to the conflict).</p>
        """

        # Define yesterday_key and today's war counts
        yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        wars_summary = summary_data.get('wars_summary', {}) or {}
        ongoing_wars = wars_summary.get('ongoing') or []
        finished_wars = wars_summary.get('finished') or []
        today_ongoing = len(ongoing_wars)
        today_finished = len(finished_wars)
        
        if ongoing_wars or finished_wars:
            html_content += '<h3>🗺️ Military Activity: Ongoing and Completed Wars</h3>'
            
            if ongoing_wars:
                html_content += '<h4>Ongoing Battles:</h4><ul>'
                for line in ongoing_wars:
                    txt = str(line)
                    txt = txt.replace('wojna', 'war').replace('Wojna', 'War').replace('wynik', 'score').replace('Wynik', 'Score')
                    html_content += f'<li class="list-item">{txt}</li>'
                html_content += '</ul>'
            else:
                html_content += '<p>No ongoing battles at this time.</p>'
                
            if finished_wars:
                html_content += '<h4>Completed Battles:</h4><ul>'
                for line in finished_wars:
                    txt = str(line)
                    txt = txt.replace('wojna', 'war').replace('Wojna', 'War').replace('wynik', 'score').replace('Wynik', 'Score')
                    html_content += f'<li class="list-item">{txt}</li>'
                html_content += '</ul>'
            else:
                html_content += '<p>No completed battles to display.</p>'
            
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
            html_content += f'<p>Military activity was recorded in {len(military_summary)} countries over the last 24 hours.</p>'
            html_content += '<table><tr><th>Country</th><th>Damage</th></tr>'
            for country in top_countries:
                dmg = military_summary[country]
                html_content += f'<tr><td>{normalize_country_name(country)}</td><td>{dmg:,}</td></tr>'
            html_content += '</table>'
            
            # Add executive summary of changes if historical data is available
            if yesterday_key in historical_data:
                html_content += '<h3>📊 Executive Summary: Key Changes</h3>'
                
                # Military changes summary
                if historical_data[yesterday_key].get('military_summary'):
                    yesterday_military = historical_data[yesterday_key]['military_summary']
                    total_today = sum(military_summary.values())
                    total_yesterday = sum(yesterday_military.values())
                    if total_yesterday > 0:
                        military_change_pct = (total_today - total_yesterday) / total_yesterday * 100.0
                        arrow = "▲" if military_change_pct > 0 else ("▼" if military_change_pct < 0 else "→")
                        change_class = "positive" if military_change_pct > 0 else ("negative" if military_change_pct < 0 else "neutral")
                        html_content += f'<p>⚔️ Total military activity: <span class="change {change_class}">{arrow} {military_change_pct:+.1f}%</span> ({total_today:,} vs {total_yesterday:,})</p>'
                
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
                            html_content += f'<p>💰 Currency volatility: {significant_changes} currencies changed by >1%</p>'
                        else:
                            html_content += '<p>💰 Currency markets: Stable (no significant changes)</p>'
                
                html_content += '<p>See detailed comparisons below for specific metrics.</p>'
                
            # Military comparison with yesterday
            if yesterday_key in historical_data and historical_data[yesterday_key].get('military_summary'):
                html_content += '<h3>⚖️ Military Activity: Compared to Yesterday</h3>'
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
                <h2>🏆 Best of the Best: Heroes Ranking</h2>
        """
        
        top_warriors_local = summary_data.get('top_warriors', [])
        if not top_warriors_local:
            html_content += '<p>No data available for top warriors from the last day.</p>'
        else:
            html_content += '<p>Here is the list of the most powerful warriors from the last 24 hours:</p>'
            cm = country_map or {}
            html_content += '<table><tr><th>Position</th><th>Warrior</th><th>Country</th><th>Damage</th></tr>'
            for i, warrior in enumerate(top_warriors_local, 1):
                username = str(warrior.get('username', 'Unknown'))
                damage = warrior.get('damage', 0)
                country = warrior.get('country', 'Unknown')
                # Resolve country name using provided maps if available
                if not country or str(country).strip().lower() == 'nieznany kraj':
                    nat_id = warrior.get('nationality_id')
                    reg_id = warrior.get('region_id')
                    if nat_id in (cm or {}):
                        country = cm.get(nat_id)
                    elif reg_id in (cm or {}):
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
                    today_usernames = {str(w.get('username', '')).lower() for w in top_warriors_local}
                    yesterday_usernames = {str(w.get('username', '')).lower() for w in yesterday_warriors}
                    
                    maintained = today_usernames.intersection(yesterday_usernames)
                    if maintained:
                        html_content += '<h4>Wojownicy, którzy utrzymali pozycje w czołówce:</h4><ul>'
                        for warrior in top_warriors_local:
                            username = str(warrior.get('username', '')).lower()
                            if username in maintained:
                                # Find yesterday's data for this warrior
                                yesterday_warrior = next((w for w in yesterday_warriors if str(w.get('username', '')).lower() == username), None)
                                if yesterday_warrior:
                                    today_damage = warrior.get('damage', 0)
                                    yesterday_damage = yesterday_warrior.get('damage', 0)
                                    if yesterday_damage > 0:
                                        change_pct = (today_damage - yesterday_damage) / yesterday_damage * 100.0
                                        arrow = "▲" if change_pct > 0 else "▼"
                                        change_class = "positive" if change_pct > 0 else "negative"
                                        html_content += f'<li class="list-item">{username.title()}: <span class="change {change_class}">{arrow} {change_pct:+.1f}%</span> ({today_damage:,} vs {yesterday_damage:,})</li>'
                        html_content += '</ul>'
                    
                    # Find new warriors
                    new_warriors = today_usernames - yesterday_usernames
                    if new_warriors:
                        html_content += '<h4>Nowi wojownicy w czołówce:</h4><ul>'
                        for warrior in top_warriors_local:
                            username = str(warrior.get('username', '')).lower()
                            if username in new_warriors:
                                damage = warrior.get('damage', 0)
                                country = warrior.get('country', 'Unknown')
                                html_content += f'<li class="list-item">{username.title()} ({country}): {damage:,} obrażeń</li>'
                        html_content += '</ul>'

        html_content += '</div>'  # End top warriors section

    # Economic summary
    if sections.get('economic', True):
        html_content += """
            <div class="section">
                <h2>💰 Economic Pulse</h2>
        """
        
        economic_data = summary_data.get('economic_summary', {})
        if not economic_data:
            html_content += '<p>No economic data available (endpoint may be unavailable).</p>'
        else:
            # Top 5 best job offers worldwide
            if economic_data.get('job_offers'):
                html_content += '<h3>💼 Top 5 Best Job Offers Worldwide</h3>'
                html_content += '<p>Best paid job offers across all countries (salary in GOLD):</p>'
                html_content += '<table><tr><th>Position</th><th>Country</th><th>Salary (GOLD)</th><th>Description</th></tr>'
                for i, offer in enumerate(economic_data['job_offers'][:5], 1):
                    country = offer.get('country', 'Unknown')
                    salary = offer.get('salary', 0)
                    description = offer.get('description', 'No description')
                    html_content += f'<tr><td>{i}</td><td>{country}</td><td>{salary:.6f}</td><td>{description}</td></tr>'
                html_content += '</table>'
            
            # Currency rates vs GOLD
            if economic_data.get('currency_rates'):
                html_content += '<h3>Currency Rates vs GOLD</h3>'
                try:
                    # Try to compute yesterday diffs if available
                    yesterday_key = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                    yesterday_rates = {}
                    
                    if yesterday_key in historical_data and historical_data[yesterday_key].get('economic_summary'):
                        yesterday_rates = historical_data[yesterday_key]['economic_summary'].get('currency_rates', {})
                    
                    html_content += '<table><tr><th>Currency</th><th>Rate (GOLD per 1)</th><th>Yesterday Rate</th><th>Change %</th></tr>'
                    
                    # Sort currencies by current rate
                    sorted_currencies = sorted(economic_data['currency_rates'].items(), key=lambda x: float(x[1]) if x[1] else 0)
                    
                    for currency_id, rate in sorted_currencies:
                        try:
                            current_rate = float(rate) if rate else 0
                            # Convert currency_id to string for yesterday_rates lookup
                            currency_id_str = str(currency_id)
                            yesterday_rate = float(yesterday_rates.get(currency_id_str, 0)) if yesterday_rates.get(currency_id_str) else 0
                            
                            # Get currency name and flag from maps
                            currency_code = currency_codes_map.get(currency_id, "") if currency_codes_map else ""
                            currency_name_raw = currencies_map.get(currency_id, f"Currency {currency_id}") if currencies_map else f"Currency {currency_id}"
                            
                            # Get flag for this currency
                            # If currency_code is empty, use currency_name_raw as the code
                            effective_currency_code = currency_code if currency_code else currency_name_raw
                            flag = get_currency_flag(effective_currency_code, currency_name_raw)
                            
                            # Format currency name with flag
                            if effective_currency_code:
                                currency_name = f"{flag} {effective_currency_code}"
                            else:
                                currency_name = f"{flag} {currency_name_raw}"
                            
                            # Calculate change
                            if yesterday_rate > 0:
                                change_pct = (current_rate - yesterday_rate) / yesterday_rate * 100.0
                                arrow = "▲" if change_pct > 0 else ("▼" if change_pct < 0 else "→")
                                change_class = "positive" if change_pct > 0 else ("negative" if change_pct < 0 else "neutral")
                                change_text = f'<span class="change {change_class}">{arrow} {change_pct:+.2f}%</span>'
                            else:
                                change_text = '<span class="change neutral">→ +0.00%</span>'
                            
                            html_content += f'<tr><td>{currency_name}</td><td>{current_rate:.6f}</td><td>{yesterday_rate:.6f}</td><td>{change_text}</td></tr>'
                        except (ValueError, TypeError):
                            continue
                    
                    html_content += '</table>'
                except Exception as e:
                    html_content += f'<p>Error generating currency rates table: {e}</p>'
            
            # Cheapest goods from all countries
            if economic_data.get('cheapest_items_all_countries'):
                html_content += '<h3>🌍 Cheapest Goods from All Countries</h3>'
                html_content += '<p>Best offer for each product from all countries:</p>'
                
                # Create one table with all items and their best offers
                html_content += '<table><tr><th>Product</th><th>Country</th><th>Price (currency)</th><th>Price (GOLD)</th><th>Quantity</th></tr>'
                
                # Process each item type and get the best offer
                for item_id, item_data in economic_data['cheapest_items_all_countries'].items():
                    if not item_data or not isinstance(item_data, list) or len(item_data) == 0:
                        continue
                    
                    # Get item name from map - try both string and int keys
                    item_name = None
                    if isinstance(item_id, str):
                        item_name = items_map.get(item_id) or items_map.get(int(item_id) if item_id.isdigit() else None)
                    elif isinstance(item_id, int):
                        item_name = items_map.get(item_id) or items_map.get(str(item_id))
                    else:
                        item_name = items_map.get(str(item_id))
                    
                    if not item_name:
                        item_name = f"Item {item_id}"
                    
                    # Get item icon
                    item_icon = get_item_icon(item_name)
                    
                    # Get the best offer (first one in the sorted list)
                    best_offer = item_data[0]
                    country_name = best_offer.get('country', 'Unknown')
                    price_currency = best_offer.get('price_currency', 0)
                    price_gold = best_offer.get('price_gold', 0)
                    amount = best_offer.get('amount', 0)
                    
                    # Get country flag
                    country_flag = get_country_flag(country_name)
                    
                    html_content += f'<tr>'
                    html_content += f'<td>{item_icon} {item_name}</td>'
                    html_content += f'<td>{country_flag} {country_name}</td>'
                    html_content += f'<td>{price_currency:.3f}</td>'
                    html_content += f'<td>{price_gold:.6f}</td>'
                    html_content += f'<td>{amount}</td>'
                    html_content += f'</tr>'
                
                html_content += '</table>'
            else:
                # Add useful economic information instead of empty section
                html_content += '<h3>📊 Additional Economic Information</h3>'
                
                # Show extreme currency rates
                if economic_data.get('currency_rates'):
                    rates = [(k, float(v)) for k, v in economic_data['currency_rates'].items() if v]
                    if rates:
                        rates.sort(key=lambda x: x[1])
                        html_content += '<div class="category-section">'
                        html_content += '<h4 class="category-title">Skrajne Kursy Walut</h4>'
                        html_content += f'<p>Najniższy kurs: {rates[0][1]:.6f} GOLD za 1 {rates[0][0]}</p>'
                        html_content += f'<p>Najwyższy kurs: {rates[-1][1]:.6f} GOLD za 1 {rates[-1][0]}</p>'
                        html_content += '</div>'
                
                # Show countries with lowest NPC wages
                if economic_data.get('npc_wages'):
                    wages = [(k, float(v)) for k, v in economic_data['npc_wages'].items() if v]
                    if wages:
                        wages.sort(key=lambda x: x[1])
                        html_content += '<div class="category-section">'
                        html_content += '<h4 class="category-title">Kraje z Najniższymi Płacami NPC</h4>'
                        html_content += '<ul>'
                        for country, wage in wages[:5]:
                            html_content += f'<li class="list-item">{country}: {wage:.2f} GOLD</li>'
                        html_content += '</ul></div>'
                
                # Show available data keys
                html_content += '<div class="category-section">'
                html_content += '<h4 class="category-title">Dostępne Dane w Systemie</h4>'
                html_content += '<ul>'
                for key in economic_data.keys():
                    if key == 'currency_rates':
                        html_content += f'<li class="list-item"><strong>{key}:</strong> Kursy walut ({len(economic_data[key])} walut)</li>'
                    elif key == 'npc_wages':
                        html_content += f'<li class="list-item"><strong>{key}:</strong> Płace NPC ({len(economic_data[key])} krajów)</li>'
                    elif key == 'job_offers':
                        html_content += f'<li class="list-item"><strong>{key}:</strong> Oferty pracy ({len(economic_data[key])} ofert)</li>'
                    else:
                        html_content += f'<li class="list-item"><strong>{key}:</strong> {description}</li>'
                html_content += '</ul>'
                html_content += '<p><em>💡 Dane o najtańszych towarach są pobierane w tle i będą dostępne w kolejnych raportach.</em></p>'
                html_content += '</div>'

        # Production analysis as part of economic section
        production_data = summary_data.get('production_data', [])
        if sections.get('production', True) and production_data:
            html_content += """
                <h3>🏭 Regional Productivity Analysis</h3>
                <p>Analysis of production efficiency in different regions for various products.</p>
            """
            
            # Group by item type and show top 10 for each
            items_groups = {}
            for data in production_data:
                item_name = getattr(data, 'item_name', 'unknown')
                if item_name not in items_groups:
                    items_groups[item_name] = []
                items_groups[item_name].append(data)
            
            # Sort each group by efficiency score and take top 10
            for item_name in items_groups:
                items_groups[item_name].sort(key=lambda x: x.efficiency_score, reverse=True)
                items_groups[item_name] = items_groups[item_name][:10]  # Top 10 najkonkurencyjniejszych
            
            # Display each item type
            for item_name, items in items_groups.items():
                if items:
                    # Capitalize and translate item name
                    item_display_name = item_name.capitalize()
                    if item_name == 'grain':
                        item_display_name = 'Grain'
                    elif item_name == 'iron':
                        item_display_name = 'Iron'
                    elif item_name == 'titanium':
                        item_display_name = 'Titanium'
                    elif item_name == 'fuel':
                        item_display_name = 'Fuel'
                    elif item_name == 'food':
                        item_display_name = 'Food'
                    elif item_name == 'weapon':
                        item_display_name = 'Weapons'
                    elif item_name == 'aircraft':
                        item_display_name = 'Aircraft'
                    elif item_name == 'airplane ticket':
                        item_display_name = 'Airplane Tickets'
                    
                    html_content += f'<div class="category-section"><h4 class="category-title">{item_display_name} - Top 10 Most Competitive Regions</h4>'
                    html_content += '<table><tr><th>Region</th><th>Country</th><th>Q1</th><th>Q2</th><th>Q3</th><th>Q4</th><th>Q5</th><th>Bonus</th><th>NPC Wages (GOLD)</th><th>Score</th></tr>'
                    
                    for item in items:
                        html_content += f'<tr>'
                        html_content += f'<td>{item.region_name}</td>'
                        html_content += f'<td>{item.country_name}</td>'
                        html_content += f'<td>{item.production_q1}</td>'
                        html_content += f'<td>{item.production_q2}</td>'
                        html_content += f'<td>{item.production_q3}</td>'
                        html_content += f'<td>{item.production_q4}</td>'
                        html_content += f'<td>{item.production_q5}</td>'
                        html_content += f'<td>{item.total_bonus:.2f}</td>'
                        html_content += f'<td>{item.npc_wages:.2f}</td>'
                        html_content += f'<td>{item.efficiency_score:.2f}</td>'
                        html_content += f'</tr>'
                    
                    html_content += '</table></div>'

        html_content += '</div>'  # End economic section

    # Footer
    html_content += f"""
        <div class="footer">
            <p>Report generated by Eclesiar application</p>
            <p>Generation date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
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
    
    print(f"HTML report successfully generated as '{file_path}'")
    return file_path
