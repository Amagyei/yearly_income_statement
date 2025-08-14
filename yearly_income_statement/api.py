import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day, add_years
from datetime import datetime, timedelta
import json

# Row types for structured data
ROW_TYPES = {
    'HEADER': 'header',
    'SUB_HEADER': 'sub_header', 
    'ACCOUNT': 'account',
    'TOTAL': 'total',
    'SUMMARY': 'summary'
}

def safe_ratio(numerator, denominator, default='N/A'):
    """Helper function to safely calculate ratios with error handling"""
    if not denominator or denominator == 0:
        return default
    try:
        ratio = (numerator / denominator) * 100
        return round(ratio, 1)
    except (TypeError, ValueError, ZeroDivisionError):
        return default

def get_previous_fiscal_year(current_fiscal_year):
    """Get the previous fiscal year name"""
    try:
        current_fy = frappe.get_doc("Fiscal Year", current_fiscal_year)
        prev_year_start = frappe.utils.add_months(current_fy.year_start_date, -12)
        
        prev_fiscal_year = frappe.db.sql("""
            SELECT name FROM `tabFiscal Year`
            WHERE year_start_date <= %s AND year_end_date >= %s
            LIMIT 1
        """, (prev_year_start, prev_year_start), as_dict=1)
        
        return prev_fiscal_year[0]['name'] if prev_fiscal_year else current_fiscal_year
    except Exception as e:
        frappe.log_error(f"Error getting previous fiscal year: {str(e)}")
        return current_fiscal_year

def get_all_accounts(company, root_type):
    """Get all accounts of a specific root type using ERPNext's approach with hierarchy"""
    return frappe.db.sql("""
        SELECT name, account_name, account_number, root_type, parent_account, 
               is_group, disabled, lft, rgt, account_type, include_in_gross
        FROM `tabAccount`
        WHERE company = %s AND root_type = %s AND disabled = 0
        ORDER BY lft
    """, (company, root_type), as_dict=1)

def get_gl_entries_for_period(company, from_date, to_date, filters=None):
    """Get GL entries for a period with filters (mimics ERPNext's get_accounting_entries)"""
    conditions = ["company = %s", "posting_date BETWEEN %s AND %s", "is_cancelled = 0"]
    params = [company, from_date, to_date]
    
    if filters:
        if filters.get("cost_center"):
            # Handle cost center filtering like ERPNext
            cost_centers = get_cost_centers_with_children(filters.get("cost_center"))
            conditions.append("cost_center IN ({})".format(','.join(['%s'] * len(cost_centers))))
            params.extend(cost_centers)
    
    sql = """
        SELECT account, SUM(debit) as debit, SUM(credit) as credit,
               SUM(debit - credit) as net_amount
        FROM `tabGL Entry`
        WHERE {}
        GROUP BY account
    """.format(" AND ".join(conditions))
    
    return frappe.db.sql(sql, params, as_dict=1)

def get_cost_centers_with_children(cost_centers):
    """Get cost center and its children (mimics ERPNext's function)"""
    if not isinstance(cost_centers, list):
        cost_centers = [d.strip() for d in cost_centers.strip().split(",") if d]
    
    all_cost_centers = []
    for d in cost_centers:
        if frappe.db.exists("Cost Center", d):
            lft, rgt = frappe.db.get_value("Cost Center", d, ["lft", "rgt"])
            children = frappe.get_all("Cost Center", filters={"lft": [">=", lft], "rgt": ["<=", rgt]})
            all_cost_centers += [c.name for c in children]
        else:
            frappe.throw(_("Cost Center: {0} does not exist").format(d))
    
    return list(set(all_cost_centers))

def get_budget_data(fiscal_year, account, cost_center=None):
    """Get budget data for an account"""
    conditions = ["b.fiscal_year = %s", "ba.account = %s"]
    params = [fiscal_year, account]
    
    if cost_center:
        conditions.append("b.cost_center = %s")
        params.append(cost_center)
    
    sql = """
        SELECT SUM(ba.budget_amount) as budget_amount
        FROM `tabBudget Account` ba
        INNER JOIN `tabBudget` b ON ba.parent = b.name
        WHERE {}
    """.format(" AND ".join(conditions))
    
    result = frappe.db.sql(sql, params, as_dict=1)
    return result[0]['budget_amount'] if result and result[0]['budget_amount'] else 0

