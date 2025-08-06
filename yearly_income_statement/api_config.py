"""
API Configuration for Yearly Income Statement Dashboard

This file documents all available API endpoints for the dashboard.
"""

API_ENDPOINTS = {
    # Basic Data Endpoints
    "get_budget_data": {
        "url": "/api/method/yearly_income_statement.api.get_budget_data",
        "method": "GET",
        "description": "Get budget data from Budget doctype",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "budget_data": "Array of budget records",
            "filters": "Applied filters"
        }
    },
    
    "get_actual_data": {
        "url": "/api/method/yearly_income_statement.api.get_actual_data",
        "method": "GET",
        "description": "Get actual data from GL Entry",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center, from_date, to_date"
        },
        "returns": {
            "actual_data": "Array of actual expense records",
            "filters": "Applied filters"
        }
    },
    
    "get_forecast_data": {
        "url": "/api/method/yearly_income_statement.api.get_forecast_data",
        "method": "GET",
        "description": "Get forecast data (placeholder for custom forecast doctype)",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "forecast_data": "Array of forecast records",
            "filters": "Applied filters"
        }
    },
    
    # Combined Dashboard Endpoints
    "get_dashboard_data": {
        "url": "/api/method/yearly_income_statement.api.get_dashboard_data",
        "method": "GET",
        "description": "Get combined dashboard data with budget, actual, and forecast",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "dashboard_data": "Array of processed dashboard rows",
            "filters": "Applied filters"
        }
    },
    
    "get_comprehensive_dashboard_data": {
        "url": "/api/method/yearly_income_statement.advanced_api.get_comprehensive_dashboard_data",
        "method": "GET",
        "description": "Get comprehensive dashboard data with historical comparisons",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "dashboard_data": "Array of comprehensive dashboard rows with all periods",
            "filters": "Applied filters"
        }
    },
    
    # Historical Data Endpoints
    "get_historical_data": {
        "url": "/api/method/yearly_income_statement.advanced_api.get_historical_data",
        "method": "GET",
        "description": "Get historical data for year-over-year comparisons",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "current_year": "Current fiscal year data",
            "previous_year": "Previous fiscal year data",
            "filters": "Applied filters"
        }
    },
    
    "get_ytd_data": {
        "url": "/api/method/yearly_income_statement.advanced_api.get_ytd_data",
        "method": "GET",
        "description": "Get Year-to-Date data with proportional budget calculations",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "ytd_budget_data": "YTD budget data",
            "ytd_actual_data": "YTD actual data",
            "ytd_ratio": "YTD ratio calculation",
            "from_date": "YTD start date",
            "to_date": "YTD end date",
            "filters": "Applied filters"
        }
    },
    
    "get_forecast_calculations": {
        "url": "/api/method/yearly_income_statement.advanced_api.get_forecast_calculations",
        "method": "GET",
        "description": "Calculate forecast data based on trends and historical data",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "forecast_data": "Array of forecast calculations",
            "filters": "Applied filters"
        }
    },
    
    # Summary Data Endpoints
    "get_summary_data": {
        "url": "/api/method/yearly_income_statement.api.get_summary_data",
        "method": "GET",
        "description": "Get summary data for dashboard cards",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center"
        },
        "returns": {
            "summary": {
                "total_budget": "Total budget amount",
                "total_actual": "Total actual amount",
                "total_variance": "Total variance",
                "ytd_budget": "YTD budget amount",
                "ytd_actual": "YTD actual amount",
                "ytd_variance": "YTD variance",
                "forecast_budget": "Forecast budget amount",
                "forecast_actual": "Forecast actual amount",
                "forecast_variance": "Forecast variance"
            },
            "filters": "Applied filters"
        }
    },
    
    # Filter Data Endpoints
    "get_companies": {
        "url": "/api/method/yearly_income_statement.api.get_companies",
        "method": "GET",
        "description": "Get list of companies for filter dropdown",
        "parameters": {},
        "returns": {
            "companies": "Array of company records with name and company_name"
        }
    },
    
    "get_fiscal_years": {
        "url": "/api/method/yearly_income_statement.api.get_fiscal_years",
        "method": "GET",
        "description": "Get list of fiscal years for filter dropdown",
        "parameters": {},
        "returns": {
            "fiscal_years": "Array of fiscal year records with name, year_start_date, year_end_date"
        }
    },
    
    "get_cost_centers": {
        "url": "/api/method/yearly_income_statement.api.get_cost_centers",
        "method": "GET",
        "description": "Get list of cost centers for filter dropdown",
        "parameters": {
            "filters": "JSON object with company (optional)"
        },
        "returns": {
            "cost_centers": "Array of cost center records with name, cost_center_name, cost_center_number"
        }
    },
    
    "get_expense_accounts": {
        "url": "/api/method/yearly_income_statement.api.get_expense_accounts",
        "method": "GET",
        "description": "Get list of expense accounts for filter dropdown",
        "parameters": {
            "filters": "JSON object with company (optional)"
        },
        "returns": {
            "accounts": "Array of account records with name, account_name, account_type"
        }
    },
    
    # Export Endpoints
    "export_dashboard_data": {
        "url": "/api/method/yearly_income_statement.advanced_api.export_dashboard_data",
        "method": "GET",
        "description": "Export dashboard data in various formats",
        "parameters": {
            "filters": "JSON object with company, fiscal_year, cost_center",
            "format": "Export format (excel, csv, pdf)"
        },
        "returns": {
            "export_data": "Formatted data for export",
            "format": "Export format",
            "filters": "Applied filters"
        }
    }
}

