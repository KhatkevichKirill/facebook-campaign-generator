# Accounts Dictionary

The `accounts.json` dictionary contains a mapping of account names to their IDs for Facebook Marketing API.

## Structure

```json
{
  "account_1": "1824596061915489",
  "account_2": "81405705227234275",
  "account_3": "13402556184214015"
}
```

## Usage

1. In `projects.json`, account names are specified in the `account_names` field:
   ```json
   {
     "DuoChat": {
       "account_names": ["account_1", "account_2", "account_3"],
       ...
     }
   }
   ```

2. When creating a campaign:
   - If the project has one account — it is used automatically
   - If the project has multiple accounts — by default, the first one in order from `accounts.json` is selected
   - The selected name is mapped to `account_id` via `accounts.json`
   - The resulting `account_id` is used in API requests

## Example

**User request:**
```
Create a campaign for Mirai
```

**Process:**
1. The system finds the "Mirai" project in `projects.json`
2. Sees `account_names: ["account_1", "account_2", "account_3"]`
3. The system selects the specified account or the first one in the list if no account was specified, from `accounts.json`: `"account_1": "act_1828845960619189"`
4. Uses `account_id = "act_1828845960619189"` in API requests

## Adding New Accounts

To add a new account:
1. Add an entry to `accounts.json`: `"Name": "act_ID"`
2. Add the name to `account_names` of the corresponding project in `projects.json`