def calculate_account_financial_data(account, current_gl_entries, prev_gl_entries, ytd_gl_entries, 
                                   ytd_last_year_gl_entries, current_month_gl_entries, 
                                   current_month_last_year_gl_entries, fiscal_year, prev_fiscal_year,
                                   from_date, to_date, ytd_end_date, selected_cost_center, selected_month):
    """Calculate financial data for an account using pre-fetched GL entries"""
    
    account_code = account['name']
    account_type = account['root_type']
    
    # Get current year actual data from pre-fetched GL entries
    current_actual_amount = 0
    for entry in current_gl_entries:
        if entry['account'] == account_code:
            current_actual_amount += entry['net_amount']
    
    # Get current year budget
    current_budget_amount = get_budget_data(fiscal_year, account_code, selected_cost_center)
    
    # Get previous year data from pre-fetched GL entries
    prev_actual_amount = 0
    for entry in prev_gl_entries:
        if entry['account'] == account_code:
            prev_actual_amount += entry['net_amount']
    
    prev_budget_amount = get_budget_data(prev_fiscal_year, account_code, selected_cost_center)
    
    # Calculate YTD data from pre-fetched GL entries
    ytd_actual_amount = 0
    for entry in ytd_gl_entries:
        if entry['account'] == account_code:
            ytd_actual_amount += entry['net_amount']
    
    # Calculate YTD budget (proportional)
    days_elapsed = (getdate(ytd_end_date) - getdate(from_date)).days
    total_days = (getdate(to_date) - getdate(from_date)).days
    ytd_budget_amount = current_budget_amount * (days_elapsed / total_days) if total_days > 0 else 0
    
    # Get YTD last year data from pre-fetched GL entries
    ytd_last_year_amount = 0
    for entry in ytd_last_year_gl_entries:
        if entry['account'] == account_code:
            ytd_last_year_amount += entry['net_amount']
    
    # Calculate current month data if month is selected
    current_month_budget_amount = 0
    current_month_actual_amount = 0
    current_month_last_year_amount = 0
    
    if selected_month and selected_month.strip() and current_month_gl_entries:
        # Current month budget (proportional)
        month_ratio = 1/12
        current_month_budget_amount = current_budget_amount * month_ratio
        
        # Current month actual from pre-fetched GL entries
        for entry in current_month_gl_entries:
            if entry['account'] == account_code:
                current_month_actual_amount += entry['net_amount']
        
        # Current month last year from pre-fetched GL entries
        for entry in current_month_last_year_gl_entries:
            if entry['account'] == account_code:
                current_month_last_year_amount += entry['net_amount']
    
    # Forecast calculations
    forecast_actual = ytd_actual_amount * (total_days / days_elapsed) if days_elapsed > 0 else 0
    forecast_budget = current_budget_amount
    
    return {
        'currentMonth': {
            'lastYear': current_month_last_year_amount,
            'budget': current_month_budget_amount,
            'actual': current_month_actual_amount,
            'actBudThisYear': safe_ratio(current_month_actual_amount, current_month_budget_amount),
            'actVsLastYear': safe_ratio(current_month_actual_amount, current_month_last_year_amount)
        },
        'yearToDate': {
            'lastYear': ytd_last_year_amount,
            'budget': ytd_budget_amount,
            'actual': ytd_actual_amount,
            'actBudThisYear': safe_ratio(ytd_actual_amount, ytd_budget_amount),
            'actVsLastYear': safe_ratio(ytd_actual_amount, ytd_last_year_amount)
        },
        'forecast': {
            'lastYear': prev_actual_amount,
            'budget': forecast_budget,
            'actual': forecast_actual,
            'actBudThisYear': safe_ratio(forecast_actual, forecast_budget),
            'actVsLastYear': safe_ratio(forecast_actual, prev_actual_amount)
        }
    }

def filter_accounts_hierarchy(accounts, depth=20):
    """Filter accounts using ERPNext's hierarchy approach"""
    parent_children_map = {}
    accounts_by_name = {}
    
    for d in accounts:
        accounts_by_name[d['name']] = d
        parent_key = d.get('parent_account') or None
        parent_children_map.setdefault(parent_key, []).append(d)
    
    filtered_accounts = []
    
    def add_to_list(parent, level):
        if level < depth:
            children = parent_children_map.get(parent) or []
            # Sort by lft to maintain tree order
            children.sort(key=lambda x: x.get('lft', 0))
            
            for child in children:
                child['indent'] = level
                filtered_accounts.append(child)
                add_to_list(child['name'], level + 1)
    
    add_to_list(None, 0)
    return filtered_accounts, accounts_by_name, parent_children_map

