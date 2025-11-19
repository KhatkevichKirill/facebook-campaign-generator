# Campaign Settings Rules

## Campaign Type
CBO → budget at campaign level  
noCBO → budget at adset level

## Optimization Model
values:
- CPA
- CPI
- tROAS

## Event (only if CPA)
Берётся из `events.json`.

## Bid Strategy
values:
- Bid cap
- Cost per result goal
- Lower cost
- Ad impression

## Daily Budget
Число.

## Bid Value
Число (float, "." separator).

## Project-Specific Settings
Берутся из словаря `projects.json` для каждого проекта:

- **Account Names**: `project.account_names` (массив названий аккаунтов, например ["DC(ДЦ)1", "DC(ДЦ)2"])
  - Названия аккаунтов маппятся на ID через словарь `accounts.json`
  - При создании кампании пользователь выбирает название аккаунта, система находит соответствующий ID
- **Campaign Objective**: `project.campaign_objective` (например, "App promotion")
- **Link Object ID**: `project.link_object_id` (формат: "o:...")
- **Application ID**: `project.application_id` (формат: "x:...")
- **Object Store URL**: `project.object_store_url` (URL приложения в магазине)
- **Beneficiary**: `project.beneficiary.default` или региональный вариант (`project.beneficiary.australia`, `project.beneficiary.taiwan`, `project.beneficiary.singapore`)
- **Payer**: `project.payer.default` или региональный вариант (`project.payer.australia`, `project.payer.taiwan`, `project.payer.singapore`)

Региональные варианты используются в зависимости от географии кампании. Если региональное значение пустое, используется `default`.

**Для API:** 
- Если у проекта несколько `account_names`, пользователю показывается список названий для выбора
- Выбранное название аккаунта маппится на `account_id` через словарь `accounts.json`
- Полученный `account_id` используется в запросах к Facebook Marketing API