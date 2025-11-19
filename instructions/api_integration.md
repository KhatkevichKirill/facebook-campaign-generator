# Facebook Marketing API Integration

## Overview

Интеграция с Facebook Marketing API для создания кампаний и адсетов через POST запросы.

## API Configuration

Конфигурация API хранится в `dictionares/api_config.json`:
- `access_token` — токен доступа к API (заполняется пользователем)
- `api_version` — версия API (по умолчанию "v23.0")
- `base_url` — базовый URL API

**Важно:** Токен доступа должен быть заполнен перед использованием API.

## API Endpoints

### Base URL
```
https://graph.facebook.com/v23.0/
```

### Campaign Creation
```
POST /{account_id}/campaigns
```

### Ad Set Creation
```
POST /{account_id}/adsets
```

## Campaign Creation Request

### Required Fields:
- `account_id` — ID рекламного аккаунта (получается из `accounts.json` по выбранному названию из `project.account_names`)
- `name` — название кампании (сгенерированный нейминг)
- `objective` — цель кампании (из `objectives.json`, маппинг `project.campaign_objective`)
- `status` — статус кампании (по умолчанию "PAUSED" или "ACTIVE")
- `special_ad_categories` — специальные категории (по умолчанию `["NONE"]`)

### Example Request:
```json
{
  "account_id": "act_123456789",
  "name": "AND_LK_Tier-1(US)_M_21-65_CPA[ad_displayed_40]_16112025_KH_noCBO_bc_ENG_LK1",
  "objective": "APP_PROMOTION",
  "status": "PAUSED",
  "special_ad_categories": ["NONE"]
}
```

### Response:
Возвращает `campaign_id`, который используется для создания Ad Set.

## Ad Set Creation Request

### Required Fields:
- `account_id` — ID рекламного аккаунта (получается из `accounts.json` по выбранному названию из `project.account_names`)
- `name` — название адсета (сгенерированный нейминг, тот же что и у кампании)
- `campaign_id` — ID созданной кампании (получается из ответа создания кампании)
- `daily_budget` — дневной бюджет (из параметров кампании)
- `billing_event` — событие биллинга (всегда `"IMPRESSIONS"`)
- `optimization_goal` — цель оптимизации (из `optimization_goals.json`, маппинг модели оптимизации)
- `bid_strategy` — стратегия ставки (из `bid_strategies.json`)
- `bid_amount` — значение ставки (только если `bid_strategy` = `"BID_CAP"`)
- `promoted_object` — объект продвижения:
  - `custom_event_type` — тип события (из `event_types.json`, маппинг из `events.json`)
  - `custom_event_str` — конкретное имя события (из `events.json`, например "session_started_3")
  - `object_store_url` — URL приложения в магазине (из `projects.json`)
  - `application_id` — ID приложения (из `projects.json`, без префикса "x:")

### Targeting Fields:
- `targeting` — объект таргетинга:
  - `geo_locations` — география:
    - `countries` — массив ISO-кодов стран:
      - Если таргетинг на весь тир → все страны тира из `tiers.json`
      - Если указаны конкретные страны → массив указанных стран
      - Если более 5 стран из разных тиров → все указанные страны (в нейминге используется WW)
    - `excluded_countries` — исключенные страны (если есть)
  - `age_min` — минимальный возраст
  - `age_max` — максимальный возраст (65+ → 65)
  - `genders` — массив гендеров: `[1]` для Men, `[2]` для Women, `[1, 2]` для Both
  - `locales` — массив языков (если язык указан, иначе пустой массив для всех языков)
  - `user_os` — массив операционных систем: `["android"]` для Android, `["ios"]` для iOS
  - `targeting_automation` — объект автоматизации таргетинга:
    - `advantage_audience` — флаг Advantage audience (1 или 0, обязательное поле)

### Example Request:
```json
{
  "account_id": "act_123456789",
  "name": "AND_LK_Tier-1(US)_M_21-65_CPA[ad_displayed_40]_16112025_KH_noCBO_bc_ENG_LK1",
  "campaign_id": "123456789012345",
  "daily_budget": 25000,
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
  "bid_amount": 520,
  "promoted_object": {
    "custom_event_type": "OTHER",
    "custom_event_str": "ad_displayed_40",
    "object_store_url": "http://play.google.com/store/apps/details?id=com.panda.likerro",
    "application_id": "627096341193498"
  },
  "targeting": {
    "geo_locations": {
      "countries": ["US"]
    },
    "age_min": 21,
    "age_max": 65,
    "genders": [1],
    "user_os": ["android"],
    "targeting_automation": {
      "advantage_audience": 1
    }
  }
}
```

