import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './index.css'

// Import custom components
import Dashboard from './components/Dashboard.vue'
import DashboardFilters from './components/DashboardFilters.vue'
import DashboardTable from './components/DashboardTable.vue'

// Import UI components
import Button from './components/ui/button.vue'
import Card from './components/ui/card.vue'
import CardContent from './components/ui/card-content.vue'
import CardHeader from './components/ui/card-header.vue'
import CardTitle from './components/ui/card-title.vue'
import Input from './components/ui/input.vue'
import Label from './components/ui/label.vue'
import Select from './components/ui/select.vue'
import SelectContent from './components/ui/select-content.vue'
import SelectItem from './components/ui/select-item.vue'
import SelectTrigger from './components/ui/select-trigger.vue'
import SelectValue from './components/ui/select-value.vue'
import Badge from './components/ui/badge.vue'
import Table from './components/ui/table.vue'
import TableBody from './components/ui/table-body.vue'
import TableCell from './components/ui/table-cell.vue'
import TableHead from './components/ui/table-head.vue'
import TableHeader from './components/ui/table-header.vue'
import TableRow from './components/ui/table-row.vue'

const globalComponents = {
	// Dashboard components
	Dashboard,
	DashboardFilters,
	DashboardTable,
	
	// UI components
	Button,
	Card,
	CardContent,
	CardHeader,
	CardTitle,
	Input,
	Label,
	Select,
	SelectContent,
	SelectItem,
	SelectTrigger,
	SelectValue,
	Badge,
	Table,
	TableBody,
	TableCell,
	TableHead,
	TableHeader,
	TableRow,
}

const app = createApp(App)

// Register global components
Object.entries(globalComponents).forEach(([name, component]) => {
	app.component(name, component)
})

app.use(router)
app.mount('#app')
