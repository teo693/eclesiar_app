from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple

from api_client import fetch_data


def fetch_account_details(account_id, cache=None):
    if cache is None:
        cache = {}
    if account_id in cache:
        return cache[account_id]
    try:
        account_data = fetch_data(f"account?account_id={account_id}", f"szczegóły konta {account_id}")
        if account_data and account_data.get('data'):
            user_info = account_data['data']
            cache[account_id] = {
                'username': user_info.get('username', f'User_{account_id}'),
                'avatar': user_info.get('avatar', ''),
                'nationality_id': user_info.get('nationality_id'),
                'region_id': user_info.get('region_id'),
                'total_damage': user_info.get('total_damage', 0),
                'total_mined_gold': user_info.get('total_mined_gold', 0)
            }
            return cache[account_id]
    except Exception:
        pass
    cache[account_id] = {
        'username': f'Fighter_{account_id}',
        'avatar': '',
        'nationality_id': None,
        'region_id': None,
        'total_damage': 0,
        'total_mined_gold': 0
    }
    return cache[account_id]


def process_hits_data(raw_data_from_file: Dict[str, Any], country_map: Dict[int, str]):
    military_summary: Dict[str, int] = {}
    warrior_data: Dict[int, int] = {}
    yesterday = datetime.now() - timedelta(days=1)
    account_cache: Dict[int, Any] = {}

    hits_data = raw_data_from_file.get('hits', {})
    for round_id, round_hits_data in hits_data.items():
        if not round_hits_data or not round_hits_data.get('data'):
            continue
        for hit in round_hits_data['data']:
            created_at_str = hit.get('created_at')
            if not created_at_str:
                continue
            try:
                if created_at_str.count(':') == 1:
                    created_at_str += ":00"
                created_at = datetime.strptime(created_at_str, "%Y-%m-%d %H:%M:%S")
                if created_at > yesterday:
                    damage = hit.get('damage', 0)
                    fighter = hit.get('fighter', {})
                    fighter_id = fighter.get('id') if fighter else None
                    if damage > 0 and fighter_id:
                        warrior_data[fighter_id] = warrior_data.get(fighter_id, 0) + damage
            except Exception:
                continue

    top_fighter_ids = sorted(warrior_data.keys(), key=lambda x: warrior_data[x], reverse=True)[:15]
    top_warriors: List[Dict[str, Any]] = []
    for fighter_id in top_fighter_ids:
        account_details = fetch_account_details(fighter_id, account_cache)
        warrior_info = {
            'id': fighter_id,
            'username': account_details['username'],
            'avatar': account_details['avatar'],
            'damage': warrior_data[fighter_id],
            'nationality_id': account_details['nationality_id'],
            'region_id': account_details['region_id'],
            'total_damage': account_details['total_damage']
        }
        country_name = "Nieznany Kraj"
        if account_details['nationality_id'] and account_details['nationality_id'] in country_map:
            country_name = country_map[account_details['nationality_id']]
        elif account_details['region_id'] and account_details['region_id'] in country_map:
            country_name = country_map[account_details['region_id']]
        warrior_info['country'] = country_name
        top_warriors.append(warrior_info)
        military_summary[country_name] = military_summary.get(country_name, 0) + warrior_data[fighter_id]

    top_warriors = sorted(top_warriors, key=lambda x: x.get('damage', 0), reverse=True)[:10]
    return military_summary, top_warriors


def build_wars_summary(raw_data_from_file: Dict[str, Any], country_map: Dict[int, str]):
    wars_payload = (raw_data_from_file or {}).get('wars') or {}
    wars_list = wars_payload.get('data') or []

    ongoing: List[str] = []
    finished: List[str] = []

    from datetime import datetime as _dt
    for w in wars_list:
        war_id = w.get('id')
        atk_name = None
        def_name = None
        try:
            # API may return either attacker/defender or attackers/defenders
            atk_obj = w.get('attacker') or w.get('attackers') or {}
            dfd_obj = w.get('defender') or w.get('defenders') or {}
            atk_name = (atk_obj.get('name') if isinstance(atk_obj, dict) else None) or (
                country_map.get(atk_obj.get('id')) if isinstance(atk_obj, dict) else None
            )
            def_name = (dfd_obj.get('name') if isinstance(dfd_obj, dict) else None) or (
                country_map.get(dfd_obj.get('id')) if isinstance(dfd_obj, dict) else None
            )
        except Exception:
            atk_name = None
            def_name = None
        if not atk_name:
            atk_name = w.get('attacker_name') or f"Kraj {w.get('attacker_id', '?')}"
        if not def_name:
            def_name = w.get('defender_name') or f"Kraj {w.get('defender_id', '?')}"

        # Region is a top-level field in the new API shape
        region_name = None
        try:
            region = w.get('region')
            if isinstance(region, dict):
                region_name = region.get('name') or region.get('title')
        except Exception:
            region_name = None

        title = f"{atk_name} vs {def_name} (wojna #{war_id})"
        if region_name:
            title = f"{title} — region {region_name}"
        status = (w.get('status') or '').lower()
        is_finished = w.get('is_finished')
        end_date = w.get('end_date') or w.get('finished_at')

        classified_finished = False
        try:
            if is_finished is True:
                classified_finished = True
            elif status in ['finished', 'ended', 'closed', 'completed']:
                classified_finished = True
            elif end_date:
                try:
                    dt = _dt.fromisoformat(str(end_date).replace('Z', '+00:00'))
                    if dt <= _dt.now(dt.tzinfo) if dt.tzinfo else dt <= _dt.now():
                        classified_finished = True
                except Exception:
                    pass
        except Exception:
            pass

        line_extra = None
        try:
            # Support both attacker_score/defender_score and attackers_score/defenders_score
            score_a = w.get('attacker_score') if 'attacker_score' in w else w.get('attackers_score')
            score_d = w.get('defender_score') if 'defender_score' in w else w.get('defenders_score')
            if isinstance(score_a, (int, float)) and isinstance(score_d, (int, float)):
                line_extra = f" (wynik {int(score_a)}:{int(score_d)})"
        except Exception:
            line_extra = None

        display_line = title + (line_extra or '')
        if classified_finished:
            finished.append(display_line)
        else:
            ongoing.append(display_line)

    return {"ongoing": ongoing, "finished": finished}


