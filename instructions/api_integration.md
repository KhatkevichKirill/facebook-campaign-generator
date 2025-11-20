# Facebook Marketing API Integration

## Overview

Integration with Facebook Marketing API for creating campaigns and ad sets via POST requests.

## API Configuration

API configuration is stored in `dictionares/api_config.json`:
- `access_token` — API access token (filled by user)
- `api_version` — API version (default "v23.0")
- `base_url` — base API URL

**Important:** The access token must be filled before using the API.

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

### Adlocales Updating
```
search?type=adlocale&q={language}
```


## Campaign Creation Request

### Required Fields:
- `account_id` — Ad account ID (obtained from `accounts.json` by selected name from `project.account_names`)
- `name` — Campaign name (generated naming)
- `objective` — Campaign objective (from `objectives.json`, mapping of `project.campaign_objective`)
- `status` — Campaign status (default "PAUSED" or "ACTIVE")
- `special_ad_categories` — Special ad categories (default `["NONE"]`)

### Example Request:
```json
{
  "account_id": "act_123456789",
  "name": "AND_Europe(IT)_M_21-65_CPA[ad_displayed_40]_16112025_KH_noCBO_bc_ENG_LK1",
  "objective": "APP_PROMOTION",
  "status": "PAUSED",
  "special_ad_categories": ["NONE"]
}
```

### Response:
Returns `campaign_id`, which is used to create the Ad Set.

## Ad Set Creation Request

### Required Fields:
- `account_id` — Ad account ID (obtained from `accounts.json` by selected name from `project.account_names`)
- `name` — Ad set name (generated naming, same as campaign)
- `campaign_id` — Created campaign ID (obtained from campaign creation response)
- `daily_budget` — Daily budget (from campaign parameters)
- `billing_event` — Billing event (always `"IMPRESSIONS"`)
- `optimization_goal` — Optimization goal (from `optimization_goals.json`, mapping of optimization model)
- `bid_strategy` — Bid strategy (from `bid_strategies.json`)
- `bid_amount` — Bid value (only if `bid_strategy` = `"BID_CAP"`)
- `promoted_object` — Promoted object:
  - `custom_event_type` — Event type (from `event_types.json`, mapping from `events.json`)
  - `custom_event_str` — Specific event name (from `events.json`, e.g., "session_started_3")
  - `object_store_url` — App store URL (from `projects.json`)
  - `application_id` — Application ID (from `projects.json`, without "x:" prefix)

### Targeting Fields:
- `targeting` — Targeting object:
  - `geo_locations` — Geography:
    - `countries` — Array of ISO country codes:
      - If targeting entire tier → all tier countries from `tiers.json`
      - If specific countries are specified → array of specified countries
      - If more than 5 countries from different tiers → all specified countries (WW is used in naming)
    - `excluded_countries` — Excluded countries (if any)
  - `age_min` — Minimum age
  - `age_max` — Maximum age (65+ → 65)
  - `genders` — Array of genders: `[1]` for Men, `[2]` for Women, `[1, 2]` for Both
  - `locales` — Array of languages (if language is specified, otherwise empty array for all languages)
  - `user_os` — Array of operating systems: `["android"]` for Android, `["ios"]` for iOS
  - `targeting_automation` — Targeting automation object:
    - `advantage_audience` — Advantage audience flag (1 or 0, required field)

### Example Request:
```json
{
  "account_id": "act_123456789",
  "name": "AND_Tier-1(US)_M_21-65_CPA[ad_displayed_40]_16112025_KH_noCBO_bc_ENG_AK1",
  "campaign_id": "123456789012345",
  "daily_budget": 25000,
  "billing_event": "IMPRESSIONS",
  "optimization_goal": "OFFSITE_CONVERSIONS",
  "bid_strategy": "LOWEST_COST_WITH_BID_CAP",
  "bid_amount": 520,
  "promoted_object": {
    "custom_event_type": "OTHER",
    "custom_event_str": "ad_displayed_40",
    "object_store_url": "https://play.google.com/store/apps/details?id=com.guardiangridgames.hidden",
    "application_id": "627096341267498"
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
Mapping from `campaign_objective` to `objectives.json`:
- "App promotion" → "APP_PROMOTION"

### Optimization Goals
Mapping from optimization model to `optimization_goals.json`:
- "CPA" → "OFFSITE_CONVERSIONS"
- "CPI" → "APP_INSTALLS"
- "tROAS" → "VALUE_OPTIMIZATION"

### Bid Strategies
Mapping from bid strategy to `bid_strategies.json`:
- "Bid cap" → "BID_CAP" (requires `bid_amount`)
- "Cost per result goal" → "COST_CAP"
- "Lower cost" → "LOWEST_COST_WITHOUT_BID_CAP"
- "Ad impression" → "COST_PER_IMPRESSION"

### Events (for CPA)
Events from `events.json` are mapped to types via `event_types.json`:
- "ad_displayed_20" → type "OTHER" (custom event)
- "ad_displayed_40" → type "OTHER" (custom event)
- "session_started_3/4/5" → type "OTHER" (custom event)

**Important:** 
- `ad_displayed_20` and `ad_displayed_40` are custom events (OTHER), not AD_IMPRESSION
- AD_IMPRESSION is used **only** for tROAS/ROAS campaigns, where Value is used based on these events

### Gender Mapping
- "Men" → `[1]`
- "Women" → `[2]`
- "Both" → `[1, 2]`

### Language Mapping
Languages from `languages.json` are mapped to Facebook locale IDs:
- "EN" → `[6003, 6004]` (English US, English UK)
- "ES" → `[6005]` (Spanish)
- etc.

If language is not specified, `locales` remains an empty array `[]` (targeting all languages).

## Workflow

**API is the only method for creating campaigns. CSV files are no longer created.**

1. Campaign naming is generated
2. Naming is shown to the user for confirmation
3. After confirmation:
   - **Account selection**: If the project has multiple `account_names`, a list of names is shown for selection
   - **Account mapping**: The selected name is mapped to `account_id` via the `accounts.json` dictionary
   - **Campaign is created via API** (uses `account_id`, receives `campaign_id`)
   - **Ad Set is created via API** (uses `account_id` and `campaign_id`, receives `adset_id`)
   - **Entry is automatically added to `logs.csv`** with fields:
     - `campaign_name` — generated naming
     - `campaign_id` — created campaign ID
     - `adset_id` — created ad set ID
     - `created_at` — creation date and time

## Automatic Logging

After successful creation of Campaign and Ad Set, an entry is automatically added to `logs.csv`:

```python
from utils.logging import log_campaign_creation

# После успешного создания Campaign и Ad Set:
log_campaign_creation(
    campaign_name="AND_LK_Tier-1(AU,CA)_M_24-65+_CPA[session_started_3]_17112025_KH_noCBO_bc_ENG",
    campaign_id="120234676409240622",
    adset_id="120234677752700622"
)
```

Or manually via CSV:

```python
import csv
from datetime import datetime

# Adding entry to logs.csv
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

On API errors:
- Show error message to user
- **Do not create any CSV files** — all campaigns are managed only via API
- Entry in `logs.csv` is **NOT added** if campaign or ad set were not created via API

        