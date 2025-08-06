import frappe
from frappe import _
from frappe.utils import flt, getdate, add_months, get_first_day, get_last_day, today
from datetime import datetime, timedelta
import json


@frappe.whitelist()
def get_historical_data(filters=None):
	"""
	Get historical data for year-over-year comparisons
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	current_fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	
	# Get previous fiscal year
	current_fy = frappe.get_doc("Fiscal Year", current_fiscal_year)
	prev_fiscal_year = get_previous_fiscal_year(current_fiscal_year)
	
	# Get data for both years
	current_data = get_fiscal_year_data(company, current_fiscal_year, cost_center)
	previous_data = get_fiscal_year_data(company, prev_fiscal_year, cost_center)
	
	return {
		'current_year': current_data,
		'previous_year': previous_data,
		'filters': filters
	}


def get_fiscal_year_data(company, fiscal_year, cost_center=None):
	"""
	Get budget and actual data for a specific fiscal year
	"""
	# Get budget data
	budget_data = frappe.db.sql("""
		SELECT 
			ba.account,
			ba.budget_amount,
			b.cost_center
		FROM `tabBudget Account` ba
		INNER JOIN `tabBudget` b ON ba.parent = b.name
		WHERE b.company = %s 
		AND b.fiscal_year = %s
		AND b.docstatus = 1
	""", (company, fiscal_year), as_dict=1)
	
	# Get fiscal year dates
	fy = frappe.get_doc("Fiscal Year", fiscal_year)
	from_date = fy.year_start_date
	to_date = fy.year_end_date
	
	# Get actual data
	conditions = [
		"gle.company = %s",
		"gle.posting_date BETWEEN %s AND %s",
		"gle.docstatus = 1"
	]
	params = [company, from_date, to_date]
	
	if cost_center:
		conditions.append("gle.cost_center = %s")
		params.append(cost_center)
	
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
		'budget_data': budget_data,
		'actual_data': actual_data,
		'fiscal_year': fiscal_year,
		'from_date': from_date,
		'to_date': to_date
	}


def get_previous_fiscal_year(current_fiscal_year):
	"""
	Get the previous fiscal year name
	"""
	current_fy = frappe.get_doc("Fiscal Year", current_fiscal_year)
	prev_year_start = add_months(current_fy.year_start_date, -12)
	
	# Find fiscal year that contains the previous year start date
	prev_fiscal_year = frappe.db.sql("""
		SELECT name FROM `tabFiscal Year`
		WHERE year_start_date <= %s AND year_end_date >= %s
	""", (prev_year_start, prev_year_start), as_dict=1)
	
	if prev_fiscal_year:
		return prev_fiscal_year[0].name
	else:
		# Fallback: create a fiscal year name
		year = prev_year_start.year
		return f"{year}-{year+1}"


@frappe.whitelist()
def get_ytd_data(filters=None):
	"""
	Get Year-to-Date data
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	
	# Get fiscal year
	fy = frappe.get_doc("Fiscal Year", fiscal_year)
	from_date = fy.year_start_date
	to_date = today()  # Current date
	
	# Get YTD budget (proportional to current date)
	year_days = (fy.year_end_date - fy.year_start_date).days
	current_days = (to_date - fy.year_start_date).days
	ytd_ratio = min(current_days / year_days, 1) if year_days > 0 else 0
	
	# Get budget data
	budget_data = frappe.db.sql("""
		SELECT 
			ba.account,
			ba.budget_amount * %s as ytd_budget_amount,
			b.cost_center
		FROM `tabBudget Account` ba
		INNER JOIN `tabBudget` b ON ba.parent = b.name
		WHERE b.company = %s 
		AND b.fiscal_year = %s
		AND b.docstatus = 1
	""", (ytd_ratio, company, fiscal_year), as_dict=1)
	
	# Get YTD actual data
	conditions = [
		"gle.company = %s",
		"gle.posting_date BETWEEN %s AND %s",
		"gle.docstatus = 1"
	]
	params = [company, from_date, to_date]
	
	if cost_center:
		conditions.append("gle.cost_center = %s")
		params.append(cost_center)
	
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
		'ytd_budget_data': budget_data,
		'ytd_actual_data': actual_data,
		'ytd_ratio': ytd_ratio,
		'from_date': from_date,
		'to_date': to_date,
		'filters': filters
	}


