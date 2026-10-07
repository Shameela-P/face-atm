<script lang="ts">
	import { enhance } from '$app/forms';
	import { 
		LogOut, ArrowDownToLine, ArrowUpToLine, History, Wallet, 
		CheckCircle2, AlertCircle, Loader2, X, ShieldCheck, CreditCard, Landmark, Eye
	} from '@lucide/svelte';

	let { data, form } = $props();

	let activeModal = $state<'none' | 'withdraw' | 'deposit' | 'history' | 'balance'>('none');
	let amount = $state('');
	let loading = $state(false);

	function openModal(type: 'withdraw' | 'deposit' | 'history' | 'balance') {
		activeModal = type;
		amount = '';
	}

	function closeModal() {
		activeModal = 'none';
	}

	function maskCard(card: string) {
		if (!card) return '**** **** **** ****';
		const clean = card.replace(/\s+/g, '');
		if (clean.length < 4) return '**** **** **** ' + clean;
		return '**** **** **** ' + clean.slice(-4);
	}
</script>

<svelte:head>
	<title>ATM Terminal - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 relative font-sans text-slate-100 overflow-hidden">
	<!-- Cyber Grid & Ambient Background -->
	<div class="absolute inset-0 bg-radial from-brand-950/30 via-slate-950 to-slate-950 pointer-events-none"></div>
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px]"></div>

	<div class="max-w-4xl w-full relative z-10 space-y-6">
		
		<!-- ATM Terminal Header Bar -->
		<div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row items-center justify-between gap-4">
			<div class="flex items-center gap-3">
				<div class="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center shadow-lg shadow-emerald-500/10">
					<ShieldCheck class="w-7 h-7" />
				</div>
				<div>
					<h1 class="text-xl font-bold text-white tracking-tight">Welcome, {data.user.name}</h1>
					<p class="text-xs text-slate-400 font-mono mt-0.5">
						ATM Card: <span class="text-cyan-400 font-bold">{maskCard(data.user.card)}</span>
					</p>
				</div>
			</div>

			<div class="flex items-center gap-3">
				<div class="hidden sm:block text-right">
					<span class="text-[11px] text-slate-500 font-mono block">SESSION AUTHENTICATED</span>
					<span class="text-xs text-emerald-400 font-semibold flex items-center justify-end gap-1">
						<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
						FaceNet 1:1 Verified
					</span>
				</div>

				<form method="POST" action="?/logout">
					<button
						type="submit"
						class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-rose-500/20 hover:text-rose-400 text-slate-300 border border-slate-700 hover:border-rose-500/30 transition-all font-semibold text-xs"
					>
						<LogOut class="w-4 h-4" />
						Exit Session
					</button>
				</form>
			</div>
		</div>

		<!-- Alert Banners -->
		{#if form?.message}
			<div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center gap-3 text-emerald-400 text-sm font-medium animate-in fade-in">
				<CheckCircle2 class="w-5 h-5 shrink-0 text-emerald-400" />
				<p>{form.message}</p>
			</div>
		{/if}

		{#if form?.error}
			<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-center gap-3 text-rose-400 text-sm font-medium animate-in fade-in">
				<AlertCircle class="w-5 h-5 shrink-0 text-rose-400" />
				<p>{form.error}</p>
			</div>
		{/if}

		<!-- Main Dashboard Interface -->
		<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
			
			<!-- Balance & Account Card -->
			<div class="lg:col-span-2 bg-gradient-to-br from-slate-900 via-slate-900 to-brand-950/80 border border-slate-800 rounded-3xl p-8 text-white shadow-2xl relative overflow-hidden backdrop-blur-xl flex flex-col justify-between min-h-[260px]">
				<div class="absolute top-0 right-0 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none"></div>

				<div class="relative z-10 space-y-2">
					<div class="flex justify-between items-start">
						<div>
							<p class="text-xs font-semibold uppercase tracking-wider text-slate-400">Available Account Balance</p>
							<h2 class="text-5xl font-black text-white tracking-tight mt-1">₹{(data.user.deposit ?? 0).toLocaleString('en-IN')}</h2>
						</div>
						<div class="p-3 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
							<Landmark class="w-6 h-6" />
						</div>
					</div>
				</div>

				<div class="relative z-10 pt-6 border-t border-slate-800/80 flex flex-wrap items-center justify-between gap-4">
					<div class="text-xs text-slate-400 space-y-0.5">
						<p><span class="text-slate-500">Bank:</span> <strong class="text-slate-200">{data.accounts[0]?.bank || 'SecureBank'}</strong></p>
						<p><span class="text-slate-500">Account:</span> <strong class="text-slate-200 font-mono">{data.user.accno}</strong></p>
					</div>

					<button 
						onclick={() => openModal('history')}
						class="px-5 py-2.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs font-semibold transition-all inline-flex items-center gap-2"
					>
						<History class="w-4 h-4" />
						View Mini Statement
					</button>
				</div>
			</div>

			<!-- Large Touch Action Buttons Grid -->
			<div class="bg-slate-900/80 border border-slate-800 rounded-3xl p-6 shadow-2xl backdrop-blur-xl flex flex-col justify-center space-y-4">
				<h3 class="text-xs font-bold uppercase tracking-wider text-slate-400 text-center">Select ATM Transaction</h3>
				
				<div class="grid grid-cols-2 gap-3">
					<button 
						onclick={() => openModal('withdraw')}
						class="flex flex-col items-center justify-center gap-2 p-5 rounded-2xl bg-slate-950 hover:bg-brand-500/10 border border-slate-800 hover:border-brand-500/40 text-slate-200 hover:text-brand-400 transition-all active:scale-[0.97] group"
					>
						<div class="p-3 rounded-xl bg-brand-500/10 border border-brand-500/20 text-brand-400 group-hover:scale-110 transition-transform">
							<ArrowDownToLine class="w-6 h-6" />
						</div>
						<span class="text-xs font-bold">Withdrawal</span>
					</button>

					<button 
						onclick={() => openModal('deposit')}
						class="flex flex-col items-center justify-center gap-2 p-5 rounded-2xl bg-slate-950 hover:bg-emerald-500/10 border border-slate-800 hover:border-emerald-500/40 text-slate-200 hover:text-emerald-400 transition-all active:scale-[0.97] group"
					>
						<div class="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 group-hover:scale-110 transition-transform">
							<ArrowUpToLine class="w-6 h-6" />
						</div>
						<span class="text-xs font-bold">Deposit</span>
					</button>

					<button 
						onclick={() => openModal('withdraw')}
						class="flex flex-col items-center justify-center gap-2 p-5 rounded-2xl bg-slate-950 hover:bg-purple-500/10 border border-slate-800 hover:border-purple-500/40 text-slate-200 hover:text-purple-400 transition-all active:scale-[0.97] group"
					>
						<div class="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-purple-400 group-hover:scale-110 transition-transform">
							<Wallet class="w-6 h-6" />
						</div>
						<span class="text-xs font-bold">Fast Cash</span>
					</button>

					<button 
						onclick={() => openModal('history')}
						class="flex flex-col items-center justify-center gap-2 p-5 rounded-2xl bg-slate-950 hover:bg-cyan-500/10 border border-slate-800 hover:border-cyan-500/40 text-slate-200 hover:text-cyan-400 transition-all active:scale-[0.97] group"
					>
						<div class="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 group-hover:scale-110 transition-transform">
							<History class="w-6 h-6" />
						</div>
						<span class="text-xs font-bold">Statement</span>
					</button>
				</div>
			</div>

		</div>
	</div>
</div>

<!-- Withdraw Modal -->
{#if activeModal === 'withdraw'}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
		<div class="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-6 shadow-2xl relative">
			<div class="flex justify-between items-center border-b border-slate-800 pb-4">
				<div class="flex items-center gap-3">
					<div class="p-2.5 rounded-xl bg-brand-500/10 text-brand-400 border border-brand-500/20">
						<ArrowDownToLine class="w-5 h-5" />
					</div>
					<div>
						<h3 class="text-lg font-bold text-white">Cash Withdrawal</h3>
						<p class="text-xs text-slate-400">Available: ₹{(data.user.deposit ?? 0).toLocaleString('en-IN')}</p>
					</div>
				</div>
				<button onclick={closeModal} class="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<form 
				method="POST" 
				action="?/withdraw"
				use:enhance={() => {
					loading = true;
					return async ({ update }) => {
						await update();
						loading = false;
						closeModal();
					};
				}}
				class="space-y-4"
			>
				<div>
					<label for="amount" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
						Withdrawal Amount (₹)
					</label>
					<input 
						type="number" 
						id="amount" 
						name="amount" 
						bind:value={amount}
						placeholder="Enter amount..." 
						min="100"
						step="100"
						required 
						class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3.5 text-2xl font-mono text-center text-white placeholder-slate-600 focus:outline-none focus:border-brand-500 transition-colors"
					/>
				</div>

				<div>
					<span class="block text-[11px] font-semibold text-slate-500 uppercase tracking-wider mb-2">Quick Presets</span>
					<div class="grid grid-cols-3 gap-2">
						{#each [500, 1000, 2000, 5000, 10000, 20000] as preset}
							<button 
								type="button" 
								onclick={() => amount = preset.toString()} 
								class="py-2.5 text-xs font-bold font-mono bg-slate-950 hover:bg-brand-500/20 hover:text-brand-400 text-slate-300 rounded-xl transition-colors border border-slate-800 hover:border-brand-500/30"
							>
								₹{preset.toLocaleString('en-IN')}
							</button>
						{/each}
					</div>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-800">
					<button type="button" onclick={closeModal} class="px-5 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold transition-colors">
						Cancel
					</button>
					<button 
						type="submit" 
						disabled={loading || !amount}
						class="flex items-center gap-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 text-white px-6 py-2.5 rounded-xl font-bold text-xs transition-all shadow-lg shadow-brand-500/20 disabled:opacity-40"
					>
						{#if loading}
							<Loader2 class="w-4 h-4 animate-spin" />
							Processing...
						{:else}
							Confirm Withdrawal
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Deposit Modal -->
{#if activeModal === 'deposit'}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
		<div class="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 space-y-6 shadow-2xl relative">
			<div class="flex justify-between items-center border-b border-slate-800 pb-4">
				<div class="flex items-center gap-3">
					<div class="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
						<ArrowUpToLine class="w-5 h-5" />
					</div>
					<div>
						<h3 class="text-lg font-bold text-white">Cash Deposit</h3>
						<p class="text-xs text-slate-400">Account: {data.user.accno}</p>
					</div>
				</div>
				<button onclick={closeModal} class="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<form 
				method="POST" 
				action="?/deposit"
				use:enhance={() => {
					loading = true;
					return async ({ update }) => {
						await update();
						loading = false;
						closeModal();
					};
				}}
				class="space-y-4"
			>
				<div>
					<label for="depositAmount" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
						Deposit Amount (₹)
					</label>
					<input 
						type="number" 
						id="depositAmount" 
						name="amount" 
						bind:value={amount}
						placeholder="Enter deposit amount..." 
						min="100"
						step="100"
						required 
						class="w-full bg-slate-950 border border-slate-800 rounded-2xl px-4 py-3.5 text-2xl font-mono text-center text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500 transition-colors"
					/>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-800">
					<button type="button" onclick={closeModal} class="px-5 py-2.5 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-xs font-semibold transition-colors">
						Cancel
					</button>
					<button 
						type="submit" 
						disabled={loading || !amount}
						class="flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white px-6 py-2.5 rounded-xl font-bold text-xs transition-all shadow-lg shadow-emerald-500/20 disabled:opacity-40"
					>
						{#if loading}
							<Loader2 class="w-4 h-4 animate-spin" />
							Processing...
						{:else}
							Confirm Deposit
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- History Statement Modal -->
{#if activeModal === 'history'}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
		<div class="bg-slate-900 border border-slate-800 rounded-3xl max-w-xl w-full p-6 space-y-6 shadow-2xl relative max-h-[85vh] overflow-y-auto">
			<div class="flex justify-between items-center border-b border-slate-800 pb-4">
				<div class="flex items-center gap-3">
					<div class="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
						<History class="w-5 h-5" />
					</div>
					<div>
						<h3 class="text-lg font-bold text-white">Account Mini Statement</h3>
						<p class="text-xs text-slate-400 font-mono">Account #{data.user.accno}</p>
					</div>
				</div>
				<button onclick={closeModal} class="p-2 rounded-xl bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<div class="space-y-2.5">
				{#each data.transactions as tx}
					<div class="flex justify-between items-center p-3.5 bg-slate-950 rounded-xl border border-slate-800/80">
						<div>
							<span class="font-semibold text-sm text-slate-200">{tx.name}</span>
							<p class="text-[11px] text-slate-500 font-mono mt-0.5">{new Date(tx.rdate).toLocaleString()}</p>
						</div>
						<div class="text-right">
							<span class="font-bold font-mono text-sm {tx.name === 'Deposit' ? 'text-emerald-400' : 'text-slate-200'}">
								{tx.name === 'Deposit' ? '+' : '-'}₹{tx.amount.toLocaleString('en-IN')}
							</span>
						</div>
					</div>
				{:else}
					<div class="text-center py-8 text-slate-500 text-xs">
						No transaction records found for this account.
					</div>
				{/each}
			</div>

			<div class="pt-2 flex justify-end">
				<button onclick={closeModal} class="px-5 py-2.5 rounded-xl bg-slate-800 text-white text-xs font-semibold hover:bg-slate-700 transition-colors">
					Close Statement
				</button>
			</div>
		</div>
	</div>
{/if}
