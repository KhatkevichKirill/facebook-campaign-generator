#!/usr/bin/env python3
"""
Скрипт для создания одной кампании Facebook через API
"""
import os
import sys
from datetime import datetime
from utils.tier_utils import load_tiers, get_all_countries_for_tier, format_tier_for_naming
from utils.logging import log_campaign_creation
from utils.csv_generator import create_csv_fallback
from utils.naming import generate_campaign_name
from utils.campaign_builder import create_campaign_via_api, create_adset_via_api
from utils.config_loader import load_json


def get_locale_ids(lang_code, locales_data):
    """
    Маппинг языковых кодов на Facebook locale IDs из словаря locales.json
    """
    return locales_data.get(lang_code, [])


def main():
    """Основная функция"""
    # Параметры кампании
    project_name = "DuoChat"
    os_name = "AND"
    tier_name = "Latam"
    gender = "M"
    event_name = "4 сессии"
    daily_budget = 50.0
    bid_value = 0.30
    age = "18-65+"
    language_name = "Испанский"
    
    # Загружаем справочники
    projects = load_json('dictionares/projects.json')
    accounts = load_json('dictionares/accounts.json')
    events = load_json('dictionares/events.json')
    languages = load_json('dictionares/languages.json')
    locales_data = load_json('dictionares/locales.json')
    objectives = load_json('dictionares/objectives.json')
    optimization_goals = load_json('dictionares/optimization_goals.json')
    bid_strategies = load_json('dictionares/bid_strategies.json')
    event_types = load_json('dictionares/event_types.json')
    api_config = load_json('dictionares/api_config.json')
    tiers_data = load_tiers()
    
    # Получаем данные проекта
    project = projects[project_name]
    project_alias = project['alias']
    
    # Получаем событие
    event_code = events[event_name]  # session_started_4
    
    # Получаем язык
    lang_code = languages[language_name]  # ES
    
    # Определяем параметры
    opt_model = "CPA"
    campaign_type = "noCBO"
    bid_strategy = "Bid cap"
    bid_strategy_short = "bc"
    autor = "KH"
    
    # Дата
    today = datetime.now()
    date_str = today.strftime("%d%m%Y")
    
    # Возраст
    age_parts = age.replace('+', '').split('-')
    age_min = int(age_parts[0])
    age_max = int(age_parts[1]) if len(age_parts) > 1 else 65
    
    # Гендер
    genders_map = {"M": [1], "F": [2], "MF": [1, 2]}
    genders = genders_map[gender]
    
    # Тир
    tier_mapping = {
        "Latam": "LatAm",
        "latam": "LatAm",
        "LatAm": "LatAm"
    }
    tier_raw = tier_mapping.get(tier_name, tier_name)
    tier = format_tier_for_naming(tier_raw)
    countries = get_all_countries_for_tier(tier_raw)
    
    # Исключаем ограниченные страны (например, Куба)
    restricted_countries = ["CU"]  # Куба ограничена Facebook
    countries = [c for c in countries if c not in restricted_countries]
    
    # Выбираем аккаунт (DC1 по умолчанию)
    account_name = project['account_names'][0]  # DC1
    account_id = accounts[account_name]
    
    # API маппинги
    objective_api = objectives[project['campaign_objective']]
    optimization_goal_api = optimization_goals[opt_model]
    bid_strategy_api = bid_strategies[bid_strategy]
    custom_event_type_api = event_types[event_code]
    
    # Application ID без префикса "x:"
    application_id = project['application_id'].replace('x:', '')
    
    # Locales для таргетинга
    # Временно не используем locales из-за проблем с API
    # Для испанского языка в Latam можно таргетировать все языки или использовать региональные коды
    locales = []  # Таргетинг всех языков (пока не решена проблема с locales)
    
    # Параметры для нейминга
    naming_params = {
        'os': os_name,
        'project_alias': project_alias,
        'tier': tier,
        'naming_countries': [],  # Для всего тира не перечисляем страны
        'gender': gender,
        'age': age,
        'opt_model': opt_model,
        'event': event_code,
        'date': date_str,
        'autor': autor,
        'campaign_type': campaign_type,
        'bid_strategy_short': bid_strategy_short,
        'lang': lang_code,
        'extra': account_name
    }
    
    campaign_name = generate_campaign_name(naming_params)
    
    # Показываем нейминг пользователю
    print("=" * 80)
    print("ГЕНЕРАЦИЯ КАМПАНИИ")
    print("=" * 80)
    print(f"Проект: {project_name}")
    print(f"OS: {os_name}")
    print(f"Тир: {tier} ({len(countries)} стран)")
    print(f"Гендер: {gender}")
    print(f"Событие: {event_name} ({event_code})")
    print(f"Бюджет: ${daily_budget}")
    print(f"Бид: ${bid_value}")
    print(f"Возраст: {age}")
    print(f"Язык: {language_name} ({lang_code})")
    print()
    print(f"Нейминг: {campaign_name}")
    print("=" * 80)
    
    # Запрашиваем подтверждение
    confirmation = input("\nСоздать кампанию с этим неймингом? (yes/no): ").strip().lower()
    
    if confirmation != 'yes':
        print("Создание кампании отменено.")
        return
    
    # Создаем кампанию через API
    print("\nСоздание кампании через API...")
    
    try:
        # Параметры для API
        api_params = {
            'daily_budget': daily_budget,
            'optimization_goal': optimization_goal_api,
            'bid_strategy': bid_strategy_api,
            'bid_amount': bid_value,
            'custom_event_type': custom_event_type_api,
            'custom_event_str': event_code,
            'object_store_url': project['object_store_url'],
            'application_id': application_id,
            'targeting_countries': countries,
            'age_min': age_min,
            'age_max': age_max,
            'genders': genders,
            'user_os': 'android',
            'locales': locales
        }
        
        # Создаем кампанию
        campaign_id = create_campaign_via_api(
            account_id,
            campaign_name,
            objective_api,
            api_config
        )
        print(f"✓ Кампания создана: {campaign_id}")
        
        # Создаем адсет (используем targeting для совместимости)
        adset_id = create_adset_via_api(
            account_id,
            campaign_id,
            campaign_name,
            api_params,
            api_config,
            use_targeting_spec=False
        )
        print(f"✓ Адсет создан: {adset_id}")
        
        # Логируем
        log_campaign_creation(
            campaign_name=campaign_name,
            campaign_id=campaign_id,
            adset_id=adset_id
        )
        print(f"✓ Запись добавлена в logs.csv")
        
        print("\n" + "=" * 80)
        print("КАМПАНИЯ УСПЕШНО СОЗДАНА!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ Ошибка при создании кампании: {e}")
        print("\nСоздание CSV файла для ручной загрузки...")
        try:
            csv_path = create_csv_fallback(
                campaign_name=campaign_name,
                params=api_params,
                project=project
            )
            print(f"✓ CSV файл создан: {csv_path}")
            print("\nВы можете загрузить этот файл вручную через Facebook Ads Manager.")
        except Exception as csv_error:
            print(f"✗ Ошибка при создании CSV: {csv_error}")


if __name__ == "__main__":
    main()

