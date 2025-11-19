# Facebook Campaign Builder for Cursor

Этот проект позволяет автоматически создавать рекламные кампании и адсеты для Meta Ads через Facebook Marketing API или генерацию CSV файлов для ручной загрузки.

## Что умеет система

- ✅ **Автоматическое создание кампаний через Facebook Marketing API**
- ✅ Создание нейминга кампании по стандартам UA
- ✅ Сбор параметров таргетинга (tier, страны, исключения, возраст, гендер, язык)
- ✅ Выбор модели оптимизации и событий
- ✅ Формирование настроек кампании (CBO/noCBO, бюджет, стратегия ставки)
- ✅ Автоматическое логирование всех созданных кампаний
- ✅ Генерация CSV файлов (fallback при ошибках API)
- ✅ Поддержка команд на изменение параметров ("поменяй гео на Канаду", "измени ставку", "сделай гендер Women")

## Основная логика

### Workflow

1. **Генерация нейминга** — по правилам из `instructions/naming.md`
2. **Подтверждение пользователя** — показывается нейминг, ожидается подтверждение
3. **Создание через API** (по умолчанию):
   - Создание Campaign через Facebook Marketing API
   - Создание Ad Set через Facebook Marketing API
   - Автоматическое логирование в `logs.csv`
4. **Fallback при ошибках**:
   - Создание CSV файла для ручной загрузки
   - Запись в `logs.csv` не добавляется

### Структура проекта

Cursor использует:
- **Инструкции** в папке `/instructions`:
  - `naming.md` — правила нейминга кампаний
  - `campaign_settings.md` — настройки кампании и адсета
  - `targeting.md` — правила таргетинга
  - `csv_structure.md` — структура CSV и workflow
  - `api_integration.md` — интеграция с Facebook Marketing API
  - `modification_rules.md` — правила изменения параметров

- **Словари** в `/dictionares`:
  - `projects.json` — проекты с настройками (account_ids, application_id, etc.)
  - `objectives.json` — маппинг целей кампаний для API
  - `optimization_goals.json` — маппинг моделей оптимизации
  - `bid_strategies.json` — маппинг стратегий ставок
  - `event_types.json` — маппинг событий на типы для API
  - `events.json` — доступные события
  - `languages.json` — языки для нейминга
  - `locales.json` — маппинг языков на Facebook locale IDs
  - `countries.json` — коды стран
  - `os.json` — операционные системы
  - `api_config.json` — конфигурация API (access_token, api_version)

- **Примеры** в `/examples`:
  - `sample_campaign_output.csv.csv` — шаблон полного экспорта Meta Ads
  - `sample_csv_structure.csv` — упрощенная структура CSV
  - `sample_campaign_request.txt` — пример запроса

- **Утилиты** в `/utils`:
  - `logging.py` — функция автоматического логирования

## Как пользоваться

### Универсальный скрипт (рекомендуется)

Используйте `create_campaign_universal.py` для создания кампаний через командную строку:

```bash
# Создать одну кампанию для конкретного тира
python create_campaign_universal.py \
  --project DuoChat \
  --tier Latam \
  --gender M \
  --age 18-65+ \
  --budget 50 \
  --bid 0.30 \
  --event "4 сессии"

# Создать кампании для всех тиров
python create_campaign_universal.py \
  --project DuoChat \
  --all-tiers \
  --gender M \
  --age 18-65+ \
  --budget 50 \
  --bid 0.30 \
  --event "4 сессии"

# Создать WW кампанию для любого проекта
python create_campaign_universal.py \
  --project Likerro \
  --tier WW \
  --gender MF \
  --age 21-65+ \
  --budget 25 \
  --opt-model tROAS \
  --bid-strategy "Lower cost" \
  --language "Английский"
```

**Все параметры:**
- `--project` - название проекта (обязательно)
- `--os` - операционная система (AND/IOS, по умолчанию AND)
- `--gender` - гендер (M/F/MF, обязательно)
- `--age` - возраст (обязательно, например: 18-65+, 21-65)
- `--budget` - дневной бюджет (обязательно)
- `--tier` или `--all-tiers` - тир или все тиры (обязательно)
- `--opt-model` - модель оптимизации (CPA/CPI/tROAS, по умолчанию CPA)
- `--event` - событие для CPA (опционально)
- `--bid-strategy` - стратегия ставки (по умолчанию "Bid cap")
- `--bid` - значение ставки (обязательно для Bid cap и Cost per result goal)
- `--language` - язык (опционально)
- `--campaign-type` - тип кампании (CBO/noCBO, по умолчанию noCBO)
- `--autor` - автор (по умолчанию KH)
- `--account` - название аккаунта (опционально, используется первый по умолчанию)

