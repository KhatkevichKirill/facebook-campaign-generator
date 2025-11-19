#!/usr/bin/env python3
"""
Универсальный скрипт для создания кампаний Facebook через API
Поддерживает создание одной кампании или для всех тиров
"""
import argparse
import os
import sys
from datetime import datetime
from utils.tier_utils import (
    load_tiers, 
    get_all_countries_for_tier, 
    format_tier_for_naming,
    get_all_worldwide_countries
)
from utils.logging import log_campaign_creation
from utils.csv_generator import create_csv_fallback
from utils.naming import generate_campaign_name
from utils.campaign_builder import create_campaign_via_api, create_adset_via_api
from utils.config_loader import load_json


def get_locale_ids(lang_code, locales_data):
    """Маппинг языковых кодов на Facebook locale IDs"""
    return locales_data.get(lang_code, [])


def get_restricted_countries():
    """Возвращает список ограниченных стран Facebook"""
    return ["CU", "IR", "RU", "SD", "UK", "IC", "JB"]


def parse_arguments():
    """Парсит аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description='Создание кампаний Facebook через API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Создать одну кампанию для конкретного тира
  python create_campaign_universal.py --project DuoChat --tier Latam --gender M --age 18-65+ --budget 50 --bid 0.30
  
  # Создать кампании для всех тиров
  python create_campaign_universal.py --project DuoChat --all-tiers --gender M --age 18-65+ --budget 50 --bid 0.30
  
  # Создать WW кампанию для любого проекта
  python create_campaign_universal.py --project Likerro --tier WW --gender MF --age 21-65+ --budget 25 --opt-model tROAS --bid-strategy "Lower cost"
        """
    )
    
    # Обязательные параметры
    parser.add_argument('--project', required=True, help='Название проекта (DuoChat, Likerro, Pheromance)')
    parser.add_argument('--os', choices=['AND', 'IOS'], default='AND', help='Операционная система')
    parser.add_argument('--gender', choices=['M', 'F', 'MF'], required=True, help='Гендер')
    parser.add_argument('--age', required=True, help='Возраст (например, 18-65+, 21-65)')
    parser.add_argument('--budget', type=float, required=True, help='Дневной бюджет')
    
    # Тир (либо конкретный, либо --all-tiers)
    tier_group = parser.add_mutually_exclusive_group(required=True)
    tier_group.add_argument('--tier', help='Конкретный тир (Tier-1, Latam, WW, etc.)')
    tier_group.add_argument('--all-tiers', action='store_true', help='Создать кампании для всех тиров')
    
    # Оптимизация
    parser.add_argument('--opt-model', choices=['CPA', 'CPI', 'tROAS'], default='CPA', help='Модель оптимизации')
    parser.add_argument('--event', help='Событие (только для CPA, например: "4 сессии", "40 реклам")')
    
    # Стратегия ставки
    parser.add_argument('--bid-strategy', choices=['Bid cap', 'Cost per result goal', 'Lower cost', 'Ad impression'], 
                       default='Bid cap', help='Стратегия ставки')
    parser.add_argument('--bid', type=float, help='Значение ставки (обязательно для Bid cap и Cost per result goal)')
    
    # Дополнительные параметры
    parser.add_argument('--language', help='Язык (например: "Английский", "Испанский")')
    parser.add_argument('--campaign-type', choices=['CBO', 'noCBO'], default='noCBO', help='Тип кампании')
    parser.add_argument('--autor', default='KH', help='Автор кампании')
    parser.add_argument('--account', help='Название аккаунта (если не указано, используется первый из списка)')
    
    return parser.parse_args()


