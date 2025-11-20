# Facebook Campaign Builder for Cursor

This project allows you to automatically create advertising campaigns and ad sets for Meta Ads via Facebook Marketing API.

## System Capabilities

- ✅ **Automatic campaign creation via Facebook Marketing API**
- ✅ Campaign naming generation according to UA standards
- ✅ Targeting parameters collection (tier, countries, exclusions, age, gender, language)
- ✅ Optimization model and events selection
- ✅ Campaign settings formation (CBO/noCBO, budget, bid strategy)
- ✅ Automatic logging of all created campaigns
- ✅ Support for parameter modification commands ("change geo to Canada", "change bid", "set gender to Women")

## Core Logic

### Workflow

1. **Naming generation** — according to rules from `instructions/naming.md`
2. **User confirmation** — naming is shown, confirmation is awaited
3. **Creation via API** (by default):
   - Campaign creation via Facebook Marketing API
   - Ad Set creation via Facebook Marketing API
   - Automatic logging to `logs.csv`
4. **Error handling**:
   - On API errors, an error message is shown
   - CSV files are not created, entry in `logs.csv` is not added if campaign/adset were not created

### Project Structure

Cursor uses:
- **Instructions** in `/instructions` folder:
  - `naming.md` — campaign naming rules
  - `campaign_settings.md` — campaign and ad set settings
  - `targeting.md` — targeting rules
  - `csv_structure.md` — CSV structure and workflow (legacy)
  - `api_integration.md` — Facebook Marketing API integration
  - `modification_rules.md` — parameter modification rules
  - `accounts.md` — account management rules

- **Dictionaries** in `/dictionares`:
  - `projects.json` — projects with settings (account_names, application_id, etc.)
  - `accounts.json` — mapping of account names to IDs
  - `objectives.json` — campaign objectives mapping for API
  - `optimization_goals.json` — optimization models mapping
  - `bid_strategies.json` — bid strategies mapping
  - `event_types.json` — events to types mapping for API
  - `events.json` — available events
  - `languages.json` — languages for naming
  - `locales.json` — languages to Facebook locale IDs mapping
  - `countries.json` — country codes
  - `country_groups.json` — country groups for API
  - `tiers.json` — tiers to country lists mapping
  - `os.json` — operating systems
  - `api_config.json` — API configuration (access_token, api_version)

- **Examples** in `/examples`:
  - `tiers_by_countries.csv` — tier definitions by countries

- **Utilities** in `/utils`:
  - `logging.py` — automatic logging function
  - `naming.py` — naming generation
  - `campaign_builder.py` — API requests
  - `config_loader.py` — configuration loading with caching
  - `tier_utils.py` — tier utilities

## Usage

### Universal Script (Recommended)

Use `create_campaign_universal.py` to create campaigns via command line:

```bash
# Create a single campaign for a specific tier
python create_campaign_universal.py \
  --project DuoChat \
  --tier Latam \
  --gender M \
  --age 18-65+ \
  --budget 50 \
  --bid 0.30 \
  --event "4 sessions"

# Create campaigns for all tiers
python create_campaign_universal.py \
  --project DuoChat \
  --all-tiers \
  --gender M \
  --age 18-65+ \
  --budget 50 \
  --bid 0.30 \
  --event "4 sessions"

# Create WW campaign for any project
python create_campaign_universal.py \
  --project Likerro \
  --tier WW \
  --gender MF \
  --age 21-65+ \
  --budget 25 \
  --opt-model tROAS \
  --bid-strategy "Lower cost" \
  --language "English"
```

**All parameters:**
- `--project` - project name (required)
- `--os` - operating system (AND/IOS, default AND)
- `--gender` - gender (M/F/MF, required)
- `--age` - age (required, e.g.: 18-65+, 21-65)
- `--budget` - daily budget (required)
- `--tier` or `--all-tiers` - tier or all tiers (required)
- `--opt-model` - optimization model (CPA/CPI/tROAS, default CPA)
- `--event` - event for CPA (optional)
- `--bid-strategy` - bid strategy (default "Bid cap")
- `--bid` - bid value (required for Bid cap and Cost per result goal)
- `--language` - language (optional)
- `--campaign-type` - campaign type (CBO/noCBO, default noCBO)
- `--autor` - author (default KH)
- `--account` - account name (optional, first one is used by default)

