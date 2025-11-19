# CSV Structure Rules

Cursor должен создавать **только один файл** — полный экспорт Meta Ads в формате `sample_campaign_output.csv`.

## Workflow

**По умолчанию кампания создается через Facebook Marketing API. CSV файл создается только в случае ошибки API для ручной загрузки.**

### Основной Workflow (API Creation):

1. Генерируется нейминг кампании по правилам из `naming.md`
2. **Показывается сгенерированный нейминг пользователю** с запросом подтверждения
3. **Ожидается подтверждение пользователя** (только после подтверждения переходить к шагу 4)
4. **Создание через API** (см. `api_integration.md`):
   - Создается Campaign через Facebook Marketing API (POST запрос)
   - Получается `campaign_id` из ответа
   - Создается Ad Set через Facebook Marketing API с полученным `campaign_id`
   - Получается `adset_id` из ответа
   - **Автоматически добавляется запись в `logs.csv`** с полями:
     - `campaign_name` — сгенерированный нейминг
     - `campaign_id` — ID созданной кампании
     - `adset_id` — ID созданного адсета
     - `created_at` — дата и время создания

### Fallback: CSV File Creation (только при ошибке API)

**CSV файл создается ТОЛЬКО в случае ошибки при создании через API** для возможности ручной загрузки:

1. Если при создании Campaign или Ad Set через API произошла ошибка:
   - Создается файл `launches/[campaign_name].csv` на основе шаблона из `/examples/sample_campaign_output.csv.csv`
   - Нейминг применяется в поля:
     - **Campaign Name** = сгенерированный нейминг
     - **Ad Set Name** = сгенерированный нейминг (тот же)
   - Файл готов для ручной загрузки в Facebook Ads Manager
   - **Запись в `logs.csv` НЕ добавляется** (так как кампания не была создана)

**Важно:** 
- **По умолчанию используется API.** CSV создается только как fallback при ошибках.
- Промежуточные файлы не создаются. Нейминг генерируется по правилам и сразу используется.
- **Кампания/файл создается ТОЛЬКО после подтверждения пользователем.** До подтверждения ничего не создается.
- Подробности работы с API см. в `api_integration.md`

## Структура файла

Файл должен содержать все столбцы из шаблона `/examples/sample_campaign_output.csv.csv` (422 столбца).

Все поля заполняются согласно инструкциям:
- Нейминг → из `naming.md`
- Campaign settings → из `campaign_settings.md`
- Targeting → из `targeting.md`
- Project-specific fields → из `projects.json`

## Language Field (Locales)

Поле **Locales** в финальном CSV заполняется следующим образом:
- **Если язык указан**: заполняется значением из `languages.json` (например, "English (US), English (UK)")
- **Если язык НЕ указан**: поле **Locales остается пустым** (не заполняется), что означает таргетинг всех языков

## Project-Specific Fields in Campaign Output

При создании `launches/[campaign_name].csv` необходимо использовать данные из `projects.json`:

- **Campaign Objective**: `project.campaign_objective`
- **Link Object ID**: `project.link_object_id`
- **Application ID**: `project.application_id`
- **Object Store URL**: `project.object_store_url`
- **Beneficiary**: выбирается в зависимости от географии:
  - Если в странах есть AU → `project.beneficiary.australia` (если не пусто, иначе `default`)
  - Если в странах есть TW → `project.beneficiary.taiwan` (если не пусто, иначе `default`)
  - Если в странах есть SG → `project.beneficiary.singapore` (если не пусто, иначе `default`)
  - Иначе → `project.beneficiary.default`
- **Payer**: аналогично Beneficiary, но из `project.payer`

Также заполняются региональные поля:
- **Beneficiary (financial ads in Australia)**: `project.beneficiary.australia`
- **Payer (financial ads in Australia)**: `project.payer.australia`
- **Beneficiary (financial ads in Taiwan)**: `project.beneficiary.taiwan`
- **Payer (financial ads in Taiwan)**: `project.payer.taiwan`
- **Beneficiary (Taiwan)**: `project.beneficiary.taiwan`
- **Payer (Taiwan)**: `project.payer.taiwan`
- **Beneficiary (Singapore)**: `project.beneficiary.singapore`
- **Payer (Singapore)**: `project.payer.singapore`

## Logs File

Файл `logs.csv` используется для логирования всех созданных кампаний.

**Структура `logs.csv`:**
- `campaign_name` — название кампании (сгенерированный нейминг)
- `campaign_id` — ID созданной кампании (из ответа Facebook API)
- `adset_id` — ID созданного адсета (из ответа Facebook API, пустое если не создан)
- `created_at` — дата и время создания в формате ISO 8601 (YYYY-MM-DD HH:MM:SS)

При создании новой кампании через API запись автоматически добавляется в конец файла после успешного создания Campaign и Ad Set. Если файл не существует, он создается с заголовками.
