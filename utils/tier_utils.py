"""
Utility functions for working with tiers and countries
"""
import json
import os


def load_tiers():
    """Загружает словарь tiers.json"""
    tiers_file = os.path.join(os.path.dirname(__file__), '..', 'dictionares', 'tiers.json')
    with open(tiers_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_tier_for_country(country_code):
    """
    Определяет тир для одной страны
    
    Args:
        country_code: ISO код страны (например, "US")
    
    Returns:
        Название тира или None если страна не найдена
    """
    tiers = load_tiers()
    for tier, countries in tiers.items():
        if country_code in countries:
            return tier
    return None


def get_tier_for_countries(country_codes):
    """
    Определяет тир для списка стран
    
    Args:
        country_codes: список ISO кодов стран (например, ["US", "CA"])
    
    Returns:
        - Если все страны из одного тира → название тира
        - Если страны из разных тиров → None
        - Если страна не найдена → None
    """
    if not country_codes:
        return None
    
    tiers = load_tiers()
    tier_counts = {}
    
    for country in country_codes:
        tier = get_tier_for_country(country)
        if tier is None:
            return None  # Страна не найдена
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    # Если все страны из одного тира
    if len(tier_counts) == 1:
        return list(tier_counts.keys())[0]
    
    # Страны из разных тиров
    return None


def get_all_countries_for_tier(tier_name):
    """
    Получает все страны для указанного тира
    
    Args:
        tier_name: название тира (например, "LatAm")
    
    Returns:
        Список ISO кодов стран или пустой список
    """
    tiers = load_tiers()
    return tiers.get(tier_name, [])


def format_tier_for_naming(tier_name):
    """
    Форматирует название тира для нейминга
    
    Args:
        tier_name: название тира из tiers.json
    
    Returns:
        Отформатированное название для нейминга
    """
    # Маппинг для читаемости в нейминге
    mapping = {
        "Tier1": "Tier-1",
        "LatAm": "Latam"
    }
    return mapping.get(tier_name, tier_name)


def get_all_worldwide_countries(tiers_data=None):
    """
    Собирает все страны из всех тиров для таргетинга на весь мир
    
    Args:
        tiers_data: словарь тиров из tiers.json (если None, загружается автоматически)
    
    Returns:
        Отсортированный список всех стран из всех тиров
    """
    if tiers_data is None:
        tiers_data = load_tiers()
    
    all_countries = []
    for tier_name, countries in tiers_data.items():
        all_countries.extend(countries)
    # Убираем дубликаты и сортируем
    return sorted(list(set(all_countries)))


def determine_tier_and_countries(user_countries, user_tier=None):
    """
    Определяет тир и страны для таргетинга и нейминга
    
    Args:
        user_countries: список стран от пользователя (может быть пустым)
        user_tier: указанный пользователем тир (опционально)
    
    Returns:
        dict с полями:
        - tier: название тира для нейминга
        - tier_raw: название тира из tiers.json
        - countries: список стран для таргетинга
        - naming_countries: список стран для нейминга (может быть пустым)
    """
    tiers = load_tiers()
    
    # Если указан тир напрямую
    if user_tier:
        # Нормализуем название тира
        tier_mapping = {
            "Tier-1": "Tier1",
            "Latam": "LatAm",
            "latam": "LatAm",
            "tier-1": "Tier1"
        }
        tier_raw = tier_mapping.get(user_tier, user_tier)
        
        if tier_raw in tiers:
            return {
                "tier": format_tier_for_naming(tier_raw),
                "tier_raw": tier_raw,
                "countries": tiers[tier_raw],  # Все страны тира
                "naming_countries": []  # В нейминге не перечисляем
            }
    
    # Если указаны конкретные страны
    if user_countries:
        # Определяем тиры для всех стран
        country_tiers = {}
        for country in user_countries:
            tier = get_tier_for_country(country)
            if tier:
                country_tiers[tier] = country_tiers.get(tier, 0) + 1
        
        if not country_tiers:
            # Страны не найдены в словаре
            return {
                "tier": None,
                "tier_raw": None,
                "countries": user_countries,
                "naming_countries": user_countries
            }
        
        # Если все страны из одного тира
        if len(country_tiers) == 1:
            tier_raw = list(country_tiers.keys())[0]
            return {
                "tier": format_tier_for_naming(tier_raw),
                "tier_raw": tier_raw,
                "countries": user_countries,
                "naming_countries": user_countries  # Всегда перечисляем страны
            }
        
        # Страны из разных тиров
        if len(user_countries) > 5:
            # Используем WW, но перечисляем все страны в нейминге
            return {
                "tier": "WW",
                "tier_raw": "WW",
                "countries": user_countries,
                "naming_countries": user_countries  # Перечисляем все страны при WW
            }
        else:
            # 5 или менее стран из разных тиров - перечисляем все
            # Определяем тир по большинству
            tier_raw = max(country_tiers.items(), key=lambda x: x[1])[0]
            return {
                "tier": format_tier_for_naming(tier_raw),
                "tier_raw": tier_raw,
                "countries": user_countries,
                "naming_countries": user_countries
            }
    
    return None
