import frappe
from frappe import _
from frappe.utils import flt
import json
import traceback

# Import the exact same functions from ERPNext's financial statements
from erpnext.accounts.report.financial_statements import (
    get_period_list,
    get_data,
    get_columns,
    get_filtered_list_for_consolidated_report,
    compute_growth_view_data,
    compute_margin_view_data,
)

# Test API endpoints that mirror the base Frappe P&L functionality

@frappe.whitelist()
def test_connection():
    """Test basic API connectivity"""
    try:
        return {
            'success': True,
            'message': 'Test API connection successful',
            'timestamp': frappe.utils.now(),
            'frappe_version': frappe.get_version(),
            'user': frappe.session.user,
            'api_type': 'Mirror of ERPNext P&L Statement'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_period_list_generation(filters=None):
    """Test period list generation using ERPNext's get_period_list function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters (same as ERPNext P&L)
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        period_start_date = filters.get('period_start_date')
        period_end_date = filters.get('period_end_date')
        filter_based_on = filters.get('filter_based_on', 'Fiscal Year')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        
        # Use ERPNext's exact function
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=period_start_date,
            period_end_date=period_end_date,
            filter_based_on=filter_based_on,
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        return {
            'success': True,
            'filters_used': filters,
            'period_list': [
                {
                    'from_date': str(period.from_date),
                    'to_date': str(period.to_date),
                    'key': period.key,
                    'label': period.label
                }
                for period in period_list
            ],
            'total_periods': len(period_list),
            'function_used': 'erpnext.accounts.report.financial_statements.get_period_list'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_income_data_generation(filters=None):
    """Test income data generation using ERPNext's get_data function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        
        # Get period list first - INCOME FUNCTION
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Use ERPNext's exact function for income data
        # Create proper filters object for ERPNext
        erpnext_filters = frappe._dict({
            'company': company,
            'from_fiscal_year': from_fiscal_year,
            'to_fiscal_year': to_fiscal_year,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'cost_center': filters.get('cost_center', ''),
            'project': filters.get('project', ''),
            'include_default_book_entries': filters.get('include_default_book_entries', True)
        })
        
        income_data = get_data(
            company,
            "Income",
            "Credit",
            period_list,
            erpnext_filters,
            accumulated_values,
            ignore_closing_entries=True
        )
        
        # Process the data similar to ERPNext P&L
        if income_data:
            # Get sample data for testing
            sample_rows = []
            for row in income_data[:5]:  # First 5 rows
                if isinstance(row, dict):
                    sample_rows.append({
                        'account': row.get('account', ''),
                        'account_name': row.get('account_name', ''),
                        'indent': row.get('indent', 0),
                        'has_value': any(row.get(key, 0) != 0 for key in row.keys() if key not in ['account', 'account_name', 'indent', 'parent_account'])
                    })
            
            return {
                'success': True,
                'company': company,
                'root_type': 'Income',
                'periodicity': periodicity,
                'accumulated_values': accumulated_values,
                'total_income_rows': len(income_data),
                'sample_income_data': sample_rows,
                'function_used': 'erpnext.accounts.report.financial_statements.get_data',
                'period_list_length': len(period_list)
            }
        else:
            return {
                'success': True,
                'message': 'No income data found',
                'company': company,
                'function_used': 'erpnext.accounts.report.financial_statements.get_data'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_expense_data_generation(filters=None):
    """Test expense data generation using ERPNext's get_data function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        
        # Get period list first - EXPENSE FUNCTION
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Use ERPNext's exact function for expense data
        # Create proper filters object for ERPNext
        erpnext_filters = frappe._dict({
            'company': company,
            'from_fiscal_year': from_fiscal_year,
            'to_fiscal_year': to_fiscal_year,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'cost_center': filters.get('cost_center', ''),
            'project': filters.get('project', ''),
            'include_default_book_entries': filters.get('include_default_book_entries', True)
        })
        
        expense_data = get_data(
            company,
            "Expense",
            "Debit",
            period_list,
            erpnext_filters,
            accumulated_values,
            ignore_closing_entries=True
        )
        
        # Process the data similar to ERPNext P&L
        if expense_data:
            # Get sample data for testing
            sample_rows = []
            for row in expense_data[:5]:  # First 5 rows
                if isinstance(row, dict):
                    sample_rows.append({
                        'account': row.get('account', ''),
                        'account_name': row.get('account_name', ''),
                        'indent': row.get('indent', 0),
                        'has_value': any(row.get(key, 0) != 0 for key in row.keys() if key not in ['account', 'account_name', 'indent', 'parent_account'])
                    })
            
            return {
                'success': True,
                'company': company,
                'root_type': 'Expense',
                'periodicity': periodicity,
                'accumulated_values': accumulated_values,
                'total_expense_rows': len(expense_data),
                'sample_expense_data': sample_rows,
                'function_used': 'erpnext.accounts.report.financial_statements.get_data',
                'period_list_length': len(period_list)
            }
        else:
            return {
                'success': True,
                'message': 'No expense data found',
                'company': company,
                'function_used': 'erpnext.accounts.report.financial_statements.get_data'
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_columns_generation(filters=None):
    """Test columns generation using ERPNext's get_columns function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        
        # Get period list first - COLUMNS FUNCTION
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Use ERPNext's exact function for columns
        columns = get_columns(
            periodicity=periodicity,
            period_list=period_list,
            accumulated_values=accumulated_values,
            company=company
        )
        
        return {
            'success': True,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'company': company,
            'total_columns': len(columns),
            'columns': [
                {
                    'fieldname': col.get('fieldname', ''),
                    'label': col.get('label', ''),
                    'fieldtype': col.get('fieldtype', ''),
                    'width': col.get('width', ''),
                    'align': col.get('align', '')
                }
                for col in columns
            ],
            'function_used': 'erpnext.accounts.report.financial_statements.get_columns'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_complete_pnl_execution(filters=None):
    """Test complete P&L execution mirroring ERPNext's execute function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters (same as ERPNext P&L)
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        selected_view = filters.get('selected_view', 'Report')
        
        # Step 1: Get period list (same as ERPNext)
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Step 2: Get income data (same as ERPNext)
        # Create proper filters object for ERPNext
        erpnext_filters = frappe._dict({
            'company': company,
            'from_fiscal_year': from_fiscal_year,
            'to_fiscal_year': to_fiscal_year,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'cost_center': filters.get('cost_center', ''),
            'project': filters.get('project', ''),
            'include_default_book_entries': filters.get('include_default_book_entries', True)
        })
        
        income = get_data(
            company=company,
            root_type="Income",
            balance_must_be="Credit",
            period_list=period_list,
            filters=erpnext_filters,
            accumulated_values=accumulated_values,
            ignore_closing_entries=True
        )
        
        # Step 3: Get expense data (same as ERPNext)
        expense = get_data(
            company=company,
            root_type="Expense",
            balance_must_be="Debit",
            period_list=period_list,
            filters=erpnext_filters,
            accumulated_values=accumulated_values,
            ignore_closing_entries=True
        )
        
        # Step 4: Calculate net profit/loss (same logic as ERPNext)
        net_profit_loss = None
        if income and expense:
            # Find the last period key
            last_period_key = period_list[-1].key if period_list else None
            
            if last_period_key:
                total_income = flt(income[-2].get(last_period_key, 0), 3) if income else 0
                total_expense = flt(expense[-2].get(last_period_key, 0), 3) if expense else 0
                net_profit = total_income - total_expense
                
                net_profit_loss = {
                    'account_name': "'" + _("Profit for the year") + "'",
                    'account': "'" + _("Profit for the year") + "'",
                    'warn_if_negative': True,
                    last_period_key: net_profit,
                    'total': net_profit
                }
        
        # Step 5: Combine data (same as ERPNext)
        data = []
        if income:
            data.extend(income)
        if expense:
            data.extend(expense)
        if net_profit_loss:
            data.append(net_profit_loss)
        
        # Step 6: Get columns (same as ERPNext)
        columns = get_columns(
            periodicity=periodicity,
            period_list=period_list,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Step 7: Apply view transformations (same as ERPNext)
        if selected_view == "Growth":
            compute_growth_view_data(data, period_list)
        elif selected_view == "Margin":
            compute_margin_view_data(data, period_list, accumulated_values)
        
        return {
            'success': True,
            'filters_used': filters,
            'execution_summary': {
                'periods_generated': len(period_list),
                'income_rows': len(income) if income else 0,
                'expense_rows': len(expense) if expense else 0,
                'net_profit_loss': net_profit_loss is not None,
                'total_data_rows': len(data),
                'total_columns': len(columns)
            },
            'sample_data': {
                'first_income_row': income[0] if income else None,
                'first_expense_row': expense[0] if expense else None,
                'net_profit_loss': net_profit_loss
            },
            'functions_used': [
                'erpnext.accounts.report.financial_statements.get_period_list',
                'erpnext.accounts.report.financial_statements.get_data',
                'erpnext.accounts.report.financial_statements.get_columns',
                'erpnext.accounts.report.financial_statements.compute_growth_view_data',
                'erpnext.accounts.report.financial_statements.compute_margin_view_data'
            ],
            'mirror_status': '1:1 copy of ERPNext P&L execute function'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_growth_view_computation(filters=None):  # GROWTH VIEW FUNCTION
    """Test growth view computation using ERPNext's compute_growth_view_data function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Get sample data first
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        
        # Get period list - GROWTH VIEW FUNCTION
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Get sample income data - GROWTH VIEW FUNCTION
        # Create proper filters object for ERPNext
        erpnext_filters = frappe._dict({
            'company': company,
            'from_fiscal_year': from_fiscal_year,
            'to_fiscal_year': to_fiscal_year,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'cost_center': filters.get('cost_center', ''),
            'project': filters.get('project', ''),
            'include_default_book_entries': filters.get('include_default_book_entries', True)
        })
        
        income = get_data(
            company,
            "Income",
            "Credit",
            period_list,
            erpnext_filters,
            accumulated_values,
            ignore_closing_entries=True
        )
        
        if not income:
            return {
                'success': True,
                'message': 'No income data available for growth view computation',
                'function_used': 'erpnext.accounts.report.financial_statements.compute_growth_view_data'
            }
        
        # Create a copy for testing (same as ERPNext)
        test_data = income[:3]  # Test with first 3 rows
        
        # Use ERPNext's exact function
        compute_growth_view_data(test_data, period_list)
        
        return {
            'success': True,
            'filters_used': filters,
            'growth_computation': {
                'data_rows_processed': len(test_data),
                'periods_available': len(period_list),
                'growth_columns_added': any('growth' in str(col) for row in test_data for col in row.values()),
                'sample_processed_row': test_data[0] if test_data else None
            },
            'function_used': 'erpnext.accounts.report.financial_statements.compute_growth_view_data',
            'mirror_status': '1:1 copy of ERPNext growth view computation'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_margin_view_computation(filters=None):  # MARGIN VIEW FUNCTION
    """Test margin view computation using ERPNext's compute_margin_view_data function"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Get sample data first - MARGIN VIEW FUNCTION
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        periodicity = filters.get('periodicity', 'Yearly')
        accumulated_values = filters.get('accumulated_values', False)
        
        # Get period list - MARGIN VIEW FUNCTION
        period_list = get_period_list(
            from_fiscal_year=from_fiscal_year,
            to_fiscal_year=to_fiscal_year,
            period_start_date=None,
            period_end_date=None,
            filter_based_on='Fiscal Year',
            periodicity=periodicity,
            accumulated_values=accumulated_values,
            company=company
        )
        
        # Get sample income data - MARGIN VIEW FUNCTION
        # Create proper filters object for ERPNext
        erpnext_filters = frappe._dict({
            'company': company,
            'from_fiscal_year': from_fiscal_year,
            'to_fiscal_year': to_fiscal_year,
            'periodicity': periodicity,
            'accumulated_values': accumulated_values,
            'cost_center': filters.get('cost_center', ''),
            'project': filters.get('project', ''),
            'include_default_book_entries': filters.get('include_default_book_entries', True)
        })
        
        income = get_data(
            company,
            "Income",
            "Credit",
            period_list,
            erpnext_filters,
            accumulated_values,
            ignore_closing_entries=True
        )
        
        if not income:
            return {
                'success': True,
                'message': 'No income data available for margin view computation',
                'function_used': 'erpnext.accounts.report.financial_statements.compute_margin_view_data'
            }
        
        # Create a copy for testing (same as ERPNext)
        test_data = income[:3]  # Test with first 3 rows
        
        # Use ERPNext's exact function
        compute_margin_view_data(test_data, period_list, accumulated_values)
        
        return {
            'success': True,
            'filters_used': filters,
            'margin_computation': {
                'data_rows_processed': len(test_data),
                'periods_available': len(period_list),
                'accumulated_values': accumulated_values,
                'margin_columns_added': any('margin' in str(col) for row in test_data for col in row.values()),
                'sample_processed_row': test_data[0] if test_data else None
            },
            'function_used': 'erpnext.accounts.report.financial_statements.compute_margin_view_data',
            'mirror_status': '1:1 copy of ERPNext margin view computation'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def test_gl_entries(filters=None):
    """Test GL entries retrieval and display in tables"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Extract parameters
        company = filters.get('company', 'Western Serene Atlantic Hotel Ltd')
        from_fiscal_year = filters.get('from_fiscal_year', '2025')
        to_fiscal_year = filters.get('to_fiscal_year', '2025')
        cost_center = filters.get('cost_center', '')
        
        # Get fiscal year dates
        try:
            fy_doc = frappe.get_doc("Fiscal Year", from_fiscal_year)
            from_date = str(fy_doc.year_start_date)
            to_date = str(fy_doc.year_end_date)
        except Exception as e:
            return {
                'success': False,
                'error': f'Fiscal year {from_fiscal_year} not found: {str(e)}'
            }
        
        # Build conditions for GL entries
        conditions = ["company = %s", "posting_date BETWEEN %s AND %s", "is_cancelled = 0"]
        params = [company, from_date, to_date]
        
        if cost_center:
            conditions.append("cost_center = %s")
            params.append(cost_center)
        
        # Get GL entries with account details
        sql = """
            SELECT 
                gle.account,
                gle.debit,
                gle.credit,
                gle.posting_date,
                gle.voucher_type,
                gle.voucher_no,
                gle.cost_center,
                acc.account_name,
                acc.root_type,
                acc.account_type
            FROM `tabGL Entry` gle
            LEFT JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE {}
            ORDER BY gle.posting_date DESC, ABS(gle.debit - gle.credit) DESC
            LIMIT 50
        """.format(" AND ".join(conditions))
        
        gl_entries = frappe.db.sql(sql, params, as_dict=1)
        
        # Get summary by account
        summary_sql = """
            SELECT 
                gle.account,
                acc.account_name,
                acc.root_type,
                SUM(gle.debit) as total_debit,
                SUM(gle.credit) as total_credit,
                SUM(gle.debit - gle.credit) as net_amount,
                COUNT(*) as entry_count
            FROM `tabGL Entry` gle
            LEFT JOIN `tabAccount` acc ON gle.account = acc.name
            WHERE {}
            GROUP BY gle.account
            ORDER BY ABS(SUM(gle.debit - gle.credit)) DESC
            LIMIT 30
        """.format(" AND ".join(conditions))
        
        account_summary = frappe.db.sql(summary_sql, params, as_dict=1)
        
        # Calculate totals
        total_debit = sum(entry.get('debit', 0) for entry in gl_entries)
        total_credit = sum(entry.get('credit', 0) for entry in gl_entries)
        total_net = sum(entry.get('debit', 0) - entry.get('credit', 0) for entry in gl_entries)
        
        return {
            'success': True,
            'company': company,
            'fiscal_year': from_fiscal_year,
            'date_range': {'from': from_date, 'to': to_date},
            'cost_center': cost_center,
            'gl_entries': {
                'total_entries': len(gl_entries),
                'sample_entries': gl_entries[:10],
                'total_debit': total_debit,
                'total_credit': total_credit,
                'total_net': total_net
            },
            'account_summary': {
                'total_accounts': len(account_summary),
                'accounts': account_summary
            },
            'data_structure': {
                'gl_entries_fields': ['account', 'debit', 'credit', 'posting_date', 'voucher_type', 'voucher_no', 'cost_center', 'account_name', 'root_type', 'account_type'],
                'summary_fields': ['account', 'account_name', 'root_type', 'total_debit', 'total_credit', 'net_amount', 'entry_count']
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }

@frappe.whitelist()
def get_test_summary():
    """Get summary of all available test endpoints"""
    return {
        'success': True,
        'api_type': 'Mirror of ERPNext Profit and Loss Statement',
        'description': 'This test API replicates the exact functionality of ERPNext\'s base P&L statement by importing and using the same functions',
        'test_endpoints': [
            {
                'name': 'test_connection',
                'description': 'Test basic API connectivity',
                'parameters': 'None',
                'returns': 'Connection status and API info'
            },
            {
                'name': 'test_period_list_generation',
                'description': 'Test period list generation using ERPNext\'s get_period_list',
                'parameters': 'filters (JSON string with fiscal year, periodicity, etc.)',
                'returns': 'Generated period list and metadata'
            },
            {
                'name': 'test_income_data_generation',
                'description': 'Test income data generation using ERPNext\'s get_data',
                'parameters': 'filters (JSON string)',
                'returns': 'Income data and processing results'
            },
            {
                'name': 'test_expense_data_generation',
                'description': 'Test expense data generation using ERPNext\'s get_data',
                'parameters': 'filters (JSON string)',
                'returns': 'Expense data and processing results'
            },
            {
                'name': 'test_columns_generation',
                'description': 'Test columns generation using ERPNext\'s get_columns',
                'parameters': 'filters (JSON string)',
                'returns': 'Generated columns and metadata'
            },
            {
                'name': 'test_complete_pnl_execution',
                'description': 'Test complete P&L execution mirroring ERPNext\'s execute function',
                'parameters': 'filters (JSON string)',
                'returns': 'Complete P&L execution results'
            },
            {
                'name': 'test_growth_view_computation',
                'description': 'Test growth view computation using ERPNext\'s compute_growth_view_data',
                'parameters': 'filters (JSON string)',
                'returns': 'Growth view computation results'
            },
            {
                'name': 'test_margin_view_computation',
                'description': 'Test margin view computation using ERPNext\'s compute_margin_view_data',
                'parameters': 'filters (JSON string)',
                'returns': 'Margin view computation results'
            },
            {
                'name': 'test_gl_entries',
                'description': 'Test GL entries retrieval and display in tables',
                'parameters': 'filters (JSON string)',
                'returns': 'GL entries data and account summary'
            }
        ],
        'erpnext_functions_imported': [
            'get_period_list',
            'get_data',
            'get_columns',
            'get_filtered_list_for_consolidated_report',
            'compute_growth_view_data',
            'compute_margin_view_data'
        ],
        'usage': 'Call these endpoints to test the exact same functionality as ERPNext\'s base P&L statement',
        'example': 'POST /api/method/yearly_income_statement.test_api.test_complete_pnl_execution',
        'mirror_status': '1:1 copy of ERPNext P&L functionality'
    } 

@frappe.whitelist()
def test_dashboard_data_structure(filters=None):
    """Test the dashboard data structure to debug revenue grouping and zero subtotals"""
    try:
        if isinstance(filters, str):
            filters = json.loads(filters)
        
        if filters is None:
            filters = {}
        
        # Import the dashboard API function
        from yearly_income_statement.api import get_dashboard_data
        
        # Call the dashboard API
        result = get_dashboard_data(filters)
        
        # Analyze the data structure
        dashboard_data = result.get('dashboard_data', [])
        
        # Count different types
        header_count = len([row for row in dashboard_data if row.get('type') == 'header'])
        account_count = len([row for row in dashboard_data if row.get('type') == 'account'])
        total_count = len([row for row in dashboard_data if row.get('type') == 'total'])
        
        # Analyze income structure
        income_headers = [row for row in dashboard_data if row.get('type') == 'header' and row.get('root_type') == 'Income']
        income_accounts = [row for row in dashboard_data if row.get('type') == 'account' and row.get('root_type') == 'Income']
        
        # Analyze expense structure
        expense_headers = [row for row in dashboard_data if row.get('type') == 'header' and row.get('root_type') == 'Expense']
        expense_accounts = [row for row in dashboard_data if row.get('type') == 'account' and row.get('root_type') == 'Expense']
        
        # Sample data for debugging
        sample_income_headers = [{'category': row.get('category'), 'account': row.get('account')} for row in income_headers[:5]]
        sample_income_accounts = [{'category': row.get('category'), 'account': row.get('account'), 'indent': row.get('indent')} for row in income_accounts[:5]]
        sample_expense_accounts = [{'category': row.get('category'), 'account': row.get('account'), 'indent': row.get('indent')} for row in expense_accounts[:5]]
        
        return {
            'success': True,
            'filters_used': filters,
            'data_summary': {
                'total_rows': len(dashboard_data),
                'headers': header_count,
                'accounts': account_count,
                'totals': total_count
            },
            'income_structure': {
                'headers_count': len(income_headers),
                'accounts_count': len(income_accounts),
                'sample_headers': sample_income_headers,
                'sample_accounts': sample_income_accounts
            },
            'expense_structure': {
                'headers_count': len(expense_headers),
                'accounts_count': len(expense_accounts),
                'sample_accounts': sample_expense_accounts
            },
            'full_data_sample': dashboard_data[:10]  # First 10 rows for detailed inspection
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        } 