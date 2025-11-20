# Targeting Rules

## Countries (geo)

### Facebook Restricted Countries

The following countries **MUST NOT be used** in targeting, as they are restricted by Facebook:
- **CU** (Cuba)
- **IR** (Iran)
- **RU** (Russia)
- **SD** (Sudan)
- **UK** (incorrect code, should be **GB** for United Kingdom)

These countries are excluded from `tiers.json` and should not appear in `targeting.geo_locations.countries`.

**Important:** If the user specified one of these countries, either exclude it from targeting or warn the user.

### Geography Determination

1. **Targeting entire tier** (e.g., "Latam"):
   - For tiers that have a mapping in `country_groups.json` (e.g., Africa, Asia, Europe, LatAm), `targeting.geo_locations.country_groups` is used in API
   - For the `WW` tier, `targeting.geo_locations.country_groups = ["worldwide"]` and `targeting.geo_locations.is_worldwide = true` are used
   - For tiers without mapping in `country_groups.json`, a list of countries from `tiers.json` is used in `targeting.geo_locations.countries`
   - In naming, only the tier is specified without listing countries

2. **Targeting specific countries**:
   - If 5 or fewer countries are specified:
     - Tier is determined for these countries via `tiers.json`
     - If all countries are from one tier → that tier is used in naming, countries are listed in parentheses
     - If countries are from different tiers → all countries are listed in parentheses, tier is determined by majority
   - If more than 5 countries are specified:
     - Tiers are determined for all countries via `tiers.json`
     - If all countries are from one tier → that tier is used in naming, countries are listed in parentheses
     - If countries are from different tiers → `WW` is used in naming, **all countries are listed in parentheses**

3. **`tiers.json` dictionary**:
   - Created based on `examples/tiers_by_countries.csv`
   - Contains mapping of tiers to country lists
   - Used to determine tier by countries and for targeting entire tier
   - Available via `utils/tier_utils.py` utility for programmatic tier determination

**Examples:**
- Targeting "Latam" → all LatAm countries from `tiers.json` in targeting, naming: `AND_LK_Latam_M_21-65_...`
- Countries ["US", "CA"] → Tier1 tier, naming: `AND_LK_Tier-1(US,CA)_M_21-65_...`
- Countries ["BR", "MX", "AR", "CO", "CL", "PE", "EC"] (7 countries, all LatAm) → LatAm tier, naming: `AND_LK_Latam(BR,MX,AR,CO,CL,PE,EC)_M_21-65_...`
- Countries ["US", "CA", "BR", "MX", "AR", "CO", "CL"] (7 countries, different tiers) → WW tier, naming: `AND_LK_WW(US,CA,BR,MX,AR,CO,CL)_M_21-65_...`

## Country exclusions
Optional field.
If present:
- excluded countries MUST NOT appear in final geography
- value must appear in `targeting.geo_locations.excluded_countries` in API request

## Gender
Men → targeting.men  
Women → targeting.women  
Both → target all

## Age
Any range, e.g.:
- 18–44
- 25–65+
- 18–65+

## Language
For Ad set settings, taken from `locales.json`.  
For naming, ISO 639-1 format is taken from `languages.json`.
ISO 639-1 is used in naming.
In language settings, the "key" parameter is used.

**By default (if language is not specified):**
- In targeting, the parameter is not passed
- In naming, `_ALL_` is used (see `naming.md`)