@frappe.whitelist()
def get_forecast_calculations(filters=None):
	"""
	Calculate forecast data based on trends and historical data
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	company = filters.get('company')
	fiscal_year = filters.get('fiscal_year')
	cost_center = filters.get('cost_center')
	
	# Get historical data for trend analysis
	historical_data = get_historical_data(filters)
	current_data = historical_data['current_year']
	previous_data = historical_data['previous_year']
	
	# Calculate trends
	forecast_data = calculate_forecast_trends(current_data, previous_data)
	
	return {
		'forecast_data': forecast_data,
		'filters': filters
	}


def calculate_forecast_trends(current_data, previous_data):
	"""
	Calculate forecast based on trends
	"""
	forecast_data = []
	
	# Create lookup dictionaries
	current_budget = {}
	current_actual = {}
	previous_budget = {}
	previous_actual = {}
	
	# Process current year data
	for item in current_data['budget_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		current_budget[key] = flt(item.get('budget_amount', 0))
	
	for item in current_data['actual_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		current_actual[key] = flt(item.get('net_amount', 0))
	
	# Process previous year data
	for item in previous_data['budget_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		previous_budget[key] = flt(item.get('budget_amount', 0))
	
	for item in previous_data['actual_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		previous_actual[key] = flt(item.get('net_amount', 0))
	
	# Calculate forecasts
	all_keys = set(list(current_budget.keys()) + list(current_actual.keys()))
	
	for key in all_keys:
		account, cost_center = key.split('_', 1) if '_' in key else (key, '')
		
		current_budget_amount = current_budget.get(key, 0)
		current_actual_amount = current_actual.get(key, 0)
		previous_budget_amount = previous_budget.get(key, 0)
		previous_actual_amount = previous_actual.get(key, 0)
		
		# Calculate growth rate
		growth_rate = 0
		if previous_actual_amount and previous_actual_amount != 0:
			growth_rate = (current_actual_amount - previous_actual_amount) / previous_actual_amount
		
		# Calculate forecast (simple trend-based)
		forecast_budget = current_budget_amount * (1 + growth_rate)
		forecast_actual = current_actual_amount * (1 + growth_rate)
		
		forecast_data.append({
			'account': account,
			'cost_center': cost_center,
			'forecast_budget': forecast_budget,
			'forecast_actual': forecast_actual,
			'growth_rate': growth_rate * 100,  # Convert to percentage
			'current_budget': current_budget_amount,
			'current_actual': current_actual_amount,
			'previous_budget': previous_budget_amount,
			'previous_actual': previous_actual_amount
		})
	
	return forecast_data


@frappe.whitelist()
def get_comprehensive_dashboard_data(filters=None):
	"""
	Get comprehensive dashboard data with all periods and calculations
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	try:
		# Use the main dashboard data function which gets real data
		from yearly_income_statement.api import get_dashboard_data
		dashboard_result = get_dashboard_data(filters)
		
		return dashboard_result
	except Exception as e:
		frappe.log_error(f"Error in get_comprehensive_dashboard_data: {str(e)}")
		# Return empty data if there's an error
		return {
			'dashboard_data': [],
			'filters': filters
		}


