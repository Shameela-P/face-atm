<script lang="ts">
	import { 
		FileText, Download, BarChart3, ShieldAlert, ArrowRightLeft, 
		Users, CheckCircle2, LifeBuoy, Fingerprint, TrendingUp, TrendingDown, Layers
	} from '@lucide/svelte';

	let { data } = $props();

	function downloadCsv(type: 'customers' | 'transactions' | 'incidents') {
		let csvContent = 'data:text/csv;charset=utf-8,';
		
		if (type === 'customers') {
			csvContent += 'Customer ID,Name,Email,Card Number,Account Number,Balance,Created At\n';
			data.customers.forEach((c: any) => {
				const maskedCard = c.card ? '**** **** **** ' + c.card.slice(-4) : 'N/A';
				csvContent += `"${c.id}","${c.name}","${c.email}","${maskedCard}","${c.account}",${c.balance},"${c.createdAt}"\n`;
			});
		} else if (type === 'transactions') {
			csvContent += 'Transaction ID,Customer ID,Name,Type,Amount,Balance After,Timestamp\n';
			data.transactions.forEach((t: any) => {
				csvContent += `"${t.id}","${t.customerId}","${t.name}","${t.type}",${t.amount},${t.balanceAfter},"${t.timestamp}"\n`;
			});
		} else if (type === 'incidents') {
			csvContent += 'Incident ID,Customer ID,Card Number,Incident Type,Status,Timestamp\n';
			data.incidents.forEach((i: any) => {
				const maskedCard = i.card ? '**** **** **** ' + i.card.slice(-4) : 'N/A';
				csvContent += `"${i.id}","${i.customerId}","${maskedCard}","${i.type}","${i.status}","${i.timestamp}"\n`;
			});
		}

		const encodedUri = encodeURI(csvContent);
		const link = document.createElement('a');
		link.setAttribute('href', encodedUri);
		link.setAttribute('download', `${type}_report_${new Date().toISOString().split('T')[0]}.csv`);
		document.body.appendChild(link);
		link.click();
		document.body.removeChild(link);
	}
</script>

