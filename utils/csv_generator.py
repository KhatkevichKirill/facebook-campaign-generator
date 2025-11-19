"""
Utility function for generating CSV fallback files when API fails
"""
import csv
import os
import json
from typing import Dict, List, Optional


# Маппинг locale IDs на названия для CSV
LOCALE_NAMES = {
    6003: "English (US)",
    6004: "English (UK)",
    6005: "Spanish",
    6006: "Portuguese",
    6007: "French",
    6008: "German"
}

# Маппинг стратегий ставок для CSV
BID_STRATEGY_CSV = {
    "LOWEST_COST_WITH_BID_CAP": "Bid cap",
    "COST_CAP": "Cost per result goal",
    "LOWEST_COST_WITHOUT_BID_CAP": "Lower cost",
    "COST_PER_IMPRESSION": "Ad impression"
}

# Маппинг целей оптимизации для CSV
OPTIMIZATION_GOAL_CSV = {
    "OFFSITE_CONVERSIONS": "OFFSITE_CONVERSIONS",
    "APP_INSTALLS": "APP_INSTALLS",
    "VALUE": "VALUE"  # Для tROAS используется VALUE, не VALUE_OPTIMIZATION
}


def get_locale_names_for_csv(locale_ids: List[int]) -> str:
    """
    Преобразует список locale IDs в строку для CSV поля Locales
    
    Args:
        locale_ids: список locale IDs (например, [6003, 6004])
    
    Returns:
        Строка вида "English (US), English (UK)" или пустая строка
    """
    if not locale_ids:
        return ""
    
    names = [LOCALE_NAMES.get(locale_id, f"Locale {locale_id}") for locale_id in locale_ids]
    return ", ".join(names)


def get_beneficiary_payer(project: Dict, countries: List[str], field: str) -> str:
    """
    Определяет Beneficiary или Payer на основе географии
    
    Args:
        project: данные проекта из projects.json
        countries: список стран таргетинга
        field: "beneficiary" или "payer"
    
    Returns:
        Значение beneficiary или payer
    """
    project_field = project.get(field, {})
    
    # Проверяем региональные варианты
    if "AU" in countries and project_field.get("australia"):
        return project_field["australia"]
    if "TW" in countries and project_field.get("taiwan"):
        return project_field["taiwan"]
    if "SG" in countries and project_field.get("singapore"):
        return project_field["singapore"]
    
    # Используем default
    return project_field.get("default", "")


def get_regional_regulated_categories(countries: List[str]) -> str:
    """
    Определяет Regional Regulated Categories на основе географии
    
    Args:
        countries: список стран таргетинга
    
    Returns:
        Строка с категориями через запятую или пустая строка
    """
    categories = []
    if "TW" in countries:
        categories.append("TAIWAN_UNIVERSAL")
    if "SG" in countries:
        categories.append("SINGAPORE_UNIVERSAL")
    
    return ",".join(categories) if categories else ""


def get_device_platforms(user_os: str) -> str:
    """
    Преобразует user_os в Device Platforms для CSV
    
    Args:
        user_os: "android" или "ios"
    
    Returns:
        Строка для поля Device Platforms
    """
    if user_os == "android":
        return "Android_Smartphone, Android_Tablet"
    elif user_os == "ios":
        return "iOS_Phone, iOS_Tablet"
    return ""


def format_custom_event_name(event_code: str) -> str:
    """
    Форматирует код события для CSV поля Custom Event Name
    
    Args:
        event_code: код события (например, "ad_displayed_40")
    
    Returns:
        Отформатированное имя события (например, "40_ads_view")
    """
    # Маппинг событий на формат CSV
    event_mapping = {
        "ad_displayed_20": "20_ads_view",
        "ad_displayed_40": "40_ads_view",
        "ad_displayed_80": "80_ads_view",
        "session_started_3": "3_sessions",
        "session_started_4": "4_sessions",
        "session_started_5": "5_sessions"
    }
    
    return event_mapping.get(event_code, event_code)