def create_single_campaign_data(
    project,
    accounts,
    tier_name,
    params,
    tiers_data
):
    """Создает данные для одной кампании"""
    # Определяем тир и страны
    if tier_name == "WW":
        tier_raw = "WW"
        tier = "WW"
        countries = get_all_worldwide_countries(tiers_data)
        # Исключаем ограниченные страны
        restricted = get_restricted_countries()
        countries = [c for c in countries if c not in restricted]
        naming_countries = []  # Для WW не перечисляем страны в нейминге
    else:
        tier_mapping = {
            "Tier-1": "Tier1",
            "Latam": "LatAm",
            "latam": "LatAm",
            "LatAm": "LatAm"
        }
        tier_raw = tier_mapping.get(tier_name, tier_name)
        tier = format_tier_for_naming(tier_raw)
        countries = get_all_countries_for_tier(tier_raw)
        # Исключаем ограниченные страны
        restricted = get_restricted_countries()
        countries = [c for c in countries if c not in restricted]
        naming_countries = []  # Для всего тира не перечисляем страны
    
    # Выбираем аккаунт
    if params.get('account_name'):
        account_name = params['account_name']
    else:
        account_name = project['account_names'][0]
    account_id = accounts[account_name]
    
    # Генерируем нейминг
    naming_params = {
        'os': params['os'],
        'project_alias': project['alias'],
        'tier': tier,
        'naming_countries': naming_countries,
        'gender': params['gender'],
        'age': params['age'],
        'opt_model': params['opt_model'],
        'event': params.get('event_code'),
        'date': params['date'],
        'autor': params['autor'],
        'campaign_type': params['campaign_type'],
        'bid_strategy_short': params['bid_strategy_short'],
        'lang': params['lang'],
        'extra': account_name
    }
    
    campaign_name = generate_campaign_name(naming_params)
    
    return {
        'name': campaign_name,
        'tier': tier,
        'tier_raw': tier_raw,
        'countries': countries,
        'account_id': account_id,
        'account_name': account_name
    }


