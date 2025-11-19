"""
Utility functions for loading configuration files with caching
"""
import json
import os
from functools import lru_cache
from typing import Dict, Any


# Кэш для загруженных JSON файлов
_config_cache: Dict[str, Any] = {}


def load_json(file_path: str, use_cache: bool = True) -> Dict:
    """
    Загружает JSON файл с опциональным кэшированием
    
    Args:
        file_path: путь к JSON файлу (относительный или абсолютный)
        use_cache: использовать кэш (по умолчанию True)
    
    Returns:
        Словарь с данными из JSON файла
    """
    # Нормализуем путь
    if not os.path.isabs(file_path):
        # Относительный путь - делаем относительно корня проекта
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(base_dir, file_path)
    
    # Проверяем кэш
    if use_cache and file_path in _config_cache:
        return _config_cache[file_path]
    
    # Загружаем файл
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Сохраняем в кэш
    if use_cache:
        _config_cache[file_path] = data
    
    return data


def clear_cache():
    """Очищает кэш конфигураций"""
    global _config_cache
    _config_cache.clear()


def get_cached_configs() -> Dict[str, Any]:
    """Возвращает все закэшированные конфигурации"""
    return _config_cache.copy()

