<script lang="ts">
	import { CreditCard, Search, ShieldCheck, Landmark, DollarSign, UserCheck } from '@lucide/svelte';

	let { data } = $props();

	let searchTerm = $state('');
	let statusFilter = $state('ALL');

	function maskCard(cardNo: string) {
		if (!cardNo || cardNo === 'N/A') return 'N/A';
		if (cardNo.length <= 4) return cardNo;
		return '**** **** **** ' + cardNo.slice(-4);
	}

	function maskAccount(accNo: string) {
		if (!accNo || accNo === 'N/A') return 'N/A';
		if (accNo.length <= 4) return accNo;
		return '****' + accNo.slice(-4);
	}

	let filteredAccounts = $derived(
		data.accounts.filter(a => {
			const accNo = a.accountNumber || '';
			const name = a.customerName || '';
			const card = a.cardNumber || '';
			const bank = a.bank || '';

			const matchesSearch = 
				accNo.toLowerCase().includes(searchTerm.toLowerCase()) ||
				name.toLowerCase().includes(searchTerm.toLowerCase()) ||
				card.includes(searchTerm) ||
				bank.toLowerCase().includes(searchTerm.toLowerCase());
			
			const matchesStatus = statusFilter === 'ALL' || a.status === statusFilter;
			return matchesSearch && matchesStatus;
		})
	);
</script>

<svelte:head>
	<title>Accounts & Cards - SecureATM</title>
</svelte:head>

<div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight">Bank Accounts & Cards</h1>
		<p class="text-slate-400 text-xs sm:text-sm mt-1">Multi-account bank mappings and ATM card binding registry</p>
	</div>
</div>

<!-- Account Metrics Overview -->
<div class="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center shrink-0">
			<CreditCard class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Total Linked Accounts</p>
			<h3 class="text-2xl font-bold font-mono text-white">{data.accounts.length}</h3>
		</div>
	</div>

	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shrink-0">
			<DollarSign class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Total Account Deposits</p>
			<h3 class="text-2xl font-bold font-mono text-emerald-400">₹{data.totalBalance.toLocaleString()}</h3>
		</div>
	</div>

	<div class="bg-slate-900/90 p-5 rounded-2xl shadow-xl border border-slate-800/80 flex items-center gap-4">
		<div class="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center shrink-0">
			<Landmark class="w-6 h-6" />
		</div>
		<div>
			<p class="text-xs font-semibold text-slate-400 mb-1">Issuing Banking Node</p>
			<h3 class="text-lg font-bold text-white">SecureBank Network</h3>
		</div>
	</div>
</div>

<!-- Accounts Data Table -->
<div class="bg-slate-900/90 rounded-2xl shadow-xl border border-slate-800/80 overflow-hidden">
	<div class="p-4 border-b border-slate-800/80 flex flex-col md:flex-row justify-between items-center gap-4 bg-slate-950/40">
		<div class="relative w-full md:w-80">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
			<input 
				type="text" 
				bind:value={searchTerm}
				placeholder="Search account, customer, card..." 
				class="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-800 bg-slate-950 text-slate-200 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition-all text-xs placeholder:text-slate-500"
			/>
		</div>

		<div class="flex items-center gap-3 w-full md:w-auto justify-between md:justify-end">
			<select 
				bind:value={statusFilter}
				class="px-3 py-2 rounded-xl border border-slate-800 bg-slate-950 text-slate-200 text-xs focus:border-brand-500 outline-none font-medium"
			>
				<option value="ALL">All Statuses</option>
				<option value="ACTIVE">Active Only</option>
				<option value="SUSPENDED">Suspended Only</option>
			</select>
			<span class="text-xs text-slate-400 font-mono">Total: {filteredAccounts.length}</span>
		</div>
	</div>

	<div class="overflow-x-auto">
		<table class="w-full text-left text-xs whitespace-nowrap">
			<thead class="bg-slate-950/60 text-slate-400 border-b border-slate-800/80 uppercase tracking-wider font-mono">
				<tr>
					<th class="px-6 py-4 font-semibold">Account Number</th>
					<th class="px-6 py-4 font-semibold">Customer Name</th>
					<th class="px-6 py-4 font-semibold">ATM Card Number</th>
					<th class="px-6 py-4 font-semibold">Bank / Branch</th>
					<th class="px-6 py-4 font-semibold text-right">Available Balance</th>
					<th class="px-6 py-4 font-semibold text-center">Status</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-800/50 text-slate-300 font-mono">
				{#each filteredAccounts as acc}
					<tr class="hover:bg-slate-800/40 transition-colors">
						<td class="px-6 py-4 font-bold text-slate-100">{maskAccount(acc.accountNumber)}</td>
						<td class="px-6 py-4 font-sans">
							<div class="font-bold text-slate-100">{acc.customerName}</div>
							<div class="text-[11px] text-slate-500">{acc.email}</div>
						</td>
						<td class="px-6 py-4 text-slate-400">
							{maskCard(acc.cardNumber)}
						</td>
						<td class="px-6 py-4 font-sans">
							<div class="text-slate-200 font-semibold">{acc.bank}</div>
							<div class="text-[11px] text-slate-500">{acc.branch}</div>
						</td>
						<td class="px-6 py-4 text-right font-bold text-emerald-400">
							₹{(acc.balance ?? 0).toLocaleString()}
						</td>
						<td class="px-6 py-4 text-center font-sans">
							<span class={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${acc.status === 'ACTIVE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'}`}>
								<UserCheck class="w-3.5 h-3.5" />
								{acc.status}
							</span>
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="6" class="px-6 py-12 text-center text-slate-500 font-sans">
							No matching accounts found in Firebase Realtime Database.
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>