### Using via Cursor (Interactive Mode)

### Basic Request

```
Create a campaign for project Likerro, Android, countries US and Australia, 
gender: women, age: 24-65+, CPA, event: four sessions, 
English language, Bid Cap 5.5 and budget 200. No CBO
```

### What Happens

1. Cursor generates naming according to rules
2. Shows naming for confirmation
3. After confirmation:
   - Creates Campaign via API
   - Creates Ad Set via API
   - Adds entry to `logs.csv`

### Request Examples

**Creating a campaign:**
```
Create a campaign: Likerro, Android, Tier-1, US, Men, 21-65+, 
CPA, 40 ads, English, Bid cap, 5.2, budget 250, noCBO
```

**Modifying parameters:**
```
Change geo to Canada
Change bid to 6.0
Set gender to Women
Change age to 25-65+
```

## Setup

### 1. API Configuration

Create file `dictionares/api_config.json` based on `dictionares/api_config.json.example`:
```json
{
  "access_token": "YOUR_ACCESS_TOKEN",
  "api_version": "v23.0",
  "base_url": "https://graph.facebook.com"
}
```

**Important:** `api_config.json` is not included in the repository for security reasons. Copy `api_config.json.example` and fill in your data.

### 2. Projects Configuration

Edit `dictionares/projects.json`:
```json
{
  "Likerro": {
    "account_names": ["account_1", "account_2"],
    "campaign_objective": "App promotion",
    "application_id": "x:627096341193498",
    "object_store_url": "http://play.google.com/store/apps/details?id=...",
    ...
  }
}
```

**Note:** Projects use `account_names` (account name references), not `account_ids`. Account names are mapped to IDs via `dictionares/accounts.json`.

## File Structure

```
facebook-campaign-generator/
├── create_campaign_universal.py  # Universal script for creating campaigns (CLI usage)
├── dictionares/                  # Dictionaries and configuration
│   ├── projects.json             # Project settings
│   ├── accounts.json             # Account names to IDs mapping
│   ├── api_config.json           # API configuration
│   ├── objectives.json           # Objectives mapping
│   ├── optimization_goals.json   # Optimization goals mapping
│   ├── bid_strategies.json       # Bid strategies mapping
│   ├── event_types.json          # Event types mapping
│   ├── events.json               # Available events
│   ├── languages.json            # Languages for naming
│   ├── locales.json              # Languages to locale IDs mapping
│   ├── countries.json            # Country codes
│   ├── country_groups.json      # Country groups for API
│   ├── tiers.json                # Tiers to countries mapping
│   └── os.json                   # Operating systems
├── instructions/                 # Instructions for Cursor
│   ├── naming.md                 # Campaign naming rules
│   ├── campaign_settings.md      # Campaign and ad set settings
│   ├── targeting.md              # Targeting rules
│   ├── csv_structure.md          # CSV structure (legacy)
│   ├── api_integration.md        # API integration
│   ├── modification_rules.md     # Parameter modification rules
│   └── accounts.md                # Account management rules
├── examples/                     # Examples and templates
│   └── tiers_by_countries.csv    # Tier definitions by countries
├── launches/                     # Historical CSV files (legacy, not used anymore)
├── utils/                        # Utilities
│   ├── naming.py                 # Naming generation
│   ├── campaign_builder.py       # API requests
│   ├── config_loader.py          # Configuration loading with caching
│   ├── tier_utils.py             # Tier utilities
│   └── logging.py                # Automatic logging
└── logs.csv                      # Log of all created campaigns
```

## Logging

All created campaigns are automatically logged to `logs.csv`:

| Field | Description |
|------|-------------|
| `campaign_name` | Campaign name (naming) |
| `campaign_id` | Created campaign ID (from API) |
| `adset_id` | Created ad set ID (from API) |
| `created_at` | Creation date and time |

**Important:** Entry is added only after successful creation of Campaign and Ad Set via API.

## Error Handling

On API errors:
- Error message is shown
- CSV files are not created, entry in `logs.csv` is not added if campaign/adset were not created

## Additional Information

- API integration details: see `instructions/api_integration.md`
- Naming rules: see `instructions/naming.md`
- CSV structure: see `instructions/csv_structure.md`
- Targeting rules: see `instructions/targeting.md`
- Account management: see `instructions/accounts.md`
- Examples: see `/examples`