def get_income_parent_group(account_code):
    """Determine the parent group for an income account based on account code patterns"""
    if not account_code:
        return 'Other Income'
    
    # Convert to string and extract the numeric part
    account_str = str(account_code)
    
    # Extract the main account number (e.g., "40001" from "40001 - Rooms Revenue - WSAH")
    if ' - ' in account_str:
        main_code = account_str.split(' - ')[0]
    else:
        main_code = account_str
    
    print(f"Processing account code: '{account_str}' -> main_code: '{main_code}'")
    
    # Define regex patterns for different income groups
    import re
    
    # Rooms Revenue - 400xx pattern (excluding 401xx, 402xx, 403xx, 404xx, 411xx)
    if re.match(r'^400\d{2}$', main_code) and not re.match(r'^40[1-4]\d{2}$', main_code):
        print(f"  -> Matches Rooms Revenue pattern")
        return 'Rooms Revenue'
    
    # Food Revenue - 401xx pattern
    if re.match(r'^401\d{2}$', main_code):
        print(f"  -> Matches Food Revenue pattern")
        return 'Food Revenue'
    
    # Beverage Revenue - 402xx pattern
    if re.match(r'^402\d{2}$', main_code):
        print(f"  -> Matches Beverage Revenue pattern")
        return 'Beverage Revenue'
    
    # Other Revenue - 403xx, 404xx, 411xx patterns
    if re.match(r'^40[34]\d{2}$', main_code) or re.match(r'^411\d{2}$', main_code):
        print(f"  -> Matches Other Revenue pattern")
        return 'Other Revenue'
    
    print(f"  -> No pattern match, defaulting to Other Income")
    # Default fallback
    return 'Other Income'

def _extract_first3_code(account: dict) -> str:
    """Extract the 3-digit family code from an account's number/name.
    Falls back to 'OTHER' when pattern not matched.
    """
    import re
    raw = account.get('account_number') or account.get('name', '')
    code = str(raw).split(' - ')[0]
    m = re.match(r'^(\d{3})\d{2}$', code)
    return m.group(1) if m else 'OTHER'

def _common_word_label(accounts: list[str]) -> str:
    """Pick a reasonable label from common words across account names."""
    if not accounts:
        return 'Other Income'
    tokens_sets = []
    for name in accounts[:5]:  # limit to first few for performance
        words = [w for w in str(name).lower().replace('&', ' ').replace('/', ' ').split() if w.isalpha()]
        tokens_sets.append(set(words))
    if not tokens_sets:
        return 'Other Income'
    common = set.intersection(*tokens_sets) if len(tokens_sets) > 1 else tokens_sets[0]
    # Prefer domain words
    preference = ['rooms', 'room', 'food', 'beverage', 'bar', 'restaurant', 'functions', 'other', 'revenue']
    for word in preference:
        if word in common:
            return f"{word.title()} Revenue" if 'revenue' not in word else word.title()
    if common:
        word = sorted(common, key=len, reverse=True)[0]
        return word.title()
    # Fallback
    return 'Other Income'

