<script lang="ts">
	import { enhance } from '$app/forms';
	import { LogOut, ArrowDownToLine, ArrowUpToLine, History, Wallet, CheckCircle2, AlertCircle, Loader2, X } from '@lucide/svelte';

	let { data, form } = $props();

	let activeModal = $state<'none' | 'withdraw' | 'deposit' | 'history'>('none');
	let amount = $state('');
	let loading = $state(false);

	function openModal(type: 'withdraw' | 'deposit' | 'history') {
		activeModal = type;
		amount = '';
	}

	function closeModal() {
		activeModal = 'none';
	}
</script>

<svelte:head>
	<title>Dashboard - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-900 flex flex-col items-center py-12 px-4">
	<div class="max-w-4xl w-full">
		
		<!-- Header -->
		<div class="flex justify-between items-center bg-white rounded-3xl p-6 shadow-xl mb-8">
			<div>
				<h1 class="text-2xl font-bold text-slate-900">Welcome, {data.user.name}</h1>
				<p class="text-slate-500 font-mono mt-1">Card: **** **** **** {(data.user.card || 'XXXX').slice(-4)}</p>
			</div>
			
			<form method="POST" action="?/logout">
				<button
					type="submit"
					class="flex items-center gap-2 px-5 py-2.5 rounded-xl text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors font-medium"
				>
					<LogOut class="w-5 h-5" />
					Exit
				</button>
			</form>
		</div>

		{#if form?.message}
			<div class="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-2xl flex items-center gap-3 text-green-400">
				<CheckCircle2 class="w-5 h-5 shrink-0" />
				<p class="text-sm font-medium">{form.message}</p>
			</div>
		{/if}

		{#if form?.error}
			<div class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-center gap-3 text-red-400">
				<AlertCircle class="w-5 h-5 shrink-0" />
				<p class="text-sm font-medium">{form.error}</p>
			</div>
		{/if}

		<!-- Dashboard Grid -->
		<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
			
			<!-- Balance Card -->
			<div class="col-span-full lg:col-span-2 bg-gradient-to-br from-brand-900 to-brand-800 rounded-3xl p-8 text-white shadow-xl shadow-brand-900/20 relative overflow-hidden">
				<div class="absolute -right-8 -top-8 w-48 h-48 bg-white/10 rounded-full blur-2xl"></div>
				<div class="relative z-10">
					<p class="text-brand-200 font-medium mb-2">Available Balance</p>
					<h2 class="text-5xl font-bold tracking-tight mb-8">₹{(data.user.deposit ?? 0).toLocaleString()}</h2>
					<div class="flex gap-4">
						<button 
							onclick={() => openModal('history')}
							class="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-6 py-3 rounded-xl font-medium transition-colors"
						>
							View Statement
						</button>
					</div>
				</div>
			</div>

			<!-- Quick Actions -->
			<div class="bg-white rounded-3xl p-8 shadow-xl flex flex-col justify-center">
				<h3 class="font-semibold text-slate-900 mb-6 text-lg">Quick Actions</h3>
				<div class="grid grid-cols-2 gap-4">
					<button 
						onclick={() => openModal('withdraw')}
						class="flex flex-col items-center justify-center gap-3 p-4 rounded-2xl bg-slate-50 hover:bg-brand-50 hover:text-brand-600 transition-colors text-slate-600 border border-slate-100"
					>
						<ArrowDownToLine class="w-6 h-6" />
						<span class="text-sm font-medium">Withdraw</span>
					</button>
					
					<button 
						onclick={() => openModal('deposit')}
						class="flex flex-col items-center justify-center gap-3 p-4 rounded-2xl bg-slate-50 hover:bg-brand-50 hover:text-brand-600 transition-colors text-slate-600 border border-slate-100"
					>
						<ArrowUpToLine class="w-6 h-6" />
						<span class="text-sm font-medium">Deposit</span>
					</button>

					<button 
						onclick={() => openModal('withdraw')}
						class="flex flex-col items-center justify-center gap-3 p-4 rounded-2xl bg-slate-50 hover:bg-brand-50 hover:text-brand-600 transition-colors text-slate-600 border border-slate-100"
					>
						<Wallet class="w-6 h-6" />
						<span class="text-sm font-medium">Fast Cash</span>
					</button>

					<button 
						onclick={() => openModal('history')}
						class="flex flex-col items-center justify-center gap-3 p-4 rounded-2xl bg-slate-50 hover:bg-brand-50 hover:text-brand-600 transition-colors text-slate-600 border border-slate-100"
					>
						<History class="w-6 h-6" />
						<span class="text-sm font-medium">History</span>
					</button>
				</div>
			</div>

		</div>
	</div>
</div>

<!-- Withdraw Modal -->
{#if activeModal === 'withdraw'}
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl relative">
			<div class="flex justify-between items-center mb-6">
				<h2 class="text-xl font-bold text-slate-900">Cash Withdrawal</h2>
				<button onclick={closeModal} class="text-slate-400 hover:text-slate-600 p-2 rounded-xl">
					<X class="w-6 h-6" />
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
					<label for="amount" class="block text-sm font-medium text-slate-700 mb-2">Withdrawal Amount (₹)</label>
					<input 
						type="number" 
						id="amount" 
						name="amount" 
						bind:value={amount}
						placeholder="500" 
						min="100"
						step="100"
						required 
						class="w-full px-4 py-3 border border-slate-200 rounded-xl text-lg font-mono focus:border-brand-500 outline-none"
					/>
				</div>

				<div class="grid grid-cols-3 gap-2">
					{#each [500, 1000, 2000, 5000, 10000, 20000] as preset}
						<button 
							type="button" 
							onclick={() => amount = preset.toString()} 
							class="py-2 text-xs font-semibold bg-slate-100 hover:bg-brand-50 hover:text-brand-600 rounded-lg transition-colors border border-slate-200"
						>
							₹{preset}
						</button>
					{/each}
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
					<button type="button" onclick={closeModal} class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-sm font-medium">Cancel</button>
					<button 
						type="submit" 
						disabled={loading || !amount}
						class="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-md shadow-brand-500/20 disabled:opacity-50"
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
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl relative">
			<div class="flex justify-between items-center mb-6">
				<h2 class="text-xl font-bold text-slate-900">Cash Deposit</h2>
				<button onclick={closeModal} class="text-slate-400 hover:text-slate-600 p-2 rounded-xl">
					<X class="w-6 h-6" />
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
					<label for="depositAmount" class="block text-sm font-medium text-slate-700 mb-2">Deposit Amount (₹)</label>
					<input 
						type="number" 
						id="depositAmount" 
						name="amount" 
						bind:value={amount}
						placeholder="1000" 
						min="100"
						step="100"
						required 
						class="w-full px-4 py-3 border border-slate-200 rounded-xl text-lg font-mono focus:border-brand-500 outline-none"
					/>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
					<button type="button" onclick={closeModal} class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-sm font-medium">Cancel</button>
					<button 
						type="submit" 
						disabled={loading || !amount}
						class="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-md shadow-brand-500/20 disabled:opacity-50"
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
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
		<div class="bg-white rounded-3xl max-w-xl w-full p-6 shadow-2xl relative max-h-[85vh] overflow-y-auto">
			<div class="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
				<div>
					<h2 class="text-xl font-bold text-slate-900">Transaction History</h2>
					<p class="text-xs text-slate-500">Account Mini Statement for {data.user.accno}</p>
				</div>
				<button onclick={closeModal} class="text-slate-400 hover:text-slate-600 p-2 rounded-xl">
					<X class="w-6 h-6" />
				</button>
			</div>

			<div class="space-y-3">
				{#each data.transactions as tx}
					<div class="flex justify-between items-center p-3.5 bg-slate-50 rounded-xl border border-slate-100">
						<div>
							<span class="font-semibold text-sm text-slate-900">{tx.name}</span>
							<p class="text-xs text-slate-500 mt-0.5">{tx.rdate}</p>
						</div>
						<div class="text-right">
							<span class="font-bold text-sm {tx.name === 'Deposit' ? 'text-green-600' : 'text-slate-900'}">
								{tx.name === 'Deposit' ? '+' : '-'}₹{tx.amount.toLocaleString()}
							</span>
						</div>
					</div>
				{:else}
					<p class="text-center py-8 text-slate-500 text-sm">No transaction records found for this account.</p>
				{/each}
			</div>
		</div>
	</div>
{/if}
