import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day, add_years, today
from datetime import datetime, timedelta
import json
import re

# Row types for structured data
ROW_TYPES = {
    'MAIN_HEADER': 'main_header',
    'HEADER': 'header',
    'SUB_HEADER': 'sub_header',
    'SUB_SUB_HEADER': 'sub_sub_header',
    'ACCOUNT': 'account',
    'TOTAL': 'total'
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

def build_include_in_gross_map(company: str) -> dict[str, int]:
    """Return {account_name: 0/1} where 1 if the account OR any ancestor has include_in_gross."""
    rows = frappe.db.sql("""
        SELECT a.name,
               MAX(COALESCE(p.include_in_gross, 0)) AS inc_gross_any_parent
        FROM `tabAccount` a
        JOIN `tabAccount` p
          ON p.lft <= a.lft AND p.rgt >= a.rgt AND p.company = a.company
        WHERE a.company = %s
        GROUP BY a.name
    """, (company,), as_dict=1)
    return {r["name"]: int(r["inc_gross_any_parent"] or 0) for r in rows}

def build_report_class_direct_map(reporting_framework=None):
    """Return mapping of report_class -> is_direct (bool). Optionally filter by framework."""
    try:
        if reporting_framework:
            rows = frappe.db.sql(
                """
                SELECT class_name, IFNULL(is_direct, 0) as is_direct
                FROM `tabReport Classes`
                WHERE reporting_framework = %s
                """,
                (reporting_framework,),
                as_dict=True,
            )
        else:
            rows = frappe.db.sql(
                """
                SELECT class_name, IFNULL(is_direct, 0) as is_direct
                FROM `tabReport Classes`
                """,
                as_dict=True,
            )
        result = {}
        for r in rows:
            key = (r.get("class_name") or "").strip()
            if key:
                result[key] = bool(r.get("is_direct", 0))
        return result
    except Exception as e:
        frappe.log_error(f"Error building report_class direct map: {str(e)}")
        return {}


def compute_section_and_flags(acc, inc_gross_map, report_class_direct_map=None):
    """Determine section and cost-of-sales flags using ERPNext-native semantics augmented with report_class.is_direct."""
    if report_class_direct_map is None:
        report_class_direct_map = {}

    root = (acc.get("root_type") or "").strip()
    acct_type = (acc.get("account_type") or "").strip()
    inc_gross = bool(inc_gross_map.get(acc["name"], 0))
    report_class = (acc.get("report_class") or "").strip()

    # Hotel-specific cost of sales report classes
    HOTEL_COS_CLASSES = {"Food", "Beverage", "Room", "Other Costs", "Cost of Sales"}

    # Report class direct flag (from doctype)
    rc_is_direct = bool(report_class_direct_map.get(report_class, False))



    # Determine if this is a cost of sales account
    is_cost_of_sales = (
        root == "Expense" and (
            inc_gross or
            acct_type in {"Cost of Goods Sold", "Direct Expenses", "Cost of Sales"} or
            report_class in HOTEL_COS_CLASSES or
            rc_is_direct  # treat expense classes marked direct as cost of sales/direct expenses
        )
    )

    # Define specific expense categories for proper classification
    SALARY_EXPENSE_CLASSES = {
        "Salaries & Wages", "Salary", "Wages", "Payroll"
    }

    PAYROLL_BURDEN_CLASSES = {
        "Payroll Burden", "Burden", "Statutory", "Employer",
        "Social Security", "Provident Fund", "Pension", "SSNIT",
        "Gratuity", "Severance", "Vacation Pay", "Sick Pay"
    }

    DIRECT_OPERATIONAL_CLASSES = {
        "Direct Expenses", "Operational", "Maintenance", "Utilities", "Supplies"
    }

    # Administrative and overhead expenses (should be Indirect)
    ADMINISTRATIVE_CLASSES = {
        "Administrative Expenses", "Admin", "Overhead", "Office",
        "Marketing", "Advertising", "Professional Fees", "Depreciation",
        "Amortization", "Insurance", "Rent", "Taxes", "Miscellaneous"
    }

    # Determine if this is a salary/wages expense
    is_salary_expense = (
        root == "Expense" and
        not is_cost_of_sales and
        (report_class in SALARY_EXPENSE_CLASSES or
         "salary" in report_class.lower() or
         "wage" in report_class.lower())
    )

    # Determine if this is a payroll burden expense
    is_payroll_burden = (
        root == "Expense" and
        not is_cost_of_sales and
        any(keyword.lower() in report_class.lower() for keyword in
            ["burden", "statutory", "employer", "social security", "provident",
             "pension", "ssnit", "gratuity", "severance", "vacation", "sick"])
    )

    # Determine if this is a direct operational expense
    is_direct_operational = (
        root == "Expense" and
        not is_cost_of_sales and
        (rc_is_direct or report_class in DIRECT_OPERATIONAL_CLASSES)
    )

    # Determine if this is an administrative/overhead expense (Indirect)
    is_administrative = (
        root == "Expense" and
        not is_cost_of_sales and
        any(keyword.lower() in report_class.lower() for keyword in
            ["administrative", "admin", "overhead", "office", "marketing",
             "insurance", "rent", "depreciation", "amortization"])
    )

    # Determine if this is direct revenue
    is_direct_revenue = (
        root == "Income" and (
            rc_is_direct or
            report_class in {"Room", "Food", "Beverage", "Spa", "Conference", "Pool", "Gym", "Direct Revenue", "Other Revenue"}
        )
    )

    # Return appropriate section and flags
    if root == "Income":
        if is_direct_revenue:
            return "Direct Revenue", True
        else:
            return "Indirect Revenue", False
    elif root == "Expense":
        if is_cost_of_sales:
            return "Cost of Sales", True
        elif is_salary_expense:
            return "Salaries & Wages", True
        elif is_payroll_burden:
            return "Payroll Burden", True
        elif is_direct_operational:
            return "Direct Expenses", True
        elif is_administrative:
            return "Indirect Expenses", True
        else:
            # Only truly uncategorized expenses should default to Indirect Expenses
            return "Indirect Expenses", False
    else:
        return "Other", False

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
    """True ERPNext tree: keep parent_account, lft, rgt. Include report_class."""
    return frappe.db.sql("""
        SELECT
            name,
            account_name,
            account_number,
            root_type,
            parent_account,
            is_group,
            disabled,
            lft,
            rgt,
            account_type,
            include_in_gross,
            IFNULL(report_class, '') AS report_class
        FROM `tabAccount`
        WHERE company = %s
          AND root_type = %s
          AND disabled = 0
        ORDER BY lft
    """, (company, root_type), as_dict=1)

def get_gl_entries_for_period(company, from_date, to_date, additional_filters=None):
    """Get GL entries for a specific period with Account join to carry report_class and root_type"""
    filters = {
        'company': company,
        'posting_date': ['between', [from_date, to_date]],
        'is_cancelled': 0
    }
    
    if additional_filters:
        filters.update(additional_filters)
    
    # Always join with Account to get report_class and root_type
    gl_entries = frappe.db.sql("""
        SELECT 
            gl.name,
            gl.account,
            gl.debit,
            gl.credit,
            gl.posting_date,
            gl.voucher_type,
            gl.voucher_no,
            gl.cost_center,
            gl.company,
            gl.fiscal_year,
            gl.party,
            gl.party_type,
            gl.against_voucher_type,
            gl.against_voucher,
            gl.remarks,
            acc.report_class,
            acc.root_type,
            acc.account_name,
            acc.is_group,
            acc.parent_account,
            acc.lft,
            acc.rgt
        FROM `tabGL Entry` gl
        INNER JOIN `tabAccount` acc ON gl.account = acc.name
        WHERE gl.company = %(company)s
          AND gl.posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND gl.is_cancelled = 0
    """ + 
        (" AND gl.cost_center = %(cost_center)s" if additional_filters and additional_filters.get('cost_center') else "") +
    """
        ORDER BY gl.posting_date, gl.name
    """, {
        'company': company,
        'from_date': from_date,
        'to_date': to_date,
        **additional_filters
    } if additional_filters else {
        'company': company,
        'from_date': from_date,
        'to_date': to_date
    }, as_dict=1)
    
    return gl_entries

def pre_aggregate_gl_entries(gl_entries):
    """Pre-aggregate GL entries per account per period to avoid double-counting"""
    aggregated = {}
    
    for entry in gl_entries:
        account = entry.get('account')
        if not account:
            continue
            
        # Create key for this account
        if account not in aggregated:
            aggregated[account] = {
                'debit': 0,
                'credit': 0,
                'net_amount': 0
            }
        
        # Sum up debits and credits
        aggregated[account]['debit'] += entry.get('debit', 0)
        aggregated[account]['credit'] += entry.get('credit', 0)
    
    # Calculate net amounts
    for account_data in aggregated.values():
        account_data['net_amount'] = account_data['debit'] - account_data['credit']
    
    return aggregated

def aggregate_monthly_amounts(gl_entries):
    """Aggregate GL entries by account and posting month (1-12) for the fiscal period provided in gl_entries.
    Returns: { account_name: { month_number: amount } }
    """
    monthly_map = {}
    for entry in gl_entries or []:
        try:
            account = entry.get('account')
            if not account:
                continue
            posting_month = getdate(entry.get('posting_date')).month
            account_map = monthly_map.setdefault(account, {})
            account_map[posting_month] = account_map.get(posting_month, 0) + (entry.get('debit', 0) - entry.get('credit', 0))
        except Exception:
            # Skip malformed entries
            continue
    # Convert to absolute values to match dashboard presentation
    for account, by_month in monthly_map.items():
        for m in list(by_month.keys()):
            by_month[m] = abs(by_month[m])
    return monthly_map

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
    
    # Forecast calculations: Forecast = YTD Actual + Remaining Budget
    remaining_budget_amount = max(current_budget_amount - ytd_budget_amount, 0)
    forecast_actual = ytd_actual_amount + remaining_budget_amount
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
                        forecast_budget_entries, forecast_actual_entries,
                        monthly_actuals_map=None, fiscal_year=None, selected_cost_center=None):
    """Process a single account and return formatted data using pre-aggregated GL entries"""
    account_name = account['name']
    
    # Pre-aggregate GL entries for each period to avoid double-counting
    ytd_aggregated = pre_aggregate_gl_entries(ytd_gl_entries)
    ytd_last_year_aggregated = pre_aggregate_gl_entries(ytd_last_year_gl_entries)
    current_month_aggregated = pre_aggregate_gl_entries(current_month_gl_entries)
    current_month_last_year_aggregated = pre_aggregate_gl_entries(current_month_last_year_gl_entries)
    
    # Get aggregated data for this specific account
    ytd_data = ytd_aggregated.get(account_name, {'net_amount': 0})
    ytd_last_year_data = ytd_last_year_aggregated.get(account_name, {'net_amount': 0})
    current_month_data = current_month_aggregated.get(account_name, {'net_amount': 0})
    current_month_last_year_data = current_month_last_year_aggregated.get(account_name, {'net_amount': 0})
    
    # Calculate amounts from pre-aggregated GL entries
    ytd_actual = abs(ytd_data['net_amount'])
    ytd_last_year = abs(ytd_last_year_data['net_amount'])
    current_month_actual = abs(current_month_data['net_amount'])
    current_month_last_year = abs(current_month_last_year_data['net_amount'])
    
    # Budget entries: compute annual budget and derive YTD/current month proportions
    annual_budget = 0
    try:
        if fiscal_year:
            annual_budget = get_budget_data(fiscal_year, account_name, selected_cost_center)
    except Exception:
        annual_budget = 0

    # Simple proportional budgets
    ytd_budget = 0
    current_month_budget = 0
    try:
        # YTD proportion based on actual months elapsed from ytd_gl_entries
        ytd_months = set()
        for e in ytd_gl_entries or []:
            if e.get('account') == account_name:
                ytd_months.add(getdate(e.get('posting_date')).month)
        months_elapsed = len(ytd_months) if ytd_months else 0
        ytd_budget = (annual_budget / 12.0) * months_elapsed if months_elapsed > 0 else 0
        current_month_budget = (annual_budget / 12.0)
    except Exception:
        pass
    
    # Calculate forecast as YTD actual + remaining budget
    remaining_budget = max(annual_budget - ytd_budget, 0)
    forecast_actual = ytd_actual + remaining_budget
    forecast_budget = annual_budget

    # Build monthly map: actuals from monthly_actuals_map, budgets as annual/12
    monthly_budget_value = (annual_budget / 12.0) if annual_budget else 0
    monthly = {}
    account_monthly_actuals = (monthly_actuals_map or {}).get(account_name, {})
    for m in range(1, 13):
        monthly[m] = {
            'actual': float(account_monthly_actuals.get(m, 0) or 0),
            'budget': float(monthly_budget_value)
        }
    
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
        },
        'monthly': monthly
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
    if filters is None:
        filters = {}
    
    # Extract filter parameters
    fiscal_year = filters.get('fiscal_year', '2025')
    selected_cost_center = filters.get('cost_center', '')
    selected_month = filters.get('month', '')
    company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
    reporting_framework = filters.get('reporting_framework', '')
    
    # Get fiscal year document
    try:
        fy_doc = frappe.get_doc("Fiscal Year", fiscal_year)
    except Exception as e:
        frappe.log_error(f"ERROR getting fiscal year: {str(e)}")
        return {'dashboard_data': [], 'filters': filters}
    
    # Set default dates based on fiscal year
    from_date = filters.get('from_date', str(fy_doc.year_start_date))
    to_date = filters.get('to_date', str(fy_doc.year_end_date))
    
    # Get previous fiscal year
    try:
        prev_fiscal_year = get_previous_fiscal_year(fiscal_year)
        prev_fy_doc = frappe.get_doc("Fiscal Year", prev_fiscal_year)
    except Exception as e:
        frappe.log_error(f"ERROR getting previous fiscal year: {str(e)}")
        return {'dashboard_data': [], 'filters': filters}
    
    # Calculate date ranges
    try:
        from_date = getdate(from_date)
        to_date = getdate(to_date)
        prev_from_date = getdate(prev_fy_doc.year_start_date)
        prev_to_date = getdate(prev_fy_doc.year_end_date)
    except Exception as e:
        frappe.log_error(f"ERROR calculating date ranges: {str(e)}")
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
        except Exception:
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
        frappe.log_error(f"ERROR calculating YTD end date: {str(e)}")
        return {'dashboard_data': [], 'filters': filters}
    
    # STEP 1: Get ALL accounts and report class map
    try:
        income_accounts = get_all_accounts(company, 'Income')
        expense_accounts = get_all_accounts(company, 'Expense')
        all_accounts = income_accounts + expense_accounts
        
        # Filter accounts by reporting framework if specified
        if reporting_framework:
            allowed_report_classes = get_report_classes_by_framework(reporting_framework)
            income_accounts = filter_accounts_by_report_classes(income_accounts, allowed_report_classes)
            expense_accounts = filter_accounts_by_report_classes(expense_accounts, allowed_report_classes)
            all_accounts = income_accounts + expense_accounts
        
        # Build include_in_gross map and report_class direct map (used in classification)
        inc_gross_map = build_include_in_gross_map(company)
        report_class_direct_map = build_report_class_direct_map(reporting_framework)
    except Exception as e:
        frappe.log_error(f"ERROR getting accounts: {str(e)}")
        return {'dashboard_data': [], 'filters': filters}
    
    # STEP 2: Pre-fetch GL entries
    current_gl_entries = get_gl_entries_for_period(
        company, from_date, to_date,
        {'cost_center': selected_cost_center} if selected_cost_center else None
    )
    prev_gl_entries = get_gl_entries_for_period(
        company, prev_from_date, prev_to_date,
        {'cost_center': selected_cost_center} if selected_cost_center else None
    )
    ytd_gl_entries = get_gl_entries_for_period(
        company, from_date, ytd_end_date,
        {'cost_center': selected_cost_center} if selected_cost_center else None
    )
    ytd_last_year_from_date = prev_from_date
    ytd_last_year_to_date = add_years(ytd_end_date, -1) if selected_month and selected_month.strip() else prev_to_date
    ytd_last_year_gl_entries = get_gl_entries_for_period(
        company, ytd_last_year_from_date, ytd_last_year_to_date,
        {'cost_center': selected_cost_center} if selected_cost_center else None
    )
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
    
    # STEP 3: Build monthly actuals map for the full fiscal year to support monthly columns
    monthly_actuals_map = aggregate_monthly_amounts(current_gl_entries)

    # STEP 4: Organize accounts using hierarchy and classify using report_class_direct_map
    try:
        income_hierarchy, income_by_name, income_parent_map = get_accounts_with_hierarchy(income_accounts, current_gl_entries)
        expense_hierarchy, expense_by_name, expense_parent_map = get_accounts_with_hierarchy(expense_accounts, current_gl_entries)
    except Exception as e:
        frappe.log_error(f"ERROR in account hierarchy organization: {str(e)}")
        return {'dashboard_data': [], 'filters': filters}

    structured_dashboard_data = []

    # STEP 1: Process Direct Revenue
    direct_revenue_accounts = []
    indirect_revenue_accounts = []
    for account in income_hierarchy:
        section, is_direct = compute_section_and_flags(account, inc_gross_map, report_class_direct_map)
        if section == "Direct Revenue":
            direct_revenue_accounts.append(account)
        elif section == "Indirect Revenue":
            indirect_revenue_accounts.append(account)

    if direct_revenue_accounts:
        structured_dashboard_data.append({
            'type': 'header', 'category': 'Direct Revenue', 'account': 'HEADER_Direct_Revenue',
            'root_type': 'Income', 'is_group': True, 'indent': 0, 'section': 'Direct Revenue'
        })
        direct_revenue_by_class = {}
        for account in direct_revenue_accounts:
            rc = account.get('report_class', '')
            direct_revenue_by_class.setdefault(rc, []).append(account)
        for report_class, accounts in direct_revenue_by_class.items():
            if not accounts:
                continue
            structured_dashboard_data.append({
                'type': 'sub_header', 'category': report_class, 'account': f'SUB_HEADER_{report_class}',
                'root_type': 'Income', 'is_group': True, 'indent': 1, 'section': 'Direct Revenue'
            })
            for account in accounts:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], [],
                    monthly_actuals_map, fiscal_year, selected_cost_center
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 1) + 2
                    account_row['section'] = 'Direct Revenue'
                    account_row['is_direct'] = True
                    account_row['report_class'] = report_class
                    structured_dashboard_data.append(account_row)
        direct_revenue_total = calculate_section_total(direct_revenue_accounts, 'TOTAL DIRECT REVENUE', 'Income')
        if direct_revenue_total:
            direct_revenue_total['section'] = 'Direct Revenue'
            structured_dashboard_data.append(direct_revenue_total)

    # STEP 2: Process Cost of Sales and other expenses remain unchanged but pass report_class_direct_map too
    cost_of_sales_accounts = []
    direct_expense_accounts = []
    indirect_expense_accounts = []
    for account in expense_hierarchy:
        section, is_direct = compute_section_and_flags(account, inc_gross_map, report_class_direct_map)



        if section == "Cost of Sales":
            cost_of_sales_accounts.append(account)
        elif section == "Direct Expenses":
            direct_expense_accounts.append(account)
        elif section == "Indirect Expenses":
            indirect_expense_accounts.append(account)

    # Add Cost of Sales section
    if cost_of_sales_accounts:
        structured_dashboard_data.append({
            'type': 'header',
            'category': 'Cost of Sales',
            'account': 'HEADER_Cost_of_Sales',
            'root_type': 'Expense',
            'is_group': True,
            'indent': 0,
            'section': 'Cost of Sales'
        })
        
        # Group by report_class
        cos_by_class = {}
        for account in cost_of_sales_accounts:
            report_class = account.get('report_class', '')
            if report_class not in cos_by_class:
                cos_by_class[report_class] = []
            cos_by_class[report_class].append(account)
        
        # Process each report_class
        for report_class, accounts in cos_by_class.items():
            if not accounts:
                continue
                
            structured_dashboard_data.append({
                'type': 'sub_header',
                'category': report_class,
                'account': f'SUB_HEADER_{report_class}',
                'root_type': 'Expense',
                'is_group': True,
                'indent': 1,
                'section': 'Cost of Sales'
            })
            
            # Process accounts in this report_class
            for account in accounts:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], [],
                    monthly_actuals_map, fiscal_year, selected_cost_center
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 1) + 2
                    account_row['section'] = 'Cost of Sales'
                    account_row['is_direct'] = True
                    account_row['report_class'] = report_class
                    structured_dashboard_data.append(account_row)
        
        # Add Cost of Sales total
        if cost_of_sales_accounts:
            cos_total = calculate_section_total(cost_of_sales_accounts, 'TOTAL COST OF SALES', 'Expense')
            if cos_total:
                cos_total['section'] = 'Cost of Sales'
                structured_dashboard_data.append(cos_total)
    
    # STEP 3: Process Direct Expenses (excluding cost of sales)
    if direct_expense_accounts:
        structured_dashboard_data.append({
            'type': 'header',
            'category': 'Direct Expenses',
            'account': 'HEADER_Direct_Expenses',
            'root_type': 'Expense',
            'is_group': True,
            'indent': 0,
            'section': 'Direct Expenses'
        })
        
        # Group by report_class
        direct_exp_by_class = {}
        for account in direct_expense_accounts:
            report_class = account.get('report_class', '')
            if report_class not in direct_exp_by_class:
                direct_exp_by_class[report_class] = []
            direct_exp_by_class[report_class].append(account)
        
        # Process each report_class
        for report_class, accounts in direct_exp_by_class.items():
            if not accounts:
                continue
                
            structured_dashboard_data.append({
                'type': 'sub_header',
                'category': report_class,
                'account': f'SUB_HEADER_{report_class}',
                'root_type': 'Expense',
                'is_group': True,
                'indent': 1,
                'section': 'Direct Expenses'
            })
            
            # Process accounts in this report_class
            for account in accounts:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], [],
                    monthly_actuals_map, fiscal_year, selected_cost_center
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 1) + 2
                    account_row['section'] = 'Direct Expenses'
                    account_row['is_direct'] = True
                    account_row['report_class'] = report_class
                    structured_dashboard_data.append(account_row)
        
        # Add Direct Expenses total
        if direct_expense_accounts:
            direct_exp_total = calculate_section_total(direct_expense_accounts, 'TOTAL DIRECT EXPENSES', 'Expense')
            if direct_exp_total:
                direct_exp_total['section'] = 'Direct Expenses'
                structured_dashboard_data.append(direct_exp_total)
    
    # STEP 4: Process Indirect Revenue
    if indirect_revenue_accounts:
        structured_dashboard_data.append({
            'type': 'header',
            'category': 'Indirect Revenue',
            'account': 'HEADER_Indirect_Revenue',
            'root_type': 'Income',
            'is_group': True,
            'indent': 0,
            'section': 'Indirect Revenue'
        })
        
        # Group by report_class
        indirect_rev_by_class = {}
        for account in indirect_revenue_accounts:
            report_class = account.get('report_class', '')
            if report_class not in indirect_rev_by_class:
                indirect_rev_by_class[report_class] = []
            indirect_rev_by_class[report_class].append(account)
        
        # Process each report_class
        for report_class, accounts in indirect_rev_by_class.items():
            if not accounts:
                continue
                
            structured_dashboard_data.append({
                'type': 'sub_header',
                'category': report_class,
                'account': f'SUB_HEADER_{report_class}',
                'root_type': 'Income',
                'is_group': True,
                'indent': 1,
                'section': 'Indirect Revenue'
            })
            
            # Process accounts in this report_class
            for account in accounts:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], [],
                    monthly_actuals_map, fiscal_year, selected_cost_center
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 1) + 2
                    account_row['section'] = 'Indirect Revenue'
                    account_row['is_direct'] = False
                    account_row['report_class'] = report_class
                    structured_dashboard_data.append(account_row)
        
        # Add Indirect Revenue total
        if indirect_revenue_accounts:
            indirect_rev_total = calculate_section_total(indirect_revenue_accounts, 'TOTAL INDIRECT REVENUE', 'Income')
            if indirect_rev_total:
                indirect_rev_total['section'] = 'Indirect Revenue'
                structured_dashboard_data.append(indirect_rev_total)
    
    # STEP 5: Process Indirect Expenses
    if indirect_expense_accounts:
        structured_dashboard_data.append({
            'type': 'header',
            'category': 'Indirect Expenses',
            'account': 'HEADER_Indirect_Expenses',
            'root_type': 'Expense',
            'is_group': True,
            'indent': 0,
            'section': 'Indirect Expenses'
        })
        
        # Group by report_class
        indirect_exp_by_class = {}
        for account in indirect_expense_accounts:
            report_class = account.get('report_class', '')
            if report_class not in indirect_exp_by_class:
                indirect_exp_by_class[report_class] = []
            indirect_exp_by_class[report_class].append(account)
        
        # Process each report_class
        for report_class, accounts in indirect_exp_by_class.items():
            if not accounts:
                continue
                
            structured_dashboard_data.append({
                'type': 'sub_header',
                'category': report_class,
                'account': f'SUB_HEADER_{report_class}',
                'root_type': 'Expense',
                'is_group': True,
                'indent': 1,
                'section': 'Indirect Expenses'
            })
            
            # Process accounts in this report_class
            for account in accounts:
                account_row = process_account_data(
                    account, ytd_gl_entries, ytd_last_year_gl_entries,
                    current_month_gl_entries, current_month_last_year_gl_entries,
                    [], [], [], [],
                    monthly_actuals_map, fiscal_year, selected_cost_center
                )
                if account_row:
                    account_row['indent'] = account.get('indent', 1) + 2
                    account_row['section'] = 'Indirect Expenses'
                    account_row['is_direct'] = False
                    account_row['report_class'] = report_class
                    structured_dashboard_data.append(account_row)
        
        # Add Indirect Expenses total
        if indirect_expense_accounts:
            indirect_exp_total = calculate_section_total(indirect_expense_accounts, 'TOTAL INDIRECT EXPENSES', 'Expense')
            if indirect_exp_total:
                indirect_exp_total['section'] = 'Indirect Expenses'
                structured_dashboard_data.append(indirect_exp_total)
    
    return {
        'dashboard_data': structured_dashboard_data,
        'filters': filters,
        'period_list': [
            {'key': 'currentMonth', 'label': 'Current Month', 'from_date': str(current_month_from_date) if current_month_from_date else '', 'to_date': str(current_month_to_date) if current_month_to_date else ''},
            {'key': 'yearToDate', 'label': 'Year to Date', 'from_date': str(from_date), 'to_date': str(ytd_end_date)},
            {'key': 'forecast', 'label': 'Forecast', 'from_date': str(from_date), 'to_date': str(to_date)}
        ],
        'summary_data': {
            'total_income': sum([row.get('total', 0) for row in structured_dashboard_data if row.get('root_type') == 'Income' and row.get('type') == 'account']),
            'total_expenses': sum([row.get('total', 0) for row in structured_dashboard_data if row.get('root_type') == 'Expense' and row.get('type') == 'account']),
            'net_profit': sum([row.get('total', 0) for row in structured_dashboard_data if row.get('root_type') == 'Income' and row.get('type') == 'account']) - sum([row.get('total', 0) for row in structured_dashboard_data if row.get('root_type') == 'Expense' and row.get('type') == 'account'])
        }
    }