## Data Mapping

### Objectives
Маппинг из `campaign_objective` в `objectives.json`:
- "App promotion" → "APP_PROMOTION"

### Optimization Goals
Маппинг из модели оптимизации в `optimization_goals.json`:
- "CPA" → "OFFSITE_CONVERSIONS"
- "CPI" → "APP_INSTALLS"
- "tROAS" → "VALUE_OPTIMIZATION"

### Bid Strategies
Маппинг из стратегии ставки в `bid_strategies.json`:
- "Bid cap" → "BID_CAP" (требует `bid_amount`)
- "Cost per result goal" → "COST_CAP"
- "Lower cost" → "LOWEST_COST_WITHOUT_BID_CAP"
- "Ad impression" → "COST_PER_IMPRESSION"

### Events (for CPA)
События из `events.json` маппятся на типы через `event_types.json`:
- "ad_displayed_20" → тип "OTHER" (кастомное событие)
- "ad_displayed_40" → тип "OTHER" (кастомное событие)
- "session_started_3/4/5" → тип "OTHER" (кастомное событие)

**Важно:** 
- `ad_displayed_20` и `ad_displayed_40` — это кастомные события (OTHER), не AD_IMPRESSION
- AD_IMPRESSION используется **только** для tROAS/ROAS кампаний, где на основе этих событий используется Value

### Gender Mapping
- "Men" → `[1]`
- "Women" → `[2]`
- "Both" → `[1, 2]`

### Language Mapping
Языки из `languages.json` маппятся на Facebook locale IDs:
- "EN" → `[6003, 6004]` (English US, English UK)
- "ES" → `[6005]` (Spanish)
- И т.д.

Если язык не указан, `locales` остается пустым массивом `[]` (таргетинг всех языков).

## Workflow

**API является основным методом создания кампаний. CSV файл создается только в случае ошибки API для ручной загрузки.**

1. Генерируется нейминг кампании
2. Показывается нейминг пользователю для подтверждения
3. После подтверждения:
   - **Выбор аккаунта**: Если у проекта несколько `account_names`, показывается список названий для выбора
   - **Маппинг аккаунта**: Выбранное название маппится на `account_id` через словарь `accounts.json`
   - **Создается Campaign через API** (используется `account_id`, получается `campaign_id`)
   - **Создается Ad Set через API** (используется `account_id` и `campaign_id`, получается `adset_id`)
   - **Автоматически добавляется запись в `logs.csv`** с полями:
     - `campaign_name` — сгенерированный нейминг
     - `campaign_id` — ID созданной кампании
     - `adset_id` — ID созданного адсета
     - `created_at` — дата и время создания

### Fallback при ошибках API

Если при создании Campaign или Ad Set через API произошла ошибка:
- **Создается CSV файл** `launches/[campaign_name].csv` для ручной загрузки
- Запись в `logs.csv` **НЕ добавляется** (так как кампания не была создана)
- Пользователь может загрузить CSV файл вручную через Facebook Ads Manager

**Важно:** 
- **По умолчанию используется API.** CSV создается только как fallback при ошибках.
- Запись в `logs.csv` добавляется автоматически только после успешного создания Campaign и Ad Set.
- При ошибках API запись в `logs.csv` не добавляется, но создается CSV файл для ручной загрузки.

## Automatic Logging

После успешного создания Campaign и Ad Set автоматически добавляется запись в `logs.csv`:

```python
from utils.logging import log_campaign_creation

# После успешного создания Campaign и Ad Set:
log_campaign_creation(
    campaign_name="AND_LK_Tier-1(AU,CA)_M_24-65+_CPA[session_started_3]_17112025_KH_noCBO_bc_ENG",
    campaign_id="120234676409240622",
    adset_id="120234677752700622"
)
```

Или вручную через CSV:

```python
import csv
from datetime import datetime

# Добавление записи в logs.csv
with open('logs.csv', 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        campaign_name,
        campaign_id,
        adset_id,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])
```

## Error Handling

При ошибках API:
- Показывать пользователю сообщение об ошибке
- **Создается CSV файл** `launches/[campaign_name].csv` для ручной загрузки
- Запись в `logs.csv` **НЕ добавляется** (так как кампания не была создана через API)
- Пользователь может загрузить CSV файл вручную через Facebook Ads Manager

