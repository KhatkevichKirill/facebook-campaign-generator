"""
Utility functions for generating campaign names according to naming rules
"""
from typing import Dict, Optional


def generate_campaign_name(params: Dict) -> str:
    """
    Генерирует нейминг кампании по правилам
    
    Формат: [OS]_[PROJECT]_[TIER]([COUNTRIES])_[GENDER]_[AGE]_[OPT MODEL][[EVENT?]]_[DATE]_[AUTOR]_[CBO/noCBO]_[BID STRATEGY]_[LANG]_[EXTRA?]
    
    Args:
        params: словарь с параметрами:
            - os: OS (AND или IOS)
            - project_alias: алиас проекта (DC, LK, PM)
            - tier: тир (Tier-1, Latam, etc.)
            - naming_countries: список стран для нейминга (опционально)
            - gender: гендер (M, F, MF)
            - age: возраст (18-65+, 21-65, etc.)
            - opt_model: модель оптимизации (CPA, CPI, tROAS)
            - event: код события (опционально, только для CPA)
            - date: дата в формате DDMMYYYY
            - autor: автор (KH, YU, etc.)
            - campaign_type: тип кампании (CBO или noCBO)
            - bid_strategy_short: короткое название стратегии ставки (bc, cc, lc, ai)
            - lang: язык (ENG, ALL, etc.)
            - extra: дополнительное поле (account name, опционально)
    
    Returns:
        Сгенерированное название кампании
    """
    # OS
    os_name = params['os']  # AND или IOS
    
    # PROJECT
    project_alias = params['project_alias']  # DC
    
    # TIER
    tier = params['tier']  # Tier-1, Latam, etc.
    
    # COUNTRIES (в скобках, если указаны)
    countries_str = ""
    if params.get('naming_countries'):
        countries_str = f"({','.join(params['naming_countries'])})"
    
    # GENDER
    gender = params['gender']  # M, F, MF
    
    # AGE
    age = params['age']  # 18-65+, 21-65, etc.
    
    # OPT MODEL
    opt_model = params['opt_model']  # CPA, CPI, tROAS
    
    # EVENT (только для CPA)
    event_str = ""
    if opt_model == "CPA" and params.get('event'):
        event_str = f"[{params['event']}]"
    
    # DATE
    date_str = params['date']  # DDMMYYYY
    
    # AUTOR
    autor = params['autor']  # KH, YU, etc.
    
    # CBO/noCBO
    campaign_type = params['campaign_type']  # CBO или noCBO
    
    # BID STRATEGY
    bid_strategy_short = params['bid_strategy_short']  # bc, cc, lc, ai
    
    # LANG
    lang = params['lang']  # ENG, ALL, etc.
    
    # EXTRA (account name)
    extra = params.get('extra', '')  # DC1, LK1, etc.
    
    # Формируем нейминг
    name_parts = [
        os_name,
        project_alias,
        tier + countries_str,
        gender,
        age,
        opt_model + event_str,
        date_str,
        autor,
        campaign_type,
        bid_strategy_short,
        lang
    ]
    
    if extra:
        name_parts.append(extra)
    
    return "_".join(name_parts)