# Sample API Usage
SAMPLE_USAGE = {
    "get_dashboard_data": {
        "request": {
            "filters": {
                "company": "Your Company",
                "fiscal_year": "2024-2025",
                "cost_center": "Main Cost Center"
            }
        },
        "response": {
            "dashboard_data": [
                {
                    "account": "Expense Account 1",
                    "account_name": "Office Supplies",
                    "cost_center": "Main Cost Center",
                    "last_year_budget": 10000,
                    "last_year_actual": 9500,
                    "last_year_act_bud": 95.0,
                    "this_year_budget": 11000,
                    "this_year_actual": 10500,
                    "this_year_act_bud": 95.45,
                    "ytd_budget": 8250,
                    "ytd_actual": 7875,
                    "ytd_act_bud": 95.45,
                    "forecast_budget": 12100,
                    "forecast_actual": 11550,
                    "forecast_act_bud": 95.45
                }
            ],
            "filters": {
                "company": "Your Company",
                "fiscal_year": "2024-2025",
                "cost_center": "Main Cost Center"
            }
        }
    }
}

# Data Structure Definitions
DATA_STRUCTURES = {
    "dashboard_row": {
        "account": "Account name",
        "account_name": "Account display name",
        "cost_center": "Cost center name",
        "last_year_budget": "Last year budget amount",
        "last_year_actual": "Last year actual amount",
        "last_year_act_bud": "Last year actual/budget ratio (%)",
        "this_year_budget": "This year budget amount",
        "this_year_actual": "This year actual amount",
        "this_year_act_bud": "This year actual/budget ratio (%)",
        "this_year_vs_last_year": "This year vs last year ratio (%)",
        "ytd_budget": "Year-to-date budget amount",
        "ytd_actual": "Year-to-date actual amount",
        "ytd_act_bud": "YTD actual/budget ratio (%)",
        "ytd_vs_last_year": "YTD vs last year ratio (%)",
        "forecast_budget": "Forecast budget amount",
        "forecast_actual": "Forecast actual amount",
        "forecast_act_bud": "Forecast actual/budget ratio (%)",
        "forecast_vs_last_year": "Forecast vs last year ratio (%)"
    },
    
    "summary_data": {
        "total_budget": "Total budget amount",
        "total_actual": "Total actual amount",
        "total_variance": "Total variance (budget - actual)",
        "ytd_budget": "YTD budget amount",
        "ytd_actual": "YTD actual amount",
        "ytd_variance": "YTD variance",
        "forecast_budget": "Forecast budget amount",
        "forecast_actual": "Forecast actual amount",
        "forecast_variance": "Forecast variance"
    }
}

# Error Handling
ERROR_CODES = {
    "INVALID_FILTERS": "Invalid filter parameters provided",
    "NO_DATA_FOUND": "No data found for the specified filters",
    "INVALID_COMPANY": "Company not found or access denied",
    "INVALID_FISCAL_YEAR": "Fiscal year not found",
    "INVALID_COST_CENTER": "Cost center not found",
    "DATABASE_ERROR": "Database error occurred",
    "PERMISSION_DENIED": "Permission denied to access data"
} 