def build_income_clusters(income_hierarchy: list, income_accounts_catalog: list) -> list:
    """Cluster income leaf accounts by first-3-digit code and produce a list of
    {label, accounts} clusters. Label selection order:
      1) Account whose account_number == f"{first3}00" (its account_name)
      2) Known mapping (400 Rooms, 401 Food, 402 Beverage)
      3) Common word heuristic from account names
      4) 'Other Income'
    """
    # Map known first3 to labels
    known_labels = {
        '400': 'Rooms Revenue',
        '401': 'Food Revenue',
        '402': 'Beverage Revenue',
        '403': 'Other Revenue',
        '404': 'Other Revenue',
        '411': 'Other Revenue',
    }

    # Consider only leaf accounts from the rendered hierarchy
    leaves = [a for a in income_hierarchy if not a.get('is_group')]
    # Sort by account_number then name for stability
    def sort_key(a):
        code = str(a.get('account_number') or '').split(' - ')[0]
        return (code, a.get('account_name') or a.get('name'))
    leaves.sort(key=sort_key)

    clusters = []
    current_key = None
    current_accounts = []

    def flush_cluster():
        if not current_accounts:
            return
        first3 = current_key or 'OTHER'
        # Try find parent code account f"{first3}00"
        parent_label = None
        parent_code = f"{first3}00"
        for acc in income_accounts_catalog:
            acc_code = str(acc.get('account_number') or acc.get('name', '')).split(' - ')[0]
            if acc_code == parent_code:
                parent_label = acc.get('account_name') or acc.get('name')
                break
        if not parent_label:
            parent_label = known_labels.get(first3)
        if not parent_label:
            parent_label = _common_word_label([a.get('account_name') or a.get('name') for a in current_accounts])
        if not parent_label:
            parent_label = 'Other Income'
        clusters.append({'label': parent_label, 'first3': first3, 'accounts': list(current_accounts)})

    for acc in leaves:
        key = _extract_first3_code(acc)
        if current_key is None:
            current_key = key
        if key != current_key:
            flush_cluster()
            current_accounts = []
            current_key = key
        current_accounts.append(acc)
    # flush last
    flush_cluster()
    return clusters

def get_accounts_with_hierarchy(accounts, gl_entries):
    """Organize accounts using ERPNext's hierarchical approach"""
    # Filter accounts to create proper hierarchy
    filtered_accounts, accounts_by_name, parent_children_map = filter_accounts_hierarchy(accounts)
    
    # Add GL entries to each account
    for account in filtered_accounts:
        account_name = account['name']
        account_entries = [entry for entry in gl_entries if entry.get('account') == account_name]
        account['gl_entries'] = account_entries
    
    return filtered_accounts, accounts_by_name, parent_children_map

def process_account_data(account, ytd_gl_entries, ytd_last_year_gl_entries, 
                        current_month_gl_entries, current_month_last_year_gl_entries,
                        ytd_budget_entries, current_month_budget_entries,
                        forecast_budget_entries, forecast_actual_entries):
    """Process a single account and return formatted data"""
    account_name = account['name']
    
    # Get GL entries for this specific account
    account_gl_ytd = [entry for entry in ytd_gl_entries if entry.get('account') == account_name]
    account_gl_ytd_last_year = [entry for entry in ytd_last_year_gl_entries if entry.get('account') == account_name]
    account_gl_current_month = [entry for entry in current_month_gl_entries if entry.get('account') == account_name]
    account_gl_current_month_last_year = [entry for entry in current_month_last_year_gl_entries if entry.get('account') == account_name]
    
    # Calculate amounts from GL entries
    ytd_actual = sum(abs(entry.get('debit', 0) - entry.get('credit', 0)) for entry in account_gl_ytd)
    ytd_last_year = sum(abs(entry.get('debit', 0) - entry.get('credit', 0)) for entry in account_gl_ytd_last_year)
    current_month_actual = sum(abs(entry.get('debit', 0) - entry.get('credit', 0)) for entry in account_gl_current_month)
    current_month_last_year = sum(abs(entry.get('debit', 0) - entry.get('credit', 0)) for entry in account_gl_current_month_last_year)
    
    # Budget entries are not implemented yet, so use 0
    ytd_budget = 0
    current_month_budget = 0
    
    # Calculate forecast (simplified)
    forecast_actual = ytd_actual * 1.2  # Simple forecast logic
    forecast_budget = ytd_budget * 1.2
    
    return {
        'type': 'account',
        'category': account.get('account_name', account_name),
        'account': account_name,
        'root_type': account.get('root_type'),
        'currentMonth': {
            'lastYear': current_month_last_year,
            'budget': current_month_budget,
            'actual': current_month_actual,
            'actBudThisYear': safe_ratio(current_month_actual, current_month_budget),
            'actVsLastYear': safe_ratio(current_month_actual, current_month_last_year)
        },
        'yearToDate': {
            'lastYear': ytd_last_year,
            'budget': ytd_budget,
            'actual': ytd_actual,
            'actBudThisYear': safe_ratio(ytd_actual, ytd_budget),
            'actVsLastYear': safe_ratio(ytd_actual, ytd_last_year)
        },
        'forecast': {
            'lastYear': ytd_last_year,
            'budget': forecast_budget,
            'actual': forecast_actual,
            'actBudThisYear': safe_ratio(forecast_actual, forecast_budget),
            'actVsLastYear': safe_ratio(forecast_actual, ytd_last_year)
        }
    }

