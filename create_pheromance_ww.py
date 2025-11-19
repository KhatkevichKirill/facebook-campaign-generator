#!/usr/bin/env python3
"""
Скрипт для создания кампании Pheromance с таргетингом на весь мир
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


def get_all_worldwide_countries(tiers_data):
    """Собирает все страны из всех тиров для таргетинга на весь мир"""
    all_countries = []
    for tier_name, countries in tiers_data.items():
        all_countries.extend(countries)
    # Убираем дубликаты и сортируем
    return sorted(list(set(all_countries)))


def main():
    """Основная функция"""
    # Параметры кампании
    project_name = "Pheromance"
    os_name = "AND"  # По умолчанию Android
    tier_name = "WW"  # Весь мир
    gender = "MF"  # По умолчанию Both (не указан)
    age = "21-65+"  # Для dating приложений минимальный возраст 21+
    language_name = "Фрунцузский"  # Французский
    opt_model = "tROAS"
    daily_budget = 25.0
    bid_strategy = "Lower cost"
    
    # Загружаем справочники
    projects = load_json('dictionares/projects.json')
    accounts = load_json('dictionares/accounts.json')
    languages = load_json('dictionares/languages.json')
    locales_data = load_json('dictionares/locales.json')
    objectives = load_json('dictionares/objectives.json')
    optimization_goals = load_json('dictionares/optimization_goals.json')
    bid_strategies = load_json('dictionares/bid_strategies.json')
    api_config = load_json('dictionares/api_config.json')
    tiers_data = load_tiers()
    
    # Получаем данные проекта
    project = projects[project_name]
    project_alias = project['alias']
    
    # Получаем язык
    lang_code = languages[language_name]  # FR
    
    # Определяем параметры
    campaign_type = "noCBO"  # По умолчанию
    bid_strategy_short = "lc"  # Lower cost
    autor = "KH"  # По умолчанию
    
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
    
    # Тир - весь мир
    tier = "WW"
    countries = get_all_worldwide_countries(tiers_data)
    
    # Исключаем ограниченные и неверные коды стран
    restricted_countries = [
        "CU",  # Куба ограничена Facebook
        "IR",  # Иран ограничен Facebook
        "RU",  # Россия ограничена Facebook
        "SD",  # Судан ограничен Facebook
        "UK",  # Неверный код (должен быть GB)
        "IC",  # Неверный код
        "JB"   # Неверный код
    ]
    countries = [c for c in countries if c not in restricted_countries]
    
    # Выбираем аккаунт
    account_name = project['account_names'][0]  # PM1
    account_id = accounts[account_name]
    
    # API маппинги
    objective_api = objectives[project['campaign_objective']]
    optimization_goal_api = optimization_goals[opt_model]
    bid_strategy_api = bid_strategies[bid_strategy]
    
    # Application ID без префикса "x:"
    application_id = project['application_id'].replace('x:', '')
    
    # Locales для таргетинга
    locales = get_locale_ids(lang_code, locales_data)
    # Временно не используем locales из-за проблем с API
    locales = []  # Таргетинг всех языков (пока не решена проблема с locales)
    
    # Параметры для нейминга
    naming_params = {
        'os': os_name,
        'project_alias': project_alias,
        'tier': tier,
        'naming_countries': [],  # Для WW не перечисляем все страны в нейминге
        'gender': gender,
        'age': age,
        'opt_model': opt_model,
        'event': None,  # Для tROAS нет события
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
    print(f"Таргетинг: Весь мир (WW) - {len(countries)} стран")
    print(f"Гендер: {gender}")
    print(f"Оптимизация: {opt_model}")
    print(f"Бюджет: ${daily_budget}")
    print(f"Стратегия ставки: {bid_strategy} (Lower cost)")
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
            'bid_amount': None,  # Для Lower cost не нужен bid amount
            'custom_event_type': None,  # Для tROAS не нужны события
            'custom_event_str': None,
            'object_store_url': project['object_store_url'],
            'application_id': application_id,
            'targeting_countries': countries,
            'age_min': age_min,
            'age_max': age_max,
            'genders': genders,
            'user_os': 'android',
            'locales': locales,
            'regional_regulated_categories': ["TAIWAN_UNIVERSAL", "SINGAPORE_UNIVERSAL"]  # Для таргетинга на Тайвань и Сингапур
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

