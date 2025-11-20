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
Taken from `events.json`.

## Bid Strategy
values:
- Bid cap
- Cost per result goal
- Lower cost
- Ad impression

## Daily Budget
Number.

## Bid Value
Number (float, "." separator).

## Special ad categories
"special_ad_categories": ["NONE"]

## Project-Specific Settings
Taken from the `projects.json` dictionary for each project:

- **Account Names**: `project.account_names` (array of account names, e.g., ["account_1", "account_2"])
  - Account names are mapped to IDs via the `accounts.json` dictionary
  - When creating a campaign, the user selects an account name, and the system finds the corresponding ID
- **Campaign Objective**: `project.campaign_objective` (e.g., "App promotion")
- **Link Object ID**: `project.link_object_id` (format: "...")
- **Application ID**: `project.application_id` (format: "...")
- **Object Store URL**: `project.object_store_url` (app store URL)
- **Beneficiary**: `project.beneficiary.default` or regional variant (`project.beneficiary.australia`, `project.beneficiary.taiwan`, `project.beneficiary.singapore`)
- **Payer**: `project.payer.default` or regional variant (`project.payer.australia`, `project.payer.taiwan`, `project.payer.singapore`)

Regional variants are used depending on campaign geography. If a regional value is empty, `default` is used.

**For API:** 
- If the project has multiple `account_names`, a list of names is shown to the user for selection
- The selected account name is mapped to `account_id` via the `accounts.json` dictionary
- The resulting `account_id` is used in Facebook Marketing API requests