def create_csv_fallback(
    campaign_name: str,
    params: Dict,
    project: Dict,
    launches_dir: str = "launches"
) -> str:
    """
    Создает CSV файл для ручной загрузки при ошибке API
    
    Args:
        campaign_name: название кампании (нейминг)
        params: словарь с параметрами кампании:
            - daily_budget: дневной бюджет
            - optimization_goal: цель оптимизации (API формат)
            - bid_strategy: стратегия ставки (API формат)
            - bid_amount: значение ставки (опционально)
            - custom_event_str: код события (для CPA)
            - targeting_countries: список стран
            - age_min: минимальный возраст
            - age_max: максимальный возраст
            - genders: список гендеров [1] или [2] или [1,2]
            - user_os: "android" или "ios"
            - locales: список locale IDs (опционально)
        project: данные проекта из projects.json
        launches_dir: директория для сохранения CSV файлов
    
    Returns:
        Путь к созданному CSV файлу
    """
    # Создаем директорию если не существует
    os.makedirs(launches_dir, exist_ok=True)
    
    # Путь к шаблону
    template_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'examples',
        'sample_campaign_output.csv.csv'
    )
    
    # Читаем шаблон
    with open(template_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        template_row = next(reader) if reader else {}
    
    # Создаем новую строку на основе шаблона
    csv_row = template_row.copy()
    
    # Заполняем основные поля
    csv_row['Campaign Name'] = campaign_name
    csv_row['Ad Set Name'] = campaign_name
    csv_row['Campaign Status'] = 'PAUSED'
    csv_row['Ad Set Run Status'] = 'ACTIVE'
    csv_row['Campaign Objective'] = project.get('campaign_objective', 'App promotion')
    
    # Бюджет (noCBO - на уровне Ad Set)
    daily_budget = params.get('daily_budget', 0)
    csv_row['Ad Set Daily Budget'] = str(int(daily_budget))
    
    # Страны
    countries = params.get('targeting_countries', [])
    csv_row['Countries'] = ','.join(countries)
    
    # Гендер
    genders = params.get('genders', [])
    if genders == [1]:
        csv_row['Gender'] = 'Men'
    elif genders == [2]:
        csv_row['Gender'] = 'Women'
    else:
        csv_row['Gender'] = ''  # Both - пустое поле
    
    # Возраст
    csv_row['Age Min'] = str(params.get('age_min', 18))
    csv_row['Age Max'] = str(params.get('age_max', 65))
    
    # Locales
    locales = params.get('locales', [])
    if locales:
        csv_row['Locales'] = get_locale_names_for_csv(locales)
    else:
        csv_row['Locales'] = ''  # Пустое для всех языков
    
    # Optimization Goal
    optimization_goal = params.get('optimization_goal', '')
    csv_row['Optimization Goal'] = OPTIMIZATION_GOAL_CSV.get(optimization_goal, optimization_goal)
    
    # Billing Event
    csv_row['Billing Event'] = 'IMPRESSIONS'
    
    # Bid Amount
    bid_amount = params.get('bid_amount')
    if bid_amount:
        csv_row['Bid Amount'] = str(bid_amount)
    else:
        csv_row['Bid Amount'] = ''
    
    # Bid Strategy
    bid_strategy = params.get('bid_strategy', '')
    csv_row['Ad Set Bid Strategy'] = BID_STRATEGY_CSV.get(bid_strategy, bid_strategy)
    
    # Link Object ID
    csv_row['Link Object ID'] = project.get('link_object_id', '')
    
    # Custom Event Name (для CPA)
    custom_event_str = params.get('custom_event_str')
    if custom_event_str:
        csv_row['Custom Event Name'] = format_custom_event_name(custom_event_str)
    else:
        csv_row['Custom Event Name'] = ''
    
    # Application ID
    csv_row['Application ID'] = project.get('application_id', '')
    
    # Object Store URL
    csv_row['Object Store URL'] = project.get('object_store_url', '')
    
    # Beneficiary и Payer
    csv_row['Beneficiary'] = get_beneficiary_payer(project, countries, 'beneficiary')
    csv_row['Payer'] = get_beneficiary_payer(project, countries, 'payer')
    
    # Regional Regulated Categories
    csv_row['Regional Regulated Categories'] = get_regional_regulated_categories(countries)
    
    # Региональные поля Beneficiary и Payer
    beneficiary = project.get('beneficiary', {})
    payer = project.get('payer', {})
    csv_row['Beneficiary (financial ads in Australia)'] = beneficiary.get('australia', '')
    csv_row['Payer (financial ads in Australia)'] = payer.get('australia', '')
    csv_row['Beneficiary (financial ads in Taiwan)'] = beneficiary.get('taiwan', '')
    csv_row['Payer (financial ads in Taiwan)'] = payer.get('taiwan', '')
    csv_row['Beneficiary (Taiwan)'] = beneficiary.get('taiwan', '')
    csv_row['Payer (Taiwan)'] = payer.get('taiwan', '')
    csv_row['Beneficiary (Singapore)'] = beneficiary.get('singapore', '')
    csv_row['Payer (Singapore)'] = payer.get('singapore', '')
    
    # User Operating System
    user_os = params.get('user_os', 'android')
    if user_os == 'android':
        csv_row['User Operating System'] = 'Android'
    elif user_os == 'ios':
        csv_row['User Operating System'] = 'iOS'
    
    # Device Platforms
    csv_row['Device Platforms'] = get_device_platforms(user_os)
    
    # Destination Type
    csv_row['Destination Type'] = 'APP'
    
    # Advantage Audience
    csv_row['Advantage Audience'] = 'Yes'
    
    # Location Types
    csv_row['Location Types'] = 'home, recent'
    
    # Brand Safety Inventory Filtering Levels
    csv_row['Brand Safety Inventory Filtering Levels'] = 'FACEBOOK_RELAXED, AN_RELAXED'
    
    # Attribution Spec (для CPA)
    if optimization_goal == 'OFFSITE_CONVERSIONS':
        csv_row['Attribution Spec'] = '[{"event_type":"CLICK_THROUGH","window_days":7}]'
    else:
        csv_row['Attribution Spec'] = ''
    
    # Сохраняем CSV файл
    csv_filename = f"{campaign_name}.csv"
    csv_path = os.path.join(launches_dir, csv_filename)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(csv_row)
    
    return csv_path