def main():
    """Основная функция"""
    args = parse_arguments()
    
    # Загружаем справочники
    projects = load_json('dictionares/projects.json')
    accounts = load_json('dictionares/accounts.json')
    objectives = load_json('dictionares/objectives.json')
    optimization_goals = load_json('dictionares/optimization_goals.json')
    bid_strategies = load_json('dictionares/bid_strategies.json')
    api_config = load_json('dictionares/api_config.json')
    tiers_data = load_tiers()
    
    # Загружаем опциональные справочники
    events = {}
    event_types = {}
    if args.event:
        events = load_json('dictionares/events.json')
        event_types = load_json('dictionares/event_types.json')
    
    languages = {}
    locales_data = {}
    if args.language:
        languages = load_json('dictionares/languages.json')
        locales_data = load_json('dictionares/locales.json')
    
    # Получаем данные проекта
    if args.project not in projects:
        print(f"Ошибка: Проект '{args.project}' не найден в projects.json")
        sys.exit(1)
    
    project = projects[args.project]
    project_alias = project['alias']
    
    # Получаем событие (если указано)
    event_code = None
    if args.event:
        if args.event not in events:
            print(f"Ошибка: Событие '{args.event}' не найдено в events.json")
            sys.exit(1)
        event_code = events[args.event]
    
    # Получаем язык (если указан)
    lang_code = "ALL"
    locales = []
    if args.language:
        if args.language not in languages:
            print(f"Ошибка: Язык '{args.language}' не найден в languages.json")
            sys.exit(1)
        lang_code = languages[args.language]
        locales = get_locale_ids(lang_code, locales_data)
        # Временно не используем locales из-за проблем с API
        locales = []
    
    # Маппинг стратегий ставок
    bid_strategy_short_map = {
        'Bid cap': 'bc',
        'Cost per result goal': 'cc',
        'Lower cost': 'lc',
        'Ad impression': 'ai'
    }
    bid_strategy_short = bid_strategy_short_map.get(args.bid_strategy, 'bc')
    
    # Проверяем bid для Bid cap и Cost per result goal
    if args.bid_strategy in ['Bid cap', 'Cost per result goal'] and not args.bid:
        print(f"Ошибка: Для стратегии '{args.bid_strategy}' необходимо указать --bid")
        sys.exit(1)
    
    # Дата
    today = datetime.now()
    date_str = today.strftime("%d%m%Y")
    
    # Возраст
    age_parts = args.age.replace('+', '').split('-')
    age_min = int(age_parts[0])
    age_max = int(age_parts[1]) if len(age_parts) > 1 else 65
    
    # Гендер
    genders_map = {"M": [1], "F": [2], "MF": [1, 2]}
    genders = genders_map[args.gender]
    
    # API маппинги
    objective_api = objectives[project['campaign_objective']]
    optimization_goal_api = optimization_goals[args.opt_model]
    bid_strategy_api = bid_strategies[args.bid_strategy]
    
    # Application ID без префикса "x:"
    application_id = project['application_id'].replace('x:', '')
    
    # Custom event type (только для CPA с событиями)
    custom_event_type_api = None
    if args.opt_model == "CPA" and event_code:
        custom_event_type_api = event_types[event_code]
    
    # Параметры для всех кампаний
    base_params = {
        'os': args.os,
        'gender': args.gender,
        'age': args.age,
        'opt_model': args.opt_model,
        'campaign_type': args.campaign_type,
        'bid_strategy_short': bid_strategy_short,
        'lang': lang_code,
        'autor': args.autor,
        'date': date_str,
        'account_name': args.account,
        'event_code': event_code
    }
    
    # Определяем список тиров для обработки
    if args.all_tiers:
        tiers_to_process = list(tiers_data.keys())
    else:
        tiers_to_process = [args.tier]
    
    # Собираем информацию о кампаниях
    campaign_data_list = []
    
    print("=" * 80)
    if args.all_tiers:
        print("ГЕНЕРАЦИЯ КАМПАНИЙ ДЛЯ ВСЕХ ТИРОВ")
    else:
        print("ГЕНЕРАЦИЯ КАМПАНИИ")
    print("=" * 80)
    print(f"Проект: {args.project}")
    print(f"OS: {args.os}")
    print(f"Гендер: {args.gender}")
    if args.event:
        print(f"Событие: {args.event} ({event_code})")
    print(f"Бюджет: ${args.budget}")
    if args.bid:
        print(f"Бид: ${args.bid}")
    print(f"Возраст: {args.age}")
    if args.language:
        print(f"Язык: {args.language} ({lang_code})")
    print()
    
    for tier_name in tiers_to_process:
        camp_data = create_single_campaign_data(
            project,
            accounts,
            tier_name,
            base_params,
            tiers_data
        )
        campaign_data_list.append(camp_data)
        
        print(f"Тир: {camp_data['tier']}")
        print(f"  Страны: {len(camp_data['countries'])} стран")
        print(f"  Нейминг: {camp_data['name']}")
        print()
    
    print("=" * 80)
    print(f"Всего будет создано кампаний: {len(campaign_data_list)}")
    print("=" * 80)
    
    # Запрашиваем подтверждение
    confirmation = input("\nСоздать кампании с этими неймингами? (yes/no): ").strip().lower()
    
    if confirmation != 'yes':
        print("Создание кампаний отменено.")
        return
    
    # Создаем кампании через API
    print("\nСоздание кампаний через API...")
    
    for i, camp_data in enumerate(campaign_data_list, 1):
        print(f"\n[{i}/{len(campaign_data_list)}] Создание кампании для тира {camp_data['tier']}...")
        
        try:
            # Параметры для API
            api_params = {
                'daily_budget': args.budget,
                'optimization_goal': optimization_goal_api,
                'bid_strategy': bid_strategy_api,
                'bid_amount': args.bid,
                'custom_event_type': custom_event_type_api,
                'custom_event_str': event_code,
                'object_store_url': project['object_store_url'],
                'application_id': application_id,
                'targeting_countries': camp_data['countries'],
                'age_min': age_min,
                'age_max': age_max,
                'genders': genders,
                'user_os': 'android' if args.os == 'AND' else 'ios',
                'locales': locales
            }
            
            # Regional regulated categories для WW или если есть TW/SG в странах
            if camp_data['tier'] == "WW" or "TW" in camp_data['countries'] or "SG" in camp_data['countries']:
                api_params['regional_regulated_categories'] = ["TAIWAN_UNIVERSAL", "SINGAPORE_UNIVERSAL"]
            
            # Создаем кампанию
            campaign_id = create_campaign_via_api(
                camp_data['account_id'],
                camp_data['name'],
                objective_api,
                api_config
            )
            print(f"  ✓ Кампания создана: {campaign_id}")
            
            # Создаем адсет
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
            print(f"  ✗ Ошибка: {e}")
            print(f"  Создание CSV файла для ручной загрузки...")
            try:
                csv_path = create_csv_fallback(
                    campaign_name=camp_data['name'],
                    params=api_params,
                    project=project
                )
                print(f"  ✓ CSV файл создан: {csv_path}")
            except Exception as csv_error:
                print(f"  ✗ Ошибка при создании CSV: {csv_error}")
    
    print("\n" + "=" * 80)
    print("ГОТОВО!")
    print("=" * 80)


if __name__ == "__main__":
    main()
