"""
Utility function for logging campaign creation to logs.csv
"""
import csv
import os
from datetime import datetime


def log_campaign_creation(campaign_name, campaign_id=None, adset_id=None, logs_file='logs.csv'):
    """
    Добавляет запись о создании кампании в logs.csv
    
    Args:
        campaign_name: Название кампании (нейминг)
        campaign_id: ID созданной кампании (из Facebook API)
        adset_id: ID созданного адсета (из Facebook API)
        logs_file: Путь к файлу логов (по умолчанию 'logs.csv')
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Проверяем, существует ли файл
    file_exists = os.path.exists(logs_file)
    
    # Читаем существующие записи
    rows = []
    if file_exists:
        try:
            with open(logs_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
        except Exception as e:
            print(f"Warning: Could not read existing logs: {e}")
            rows = []
    
    # Проверяем заголовок
    if not rows or rows[0] != ['campaign_name', 'campaign_id', 'adset_id', 'created_at']:
        rows = [['campaign_name', 'campaign_id', 'adset_id', 'created_at']]
    
    # Добавляем новую запись
    new_row = [
        campaign_name,
        campaign_id or '',
        adset_id or '',
        created_at
    ]
    rows.append(new_row)
    
    # Записываем обратно
    try:
        with open(logs_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        return True
    except Exception as e:
        print(f"Error writing to logs file: {e}")
        return False