### Использование через Cursor (для интерактивного режима)

### Базовый запрос

```
Создай кампанию для проекта Likerro, Android, страны US и Австралия, 
гендер: женщины, возраст: 24-65+, на CPA, событие: четыре сессии, 
английский язык, ставка Bid Cap 5.5 и бюджет 200. Не CBO
```

### Что происходит

1. Cursor генерирует нейминг по правилам
2. Показывает нейминг для подтверждения
3. После подтверждения:
   - Создает Campaign через API
   - Создает Ad Set через API
   - Добавляет запись в `logs.csv`

### Примеры запросов

**Создание кампании:**
```
Создай кампанию: Likerro, Android, Tier-1, US, Men, 21-65+, 
CPA, 40 реклам, English, Bid cap, 5.2, бюджет 250, noCBO
```

**Изменение параметров:**
```
Поменяй гео на Канаду
Измени ставку на 6.0
Сделай гендер Women
Измени возраст на 25-65+
```

## Настройка

### 1. Конфигурация API

Создайте файл `dictionares/api_config.json` на основе `dictionares/api_config.json.example`:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "api_version": "v23.0",
  "base_url": "https://graph.facebook.com"
}
```

**Важно:** `api_config.json` не включен в репозиторий по соображениям безопасности. Скопируйте `api_config.json.example` и заполните своими данными.

### 2. Настройка проектов

Отредактируйте `dictionares/projects.json`:
```json
{
  "Likerro": {
    "alias": "LK",
    "account_ids": ["act_123456789"],
    "campaign_objective": "App promotion",
    "application_id": "x:627096341193498",
    "object_store_url": "http://play.google.com/store/apps/details?id=...",
    ...
  }
}
```

## Структура файлов

```
FacebookCampaignGenerator/
├── create_campaign_universal.py  # Универсальный скрипт для создания кампаний (рекомендуется)
├── create_campaign.py            # Создание кампаний для всех тиров (legacy)
├── create_single_campaign.py      # Создание одной кампании (legacy)
├── create_pheromance_ww.py        # Создание WW кампании (legacy)
├── dictionares/          # Словари и конфигурация
│   ├── projects.json     # Настройки проектов
│   ├── api_config.json   # Конфигурация API
│   ├── objectives.json   # Маппинг целей
│   ├── optimization_goals.json
│   ├── bid_strategies.json
│   ├── event_types.json
│   ├── events.json
│   ├── languages.json
│   ├── locales.json
│   └── ...
├── instructions/         # Инструкции для Cursor
│   ├── naming.md
│   ├── campaign_settings.md
│   ├── targeting.md
│   ├── csv_structure.md
│   ├── api_integration.md
│   └── modification_rules.md
├── examples/            # Примеры и шаблоны
├── launches/            # CSV файлы (fallback при ошибках)
├── utils/               # Утилиты
│   ├── naming.py        # Генерация нейминга
│   ├── campaign_builder.py  # API запросы
│   ├── config_loader.py     # Загрузка конфигураций с кэшированием
│   ├── csv_generator.py     # Генерация CSV fallback
│   ├── tier_utils.py        # Работа с тирами
│   └── logging.py          # Автоматическое логирование
└── logs.csv            # Лог всех созданных кампаний
```

## Логирование

Все созданные кампании автоматически логируются в `logs.csv`:

| Поле | Описание |
|------|----------|
| `campaign_name` | Название кампании (нейминг) |
| `campaign_id` | ID созданной кампании (из API) |
| `adset_id` | ID созданного адсета (из API) |
| `created_at` | Дата и время создания |

**Важно:** Запись добавляется только после успешного создания Campaign и Ad Set через API.

## Обработка ошибок

При ошибках API:
- Показывается сообщение об ошибке
- Создается CSV файл `launches/[campaign_name].csv` для ручной загрузки
- Запись в `logs.csv` не добавляется

## Дополнительная информация

- Подробности работы с API: см. `instructions/api_integration.md`
- Правила нейминга: см. `instructions/naming.md`
- Структура CSV: см. `instructions/csv_structure.md`
- Примеры запросов: см. `/examples`