def is_report_class_direct(report_class_name):
    """Check if a report class is marked as direct"""
    try:
        # Query the Report Classes doctype to check is_direct flag
        report_class = frappe.get_doc('Report Classes', report_class_name)
        return bool(report_class.get('is_direct', 0))
    except Exception as e:
        frappe.log_error(f"Error checking report class {report_class_name}: {str(e)}")
        return False

@frappe.whitelist()
def get_direct_revenue_data(filters=None):
    """Get Direct Revenue data specifically"""
    try:
        # Get the main dashboard data
        dashboard_response = get_dashboard_data(filters)
        if not dashboard_response or 'dashboard_data' not in dashboard_response:
            return []

        # Build report class direct map (respect reporting framework if provided)
        reporting_framework = (filters or {}).get('reporting_framework') if isinstance(filters, dict) else None
        rc_direct_map = build_report_class_direct_map(reporting_framework)

        direct_revenue_data = []
        for row in dashboard_response['dashboard_data']:
            if (
                row.get('type') == 'account' and
                row.get('root_type') == 'Income'
            ):
                rc = row.get('report_class')
                if rc and rc_direct_map.get(rc, False):
                    account_data = {
                        'account': row.get('account', ''),
                        'account_name': row.get('account_name', ''),
                        'report_class': rc,
                        'is_direct': True,
                        'currentMonth': row.get('currentMonth', {}),
                        'yearToDate': row.get('yearToDate', {}),
                        'forecast': row.get('forecast', {}),
                        'monthly': row.get('monthly', {})
                    }
                    direct_revenue_data.append(account_data)
        return direct_revenue_data
    except Exception as e:
        frappe.log_error(f"Error in get_direct_revenue_data: {str(e)}")
        return []

