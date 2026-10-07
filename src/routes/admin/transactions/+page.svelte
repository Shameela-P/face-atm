<script lang="ts">
	import { ArrowDownToLine, ArrowUpToLine, Search, Filter, ArrowRightLeft, DollarSign } from '@lucide/svelte';
	let { data } = $props();
	
	let searchTerm = $state('');
	
	function maskAccount(accNo: string) {
		if (!accNo || accNo === 'N/A') return 'N/A';
		if (accNo.length <= 4) return accNo;
		return '****' + accNo.slice(-4);
	}

	let totalDeposits = $derived(
		data.transactions
			.filter(t => t.name === 'Deposit')
			.reduce((acc, t) => acc + (t.amount || 0), 0)
	);

	let totalWithdrawals = $derived(
		data.transactions
			.filter(t => t.name !== 'Deposit')
			.reduce((acc, t) => acc + (t.amount || 0), 0)
	);

	let filteredTx = $derived(
		data.transactions.filter(t => 
			(t.userName?.toLowerCase() || '').includes(searchTerm.toLowerCase()) || 
			t.accno.includes(searchTerm) ||
			t.name.toLowerCase().includes(searchTerm.toLowerCase())
		)
	);
</script>

<svelte:head>
	<title>Transactions Ledger - SecureATM</title>
</svelte:head>

<div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight">Global Transaction Ledger</h1>
		<p class="text-slate-400 text-xs sm:text-sm mt-1">Audit log of all ATM deposits and withdrawal operations</p>
	</div>
</div>

<!-- Transaction Metrics Overview -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center shrink-0">
			<ArrowRightLeft class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Total Transactions</p>
			<h3 class="text-2xl font-bold font-mono text-white">{data.transactions.length}</h3>
		</div>
	</div>

	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
			<ArrowDownToLine class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Total Deposits Volume</p>
			<h3 class="text-2xl font-bold font-mono text-emerald-400">₹{totalDeposits.toLocaleString()}</h3>
		</div>
	</div>

	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
			<ArrowUpToLine class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Total Withdrawals Volume</p>
			<h3 class="text-2xl font-bold font-mono text-blue-400">₹{totalWithdrawals.toLocaleString()}</h3>
		</div>
	</div>
</div>

<div class="bg-slate-900/90 rounded-2xl shadow-xl border border-slate-800/80 overflow-hidden">
	<div class="p-4 border-b border-slate-800/80 flex justify-between items-center bg-slate-950/40">
		<div class="relative w-80">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
			<input 
				type="text" 
				bind:value={searchTerm}
				placeholder="Search by user, account, or type..." 
				class="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-800 bg-slate-950 text-slate-200 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition-all text-xs placeholder:text-slate-500"
			/>
		</div>
		<div class="text-xs text-slate-400 font-mono">
			Total Records: {filteredTx.length}
		</div>
	</div>

	<div class="overflow-x-auto">
		<table class="w-full text-left text-xs whitespace-nowrap">
			<thead class="bg-slate-950/60 text-slate-400 border-b border-slate-800/80 uppercase tracking-wider font-mono">
				<tr>
					<th class="px-6 py-4 font-semibold">TX ID</th>
					<th class="px-6 py-4 font-semibold">Operation Type</th>
					<th class="px-6 py-4 font-semibold">Account Owner</th>
					<th class="px-6 py-4 font-semibold">Account No</th>
					<th class="px-6 py-4 font-semibold text-right">Amount</th>
					<th class="px-6 py-4 font-semibold text-right">Timestamp</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-800/50 text-slate-300 font-mono">
				{#each filteredTx as tx}
					<tr class="hover:bg-slate-800/40 transition-colors">
						<td class="px-6 py-4 font-bold text-brand-400">#{tx.id}</td>
						<td class="px-6 py-4 font-sans">
							{#if tx.name === 'Deposit'}
								<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
									<ArrowDownToLine class="w-3.5 h-3.5" />
									DEPOSIT
								</span>
							{:else}
								<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
									<ArrowUpToLine class="w-3.5 h-3.5" />
									WITHDRAWAL
								</span>
							{/if}
						</td>
						<td class="px-6 py-4 font-sans">
							<div class="font-bold text-slate-100">{tx.userName || 'Customer'}</div>
							<div class="text-[11px] font-mono text-slate-500 mt-0.5">Customer ID: {tx.userId}</div>
						</td>
						<td class="px-6 py-4 text-slate-400">
							{maskAccount(tx.accno)}
						</td>
						<td class="px-6 py-4 text-right font-bold text-sm">
							<span class={tx.name === 'Deposit' ? 'text-emerald-400' : 'text-slate-100'}>
								{tx.name === 'Deposit' ? '+' : '-'}₹{tx.amount.toLocaleString()}
							</span>
						</td>
						<td class="px-6 py-4 text-right text-slate-400 font-sans text-xs">
							{tx.rdate}
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="px-6 py-12 text-center text-slate-500 font-sans">
							{#if searchTerm}
								No transactions found matching "{searchTerm}"
							{:else}
								No transactions recorded yet.
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
