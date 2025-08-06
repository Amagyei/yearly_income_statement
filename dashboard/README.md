# Yearly Income Statement Dashboard

A comprehensive Vue.js dashboard for tracking expenses, budgets, and forecasts across multiple periods.

## Features

- **Multi-Period Analysis**: Compare Last Year, Year-to-Date, and Forecast data
- **Advanced Filtering**: Filter by company, fiscal year, cost center, and date range
- **Real-time Data**: Connected to Frappe/ERPNext backend APIs
- **Interactive Table**: Sortable columns with visual indicators
- **Export Functionality**: Export data in various formats
- **Responsive Design**: Works on desktop and mobile devices

## Dashboard Structure

### Summary Cards
- **Last Year Total**: Budget, actual, and variance for previous year
- **Year to Date**: Current year progress with proportional calculations
- **Forecast**: Projected data based on trends and historical analysis

### Data Table
The main table displays expense categories with the following columns:

#### Last Year Section
- Budget amount
- Actual amount
- Act/Bud ratio (%)
- This Year amount
- Act/Last Year ratio (%)

#### Year to Date Section
- Budget amount (proportional)
- Actual amount
- Act/Bud ratio (%)
- This Year amount
- Act/Last Year ratio (%)

#### Forecast Section
- Budget amount
- Projected amount
- Act/Bud ratio (%)
- This Year amount
- Act/Last Year ratio (%)

## API Endpoints

The dashboard connects to the following backend endpoints:

### Data Endpoints
- `get_comprehensive_dashboard_data`: Main dashboard data
- `get_summary_data`: Summary card data
- `get_historical_data`: Year-over-year comparisons
- `get_ytd_data`: Year-to-date calculations
- `get_forecast_calculations`: Trend-based forecasts

### Filter Endpoints
- `get_companies`: Company list
- `get_fiscal_years`: Fiscal year list
- `get_cost_centers`: Cost center list
- `get_expense_accounts`: Expense account list

### Export Endpoints
- `export_dashboard_data`: Export functionality

## Development

### Prerequisites
- Node.js 18+
- Vue 3
- Tailwind CSS

### Installation
```bash
npm install
```

### Development Server
```bash
npm run dev
```

### Build
```bash
npm run build
```

## Project Structure

```
src/
├── components/
│   ├── Dashboard.vue          # Main dashboard component
│   ├── DashboardFilters.vue   # Filter controls
│   ├── DashboardTable.vue     # Data table
│   └── ui/                    # UI components
├── services/
│   └── api.js                # API service
├── data/
│   └── session.js            # Session management
└── utils/                    # Utility functions
```

## Design System

The dashboard uses a custom design system with:

- **Color Variables**: HSL-based color system with light/dark mode support
- **Typography**: Consistent text hierarchy
- **Spacing**: Tailwind-based spacing system
- **Shadows**: Custom shadow variables for depth
- **Transitions**: Smooth animations and transitions

## Data Flow

1. **Initial Load**: Dashboard loads filter options and default data
2. **Filter Changes**: User selects filters, triggers API calls
3. **Data Transformation**: API responses transformed to component format
4. **Rendering**: Components render with real-time data
5. **Export**: Data exported in selected format

## Backend Integration

The dashboard integrates with Frappe/ERPNext backend through:

- **CSRF Protection**: Secure API calls with CSRF tokens
- **Session Management**: User session handling
- **Error Handling**: Comprehensive error states
- **Loading States**: Visual feedback during API calls

## Customization

### Adding New Filters
1. Add filter to `DashboardFilters.vue`
2. Update API service
3. Modify backend endpoint

### Adding New Columns
1. Update table structure in `DashboardTable.vue`
2. Add data transformation in API service
3. Update backend data structure

### Styling Changes
1. Modify CSS variables in `index.css`
2. Update Tailwind config in `tailwind.config.js`
3. Adjust component classes as needed

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

This project is part of the Yearly Income Statement app for Frappe/ERPNext.