<svelte:head>
	<title>Executive Reports - Admin Command Center</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
					<FileText class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-2xl font-bold text-white tracking-tight">Executive Analytics & Audit Reports</h1>
					<p class="text-slate-400 text-sm mt-0.5">Real-time Firebase metrics breakdown & downloadable audit CSV ledgers</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Summary Matrix -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Registered Customers</p>
					<h3 class="text-2xl font-bold text-white mt-1">{data.reportSummary.totalCustomers}</h3>
				</div>
				<div class="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
					<Users class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-slate-400">Total verified biometric accounts</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">ATM Transactions</p>
					<h3 class="text-2xl font-bold text-white mt-1">{data.reportSummary.totalTransactions}</h3>
				</div>
				<div class="p-3 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
					<ArrowRightLeft class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-slate-400">Total deposits & withdrawals</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Deposited Volume</p>
					<h3 class="text-2xl font-bold text-emerald-400 mt-1">₹{data.reportSummary.totalDeposits.toLocaleString('en-IN')}</h3>
				</div>
				<div class="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
					<TrendingUp class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-emerald-400/80">Cumulative deposited funds</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Security Incidents</p>
					<h3 class="text-2xl font-bold text-rose-400 mt-1">{data.reportSummary.securityIncidentsCount}</h3>
				</div>
				<div class="p-3 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
					<ShieldAlert class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-rose-400/80">Face mismatches & spoof attempts</div>
		</div>
	</div>

	<!-- System Module Audits Summary Grid -->
	<div class="grid grid-cols-1 md:grid-cols-3 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-4">
			<div class="flex items-center gap-3">
				<div class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
					<Fingerprint class="w-5 h-5" />
				</div>
				<div>
					<h4 class="font-bold text-white text-sm">Biometric Scans Report</h4>
					<p class="text-xs text-slate-400">FaceNet 1:1 Verification</p>
				</div>
			</div>
			<div class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs flex justify-between items-center">
				<span class="text-slate-400">Total Scans Executed:</span>
				<span class="font-bold text-cyan-400">{data.reportSummary.verificationsCount}</span>
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-4">
			<div class="flex items-center gap-3">
				<div class="p-2 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
					<TrendingDown class="w-5 h-5" />
				</div>
				<div>
					<h4 class="font-bold text-white text-sm">Withdrawal Volume Report</h4>
					<p class="text-xs text-slate-400">ATM Cash Dispensed</p>
				</div>
			</div>
			<div class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs flex justify-between items-center">
				<span class="text-slate-400">Total Dispensed:</span>
				<span class="font-bold text-amber-400">₹{data.reportSummary.totalWithdrawals.toLocaleString('en-IN')}</span>
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm space-y-4">
			<div class="flex items-center gap-3">
				<div class="p-2 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
					<LifeBuoy class="w-5 h-5" />
				</div>
				<div>
					<h4 class="font-bold text-white text-sm">Customer Complaints</h4>
					<p class="text-xs text-slate-400">Support Ticket Log</p>
				</div>
			</div>
			<div class="bg-slate-950 p-3 rounded-lg border border-slate-800 text-xs flex justify-between items-center">
				<span class="text-slate-400">Recorded Tickets:</span>
				<span class="font-bold text-brand-400">{data.reportSummary.complaintsCount}</span>
			</div>
		</div>
	</div>

	<!-- Export Cards -->
	<h3 class="text-lg font-bold text-white tracking-tight pt-2">Downloadable Audit CSV Reports</h3>
	<div class="grid grid-cols-1 md:grid-cols-3 gap-6">
		<!-- Customer Report Card -->
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6 backdrop-blur-sm flex flex-col justify-between space-y-6">
			<div class="space-y-3">
				<div class="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center">
					<Users class="w-6 h-6" />
				</div>
				<div>
					<h4 class="text-base font-bold text-white">Customer Audit Ledger</h4>
					<p class="text-xs text-slate-400 mt-1 leading-relaxed">
						Complete customer register including masked card numbers, account numbers, registered emails, and dates.
					</p>
				</div>
			</div>
			<button 
				onclick={() => downloadCsv('customers')}
				class="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors"
			>
				<Download class="w-4 h-4 text-brand-400" />
				Export Customers CSV
			</button>
		</div>

		<!-- Transaction Report Card -->
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6 backdrop-blur-sm flex flex-col justify-between space-y-6">
			<div class="space-y-3">
				<div class="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center justify-center">
					<ArrowRightLeft class="w-6 h-6" />
				</div>
				<div>
					<h4 class="text-base font-bold text-white">Transaction History Ledger</h4>
					<p class="text-xs text-slate-400 mt-1 leading-relaxed">
						Audit log of all ATM deposits and withdrawals, transaction amounts, resulting balances, and timestamps.
					</p>
				</div>
			</div>
			<button 
				onclick={() => downloadCsv('transactions')}
				class="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors"
			>
				<Download class="w-4 h-4 text-purple-400" />
				Export Transactions CSV
			</button>
		</div>

		<!-- Security Incident Report Card -->
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-6 backdrop-blur-sm flex flex-col justify-between space-y-6">
			<div class="space-y-3">
				<div class="w-12 h-12 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20 flex items-center justify-center">
					<ShieldAlert class="w-6 h-6" />
				</div>
				<div>
					<h4 class="text-base font-bold text-white">Security Alerts Ledger</h4>
					<p class="text-xs text-slate-400 mt-1 leading-relaxed">
						Log of unauthorized access attempts, face mismatch rejections, anti-spoofing flags, and timestamps.
					</p>
				</div>
			</div>
			<button 
				onclick={() => downloadCsv('incidents')}
				class="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs flex items-center justify-center gap-2 border border-slate-700 transition-colors"
			>
				<Download class="w-4 h-4 text-rose-400" />
				Export Security Alerts CSV
			</button>
		</div>
	</div>
</div>
