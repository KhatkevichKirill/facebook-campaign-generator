"""
Utility functions for creating campaigns and adsets via Facebook Marketing API
"""
import json
from typing import Dict, List, Optional
import requests


def create_campaign_via_api(account_id: str, campaign_name: str, objective: str, api_config: Dict) -> str:
    """
    Создает кампанию через Facebook Marketing API
    
    Args:
        account_id: ID рекламного аккаунта (без префикса "act_")
        campaign_name: название кампании
        objective: цель кампании (API формат, например "APP_PROMOTION")
        api_config: конфигурация API (base_url, api_version, access_token)
    
    Returns:
        ID созданной кампании
    
    Raises:
        Exception: при ошибке создания кампании
    """
    url = f"{api_config['base_url']}/{api_config['api_version']}/act_{account_id}/campaigns"
    
    params = {
        "access_token": api_config['access_token'],
        "name": campaign_name,
        "objective": objective,
        "status": "PAUSED",
        "special_ad_categories": json.dumps(["NONE"])
    }
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('id')
    else:
        raise Exception(f"Error creating campaign: {response.status_code} - {response.text}")


def create_adset_via_api(
    account_id: str,
    campaign_id: str,
    adset_name: str,
    params: Dict,
    api_config: Dict,
    use_targeting_spec: bool = False
) -> str:
    """
    Создает адсет через Facebook Marketing API
    
    Args:
        account_id: ID рекламного аккаунта (без префикса "act_")
        campaign_id: ID кампании
        adset_name: название адсета
        params: словарь с параметрами адсета:
            - daily_budget: дневной бюджет
            - optimization_goal: цель оптимизации (API формат)
            - bid_strategy: стратегия ставки (API формат)
            - bid_amount: значение ставки (опционально, только для Bid cap)
            - custom_event_type: тип события (API формат)
            - custom_event_str: код события
            - object_store_url: URL приложения в магазине
            - application_id: ID приложения (без префикса "x:")
            - targeting_countries: список стран
            - age_min: минимальный возраст
            - age_max: максимальный возраст
            - genders: список гендеров [1] или [2] или [1,2]
            - user_os: "android" или "ios"
            - locales: список locale IDs (опционально)
            - regional_regulated_categories: список категорий (опционально)
        api_config: конфигурация API
        use_targeting_spec: использовать "targeting_spec" вместо "targeting" (для совместимости)
    
    Returns:
        ID созданного адсета
    
    Raises:
        Exception: при ошибке создания адсета
    """
    url = f"{api_config['base_url']}/{api_config['api_version']}/act_{account_id}/adsets"
    
    # Подготовка данных для запроса
    data = {
        "access_token": api_config['access_token'],
        "name": adset_name,
        "campaign_id": campaign_id,
        "daily_budget": int(params['daily_budget'] * 100),  # В центах
        "billing_event": "IMPRESSIONS",
        "optimization_goal": params['optimization_goal'],
        "bid_strategy": params['bid_strategy'],
        "status": "PAUSED"
    }
    
    # Bid amount только для Bid cap
    if params['bid_strategy'] == "LOWEST_COST_WITH_BID_CAP" and params.get('bid_amount'):
        data["bid_amount"] = int(params['bid_amount'] * 100)  # В центах
    
    # Regional regulated categories (если указаны)
    if params.get('regional_regulated_categories'):
        data["regional_regulated_categories"] = json.dumps(params['regional_regulated_categories'])
    
    # Promoted object
    promoted_object = {}
    
    # Для tROAS используем AD_IMPRESSION
    if params.get('optimization_goal') == "VALUE":
        promoted_object["custom_event_type"] = "AD_IMPRESSION"
    elif params.get('custom_event_type') and params.get('custom_event_str'):
        # Для CPA с событиями
        promoted_object["custom_event_type"] = params['custom_event_type']
        promoted_object["custom_event_str"] = params['custom_event_str']
    
    # Обязательные поля для promoted_object
    promoted_object["object_store_url"] = params['object_store_url']
    promoted_object["application_id"] = params['application_id']
    
    data["promoted_object"] = json.dumps(promoted_object)
    
    # Targeting
    targeting = {
        "geo_locations": {
            "countries": params['targeting_countries']
        },
        "age_min": params['age_min'],
        "age_max": params['age_max'],
        "genders": params['genders'],
        "user_os": [params['user_os']],
        "targeting_automation": {
            "advantage_audience": 1
        }
    }
    
    # Locales только если указан язык и не пустой список
    if params.get('locales') and len(params['locales']) > 0:
        targeting["locales"] = params['locales']
    
    # Используем правильное поле в зависимости от версии API
    targeting_field = "targeting_spec" if use_targeting_spec else "targeting"
    data[targeting_field] = json.dumps(targeting)
    
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        data = response.json()
        return data.get('id')
    else:
        raise Exception(f"Error creating adset: {response.status_code} - {response.text}")