def calculate_section_total(accounts, total_label, root_type):
    """Calculate total for a section of accounts"""
    total_data = {
        'currentMonth': {'lastYear': 0, 'budget': 0, 'actual': 0},
        'yearToDate': {'lastYear': 0, 'budget': 0, 'actual': 0}, 
        'forecast': {'lastYear': 0, 'budget': 0, 'actual': 0}
    }
    
    # Sum up all non-group accounts
    for account in accounts:
        if not account.get('is_group'):
            # This would need to aggregate the processed account data
            # For now, return a placeholder
            pass
    
    return {
        'type': 'total',
        'category': total_label,
        'root_type': root_type,
        'currentMonth': total_data['currentMonth'],
        'yearToDate': total_data['yearToDate'],
        'forecast': total_data['forecast']
    }

def create_header_row(category):
    """Create a header row for a main category"""
    return {
        'type': ROW_TYPES['HEADER'],
        'category': category.replace('_', ' ').title()
    }

def create_sub_header_row(sub_category):
    """Create a sub-header row for a sub-category"""
    return {
        'type': ROW_TYPES['SUB_HEADER'],
        'category': sub_category
    }

def create_total_row(category, totals_data):
    """Create a total row for a category"""
    return {
        'type': ROW_TYPES['TOTAL'],
        'category': f"TOTAL {category.replace('_', ' ').title()}",
        'currentMonth': totals_data.get('currentMonth', {}),
        'yearToDate': totals_data.get('yearToDate', {}),
        'forecast': totals_data.get('forecast', {})
    }

def calculate_category_totals(accounts, current_gl_entries, prev_gl_entries, ytd_gl_entries, 
                             ytd_last_year_gl_entries, current_month_gl_entries, current_month_last_year_gl_entries,
                             fiscal_year, prev_fiscal_year, from_date, to_date, ytd_end_date, 
                             selected_cost_center, selected_month):
    """Calculate totals for a category of accounts using pre-fetched GL entries"""
    totals = {
        'currentMonth': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0},
        'yearToDate': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0},
        'forecast': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0}
    }
    
    for account in accounts:
        account_data = calculate_account_financial_data(
            account, current_gl_entries, prev_gl_entries, ytd_gl_entries,
            ytd_last_year_gl_entries, current_month_gl_entries, current_month_last_year_gl_entries,
            fiscal_year, prev_fiscal_year, from_date, to_date, ytd_end_date,
            selected_cost_center, selected_month
        )
        
        # Sum up all values
        for period in ['currentMonth', 'yearToDate', 'forecast']:
            for field in ['lastYear', 'budget', 'actual']:
                totals[period][field] += account_data[period][field]
    
    # Calculate ratios for totals
    for period in ['currentMonth', 'yearToDate', 'forecast']:
        totals[period]['actBudThisYear'] = safe_ratio(totals[period]['actual'], totals[period]['budget'])
        totals[period]['actVsLastYear'] = safe_ratio(totals[period]['actual'], totals[period]['lastYear'])
    
    return totals

