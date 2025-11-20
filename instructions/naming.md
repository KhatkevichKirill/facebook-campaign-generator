# Naming Rules

Campaign naming is formed in the following order:

[OS]_[TIER]([COUNTRIES])_[GENDER]_[AGE]_[OPT MODEL][[EVENT?]]_[DATE]_[AUTOR]_[CBO/noCBO]_[BID STRATEGY]_[LANG]_[EXTRA?]

AND_Tier-1(US)_M_21-65_CPA[ad_displayed_80]_16112025_YU_noCBO_bc_ENG_account_1

## Rules for each element:

### OS
values:
- AND
- IOS

### PROJECT (legacy)
The current project uses only one project (`Mirai`), so the `[PROJECT]` segment in naming **is not used**.
If multiple projects appear in the future, it can be restored by mapping `project.name` to an alias in `projects.json`.

### Tier
values (from `tiers.json`):
- **Tier1** (in naming can be `Tier-1` for readability)
- **Asia**
- **Africa**
- **Arabian**
- **Europe**
- **LatAm** (in naming can be `Latam`)
- **CIS**
- **Other**
- **WW** (used when countries are from different tiers or more than 5 countries)

**Tier determination:**
1. If the user specified a tier directly (e.g., "Latam") — the specified tier is used
2. If specific countries are specified:
   - Countries are determined by the `tiers.json` dictionary (from `examples/tiers_by_countries.csv`)
   - If all countries are from one tier → that tier is used
   - If more than 5 countries from different tiers → `WW` is used
   - If 5 or fewer countries → the tier to which the countries belong is used (if one tier), otherwise countries are listed

### Countries
Countries are formed in a line separated by commas: `US,CA,GB`. Added in parentheses, after the tier.

**Important:** Use correct country codes (GB for United Kingdom, not UK). Restricted countries (CU, IR, RU, SD) should not be used in targeting (see `targeting.md`).

**Rules:**
- If targeting entire tier → countries are not specified in parentheses, only tier: `AND_LK_Latam_M_21-65_...`
- If specific countries are specified (5 or fewer) → listed in parentheses: `AND_LK_Tier-1(US,CA)_M_21-65_...`
- If more than 5 countries from one tier → tier is used, countries are listed in parentheses: `AND_LK_Latam(BR,MX,AR,CO,CL,PE,EC)_M_21-65_...`
- If more than 5 countries from different tiers → `WW` is used, countries are listed in parentheses: `AND_LK_WW(US,CA,BR,MX,AR,CO,CL)_M_21-65_...`

### Gender
Men → M  
Women → F  
Both → MF 

### Age
Any range, e.g., `18-44` or `18-65+`. Default `18-65+`

### Optimization Model
values:
- CPI
- CPA
- tROAS

### Event
Used only for CPA.
Taken from the `events.json` dictionary.

### Date
Date in format `DDMMYYYY`, by default today's date is used

### Author
Campaign author, default `KH`

### Campaign Type
values:
- CBO
- noCBO


### Bid Strategy
`BidCap`, `CostCap`, `LowerCost`, `AdImpression`
 

### Language
Taken from the `languages.json` dictionary (EN, ES, PT…).

**By default (if language is not specified):**
- In naming `_ALL_` is used
- In targeting all languages are targeted (Locales field remains empty in final CSV)

## Naming Usage

1. Generated naming **must be shown to the user**
2. Confirmation is requested: "Create campaign with this naming?"
3. Only after user confirmation:
   - Campaign is created via Facebook Marketing API
   - Ad Set is created via Facebook Marketing API
   - `Campaign Name` and `Ad Set Name` in API = generated naming
   - Naming is written to `logs.csv` along with creation date

Separate CSV files (in the `launches/` directory) are no longer created — the system works only via API and `logs.csv`.