def combine_dashboard_data(historical_data, ytd_data, forecast_data, filters):
	"""
	Combine all data sources into comprehensive dashboard data
	"""
	comprehensive_data = []
	
	# Get all unique accounts and cost centers
	all_accounts = set()
	
	# Collect accounts from all data sources
	for data_source in [historical_data['current_year'], historical_data['previous_year'], ytd_data]:
		for item in data_source['budget_data'] + data_source['actual_data']:
			all_accounts.add(item.get('account'))
	
	# Create lookup dictionaries
	current_budget = {}
	current_actual = {}
	previous_budget = {}
	previous_actual = {}
	ytd_budget = {}
	ytd_actual = {}
	forecast_budget = {}
	forecast_actual = {}
	
	# Process current year data
	for item in historical_data['current_year']['budget_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		current_budget[key] = flt(item.get('budget_amount', 0))
	
	for item in historical_data['current_year']['actual_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		current_actual[key] = flt(item.get('net_amount', 0))
	
	# Process previous year data
	for item in historical_data['previous_year']['budget_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		previous_budget[key] = flt(item.get('budget_amount', 0))
	
	for item in historical_data['previous_year']['actual_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		previous_actual[key] = flt(item.get('net_amount', 0))
	
	# Process YTD data
	for item in ytd_data['ytd_budget_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		ytd_budget[key] = flt(item.get('ytd_budget_amount', 0))
	
	for item in ytd_data['ytd_actual_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		ytd_actual[key] = flt(item.get('net_amount', 0))
	
	# Process forecast data
	for item in forecast_data['forecast_data']:
		key = f"{item.get('account')}_{item.get('cost_center', '')}"
		forecast_budget[key] = flt(item.get('forecast_budget', 0))
		forecast_actual[key] = flt(item.get('forecast_actual', 0))
	
	# Build comprehensive dashboard data
	for account in all_accounts:
		account_doc = frappe.get_doc("Account", account)
		
		# Get cost centers for this account
		cost_centers = set()
		for data_source in [historical_data['current_year'], historical_data['previous_year'], ytd_data]:
			for item in data_source['budget_data'] + data_source['actual_data']:
				if item.get('account') == account:
					cost_centers.add(item.get('cost_center', ''))
		
		for cost_center in cost_centers:
			key = f"{account}_{cost_center}"
			
			# Get values for all periods
			current_budget_amount = current_budget.get(key, 0)
			current_actual_amount = current_actual.get(key, 0)
			previous_budget_amount = previous_budget.get(key, 0)
			previous_actual_amount = previous_actual.get(key, 0)
			ytd_budget_amount = ytd_budget.get(key, 0)
			ytd_actual_amount = ytd_actual.get(key, 0)
			forecast_budget_amount = forecast_budget.get(key, 0)
			forecast_actual_amount = forecast_actual.get(key, 0)
			
			# Calculate ratios
			current_act_bud = (current_actual_amount / current_budget_amount * 100) if current_budget_amount else 0
			previous_act_bud = (previous_actual_amount / previous_budget_amount * 100) if previous_budget_amount else 0
			ytd_act_bud = (ytd_actual_amount / ytd_budget_amount * 100) if ytd_budget_amount else 0
			forecast_act_bud = (forecast_actual_amount / forecast_budget_amount * 100) if forecast_budget_amount else 0
			
			# Calculate year-over-year ratios
			current_vs_previous = (current_actual_amount / previous_actual_amount * 100) if previous_actual_amount else 0
			ytd_current_vs_previous = (ytd_actual_amount / previous_actual_amount * 100) if previous_actual_amount else 0
			forecast_current_vs_previous = (forecast_actual_amount / previous_actual_amount * 100) if previous_actual_amount else 0
			
			row = {
				'account': account,
				'account_name': account_doc.account_name,
				'cost_center': cost_center,
				# Last Year
				'last_year_budget': previous_budget_amount,
				'last_year_actual': previous_actual_amount,
				'last_year_act_bud': previous_act_bud,
				# This Year
				'this_year_budget': current_budget_amount,
				'this_year_actual': current_actual_amount,
				'this_year_act_bud': current_act_bud,
				'this_year_vs_last_year': current_vs_previous,
				# YTD
				'ytd_budget': ytd_budget_amount,
				'ytd_actual': ytd_actual_amount,
				'ytd_act_bud': ytd_act_bud,
				'ytd_vs_last_year': ytd_current_vs_previous,
				# Forecast
				'forecast_budget': forecast_budget_amount,
				'forecast_actual': forecast_actual_amount,
				'forecast_act_bud': forecast_act_bud,
				'forecast_vs_last_year': forecast_current_vs_previous
			}
			
			comprehensive_data.append(row)
	
	return comprehensive_data


@frappe.whitelist()
def export_dashboard_data(filters=None, format='excel'):
	"""
	Export dashboard data in various formats
	"""
	if isinstance(filters, str):
		filters = json.loads(filters)
	
	# Get dashboard data
	dashboard_result = get_comprehensive_dashboard_data(filters)
	dashboard_data = dashboard_result['dashboard_data']
	
	# Prepare export data
	export_data = []
	for row in dashboard_data:
		export_row = {
			'Account': row.get('account_name', ''),
			'Cost Center': row.get('cost_center', ''),
			'Last Year Budget': row.get('last_year_budget', 0),
			'Last Year Actual': row.get('last_year_actual', 0),
			'Last Year Act/Bud %': f"{row.get('last_year_act_bud', 0):.2f}%",
			'This Year Budget': row.get('this_year_budget', 0),
			'This Year Actual': row.get('this_year_actual', 0),
			'This Year Act/Bud %': f"{row.get('this_year_act_bud', 0):.2f}%",
			'This Year vs Last Year %': f"{row.get('this_year_vs_last_year', 0):.2f}%",
			'YTD Budget': row.get('ytd_budget', 0),
			'YTD Actual': row.get('ytd_actual', 0),
			'YTD Act/Bud %': f"{row.get('ytd_act_bud', 0):.2f}%",
			'YTD vs Last Year %': f"{row.get('ytd_vs_last_year', 0):.2f}%",
			'Forecast Budget': row.get('forecast_budget', 0),
			'Forecast Actual': row.get('forecast_actual', 0),
			'Forecast Act/Bud %': f"{row.get('forecast_act_bud', 0):.2f}%",
			'Forecast vs Last Year %': f"{row.get('forecast_vs_last_year', 0):.2f}%"
		}
		export_data.append(export_row)
	
	return {
		'export_data': export_data,
		'format': format,
		'filters': filters
	} 