@frappe.whitelist()
def get_dashboard_data(filters=None):
    """Get comprehensive dashboard data using ERPNext's logic"""
    print(f"=== API REQUEST ===")
    print(f"Filters: {filters}")
    print(f"Function called successfully")
    
    try:
        print(f"=== STARTING API PROCESSING ===")
        if filters is None:
            filters = {}
        
        # Extract filter parameters
        fiscal_year = filters.get('fiscal_year', '2025')
        selected_cost_center = filters.get('cost_center', '')
        selected_month = filters.get('month', '')
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        
        print(f"Extracted parameters:")
        print(f"  - Fiscal Year: {fiscal_year}")
        print(f"  - Cost Center: {selected_cost_center}")
        print(f"  - Month: {selected_month}")
        print(f"  - Company: {company}")
        
        # Get fiscal year document
        print(f"Getting fiscal year document for: {fiscal_year}")
        try:
            fy_doc = frappe.get_doc("Fiscal Year", fiscal_year)
            print(f"Successfully got fiscal year: {fy_doc.name}")
        except Exception as e:
            print(f"ERROR getting fiscal year: {str(e)}")
            return {'dashboard_data': [], 'filters': filters}
        
        # Set default dates based on fiscal year
        from_date = filters.get('from_date', str(fy_doc.year_start_date))
        to_date = filters.get('to_date', str(fy_doc.year_end_date))
        
        # Get previous fiscal year
        try:
            prev_fiscal_year = get_previous_fiscal_year(fiscal_year)
            prev_fy_doc = frappe.get_doc("Fiscal Year", prev_fiscal_year)
        except Exception as e:
            return {'dashboard_data': [], 'filters': filters}
        
        # Calculate date ranges
        try:
            from_date = getdate(from_date)
            to_date = getdate(to_date)
            prev_from_date = getdate(prev_fy_doc.year_start_date)
            prev_to_date = getdate(prev_fy_doc.year_end_date)
        except Exception as e:
            return {'dashboard_data': [], 'filters': filters}
        
        # Calculate current month date range if month is selected
        current_month_from_date = None
        current_month_to_date = None
        if selected_month and selected_month.strip():
            try:
                month_num = int(selected_month)
                year_num = int(fiscal_year)
                current_month_from_date = get_first_day(f"{year_num}-{month_num:02d}-01")
                current_month_to_date = get_last_day(f"{year_num}-{month_num:02d}-01")
            except Exception as e:
                pass
        
        # Calculate YTD end date
        try:
            from frappe.utils import today
            today_date = getdate(today())
            fy_start = getdate(fy_doc.year_start_date)
            fy_end = getdate(fy_doc.year_end_date)
            
            if fy_start <= today_date <= fy_end:
                ytd_end_date = today_date
            elif today_date > fy_end:
                ytd_end_date = fy_end
            else:
                ytd_end_date = fy_start
        except Exception as e:
            return {'dashboard_data': [], 'filters': filters}
        
        # STEP 1: Get ALL accounts (mimics ERPNext's get_accounts)
        print(f"Getting accounts for company: {company}")
        try:
            income_accounts = get_all_accounts(company, 'Income')
            expense_accounts = get_all_accounts(company, 'Expense')
            all_accounts = income_accounts + expense_accounts
            
            print(f"DEBUG: Found {len(income_accounts)} income accounts and {len(expense_accounts)} expense accounts")
            print(f"DEBUG: Total accounts: {len(all_accounts)}")
            if all_accounts:
                print(f"DEBUG: Sample accounts: {[acc['name'] for acc in all_accounts[:5]]}")
        except Exception as e:
            print(f"ERROR getting accounts: {str(e)}")
            return {'dashboard_data': [], 'filters': filters}
        
        # STEP 2: Get GL entries for the period (mimics ERPNext's set_gl_entries_by_account)
        # STEP 2: Pre-fetch ALL GL entries for different periods to avoid multiple queries
        print(f"Pre-fetching GL entries for all periods...")
        
        # Current year GL entries
        current_gl_entries = get_gl_entries_for_period(
            company, from_date, to_date,
            {'cost_center': selected_cost_center} if selected_cost_center else None
        )
        
        # Previous year GL entries
        prev_gl_entries = get_gl_entries_for_period(
            company, prev_from_date, prev_to_date,
            {'cost_center': selected_cost_center} if selected_cost_center else None
        )
        
        # YTD GL entries
        ytd_gl_entries = get_gl_entries_for_period(
            company, from_date, ytd_end_date,
            {'cost_center': selected_cost_center} if selected_cost_center else None
        )
        
        # YTD last year GL entries
        ytd_last_year_from_date = prev_from_date
        ytd_last_year_to_date = add_years(ytd_end_date, -1) if selected_month and selected_month.strip() else prev_to_date
        ytd_last_year_gl_entries = get_gl_entries_for_period(
            company, ytd_last_year_from_date, ytd_last_year_to_date,
            {'cost_center': selected_cost_center} if selected_cost_center else None
        )
        
        # Current month GL entries
        current_month_gl_entries = []
        current_month_last_year_gl_entries = []
        if selected_month and selected_month.strip() and current_month_from_date and current_month_to_date:
            current_month_gl_entries = get_gl_entries_for_period(
                company, current_month_from_date, current_month_to_date,
                {'cost_center': selected_cost_center} if selected_cost_center else None
            )
            
            current_month_last_year_from_date = add_years(current_month_from_date, -1)
            current_month_last_year_to_date = add_years(current_month_to_date, -1)
            current_month_last_year_gl_entries = get_gl_entries_for_period(
                company, current_month_last_year_from_date, current_month_last_year_to_date,
                {'cost_center': selected_cost_center} if selected_cost_center else None
            )
        
        print(f"DEBUG: Pre-fetched GL entries:")
        print(f"  - Current year: {len(current_gl_entries)}")
        print(f"  - Previous year: {len(prev_gl_entries)}")
        print(f"  - YTD: {len(ytd_gl_entries)}")
        print(f"  - YTD last year: {len(ytd_last_year_gl_entries)}")
        print(f"  - Current month: {len(current_month_gl_entries)}")
        print(f"  - Current month last year: {len(current_month_last_year_gl_entries)}")
        
        # STEP 3: Organize accounts using hierarchy approach (like ERPNext)
        print(f"Starting account hierarchy organization...")
        try:
            # Get Income accounts with hierarchy
            income_accounts = [acc for acc in all_accounts if acc.get('root_type') == 'Income']
            expense_accounts = [acc for acc in all_accounts if acc.get('root_type') == 'Expense']
            
            income_hierarchy, income_by_name, income_parent_map = get_accounts_with_hierarchy(income_accounts, current_gl_entries)
            expense_hierarchy, expense_by_name, expense_parent_map = get_accounts_with_hierarchy(expense_accounts, current_gl_entries)
            
            print(f"Hierarchy organization completed. Income: {len(income_hierarchy)} accounts, Expense: {len(expense_hierarchy)} accounts")
        except Exception as e:
            print(f"ERROR in account hierarchy organization: {str(e)}")
            return {'dashboard_data': [], 'filters': filters}
        
        # Build structured dashboard data using hierarchy
        structured_dashboard_data = []
        
        # Process Income accounts using dynamic clusters (by first-3-digit family)
        print("Processing Income accounts...")
        income_clusters = build_income_clusters(income_hierarchy, income_accounts)
        print(f"Built {len(income_clusters)} income clusters")
        
        # Debug: Print sample account data
        print("Sample income accounts:")
        for i, acc in enumerate(income_accounts[:5]):
            print(f"  {i+1}. {acc.get('name', 'N/A')} - {acc.get('account_number', 'N/A')} - {acc.get('account_name', 'N/A')}")
        
        print("Sample expense accounts:")
        for i, acc in enumerate(expense_accounts[:5]):
            print(f"  {i+1}. {acc.get('name', 'N/A')} - {acc.get('account_number', 'N/A')} - {acc.get('account_name', 'N/A')}")
        
        for cluster in income_clusters:
            label = cluster['label']
            print(f"Processing income cluster: {label} with {len(cluster['accounts'])} accounts")
            structured_dashboard_data.append({
                'type': 'header',
                'category': label,
                'account': f'HEADER_{label}',
                'root_type': 'Income',
                'is_group': True,
                'indent': 0
            })
            for account in cluster['accounts']:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], []  # budgets not implemented yet
                )
                if account_row:
                    account_row['indent'] = 1
                    structured_dashboard_data.append(account_row)
        
        # Add Income total
        if income_hierarchy:
            income_total = calculate_section_total(income_hierarchy, 'TOTAL INCOME', 'Income')
            if income_total:
                structured_dashboard_data.append(income_total)
        
        # Process Expense accounts
        print("Processing Expense accounts...")
        for account in expense_hierarchy:
            if account.get('is_group'):
                # This is a group account - create header
                structured_dashboard_data.append({
                    'type': 'header', 
                    'category': account.get('account_name', account['name']),
                    'account': account['name'],
                    'root_type': 'Expense',
                    'is_group': True,
                    'indent': account.get('indent', 0)
                })
            else:
                # This is a leaf account - process it
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], []  # Empty arrays for budget entries (not implemented yet)
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 0)
                    structured_dashboard_data.append(account_row)
        
        # Add Expense total
        if expense_hierarchy:
            expense_total = calculate_section_total(expense_hierarchy, 'TOTAL EXPENSE', 'Expense')
            if expense_total:
                structured_dashboard_data.append(expense_total)
        
        print(f"Dashboard data structure completed with {len(structured_dashboard_data)} rows")
        
        # Debug: Print sample of final structured data
        print("Sample structured dashboard data:")
        for i, row in enumerate(structured_dashboard_data[:10]):
            print(f"  {i+1}. Type: {row.get('type', 'N/A')}, Category: {row.get('category', 'N/A')}, Root Type: {row.get('root_type', 'N/A')}")
            if row.get('type') == 'account':
                print(f"     Account: {row.get('account', 'N/A')}, Indent: {row.get('indent', 'N/A')}")
        
        return {
            'dashboard_data': structured_dashboard_data,
            'filters': filters
        }
        
    except Exception as e:
        print(f"=== API EXCEPTION ===")
        print(f"Error: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        frappe.log_error(f"Error in get_dashboard_data: {str(e)}", "Dashboard API Error")
        return {
            'dashboard_data': [],
            'filters': filters
        }

@frappe.whitelist()
def get_companies():
    """Get list of companies for filter dropdown"""
    try:
        companies = frappe.db.sql("""
            SELECT DISTINCT company FROM `tabCompany`
            WHERE disabled = 0
            ORDER BY company
        """, as_dict=1)
        
        return [company['company'] for company in companies]
    except Exception as e:
        frappe.log_error(f"Error getting companies: {str(e)}")
        return []

@frappe.whitelist()
def get_fiscal_years():
    """Get list of fiscal years for filter dropdown"""
    try:
        fiscal_years = frappe.db.sql("""
            SELECT name FROM `tabFiscal Year`
            WHERE disabled = 0
            ORDER BY year_start_date DESC
        """, as_dict=1)
        
        return [fy['name'] for fy in fiscal_years]
    except Exception as e:
        frappe.log_error(f"Error getting fiscal years: {str(e)}")
        return []

@frappe.whitelist()
def get_cost_centers():
    """Get list of cost centers for filter dropdown"""
    try:
        cost_centers = frappe.db.sql("""
            SELECT name FROM `tabCost Center`
            WHERE is_group = 0 AND disabled = 0
            ORDER BY name
        """, as_dict=1)
        
        return [cc['name'] for cc in cost_centers]
    except Exception as e:
        frappe.log_error(f"Error getting cost centers: {str(e)}")
        return []

@frappe.whitelist()
def get_expense_accounts():
    """Get list of expense accounts for filter dropdown"""
    try:
        accounts = frappe.db.sql("""
            SELECT name, account_name FROM `tabAccount`
            WHERE root_type = 'Expense' AND is_group = 0 AND disabled = 0
            ORDER BY account_name
        """, as_dict=1)
        
        return [{'name': acc['name'], 'account_name': acc['account_name']} for acc in accounts]
    except Exception as e:
        frappe.log_error(f"Error getting expense accounts: {str(e)}")
        return []

@frappe.whitelist()
def get_report_classes_api():
    """Get all available report classes for the frontend"""
    try:
        report_classes = get_report_classes()
        return {
            'success': True,
            'report_classes': report_classes
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@frappe.whitelist()
def get_summary_data(filters=None):
    """Get summary data for the dashboard"""
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    # Get dashboard data first
    dashboard_data = get_dashboard_data(filters)
    
    # Calculate summary - only include account rows, exclude headers, sub-headers, and totals to avoid double counting
    dashboard_items = dashboard_data.get('dashboard_data', [])
    total_budget = sum(row.get('yearToDate', {}).get('budget', 0) for row in dashboard_items if row.get('type') == 'account')
    total_actual = sum(row.get('yearToDate', {}).get('actual', 0) for row in dashboard_items if row.get('type') == 'account')
    total_variance = total_budget - total_actual
    
    return {
        'summary': {
            'total_budget': total_budget,
            'total_actual': total_actual,
            'total_variance': total_variance,
            'variance_percentage': safe_ratio(total_variance, total_budget, 0)
        },
        'filters': filters
    }

@frappe.whitelist()
def get_gl_entries_with_report_class_api(filters=None):
    """Get GL entries with their report classes for frontend consumption"""
    if filters is None:
        filters = {}
    
    try:
        from_date = filters.get('from_date')
        to_date = filters.get('to_date')
        selected_cost_center = filters.get('cost_center')
        
        if not from_date or not to_date:
            return {
                'success': False,
                'error': 'from_date and to_date are required'
            }
        
        gl_entries = get_gl_entries_for_period(
            filters.get('company', 'Western Serene Atlantic Hotel Ltd'),
            from_date, to_date,
            {'cost_center': selected_cost_center} if selected_cost_center else None
        )
        
        return {
            'success': True,
            'gl_entries': gl_entries,
            'total_entries': len(gl_entries)
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }