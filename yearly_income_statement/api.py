import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day
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

# Display order for categories
DISPLAY_ORDER = [
	'REVENUE',
	'COST_OF_SALES', 
	'SALARIES_WAGES',
	'PAYROLL_BURDEN',
	'OTHER_EXPENSES',
	'ASSETS',
	'LIABILITIES',
	'EQUITY'
]

# Dynamic category mapping strategies
CATEGORY_STRATEGIES = {
    'REVENUE': {
        'root_type': 'Income',
        'account_type_patterns': ['Income Account', 'Direct Income'],
        'name_patterns': ['Revenue', 'Income', 'Sales'],
        'parent_account_patterns': ['Revenue', 'Income', 'Sales'],
        'sub_categories': {
            'FOOD': {
                'name_patterns': ['Food', 'Restaurant', 'Dining'],
                'account_type_patterns': ['Income Account'],
                'parent_patterns': ['Food', 'Restaurant']
            },
            'BEVERAGE': {
                'name_patterns': ['Beverage', 'Drink', 'Corkage', 'Bar'],
                'account_type_patterns': ['Income Account'],
                'parent_patterns': ['Beverage', 'Drink']
            }
        }
    },
    'COST_OF_SALES': {
        'root_type': 'Expense',
        'account_type_patterns': ['Direct Expense', 'Cost of Goods Sold'],
        'name_patterns': ['Cost of', 'Direct Cost', 'COGS'],
        'parent_account_patterns': ['Cost of Sales', 'Direct Expenses'],
        'sub_categories': {
            'Food': {
                'name_patterns': ['Food Cost', 'Cost of Food', 'Direct Food'],
                'account_type_patterns': ['Direct Expense'],
                'parent_patterns': ['Food Cost', 'Cost of Food']
            },
            'Beverage': {
                'name_patterns': ['Beverage Cost', 'Cost of Beverage', 'Direct Beverage'],
                'account_type_patterns': ['Direct Expense'],
                'parent_patterns': ['Beverage Cost', 'Cost of Beverage']
            }
        }
    },
    'SALARIES_WAGES': {
        'root_type': 'Expense',
        'account_type_patterns': ['Expense Account', 'Indirect Expense'],
        'name_patterns': ['Salaries', 'Wages', 'Payroll', 'Basic', 'Overtime', 'Casuals', 'Severance', 'Vacation', 'Bonus', 'Incentive'],
        'parent_account_patterns': ['Salaries', 'Wages', 'Payroll'],
        'sub_categories': {
            'SALARIES': {
                'name_patterns': ['Salaries', 'Wages', 'Basic', 'Overtime', 'Casuals'],
                'account_type_patterns': ['Expense Account'],
                'parent_patterns': ['Salaries', 'Wages']
            }
        }
    },
    'PAYROLL_BURDEN': {
        'root_type': 'Expense',
        'account_type_patterns': ['Expense Account', 'Indirect Expense'],
        'name_patterns': ['Staff Housing', 'Provident Fund', 'Social Security', 'Sick', 'Holiday', 'Night Allowance', 'Burden'],
        'parent_account_patterns': ['Payroll Burden', 'Employee Benefits'],
        'sub_categories': {
            'BURDEN': {
                'name_patterns': ['Staff Housing', 'Provident Fund', 'Social Security', 'Sick', 'Holiday', 'Night Allowance'],
                'account_type_patterns': ['Expense Account'],
                'parent_patterns': ['Payroll Burden', 'Employee Benefits']
            }
        }
    },
    'OTHER_EXPENSES': {
        'root_type': 'Expense',
        'account_type_patterns': ['Expense Account', 'Indirect Expense'],
        'name_patterns': ['Expense', 'Cost', 'Charge', 'Fee'],
        'parent_account_patterns': ['Other Expenses', 'Operating Expenses'],
        'exclude_patterns': ['Salaries', 'Wages', 'Payroll', 'Food Cost', 'Beverage Cost', 'Cost of Food', 'Cost of Beverage'],
        'sub_categories': {
            'OTHER': {
                'name_patterns': ['Sales Promoters', 'Advertising', 'Gifts', 'Samples', 'Marketing', 'Management Fees', 'Miscellaneous', 'Uniforms', 'Laundry', 'Guest Supplies', 'Decoration', 'Music', 'Entertainment', 'Internet', 'Telephone', 'Consultants', 'Licenses', 'Cleaning', 'Credit Card', 'Priority Club', 'Business Rates', 'Commissions', 'Rent', 'Insurance', 'Security', 'Audit', 'Accountancy', 'Computer', 'Maintenance', 'Energy', 'Legal', 'Depreciation', 'Bank Charges', 'Loan Interest', 'Recruitment', 'Medical'],
                'account_type_patterns': ['Expense Account', 'Indirect Expense'],
                'parent_patterns': ['Other Expenses', 'Operating Expenses']
            }
        }
    }
}

# Display order for the financial report
DISPLAY_ORDER = [
    'REVENUE',
    'COST_OF_SALES', 
    'SALARIES_WAGES',
    'PAYROLL_BURDEN',
    'OTHER_EXPENSES'
]

# Row types for frontend rendering
ROW_TYPES = {
    'HEADER': 'header',
    'SUB_HEADER': 'sub_header', 
    'ACCOUNT': 'account',
    'TOTAL': 'total',
    'SUMMARY': 'summary'
}


@frappe.whitelist()
def get_budget_data(filters=None):
	"""
	Get budget data for the dashboard
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	
	# Get budget data
	budget_data = frappe.db.sql("""
		SELECT 
			ba.account,
			ba.budget_amount,
			b.fiscal_year,
			b.cost_center,
			b.company
		FROM `tabBudget Account` ba
		INNER JOIN `tabBudget` b ON ba.parent = b.name
		WHERE b.company = %s 
		AND b.fiscal_year = %s
		AND b.docstatus = 1
	""", (company, fiscal_year), as_dict=1)
	
	# Filter by cost center if specified
	if cost_center:
		budget_data = [b for b in budget_data if b.get('cost_center') == cost_center]
	
	return {
		'budget_data': budget_data,
		'filters': filters
	}


@frappe.whitelist()
def get_actual_data(filters=None):
	"""
	Get actual data from GL Entry for the dashboard
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	from_date = filters.get('from_date')
	to_date = filters.get('to_date')
	
	# Get fiscal year dates if not provided
	if not from_date or not to_date:
		fy = frappe.get_doc("Fiscal Year", fiscal_year)
		from_date = fy.year_start_date
		to_date = fy.year_end_date
	
	# Build conditions
	conditions = [
		"gle.company = %s",
		"gle.posting_date BETWEEN %s AND %s",
		"gle.docstatus = 1"
	]
	
	params = [company, from_date, to_date]
	
	if cost_center:
		conditions.append("gle.cost_center = %s")
		params.append(cost_center)
	
	# Get actual data
	actual_data = frappe.db.sql("""
		SELECT 
			gle.account,
			gle.cost_center,
			SUM(gle.debit) as actual_debit,
			SUM(gle.credit) as actual_credit,
			SUM(gle.debit - gle.credit) as net_amount
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON gle.account = acc.name
		WHERE """ + " AND ".join(conditions) + """
		AND acc.root_type = 'Expense'
		GROUP BY gle.account, gle.cost_center
	""", params, as_dict=1)
	
	return {
		'actual_data': actual_data,
		'filters': filters
	}


@frappe.whitelist()
def get_forecast_data(filters=None):
	"""
	Get forecast data (can be calculated or from custom doctype)
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	
	# For now, return empty forecast data
	# This can be extended to fetch from custom forecast doctype
	forecast_data = []
	
	return {
		'forecast_data': forecast_data,
		'filters': filters
	}


def categorize_account(account_data):
    """
    Dynamically categorize an account using multiple strategies:
    1. Root type matching
    2. Account type matching  
    3. Name pattern matching
    4. Parent account hierarchy matching
    5. Cost center association
    
    Returns: (category, sub_category) or (None, None) if no match found
    """
    account_name = account_data.get('account_name', '').lower()
    account_code = account_data.get('name', '').lower()
    root_type = account_data.get('root_type', '')
    account_type = account_data.get('account_type', '')
    parent_account = account_data.get('parent_account', '').lower()
    
    # Contingency 1: Handle missing or invalid account data
    if not account_name and not account_code:
        return None, None
    
    # Contingency 2: Try to get missing root_type from database
    if not root_type:
        try:
            account_doc = frappe.get_doc("Account", account_data.get('name', ''))
            root_type = account_doc.root_type
        except Exception as e:
            # Fallback: Try to infer root_type from account name
            if any(word in account_name for word in ['revenue', 'income', 'sales', 'receipt']):
                root_type = 'Income'
            elif any(word in account_name for word in ['expense', 'cost', 'payment', 'charge']):
                root_type = 'Expense'
            else:
                root_type = 'Expense'  # Default fallback
    
    # Get parent account details if available
    parent_account_name = ''
    if parent_account:
        try:
            parent_doc = frappe.get_doc("Account", parent_account)
            parent_account_name = parent_doc.account_name.lower()
        except Exception as e:
            pass
    
    # Strategy 1: Check each category's criteria
    for category, strategy in CATEGORY_STRATEGIES.items():
        # Check root type first
        if strategy.get('root_type') and strategy['root_type'] != root_type:
            continue
            
        # Check account type patterns
        if 'account_type_patterns' in strategy:
            account_type_match = any(pattern.lower() in account_type.lower() 
                                   for pattern in strategy['account_type_patterns'])
            if not account_type_match:
                continue
        
        # Check name patterns
        name_match = False
        if 'name_patterns' in strategy:
            name_match = any(pattern.lower() in account_name or pattern.lower() in account_code
                           for pattern in strategy['name_patterns'])
        
        # Check parent account patterns
        parent_match = False
        if 'parent_account_patterns' in strategy:
            parent_match = any(pattern.lower() in parent_account_name
                             for pattern in strategy['parent_account_patterns'])
        
        # Check exclude patterns (for OTHER_EXPENSES)
        if 'exclude_patterns' in strategy:
            excluded = any(pattern.lower() in account_name or pattern.lower() in account_code
                          for pattern in strategy['exclude_patterns'])
            if excluded:
                continue
        
        # If we have a match, find the sub-category
        if name_match or parent_match:
            # Find the best matching sub-category
            best_sub_category = None
            best_score = 0
            
            for sub_category, sub_strategy in strategy.get('sub_categories', {}).items():
                score = 0
                
                # Check sub-category name patterns
                if 'name_patterns' in sub_strategy:
                    for pattern in sub_strategy['name_patterns']:
                        if pattern.lower() in account_name or pattern.lower() in account_code:
                            score += 2  # Higher weight for direct name match
                
                # Check sub-category account type patterns
                if 'account_type_patterns' in sub_strategy:
                    for pattern in sub_strategy['account_type_patterns']:
                        if pattern.lower() in account_type.lower():
                            score += 1
                
                # Check sub-category parent patterns
                if 'parent_patterns' in sub_strategy:
                    for pattern in sub_strategy['parent_patterns']:
                        if pattern.lower() in parent_account_name:
                            score += 1
                
                if score > best_score:
                    best_score = score
                    best_sub_category = sub_category
            
            # If no specific sub-category found, use the first one or create a default
            if not best_sub_category and strategy.get('sub_categories'):
                best_sub_category = list(strategy['sub_categories'].keys())[0]
            
            return category, best_sub_category
    
    # Strategy 2: Fallback to root_type based categorization
    if root_type == 'Income':
        return 'REVENUE', 'OTHER'
    elif root_type == 'Expense':
        # Try to categorize expense accounts more specifically
        if any(word in account_name for word in ['salary', 'wage', 'payroll', 'basic', 'overtime']):
            return 'SALARIES_WAGES', 'SALARIES'
        elif any(word in account_name for word in ['housing', 'provident', 'social', 'sick', 'holiday']):
            return 'PAYROLL_BURDEN', 'BURDEN'
        elif any(word in account_name for word in ['food', 'beverage', 'cost of']):
            if any(word in account_name for word in ['beverage', 'drink']):
                return 'COST_OF_SALES', 'Beverage'
            else:
                return 'COST_OF_SALES', 'Food'
        else:
            return 'OTHER_EXPENSES', 'OTHER'
    elif root_type == 'Asset':
        return 'ASSETS', 'CURRENT_ASSETS'
    elif root_type == 'Liability':
        return 'LIABILITIES', 'CURRENT_LIABILITIES'
    elif root_type == 'Equity':
        return 'EQUITY', 'SHAREHOLDER_EQUITY'
    
    # Contingency 3: If root_type is still unknown, try name-based inference
    
    # Try to infer from account name patterns
    if any(word in account_name for word in ['revenue', 'income', 'sales', 'receipt', 'earnings']):
        return 'REVENUE', 'OTHER'
    elif any(word in account_name for word in ['salary', 'wage', 'payroll', 'employee', 'staff']):
        return 'SALARIES_WAGES', 'SALARIES'
    elif any(word in account_name for word in ['food', 'beverage', 'kitchen', 'restaurant']):
        if any(word in account_name for word in ['beverage', 'drink', 'bar']):
            return 'COST_OF_SALES', 'Beverage'
        else:
            return 'COST_OF_SALES', 'Food'
    elif any(word in account_name for word in ['expense', 'cost', 'charge', 'fee', 'payment']):
        return 'OTHER_EXPENSES', 'OTHER'
    elif any(word in account_name for word in ['asset', 'cash', 'bank', 'inventory', 'equipment']):
        return 'ASSETS', 'CURRENT_ASSETS'
    elif any(word in account_name for word in ['liability', 'payable', 'loan', 'debt']):
        return 'LIABILITIES', 'CURRENT_LIABILITIES'
    elif any(word in account_name for word in ['equity', 'capital', 'retained', 'share']):
        return 'EQUITY', 'SHAREHOLDER_EQUITY'
    
    # Final contingency: Default to OTHER_EXPENSES for unknown accounts
    return 'OTHER_EXPENSES', 'OTHER'

def get_accounts_by_category(accounts_with_data):
    """
    Group accounts by their dynamic categories using multiple matching strategies
    """
    categorized_accounts = {}
    
    for account in accounts_with_data:
        # Get additional account data for better categorization
        account_data = {
            'name': account['name'],
            'account_name': account['account_name'],
            'root_type': account['root_type']
        }
        
        # Try to get additional account details from the database
        try:
            account_doc = frappe.get_doc("Account", account['name'])
            account_data.update({
                'account_type': account_doc.account_type,
                'parent_account': account_doc.parent_account
            })
        except Exception as e:
            # Ensure we have at least basic data
            if not account_data.get('root_type'):
                account_data['root_type'] = 'Expense'  # Default fallback
            pass
        
        # First, try basic categorization
        category, sub_category = categorize_account(account_data)
        
        # Enhance categorization with cost center associations
        cost_centers = get_cost_center_associations(account['name'])
        enhanced_category, enhanced_sub_category = enhance_categorization_with_cost_center(
            {'category': category, 'sub_category': sub_category, **account_data}, 
            cost_centers
        )
        
        # Use enhanced categorization if available, otherwise fall back to basic
        category = enhanced_category or category
        sub_category = enhanced_sub_category or sub_category
        
        if category:
            if category not in categorized_accounts:
                categorized_accounts[category] = {}
            
            if sub_category:
                if sub_category not in categorized_accounts[category]:
                    categorized_accounts[category][sub_category] = []
                categorized_accounts[category][sub_category].append(account)
            else:
                # If no sub-category found, use the first available one or create a default
                if categorized_accounts[category]:
                    first_sub_category = list(categorized_accounts[category].keys())[0]
                    categorized_accounts[category][first_sub_category].append(account)
                else:
                    # Create a default sub-category
                    default_sub = 'OTHER'
                    if default_sub not in categorized_accounts[category]:
                        categorized_accounts[category][default_sub] = []
                    categorized_accounts[category][default_sub].append(account)
        else:
            # Contingency: Accounts that don't match any custom category
            
            # Try to create a sensible category based on root_type
            fallback_category = 'OTHER_EXPENSES'  # Default
            fallback_sub_category = 'OTHER'
            
            if account_data.get('root_type') == 'Income':
                fallback_category = 'REVENUE'
                fallback_sub_category = 'OTHER'
            elif account_data.get('root_type') == 'Asset':
                fallback_category = 'ASSETS'
                fallback_sub_category = 'CURRENT_ASSETS'
            elif account_data.get('root_type') == 'Liability':
                fallback_category = 'LIABILITIES'
                fallback_sub_category = 'CURRENT_LIABILITIES'
            elif account_data.get('root_type') == 'Equity':
                fallback_category = 'EQUITY'
                fallback_sub_category = 'SHAREHOLDER_EQUITY'
            
            # Add to the fallback category
            if fallback_category not in categorized_accounts:
                categorized_accounts[fallback_category] = {}
            if fallback_sub_category not in categorized_accounts[fallback_category]:
                categorized_accounts[fallback_category][fallback_sub_category] = []
            categorized_accounts[fallback_category][fallback_sub_category].append(account)
    
    return categorized_accounts

def validate_categorization_results(categorized_accounts):
    """
    Validate and report categorization results for debugging
    """
    return categorized_accounts

def create_header_row(category):
    """
    Create a header row for a main category
    """
    return {
        'type': ROW_TYPES['HEADER'],
        'category': category.replace('_', ' ').title()
    }

def create_sub_header_row(sub_category):
    """
    Create a sub-header row for a sub-category
    """
    return {
        'type': ROW_TYPES['SUB_HEADER'],
        'category': sub_category
    }

def create_total_row(category, totals_data):
    """
    Create a total row for a category
    """
    return {
        'type': ROW_TYPES['TOTAL'],
        'category': f"TOTAL {category.replace('_', ' ').title()}",
        'currentMonth': totals_data.get('currentMonth', {}),
        'yearToDate': totals_data.get('yearToDate', {}),
        'forecast': totals_data.get('forecast', {})
    }

def get_cost_center_associations(account_code):
    """
    Get cost centers associated with an account through GL entries
    This can help with categorization if accounts are typically used with specific cost centers
    """
    try:
        cost_centers = frappe.db.sql("""
            SELECT DISTINCT cost_center 
            FROM `tabGL Entry` 
            WHERE account = %s 
            AND cost_center IS NOT NULL 
            AND cost_center != ''
            ORDER BY cost_center
            LIMIT 5
        """, (account_code,), as_dict=1)
        
        return [cc['cost_center'] for cc in cost_centers]
    except:
        return []

def enhance_categorization_with_cost_center(account_data, cost_centers):
    """
    Enhance categorization based on cost center associations
    """
    if not cost_centers:
        return account_data.get('category'), account_data.get('sub_category')
    
    # Check if cost centers suggest a different categorization
    cost_center_names = ' '.join(cost_centers).lower()
    
    # Example: If cost centers contain 'kitchen' or 'food', it might be food-related
    if any(word in cost_center_names for word in ['kitchen', 'food', 'restaurant']):
        if account_data.get('root_type') == 'Income':
            return 'REVENUE', 'FOOD'
        elif account_data.get('root_type') == 'Expense':
            return 'COST_OF_SALES', 'Food'
    
    # If cost centers contain 'bar' or 'beverage', it might be beverage-related
    elif any(word in cost_center_names for word in ['bar', 'beverage', 'drink']):
        if account_data.get('root_type') == 'Income':
            return 'REVENUE', 'BEVERAGE'
        elif account_data.get('root_type') == 'Expense':
            return 'COST_OF_SALES', 'Beverage'
    
    # If cost centers contain 'staff' or 'employee', it might be payroll-related
    elif any(word in cost_center_names for word in ['staff', 'employee', 'personnel']):
        if account_data.get('root_type') == 'Expense':
            if any(word in account_data.get('account_name', '').lower() for word in ['housing', 'benefit', 'social']):
                return 'PAYROLL_BURDEN', 'BURDEN'
            else:
                return 'SALARIES_WAGES', 'SALARIES'
    
    return account_data.get('category'), account_data.get('sub_category')

@frappe.whitelist()
def test_categorization(filters=None):
    """
    Test function to validate the categorization system
    """
    if isinstance(filters, str):
        filters = json.loads(filters)
    
    if not filters:
        filters = {}
    
    try:
        # Get sample accounts for testing
        test_accounts = frappe.db.sql("""
            SELECT DISTINCT acc.name, acc.account_name, acc.root_type, acc.account_type, acc.parent_account
            FROM `tabAccount` acc
            WHERE acc.root_type IN ('Income', 'Expense') AND acc.is_group = 0 AND acc.disabled = 0
            ORDER BY acc.root_type DESC, acc.account_name
            LIMIT 50
        """, as_dict=1)
        
        # Test individual account categorization
        for account in test_accounts[:10]:  # Test first 10 accounts
            account_data = {
                'name': account['name'],
                'account_name': account['account_name'],
                'root_type': account['root_type'],
                'account_type': account['account_type'],
                'parent_account': account['parent_account']
            }
            
            category, sub_category = categorize_account(account_data)
        
        # Test full categorization process
        categorized_accounts = get_accounts_by_category(test_accounts)
        validate_categorization_results(categorized_accounts)
        
        # Test with specific account patterns
        test_patterns = [
            {'name': 'Food Revenue - Restaurant', 'account_name': 'Food Revenue - Restaurant', 'root_type': 'Income'},
            {'name': 'Beverage Revenue - Bar', 'account_name': 'Beverage Revenue - Bar', 'root_type': 'Income'},
            {'name': 'Cost of Food', 'account_name': 'Cost of Food', 'root_type': 'Expense'},
            {'name': 'Salaries - Basic', 'account_name': 'Salaries - Basic', 'root_type': 'Expense'},
            {'name': 'Staff Housing', 'account_name': 'Staff Housing', 'root_type': 'Expense'},
            {'name': 'Advertising', 'account_name': 'Advertising', 'root_type': 'Expense'},
            {'name': 'Unknown Account', 'account_name': 'Unknown Account', 'root_type': ''},  # Test missing root_type
        ]
        
        for pattern in test_patterns:
            category, sub_category = categorize_account(pattern)
        
        return {
            'success': True,
            'message': 'Categorization test completed successfully',
            'test_accounts_count': len(test_accounts),
            'categorized_accounts': categorized_accounts
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@frappe.whitelist()
def get_dashboard_data(filters=None):
	"""
	Get structured dashboard data with hierarchical categorization
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	if not filters:
		filters = {}
	
	try:
		# Get default fiscal year (most recent)
		fiscal_year = filters.get('fiscal_year')
		selected_month = filters.get('month')
		selected_cost_center = filters.get('cost_center')
		
		if not fiscal_year:
			latest_fy = frappe.db.sql("""
				SELECT DISTINCT fiscal_year FROM `tabBudget`
				WHERE docstatus = 1
				ORDER BY fiscal_year DESC
				LIMIT 1
			""", as_dict=1)
			fiscal_year = latest_fy[0]['fiscal_year'] if latest_fy else '2023'
		
		fy_doc = frappe.get_doc("Fiscal Year", fiscal_year)
		from_date = fy_doc.year_start_date
		to_date = fy_doc.year_end_date
		
		# Get previous fiscal year
		prev_fiscal_year = get_previous_fiscal_year(fiscal_year)
		prev_fy_doc = frappe.get_doc("Fiscal Year", prev_fiscal_year)
		prev_from_date = prev_fy_doc.year_start_date
		prev_to_date = prev_fy_doc.year_end_date
		
		# Calculate current month date range if month is selected
		current_month_from_date = None
		current_month_to_date = None
		if selected_month and selected_month.strip():
			month_num = int(selected_month)
			year_num = int(fiscal_year)
			from frappe.utils import get_first_day, get_last_day
			current_month_from_date = get_first_day(f"{year_num}-{month_num:02d}-01")
			current_month_to_date = get_last_day(f"{year_num}-{month_num:02d}-01")
		
		# Simplified, robust YTD logic:
		from frappe.utils import getdate, today
		today_date = getdate(today())
		fy_start = getdate(fy_doc.year_start_date)
		fy_end = getdate(fy_doc.year_end_date)
		
		if fy_start <= today_date <= fy_end:
			ytd_end_date = today_date
		elif today_date > fy_end:
			ytd_end_date = fy_end
		else:
			ytd_end_date = fy_start
		
		# Get ALL accounts with actual data (both income and expense) - no limits
		cost_center_condition = ""
		cost_center_params = []
		if selected_cost_center and selected_cost_center.strip():
			cost_center_condition = "AND gle.cost_center = %s"
			cost_center_params = [selected_cost_center]
		
		budget_cost_center_condition = ""
		budget_cost_center_params = []
		if selected_cost_center and selected_cost_center.strip():
			budget_cost_center_condition = "AND b.cost_center = %s"
			budget_cost_center_params = [selected_cost_center]
		
		accounts_with_data = frappe.db.sql("""
			SELECT DISTINCT acc.name, acc.account_name, acc.root_type
			FROM `tabAccount` acc
			WHERE acc.root_type IN ('Income', 'Expense') AND acc.is_group = 0 AND acc.disabled = 0
			AND (
				acc.name IN (
					SELECT DISTINCT account 
					FROM `tabGL Entry` gle
					WHERE gle.posting_date BETWEEN %s AND %s
					AND gle.is_cancelled = 0
					""" + cost_center_condition + """
				)
				OR acc.name IN (
					SELECT DISTINCT ba.account
					FROM `tabBudget Account` ba
					INNER JOIN `tabBudget` b ON ba.parent = b.name
					WHERE b.fiscal_year = %s
					""" + budget_cost_center_condition + """
				)
			)
			ORDER BY acc.root_type DESC, acc.account_name
		""", [from_date, to_date] + cost_center_params + [fiscal_year] + budget_cost_center_params, as_dict=1)
		

		
		# Categorize accounts using our dynamic categorization system
		categorized_accounts = get_accounts_by_category(accounts_with_data)
		validate_categorization_results(categorized_accounts)
		
		# Build structured dashboard data
		structured_dashboard_data = []
		
		# Process each category in display order
		for category in DISPLAY_ORDER:
			if category not in categorized_accounts:
				continue
			
			# Add header row for main category
			structured_dashboard_data.append(create_header_row(category))
			
			# Process sub-categories
			for sub_category, accounts in categorized_accounts[category].items():
				# Add sub-header row
				structured_dashboard_data.append(create_sub_header_row(sub_category))
				
				# Process individual accounts
				for account in accounts:
					account_name = account['account_name']
					account_code = account['name']
					account_type = account['root_type']
					

					
					# Get financial data for this account (reuse existing logic)
					account_data = get_account_financial_data(
						account_code, account_type, fiscal_year, prev_fiscal_year,
						from_date, to_date, prev_from_date, prev_to_date,
						ytd_end_date, current_month_from_date, current_month_to_date,
						selected_cost_center, selected_month
					)
					
					# Create account row with type
					account_row = {
						'type': ROW_TYPES['ACCOUNT'],
						'category': account_name,
						'account': account_code,
						'root_type': account_type,
						'currentMonth': account_data['currentMonth'],
						'yearToDate': account_data['yearToDate'],
						'forecast': account_data['forecast']
					}
					
					structured_dashboard_data.append(account_row)
				
				# Calculate and add sub-category total
				sub_category_totals = calculate_category_totals(accounts, fiscal_year, prev_fiscal_year,
					from_date, to_date, prev_from_date, prev_to_date, ytd_end_date,
					current_month_from_date, current_month_to_date, selected_cost_center, selected_month)
				
				total_row = create_total_row(f"{category}_{sub_category}", sub_category_totals)
				structured_dashboard_data.append(total_row)
			
			# Calculate and add main category total
			all_category_accounts = []
			for sub_accounts in categorized_accounts[category].values():
				all_category_accounts.extend(sub_accounts)
			
			category_totals = calculate_category_totals(all_category_accounts, fiscal_year, prev_fiscal_year,
				from_date, to_date, prev_from_date, prev_to_date, ytd_end_date,
				current_month_from_date, current_month_to_date, selected_cost_center, selected_month)
			
			total_row = create_total_row(category, category_totals)
			structured_dashboard_data.append(total_row)
		
		# Add summary rows (Gross Profit, Net Profit/Loss)
		summary_rows = calculate_summary_rows(structured_dashboard_data)
		structured_dashboard_data.extend(summary_rows)
		

		
		return {
			'dashboard_data': structured_dashboard_data,
			'filters': filters
		}
		
	except Exception as e:
		frappe.log_error(f"Error in get_dashboard_data: {str(e)}", "Dashboard API Error")
		return {
			'dashboard_data': [],
			'filters': filters
		}


def process_dashboard_data(budget_data, actual_data, forecast_data, filters):
	"""
	Process and combine budget, actual, and forecast data
	"""
	# Create lookup dictionaries
	budget_lookup = {}
	for item in budget_data:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		budget_lookup[key] = flt(item.get('budget_amount', 0))
	
	actual_lookup = {}
	for item in actual_data:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		actual_lookup[key] = flt(item.get('net_amount', 0))
	
	# Get unique accounts and cost centers
	all_accounts = set()
	for item in budget_data + actual_data:
		all_accounts.add(item.get('account'))
	
	# Build dashboard data
	dashboard_data = []
	
	for account in all_accounts:
		account_doc = frappe.get_doc("Account", account)
		
		row = {
			'account': account,
			'account_name': account_doc.account_name,
			'cost_center': '',
			'last_year_budget': 0,
			'last_year_actual': 0,
			'last_year_act_bud': 0,
			'this_year_budget': 0,
			'this_year_actual': 0,
			'this_year_act_bud': 0,
			'ytd_budget': 0,
			'ytd_actual': 0,
			'ytd_act_bud': 0,
			'forecast_budget': 0,
			'forecast_actual': 0,
			'forecast_act_bud': 0
		}
		
		# Calculate values for each cost center
		cost_centers = set()
		for item in budget_data + actual_data:
			if item.get('account') == account:
				cost_centers.add(item.get('cost_center', ''))
		
		for cost_center in cost_centers:
			key = f"{account}_{cost_center}"
			
			budget_amount = budget_lookup.get(key, 0)
			actual_amount = actual_lookup.get(key, 0)
			
			# Calculate ratios
			act_bud_ratio = (actual_amount / budget_amount * 100) if budget_amount else 0
			
			# Update row data
			row['cost_center'] = cost_center
			row['this_year_budget'] = budget_amount
			row['this_year_actual'] = actual_amount
			row['this_year_act_bud'] = act_bud_ratio
			
			# For now, use same values for other periods
			# This can be extended to fetch historical data
			row['last_year_budget'] = budget_amount * 0.9  # Example: 10% decrease
			row['last_year_actual'] = actual_amount * 0.9
			row['last_year_act_bud'] = act_bud_ratio
			
			row['ytd_budget'] = budget_amount * 0.75  # Example: 75% of year
			row['ytd_actual'] = actual_amount * 0.75
			row['ytd_act_bud'] = act_bud_ratio
			
			row['forecast_budget'] = budget_amount * 1.1  # Example: 10% increase
			row['forecast_actual'] = actual_amount * 1.1
			row['forecast_act_bud'] = act_bud_ratio
			
			dashboard_data.append(row.copy())
	
	return dashboard_data