@frappe.whitelist()
def get_cost_of_sales_data(filters=None):
    """Get Cost of Sales data specifically"""
    try:
        # Get the main dashboard data
        dashboard_response = get_dashboard_data(filters)
        if not dashboard_response or 'dashboard_data' not in dashboard_response:
            return []

        # Build report class direct map (respect reporting framework if provided)
        reporting_framework = (filters or {}).get('reporting_framework') if isinstance(filters, dict) else None
        rc_direct_map = build_report_class_direct_map(reporting_framework)

        cost_of_sales_data = []
        for row in dashboard_response['dashboard_data']:
            if (
                row.get('type') == 'account' and 
                row.get('root_type') == 'Expense'
            ):
                rc = row.get('report_class')
                if rc and rc_direct_map.get(rc, False):
                    account_data = {
                        'account': row.get('account', ''),
                        'account_name': row.get('account_name', ''),
                        'report_class': rc,
                        'is_direct': True,
                        'currentMonth': row.get('currentMonth', {}),
                        'yearToDate': row.get('yearToDate', {}),
                        'forecast': row.get('forecast', {}),
                        'monthly': row.get('monthly', {})
                    }
                    cost_of_sales_data.append(account_data)
        return cost_of_sales_data
    except Exception as e:
        frappe.log_error(f"Error in get_cost_of_sales_data: {str(e)}")
        return []

