#!/usr/bin/env python3
"""
Universal script for creating Facebook campaigns via API
Supports creating a single campaign or campaigns for all tiers
"""
import argparse
import os
import sys
from datetime import datetime
from utils.tier_utils import (
    load_tiers, 
    get_all_countries_for_tier, 
    format_tier_for_naming,
    get_all_worldwide_countries,
    get_country_groups_for_tier
)
from utils.logging import log_campaign_creation
from utils.naming import generate_campaign_name
from utils.campaign_builder import create_campaign_via_api, create_adset_via_api
from utils.config_loader import load_json


def get_locale_ids(lang_code, locales_data):
    """Map language codes to Facebook locale IDs"""
    return locales_data.get(lang_code, [])


def get_restricted_countries():
    """Returns list of Facebook restricted countries"""
    return ["CU", "IR", "RU", "SD", "UK", "IC", "JB"]


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Create Facebook campaigns via API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Create a single campaign for a specific tier
  python create_campaign_universal.py --project DuoChat --tier Latam --gender M --age 18-65+ --budget 50 --bid 0.30
  
  # Create campaigns for all tiers
  python create_campaign_universal.py --project DuoChat --all-tiers --gender M --age 18-65+ --budget 50 --bid 0.30
  
  # Create WW campaign for any project
  python create_campaign_universal.py --project Likerro --tier WW --gender MF --age 21-65+ --budget 25 --opt-model tROAS --bid-strategy "Lower cost"
        """
    )
    
    # Required parameters
    parser.add_argument('--project', required=True, help='Project name (DuoChat, Likerro, Pheromance)')
    parser.add_argument('--os', choices=['AND', 'IOS'], default='AND', help='Operating system')
    parser.add_argument('--gender', choices=['M', 'F', 'MF'], required=True, help='Gender')
    parser.add_argument('--age', required=True, help='Age (e.g., 18-65+, 21-65)')
    parser.add_argument('--budget', type=float, required=True, help='Daily budget')
    
    # Tier (either specific or --all-tiers)
    tier_group = parser.add_mutually_exclusive_group(required=True)
    tier_group.add_argument('--tier', help='Specific tier (Tier-1, Latam, WW, etc.)')
    tier_group.add_argument('--all-tiers', action='store_true', help='Create campaigns for all tiers')
    
    # Optimization
    parser.add_argument('--opt-model', choices=['CPA', 'CPI', 'tROAS'], default='CPA', help='Optimization model')
    parser.add_argument('--event', help='Event (only for CPA, e.g.: "4 sessions", "40 ads")')
    
    # Bid strategy
    parser.add_argument('--bid-strategy', choices=['Bid cap', 'Cost per result goal', 'Lower cost', 'Ad impression'], 
                       default='Bid cap', help='Bid strategy')
    parser.add_argument('--bid', type=float, help='Bid value (required for Bid cap and Cost per result goal)')
    
    # Additional parameters
    parser.add_argument('--language', help='Language (e.g.: "English", "Spanish")')
    parser.add_argument('--campaign-type', choices=['CBO', 'noCBO'], default='noCBO', help='Campaign type')
    parser.add_argument('--autor', default='KH', help='Campaign author')
    parser.add_argument('--account', help='Account name (if not specified, first one from list is used)')
    
    return parser.parse_args()


def create_single_campaign_data(
    project,
    accounts,
    tier_name,
    params,
    tiers_data
):
    """Create data for a single campaign"""
    # Determine tier and countries
    if tier_name == "WW":
        tier_raw = "WW"
        tier = "WW"
        countries = get_all_worldwide_countries(tiers_data)
        # Exclude restricted countries
        restricted = get_restricted_countries()
        countries = [c for c in countries if c not in restricted]
        naming_countries = []  # For WW, don't list countries in naming
        is_worldwide = True
        country_group_keys = ["worldwide"]
    else:
        tier_mapping = {
            "Tier-1": "Tier1",
            "Latam": "LatAm",
            "latam": "LatAm",
            "LatAm": "LatAm"
        }
        tier_raw = tier_mapping.get(tier_name, tier_name)
        tier = format_tier_for_naming(tier_raw)
        countries = get_all_countries_for_tier(tier_raw)
        # Exclude restricted countries
        restricted = get_restricted_countries()
        countries = [c for c in countries if c not in restricted]
        naming_countries = []  # For entire tier, don't list countries
        is_worldwide = False
        country_group_keys = get_country_groups_for_tier(tier_raw)
    
    # Select account
    if params.get('account_name'):
        account_name = params['account_name']
    else:
        account_name = project['account_names'][0]
    account_id = accounts[account_name]
    
    # Generate naming
    naming_params = {
        'os': params['os'],
        'tier': tier,
        'naming_countries': naming_countries,
        'gender': params['gender'],
        'age': params['age'],
        'opt_model': params['opt_model'],
        'event': params.get('event_code'),
        'date': params['date'],
        'autor': params['autor'],
        'campaign_type': params['campaign_type'],
        'bid_strategy_short': params['bid_strategy_short'],
        'lang': params['lang'],
        'extra': account_name
    }
    
    campaign_name = generate_campaign_name(naming_params)
    
    return {
        'name': campaign_name,
        'tier': tier,
        'tier_raw': tier_raw,
        'countries': countries,
        'is_worldwide': is_worldwide,
        'country_group_keys': country_group_keys,
        'account_id': account_id,
        'account_name': account_name
    }


def main():
    """Main function"""
    args = parse_arguments()
    
    # Load dictionaries
    projects = load_json('dictionares/projects.json')
    accounts = load_json('dictionares/accounts.json')
    objectives = load_json('dictionares/objectives.json')
    optimization_goals = load_json('dictionares/optimization_goals.json')
    bid_strategies = load_json('dictionares/bid_strategies.json')
    api_config = load_json('dictionares/api_config.json')
    tiers_data = load_tiers()
    
    # Load optional dictionaries
    events = {}
    event_types = {}
    if args.event:
        events = load_json('dictionares/events.json')
        event_types = load_json('dictionares/event_types.json')
    
    languages = {}
    locales_data = {}
    if args.language:
        languages = load_json('dictionares/languages.json')
        locales_data = load_json('dictionares/locales.json')
    
    # Get project data
    if args.project not in projects:
        print(f"Error: Project '{args.project}' not found in projects.json")
        sys.exit(1)
    
    project = projects[args.project]
    
    # Get event (if specified)
    event_code = None
    if args.event:
        if args.event not in events:
            print(f"Error: Event '{args.event}' not found in events.json")
            sys.exit(1)
        event_code = events[args.event]
    
    # Get language (if specified)
    lang_code = "ALL"
    locales = []
    if args.language:
        if args.language not in languages:
            print(f"Error: Language '{args.language}' not found in languages.json")
            sys.exit(1)
        lang_code = languages[args.language]
        locales = get_locale_ids(lang_code, locales_data)
        # Temporarily not using locales due to API issues
        locales = []
    
    # Bid strategy mapping
    bid_strategy_short_map = {
        'Bid cap': 'bc',
        'Cost per result goal': 'cc',
        'Lower cost': 'lc',
        'Ad impression': 'ai'
    }
    bid_strategy_short = bid_strategy_short_map.get(args.bid_strategy, 'bc')
    
    # Check bid for Bid cap and Cost per result goal
    if args.bid_strategy in ['Bid cap', 'Cost per result goal'] and not args.bid:
        print(f"Error: For strategy '{args.bid_strategy}' --bid must be specified")
        sys.exit(1)
    
    # Date
    today = datetime.now()
    date_str = today.strftime("%d%m%Y")
    
    # Age
    age_parts = args.age.replace('+', '').split('-')
    age_min = int(age_parts[0])
    age_max = int(age_parts[1]) if len(age_parts) > 1 else 65
    
    # Gender
    genders_map = {"M": [1], "F": [2], "MF": [1, 2]}
    genders = genders_map[args.gender]
    
    # API mappings
    objective_api = objectives[project['campaign_objective']]
    optimization_goal_api = optimization_goals[args.opt_model]
    bid_strategy_api = bid_strategies[args.bid_strategy]
    
    # Application ID without "x:" prefix
    application_id = project['application_id'].replace('x:', '')
    
    # Custom event type (only for CPA with events)
    custom_event_type_api = None
    if args.opt_model == "CPA" and event_code:
        custom_event_type_api = event_types[event_code]
    
    # Parameters for all campaigns
    base_params = {
        'os': args.os,
        'gender': args.gender,
        'age': args.age,
        'opt_model': args.opt_model,
        'campaign_type': args.campaign_type,
        'bid_strategy_short': bid_strategy_short,
        'lang': lang_code,
        'autor': args.autor,
        'date': date_str,
        'account_name': args.account,
        'event_code': event_code
    }
    
    # Determine list of tiers to process
    if args.all_tiers:
        tiers_to_process = list(tiers_data.keys())
    else:
        tiers_to_process = [args.tier]
    
    # Collect campaign information
    campaign_data_list = []
    
    print("=" * 80)
    if args.all_tiers:
        print("GENERATING CAMPAIGNS FOR ALL TIERS")
    else:
        print("GENERATING CAMPAIGN")
    print("=" * 80)
    print(f"Project: {args.project}")
    print(f"OS: {args.os}")
    print(f"Gender: {args.gender}")
    if args.event:
        print(f"Event: {args.event} ({event_code})")
    print(f"Budget: ${args.budget}")
    if args.bid:
        print(f"Bid: ${args.bid}")
    print(f"Age: {args.age}")
    if args.language:
        print(f"Language: {args.language} ({lang_code})")
    print()
    
    for tier_name in tiers_to_process:
        camp_data = create_single_campaign_data(
            project,
            accounts,
            tier_name,
            base_params,
            tiers_data
        )
        campaign_data_list.append(camp_data)
        
        print(f"Tier: {camp_data['tier']}")
        print(f"  Countries: {len(camp_data['countries'])} countries")
        print(f"  Naming: {camp_data['name']}")
        print()
    
    print("=" * 80)
    print(f"Total campaigns to be created: {len(campaign_data_list)}")
    print("=" * 80)
    
    # Request confirmation
    confirmation = input("\nCreate campaigns with these namings? (yes/no): ").strip().lower()
    
    if confirmation != 'yes':
        print("Campaign creation cancelled.")
        return
    
    # Create campaigns via API
    print("\nCreating campaigns via API...")
    
    for i, camp_data in enumerate(campaign_data_list, 1):
        print(f"\n[{i}/{len(campaign_data_list)}] Creating campaign for tier {camp_data['tier']}...")
        
        try:
            # API parameters
            api_params = {
                'daily_budget': args.budget,
                'optimization_goal': optimization_goal_api,
                'bid_strategy': bid_strategy_api,
                'bid_amount': args.bid,
                'custom_event_type': custom_event_type_api,
                'custom_event_str': event_code,
                'object_store_url': project['object_store_url'],
                'application_id': application_id,
                'targeting_countries': camp_data['countries'],
                # Targeting by tier via country_groups / is_worldwide, by countries via countries
                'country_group_keys': camp_data.get('country_group_keys'),
                'is_worldwide': camp_data.get('is_worldwide', False),
                'excluded_countries': get_restricted_countries(),
                'age_min': age_min,
                'age_max': age_max,
                'genders': genders,
                'user_os': 'android' if args.os == 'AND' else 'ios',
                'locales': locales
            }
            
            # Regional regulated categories for WW or if TW/SG in countries
            if camp_data['tier'] == "WW" or "TW" in camp_data['countries'] or "SG" in camp_data['countries']:
                api_params['regional_regulated_categories'] = ["TAIWAN_UNIVERSAL", "SINGAPORE_UNIVERSAL"]
            
            # Create campaign
            campaign_id = create_campaign_via_api(
                camp_data['account_id'],
                camp_data['name'],
                objective_api,
                api_config
            )
            print(f"  ✓ Campaign created: {campaign_id}")
            
            # Create ad set
            adset_id = create_adset_via_api(
                camp_data['account_id'],
                campaign_id,
                camp_data['name'],
                api_params,
                api_config,
                use_targeting_spec=True
            )
            print(f"  ✓ Ad set created: {adset_id}")
            
            # Log
            log_campaign_creation(
                campaign_name=camp_data['name'],
                campaign_id=campaign_id,
                adset_id=adset_id
            )
            print(f"  ✓ Entry added to logs.csv")
            
        except Exception as e:
            print(f"  ✗ Error creating campaign or ad set: {e}")
    
    print("\n" + "=" * 80)
    print("DONE!")
    print("=" * 80)


if __name__ == "__main__":
    main()