@frappe.whitelist()
def get_summary_data(filters=None):
	"""
	Get summary data for the dashboard
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	# Get dashboard data first
	dashboard_data = get_dashboard_data(filters)
	
	# Calculate summary
	total_budget = sum(row.get('this_year_budget', 0) for row in dashboard_data.get('dashboard_data', []))
	total_actual = sum(row.get('this_year_actual', 0) for row in dashboard_data.get('dashboard_data', []))
	total_variance = total_budget - total_actual
	
	ytd_budget = sum(row.get('ytd_budget', 0) for row in dashboard_data.get('dashboard_data', []))
	ytd_actual = sum(row.get('ytd_actual', 0) for row in dashboard_data.get('dashboard_data', []))
	ytd_variance = ytd_budget - ytd_actual
	
	forecast_budget = sum(row.get('forecast_budget', 0) for row in dashboard_data.get('dashboard_data', []))
	forecast_actual = sum(row.get('forecast_actual', 0) for row in dashboard_data.get('dashboard_data', []))
	forecast_variance = forecast_budget - forecast_actual
	
	return {
		'summary': {
			'total_budget': total_budget,
			'total_actual': total_actual,
			'total_variance': total_variance,
			'ytd_budget': ytd_budget,
			'ytd_actual': ytd_actual,
			'ytd_variance': ytd_variance,
			'forecast_budget': forecast_budget,
			'forecast_actual': forecast_actual,
			'forecast_variance': forecast_variance
		},
		'filters': filters
	}


@frappe.whitelist()
def get_companies():
	"""
	Get list of companies for filter dropdown
	"""
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
	"""
	Get list of fiscal years for filter dropdown
	"""
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
	"""
	Get list of cost centers for filter dropdown
	"""
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
	"""
	Get list of expense accounts for filter dropdown
	"""
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


def get_previous_fiscal_year(current_fiscal_year):
	"""
	Get the previous fiscal year name
	"""
	try:
		current_fy = frappe.get_doc("Fiscal Year", current_fiscal_year)
		prev_year_start = frappe.utils.add_months(current_fy.year_start_date, -12)
		
		# Find fiscal year that contains the previous year start date
		prev_fiscal_year = frappe.db.sql("""
			SELECT name FROM `tabFiscal Year`
			WHERE year_start_date <= %s AND year_end_date >= %s
			LIMIT 1
		""", (prev_year_start, prev_year_start), as_dict=1)
		
		return prev_fiscal_year[0]['name'] if prev_fiscal_year else current_fiscal_year
	except Exception as e:
		frappe.log_error(f"Error getting previous fiscal year: {str(e)}")
		return current_fiscal_year


def get_account_financial_data(account_code, account_type, fiscal_year, prev_fiscal_year,
							  from_date, to_date, prev_from_date, prev_to_date, ytd_end_date,
							  current_month_from_date, current_month_to_date, selected_cost_center, selected_month):
	"""
	Get financial data for a specific account
	"""
	# Helper function to safely calculate ratios
	def safe_ratio(numerator, denominator, default='N/A'):
		if not denominator or denominator == 0:
			return default
		try:
			ratio = (numerator / denominator) * 100
			return round(ratio, 1)
		except (TypeError, ValueError, ZeroDivisionError):
			return default
	
	# Get budget data for current year
	current_budget_params = [fiscal_year, account_code]
	current_budget_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		current_budget_condition = "AND b.cost_center = %s"
		current_budget_params.append(selected_cost_center)
	
	current_budget = frappe.db.sql("""
		SELECT SUM(ba.budget_amount) as budget_amount
		FROM `tabBudget Account` ba
		INNER JOIN `tabBudget` b ON ba.parent = b.name
		WHERE b.fiscal_year = %s AND ba.account = %s
		""" + current_budget_condition + """
	""", current_budget_params, as_dict=1)
	
	current_budget_amount = current_budget[0]['budget_amount'] if current_budget and current_budget[0]['budget_amount'] else 0
	
	# Get actual data for current year
	current_actual_params = [account_code, from_date, to_date, account_type]
	current_actual_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		current_actual_condition = "AND gle.cost_center = %s"
		current_actual_params.append(selected_cost_center)
	
	current_actual = frappe.db.sql("""
		SELECT SUM(debit - credit) as net_amount
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON gle.account = acc.name
		WHERE gle.account = %s 
		AND gle.posting_date BETWEEN %s AND %s
		AND gle.is_cancelled = 0
		AND acc.root_type = %s
		""" + current_actual_condition + """
	""", current_actual_params, as_dict=1)
	
	current_actual_amount = current_actual[0]['net_amount'] if current_actual and current_actual[0]['net_amount'] else 0
	
	# Get current month data if month is selected
	current_month_budget_amount = 0
	current_month_actual_amount = 0
	current_month_last_year_amount = 0
	
	if selected_month and selected_month.strip() and current_month_from_date and current_month_to_date:
		# Get current month budget (proportional to annual budget)
		month_ratio = 1/12  # Simple monthly proportion
		current_month_budget_amount = current_budget_amount * month_ratio
		
		# Get current month actual data
		current_month_actual_params = [account_code, current_month_from_date, current_month_to_date, account_type]
		current_month_actual_condition = ""
		if selected_cost_center and selected_cost_center.strip():
			current_month_actual_condition = "AND gle.cost_center = %s"
			current_month_actual_params.append(selected_cost_center)
		
		current_month_actual = frappe.db.sql("""
			SELECT SUM(debit - credit) as net_amount
			FROM `tabGL Entry` gle
			INNER JOIN `tabAccount` acc ON gle.account = acc.name
			WHERE gle.account = %s 
			AND gle.posting_date BETWEEN %s AND %s
			AND gle.is_cancelled = 0
			AND acc.root_type = %s
			""" + current_month_actual_condition + """
		""", current_month_actual_params, as_dict=1)
		
		current_month_actual_amount = current_month_actual[0]['net_amount'] if current_month_actual and current_month_actual[0]['net_amount'] else 0
		
		# Get current month last year data
		from frappe.utils import add_years
		current_month_last_year_from_date = add_years(current_month_from_date, -1)
		current_month_last_year_to_date = add_years(current_month_to_date, -1)
		
		current_month_last_year_params = [account_code, current_month_last_year_from_date, current_month_last_year_to_date, account_type]
		current_month_last_year_condition = ""
		if selected_cost_center and selected_cost_center.strip():
			current_month_last_year_condition = "AND gle.cost_center = %s"
			current_month_last_year_params.append(selected_cost_center)
		
		current_month_last_year = frappe.db.sql("""
			SELECT SUM(debit - credit) as net_amount
			FROM `tabGL Entry` gle
			INNER JOIN `tabAccount` acc ON gle.account = acc.name
			WHERE gle.account = %s 
			AND gle.posting_date BETWEEN %s AND %s
			AND gle.is_cancelled = 0
			AND acc.root_type = %s
			""" + current_month_last_year_condition + """
		""", current_month_last_year_params, as_dict=1)
		
		current_month_last_year_amount = current_month_last_year[0]['net_amount'] if current_month_last_year and current_month_last_year[0]['net_amount'] else 0
	
	# Get budget data for previous year
	prev_budget_params = [prev_fiscal_year, account_code]
	prev_budget_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		prev_budget_condition = "AND b.cost_center = %s"
		prev_budget_params.append(selected_cost_center)
	
	prev_budget = frappe.db.sql("""
		SELECT SUM(ba.budget_amount) as budget_amount
		FROM `tabBudget Account` ba
		INNER JOIN `tabBudget` b ON ba.parent = b.name
		WHERE b.fiscal_year = %s AND ba.account = %s
		""" + prev_budget_condition + """
	""", prev_budget_params, as_dict=1)
	
	prev_budget_amount = prev_budget[0]['budget_amount'] if prev_budget and prev_budget[0]['budget_amount'] else 0
	
	# Get actual data for previous year
	prev_actual_params = [account_code, prev_from_date, prev_to_date, account_type]
	prev_actual_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		prev_actual_condition = "AND gle.cost_center = %s"
		prev_actual_params.append(selected_cost_center)
	
	prev_actual = frappe.db.sql("""
		SELECT SUM(debit - credit) as net_amount
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON gle.account = acc.name
		WHERE gle.account = %s 
		AND gle.posting_date BETWEEN %s AND %s
		AND gle.is_cancelled = 0
		AND acc.root_type = %s
		""" + prev_actual_condition + """
	""", prev_actual_params, as_dict=1)
	
	prev_actual_amount = prev_actual[0]['net_amount'] if prev_actual and prev_actual[0]['net_amount'] else 0
	
	# Get YTD actual data
	ytd_actual_params = [account_code, from_date, ytd_end_date, account_type]
	ytd_actual_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		ytd_actual_condition = "AND gle.cost_center = %s"
		ytd_actual_params.append(selected_cost_center)
	
	ytd_actual = frappe.db.sql("""
		SELECT SUM(debit - credit) as net_amount
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON gle.account = acc.name
		WHERE gle.account = %s 
		AND gle.posting_date BETWEEN %s AND %s
		AND gle.is_cancelled = 0
		AND acc.root_type = %s
		""" + ytd_actual_condition + """
	""", ytd_actual_params, as_dict=1)
	
	ytd_actual_amount = ytd_actual[0]['net_amount'] if ytd_actual and ytd_actual[0]['net_amount'] else 0
	
	# Calculate YTD budget (proportional to current year budget)
	days_elapsed = (frappe.utils.getdate(ytd_end_date) - frappe.utils.getdate(from_date)).days
	total_days = (frappe.utils.getdate(to_date) - frappe.utils.getdate(from_date)).days
	ytd_budget_amount = current_budget_amount * (days_elapsed / total_days) if total_days > 0 else 0
	
	# Get YTD last year data
	ytd_last_year_from_date = prev_from_date
	ytd_last_year_to_date = add_years(ytd_end_date, -1) if selected_month and selected_month.strip() else prev_to_date
	
	ytd_last_year_params = [account_code, ytd_last_year_from_date, ytd_last_year_to_date, account_type]
	ytd_last_year_condition = ""
	if selected_cost_center and selected_cost_center.strip():
		ytd_last_year_condition = "AND gle.cost_center = %s"
		ytd_last_year_params.append(selected_cost_center)
	
	ytd_last_year = frappe.db.sql("""
		SELECT SUM(debit - credit) as net_amount
		FROM `tabGL Entry` gle
		INNER JOIN `tabAccount` acc ON gle.account = acc.name
		WHERE gle.account = %s 
		AND gle.posting_date BETWEEN %s AND %s
		AND gle.is_cancelled = 0
		AND acc.root_type = %s
		""" + ytd_last_year_condition + """
	""", ytd_last_year_params, as_dict=1)
	
	ytd_last_year_amount = ytd_last_year[0]['net_amount'] if ytd_last_year and ytd_last_year[0]['net_amount'] else 0
	
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


def calculate_category_totals(accounts, fiscal_year, prev_fiscal_year, from_date, to_date, 
							 prev_from_date, prev_to_date, ytd_end_date, current_month_from_date, 
							 current_month_to_date, selected_cost_center, selected_month):
	"""
	Calculate totals for a category of accounts
	"""
	totals = {
		'currentMonth': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0},
		'yearToDate': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0},
		'forecast': {'lastYear': 0, 'budget': 0, 'actual': 0, 'actBudThisYear': 0, 'actVsLastYear': 0}
	}
	
	for account in accounts:
		account_data = get_account_financial_data(
			account['name'], account['root_type'], fiscal_year, prev_fiscal_year,
			from_date, to_date, prev_from_date, prev_to_date, ytd_end_date,
			current_month_from_date, current_month_to_date, selected_cost_center, selected_month
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


def calculate_summary_rows(structured_data):
	"""
	Calculate summary rows (Gross Profit, Net Profit/Loss)
	"""
	summary_rows = []
	
	# Find revenue and cost of sales totals
	revenue_total = None
	cost_of_sales_total = None
	
	for row in structured_data:
		if row.get('type') == ROW_TYPES['TOTAL']:
			if 'REVENUE' in row.get('category', ''):
				revenue_total = row
			elif 'COST_OF_SALES' in row.get('category', ''):
				cost_of_sales_total = row
	
	# Calculate Gross Profit
	if revenue_total and cost_of_sales_total:
		gross_profit = {
			'type': ROW_TYPES['SUMMARY'],
			'category': 'Gross Profit',
			'currentMonth': {
				'lastYear': revenue_total['currentMonth']['lastYear'] - cost_of_sales_total['currentMonth']['lastYear'],
				'budget': revenue_total['currentMonth']['budget'] - cost_of_sales_total['currentMonth']['budget'],
				'actual': revenue_total['currentMonth']['actual'] - cost_of_sales_total['currentMonth']['actual'],
				'actBudThisYear': safe_ratio(
					revenue_total['currentMonth']['actual'] - cost_of_sales_total['currentMonth']['actual'],
					revenue_total['currentMonth']['budget'] - cost_of_sales_total['currentMonth']['budget']
				),
				'actVsLastYear': safe_ratio(
					revenue_total['currentMonth']['actual'] - cost_of_sales_total['currentMonth']['actual'],
					revenue_total['currentMonth']['lastYear'] - cost_of_sales_total['currentMonth']['lastYear']
				)
			},
			'yearToDate': {
				'lastYear': revenue_total['yearToDate']['lastYear'] - cost_of_sales_total['yearToDate']['lastYear'],
				'budget': revenue_total['yearToDate']['budget'] - cost_of_sales_total['yearToDate']['budget'],
				'actual': revenue_total['yearToDate']['actual'] - cost_of_sales_total['yearToDate']['actual'],
				'actBudThisYear': safe_ratio(
					revenue_total['yearToDate']['actual'] - cost_of_sales_total['yearToDate']['actual'],
					revenue_total['yearToDate']['budget'] - cost_of_sales_total['yearToDate']['budget']
				),
				'actVsLastYear': safe_ratio(
					revenue_total['yearToDate']['actual'] - cost_of_sales_total['yearToDate']['actual'],
					revenue_total['yearToDate']['lastYear'] - cost_of_sales_total['yearToDate']['lastYear']
				)
			},
			'forecast': {
				'lastYear': revenue_total['forecast']['lastYear'] - cost_of_sales_total['forecast']['lastYear'],
				'budget': revenue_total['forecast']['budget'] - cost_of_sales_total['forecast']['budget'],
				'actual': revenue_total['forecast']['actual'] - cost_of_sales_total['forecast']['actual'],
				'actBudThisYear': safe_ratio(
					revenue_total['forecast']['actual'] - cost_of_sales_total['forecast']['actual'],
					revenue_total['forecast']['budget'] - cost_of_sales_total['forecast']['budget']
				),
				'actVsLastYear': safe_ratio(
					revenue_total['forecast']['actual'] - cost_of_sales_total['forecast']['actual'],
					revenue_total['forecast']['lastYear'] - cost_of_sales_total['forecast']['lastYear']
				)
			}
		}
		summary_rows.append(gross_profit)
	
	return summary_rows


def safe_ratio(numerator, denominator, default='N/A'):
	"""
	Helper function to safely calculate ratios with error handling
	"""
	if not denominator or denominator == 0:
		return default
	try:
		ratio = (numerator / denominator) * 100
		return round(ratio, 1)
	except (TypeError, ValueError, ZeroDivisionError):
		return default 