@frappe.whitelist()
def get_indirect_expenses_data(filters=None):
    """Get indirect expenses data using multiple filtering strategies"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        filters = filters or {}
        
        # Get the main dashboard data first
        dashboard_response = get_dashboard_data(filters)
        if not dashboard_response or 'dashboard_data' not in dashboard_response:
            return {'indirect_expenses_data': []}
        
        # Strategy 1: Use existing section classification from backend
        section_based = [
            row for row in dashboard_response['dashboard_data']
            if row.get('section') == 'Indirect Expenses' and row.get('type') == 'account'
        ]
        
        # Strategy 2: Filter by root_type + report_class.is_direct exclusion
        # Get report classes that are NOT marked as direct
        report_class_direct_map = build_report_class_direct_map(filters.get('reporting_framework'))
        
        # Get all expense accounts
        company = filters.get('company')
        if company:
            expense_accounts = get_all_accounts(company, 'Expense')
            
            # Filter for indirect expenses using multiple criteria
            indirect_by_criteria = []
            for acc in expense_accounts:
                # Skip if it's a group account
                if acc.get('is_group'):
                    continue
                    
                # Check if this account's report class is NOT marked as direct
                report_class = acc.get('report_class', '').strip()
                is_direct = report_class_direct_map.get(report_class, False)
                
                # Include if report class is NOT marked as direct
                if not is_direct:
                    # Get the GL data for this account
                    account_data = calculate_account_financial_data(
                        acc, 
                        get_gl_entries_for_period(
                            company, 
                            filters.get('from_date'),
                            filters.get('to_date'),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        get_gl_entries_for_period(
                            company, 
                            add_years(getdate(filters.get('from_date')), -1),
                            add_years(getdate(filters.get('to_date')), -1),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        get_gl_entries_for_period(
                            company, 
                            filters.get('from_date'),
                            getdate(filters.get('to_date')),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        get_gl_entries_for_period(
                            company, 
                            add_years(getdate(filters.get('from_date')), -1),
                            add_years(getdate(filters.get('to_date')), -1),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        get_gl_entries_for_period(
                            company, 
                            filters.get('from_date'),
                            getdate(filters.get('to_date')),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        get_gl_entries_for_period(
                            company, 
                            add_years(getdate(filters.get('from_date')), -1),
                            add_years(getdate(filters.get('to_date')), -1),
                            {'cost_center': filters.get('cost_center')}
                        ),
                        filters.get('fiscal_year'),
                        get_previous_fiscal_year(filters.get('fiscal_year')),
                        filters.get('from_date'),
                        filters.get('to_date'),
                        getdate(filters.get('to_date')),
                        filters.get('cost_center'),
                        filters.get('month')
                    )
                    
                    if account_data:
                        indirect_by_criteria.append({
                            'account': acc['name'],
                            'account_name': acc['account_name'],
                            'report_class': report_class,
                            'is_direct': False,
                            'root_type': 'Expense',
                            'currentMonth': account_data.get('currentMonth', {}),
                            'yearToDate': account_data.get('yearToDate', {}),
                            'forecast': account_data.get('forecast', {}),
                            'monthly': account_data.get('monthly', {})
                        })
        
        # Strategy 3: Specific indirect expense report classes
        specific_indirect_classes = {
            'Administrative', 'General & Administrative', 'Overhead', 
            'Indirect Expenses', 'Other Expenses', 'Miscellaneous'
        }
        
        specific_class_based = [
            row for row in dashboard_response['dashboard_data']
            if (row.get('type') == 'account' and 
                row.get('root_type') == 'Expense' and
                row.get('report_class') in specific_indirect_classes)
        ]
        
        # Combine all strategies and remove duplicates
        all_indirect = section_based + indirect_by_criteria + specific_class_based
        
        # Remove duplicates based on account name
        seen_accounts = set()
        unique_indirect = []
        for item in all_indirect:
            account_name = item.get('account') or item.get('account_name')
            if account_name and account_name not in seen_accounts:
                seen_accounts.add(account_name)
                unique_indirect.append(item)
        
        return {
            'indirect_expenses_data': unique_indirect,
            'filtering_strategies': {
                'section_based_count': len(section_based),
                'criteria_based_count': len(indirect_by_criteria),
                'specific_class_count': len(specific_class_based),
                'total_unique': len(unique_indirect)
            }
        }
        
    except Exception as e:
        frappe.log_error(f"Error in get_indirect_expenses_data: {str(e)}")
        return {'indirect_expenses_data': [], 'error': str(e)}

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

def get_report_classes():
    """Get the standard ERPNext report classes for P&L structure"""
    return [
        'Finance',
        'Administration', 
        'Marketing',
        'Other Costs',
        'Other Revenue',
        'Expense',
        'Payroll Burden',
        'Beverage',
        'Room',
        'Food'
    ]

def get_report_classes_by_framework(reporting_framework=None):
    """Get report classes linked to a specific reporting framework"""
    if not reporting_framework:
        # Return all report classes if no framework specified
        return get_report_classes()
    
    try:
        # Query for report classes linked to the specified framework
        # This assumes there's a relationship between report classes and frameworks
        # You may need to adjust this based on your actual data structure
        framework_report_classes = frappe.db.sql("""
            SELECT DISTINCT rc.name
            FROM `tabReport Classes` rc
            INNER JOIN `tabFramework Report Class Link` frcl ON rc.name = frcl.report_class
            WHERE frcl.parent = %s
        """, (reporting_framework,), as_dict=1)
        
        if framework_report_classes:
            return [rc.name for rc in framework_report_classes]
        else:
            # Fallback to all report classes if no framework-specific ones found
            return get_report_classes()
    except Exception as e:
        frappe.log_error(f"Error getting report classes for framework {reporting_framework}: {str(e)}")
        # Fallback to all report classes on error
        return get_report_classes()

def filter_accounts_by_report_classes(accounts, allowed_report_classes):
    """Filter accounts to only include those with allowed report classes"""
    if not allowed_report_classes:
        return accounts
    
    filtered_accounts = []
    for account in accounts:
        account_report_class = account.get('report_class', '')
        if account_report_class in allowed_report_classes:
            filtered_accounts.append(account)
    
    return filtered_accounts

def map_report_class_to_section(root_type, report_class):
    """Map (root_type, report_class) to Section for proper P&L structure"""
    if root_type == 'Income':
        return 'Revenue'
    
    if root_type == 'Expense':
        # Map expense report_classes to sections
        if report_class in ['Food', 'Beverage', 'Other Costs']:
            return 'Direct Expenses'
        elif report_class == 'Payroll Burden':
            return 'Payroll Burden'
        elif report_class in ['Finance', 'Administration', 'Marketing', 'Expense']:
            return 'Other Expenses'
        else:
            return 'Other Expenses'  # Default fallback
    
    return 'Other'  # Fallback for unknown types

@frappe.whitelist()
def get_report_classes_api():
    """Get all available report classes for the frontend"""
    try:
        # Accept optional reporting_framework parameter
        filters = frappe.request.get_json() if frappe.request.is_json() else {}
        reporting_framework = filters.get('reporting_framework', '')
        
        if reporting_framework:
            report_classes = get_report_classes_by_framework(reporting_framework)
        else:
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