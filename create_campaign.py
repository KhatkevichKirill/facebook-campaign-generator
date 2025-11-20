#!/usr/bin/env python3
"""
Скрипт для создания кампаний Facebook через API
"""
import os
import sys
from datetime import datetime
from utils.tier_utils import load_tiers, get_all_countries_for_tier, format_tier_for_naming
from utils.logging import log_campaign_creation
from utils.naming import generate_campaign_name
from utils.campaign_builder import create_campaign_via_api, create_adset_via_api
from utils.config_loader import load_json


def main():
    """Основная функция"""
    # Параметры кампании
    project_name = "DuoChat"
    os_name = "AND"
    gender = "M"
    event_name = "4 сессии"
    daily_budget = 50.0
    bid_value = 0.30
    age = "18-65+"
    
    # Загружаем справочники
    projects = load_json('dictionares/projects.json')
    accounts = load_json('dictionares/accounts.json')
    events = load_json('dictionares/events.json')
    objectives = load_json('dictionares/objectives.json')
    optimization_goals = load_json('dictionares/optimization_goals.json')
    bid_strategies = load_json('dictionares/bid_strategies.json')
    event_types = load_json('dictionares/event_types.json')
    api_config = load_json('dictionares/api_config.json')
    tiers_data = load_tiers()
    
    # Получаем данные проекта
    project = projects[project_name]
    
    # Получаем событие
    event_code = events[event_name]  # session_started_4
    
    # Определяем параметры
    opt_model = "CPA"
    campaign_type = "noCBO"
    bid_strategy = "Bid cap"
    bid_strategy_short = "bc"
    lang = "ALL"
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
    
    # API маппинги
    objective_api = objectives[project['campaign_objective']]
    optimization_goal_api = optimization_goals[opt_model]
    bid_strategy_api = bid_strategies[bid_strategy]
    custom_event_type_api = event_types[event_code]
    
    # Application ID без префикса "x:"
    application_id = project['application_id'].replace('x:', '')
    
    # Генерируем кампании для всех тиров
    all_tiers = list(tiers_data.keys())
    campaign_names = []
    
    print("=" * 80)
    print("ГЕНЕРАЦИЯ КАМПАНИЙ ДЛЯ ВСЕХ ТИРОВ")
    print("=" * 80)
    print(f"Проект: {project_name}")
    print(f"OS: {os_name}")
    print(f"Гендер: {gender}")
    print(f"Событие: {event_name} ({event_code})")
    print(f"Бюджет: ${daily_budget}")
    print(f"Бид: ${bid_value}")
    print(f"Возраст: {age}")
    print()
    
    for tier_raw in all_tiers:
        tier = format_tier_for_naming(tier_raw)
        countries = get_all_countries_for_tier(tier_raw)
        
        # Выбираем аккаунт (DC1 по умолчанию)
        account_name = project['account_names'][0]  # DC1
        account_id = accounts[account_name]
        
        # Параметры для нейминга
        naming_params = {
            'os': os_name,
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
            'lang': lang,
            'extra': account_name
        }
        
        campaign_name = generate_campaign_name(naming_params)
        campaign_names.append({
            'name': campaign_name,
            'tier': tier,
            'tier_raw': tier_raw,
            'countries': countries,
            'account_id': account_id,
            'account_name': account_name
        })
        
        print(f"Тир: {tier}")
        print(f"  Страны: {len(countries)} стран")
        print(f"  Нейминг: {campaign_name}")
        print()
    
    print("=" * 80)
    print(f"Всего будет создано кампаний: {len(campaign_names)}")
    print("=" * 80)
    
    # Запрашиваем подтверждение
    confirmation = input("\nСоздать кампании с этими неймингами? (yes/no): ").strip().lower()
    
    if confirmation != 'yes':
        print("Создание кампаний отменено.")
        return
    
    # Создаем кампании через API
    print("\nСоздание кампаний через API...")
    
    for i, camp_data in enumerate(campaign_names, 1):
        print(f"\n[{i}/{len(campaign_names)}] Создание кампании для тира {camp_data['tier']}...")
        
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
                'targeting_countries': camp_data['countries'],
                'age_min': age_min,
                'age_max': age_max,
                'genders': genders,
                'user_os': 'android',
                'locales': []  # Пустой массив для всех языков
            }
            
            # Создаем кампанию
            campaign_id = create_campaign_via_api(
                camp_data['account_id'],
                camp_data['name'],
                objective_api,
                api_config
            )
            print(f"  ✓ Кампания создана: {campaign_id}")
            
            # Создаем адсет (используем targeting_spec для совместимости)
            adset_id = create_adset_via_api(
                camp_data['account_id'],
                campaign_id,
                camp_data['name'],
                api_params,
                api_config,
                use_targeting_spec=True
            )
            print(f"  ✓ Адсет создан: {adset_id}")
            
            # Логируем
            log_campaign_creation(
                campaign_name=camp_data['name'],
                campaign_id=campaign_id,
                adset_id=adset_id
            )
            print(f"  ✓ Запись добавлена в logs.csv")
            
        except Exception as e:
            print(f"  ✗ Ошибка при создании кампании или адсета: {e}")
    
    print("\n" + "=" * 80)
    print("ГОТОВО!")
    print("=" * 80)


if __name__ == "__main__":
    main()

