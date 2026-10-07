<script lang="ts">
	import { 
		Fingerprint, Search, ShieldCheck, ShieldAlert, AlertTriangle, 
		CheckCircle2, Clock, Eye, Lock, RefreshCw, Cpu
	} from '@lucide/svelte';

	let { data } = $props();

	let searchTerm = $state('');
	let resultFilter = $state('ALL');

	const records = $derived(data.records || []);

	const filteredRecords = $derived(
		records.filter((r: any) => {
			const matchesSearch = 
				r.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
				r.customerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
				r.cardNumber.includes(searchTerm);
			
			const matchesResult = resultFilter === 'ALL' || r.result === resultFilter;
			return matchesSearch && matchesResult;
		})
	);

	function maskCard(card: string) {
		if (!card) return '**** **** **** ****';
		const clean = card.replace(/\s+/g, '');
		if (clean.length < 4) return '**** **** **** ' + clean;
		return '**** **** **** ' + clean.slice(-4);
	}
</script>

<svelte:head>
	<title>Biometric Audit - Admin Command Center</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
					<Fingerprint class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-2xl font-bold text-white tracking-tight">Biometric Audit Log</h1>
					<p class="text-slate-400 text-sm mt-0.5">Audit log of 1:1 FaceNet embedding comparisons & anti-spoofing outcomes</p>
				</div>
			</div>
		</div>
		<div class="flex items-center gap-2">
			<span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
				<Cpu class="w-3.5 h-3.5" />
				MTCNN + Liveness + FaceNet Pipeline Active
			</span>
		</div>
	</div>

	<!-- Stats Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Scans</p>
					<h3 class="text-2xl font-bold text-white mt-1">{data.stats.total}</h3>
				</div>
				<div class="p-3 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/50">
					<Fingerprint class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-slate-400">Recorded ATM facial verifications</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Matches (Granted)</p>
					<h3 class="text-2xl font-bold text-emerald-400 mt-1">{data.stats.totalMatch}</h3>
				</div>
				<div class="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
					<ShieldCheck class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-emerald-400/80 flex items-center gap-1">
				<CheckCircle2 class="w-3.5 h-3.5" />
				1:1 identity verified
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Face Mismatches</p>
					<h3 class="text-2xl font-bold text-rose-400 mt-1">{data.stats.totalMismatch}</h3>
				</div>
				<div class="p-3 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
					<ShieldAlert class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-rose-400/80 flex items-center gap-1">
				<Lock class="w-3.5 h-3.5" />
				Wrong face rejected
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Spoofs Intercepted</p>
					<h3 class="text-2xl font-bold text-amber-400 mt-1">{data.stats.totalSpoof}</h3>
				</div>
				<div class="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
					<AlertTriangle class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-amber-400/80 flex items-center gap-1">
				<AlertTriangle class="w-3.5 h-3.5" />
				Liveness test failed
			</div>
		</div>
	</div>

	<!-- Search & Filter Controls -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
		<div class="relative w-full md:w-96">
			<Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
			<input 
				type="text" 
				bind:value={searchTerm}
				placeholder="Search by ID, customer, card number..." 
				class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2 w-full md:w-auto">
			<span class="text-xs text-slate-500 font-medium whitespace-nowrap">Filter Outcome:</span>
			<select 
				bind:value={resultFilter}
				class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors"
			>
				<option value="ALL">All Outcomes</option>
				<option value="MATCH">MATCH (Identity Verified)</option>
				<option value="MISMATCH">MISMATCH (Different Person)</option>
				<option value="SPOOF">SPOOF (Photo/Screen Fake)</option>
			</select>
		</div>
	</div>

	<!-- Audit Log Table -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm whitespace-nowrap">
				<thead class="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[11px] tracking-wider">
					<tr>
						<th class="px-6 py-4 font-semibold">Verification ID</th>
						<th class="px-6 py-4 font-semibold">Card Account Owner</th>
						<th class="px-6 py-4 font-semibold">Target ATM Card</th>
						<th class="px-6 py-4 font-semibold text-center">Pipeline Mode</th>
						<th class="px-6 py-4 font-semibold text-center">Verification Outcome</th>
						<th class="px-6 py-4 font-semibold text-right">Timestamp</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-800 text-slate-300">
					{#each filteredRecords as r}
						<tr class="hover:bg-slate-800/40 transition-colors">
							<td class="px-6 py-4 font-mono font-medium text-slate-200">
								<span class="text-cyan-400">#{r.id}</span>
							</td>
							<td class="px-6 py-4">
								<div class="font-medium text-white">{r.customerName}</div>
								<div class="text-xs text-slate-500 font-mono mt-0.5">{r.email}</div>
							</td>
							<td class="px-6 py-4 font-mono text-slate-400">
								{maskCard(r.cardNumber)}
							</td>
							<td class="px-6 py-4 text-center">
								<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-[11px] font-mono font-medium bg-slate-950 border border-slate-800 text-slate-400">
									<Cpu class="w-3 h-3 text-cyan-400" />
									1:1 Card-Bound
								</span>
							</td>
							<td class="px-6 py-4 text-center">
								{#if r.result === 'MATCH'}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
										<CheckCircle2 class="w-3.5 h-3.5" />
										MATCH (VERIFIED)
									</span>
								{:else if r.result === 'SPOOF'}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
										<AlertTriangle class="w-3.5 h-3.5" />
										SPOOF DETECTED
									</span>
								{:else}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
										<ShieldAlert class="w-3.5 h-3.5" />
										MISMATCH (DENIED)
									</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-right text-xs font-mono text-slate-400">
								{new Date(r.timestamp).toLocaleString()}
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="6" class="px-6 py-12 text-center text-slate-500">
								<div class="flex flex-col items-center justify-center gap-2">
									<Fingerprint class="w-10 h-10 text-slate-700" />
									<p class="text-slate-400 font-medium">No biometric face verifications recorded yet.</p>
									<p class="text-xs text-slate-600">Verifications executed at ATM terminals will appear here in real-time.</p>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>
