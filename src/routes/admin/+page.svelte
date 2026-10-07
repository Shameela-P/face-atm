<script lang="ts">
	import { Users, CreditCard, ArrowRightLeft, ShieldAlert, Fingerprint, Database, HardDrive, ShieldCheck, Activity, ChevronRight, AlertTriangle } from '@lucide/svelte';

	let { data } = $props();

	let statsList = $derived([
		{ name: 'Total Customers', value: data.stats.totalCustomers, icon: Users, color: 'text-blue-400', bg: 'bg-blue-500/10 border-blue-500/20' },
		{ name: 'Total Cards / Accounts', value: data.stats.totalCards, icon: CreditCard, color: 'text-indigo-400', bg: 'bg-indigo-500/10 border-indigo-500/20' },
		{ name: 'Total Transactions', value: data.stats.totalTransactions, icon: ArrowRightLeft, color: 'text-purple-400', bg: 'bg-purple-500/10 border-purple-500/20' },
		{ name: 'Successful Biometric Verification', value: data.stats.successfulVerificationsCount, icon: Fingerprint, color: 'text-emerald-400', bg: 'bg-emerald-500/10 border-emerald-500/20' },
		{ name: 'Failed Verifications', value: data.stats.failedVerificationsCount, icon: Fingerprint, color: 'text-amber-400', bg: 'bg-amber-500/10 border-amber-500/20' },
		{ name: 'Security Incidents', value: data.stats.securityIncidentsCount, icon: ShieldAlert, color: 'text-rose-400', bg: 'bg-rose-500/10 border-rose-500/20' },
	]);

	function maskCard(cardNo: string) {
		if (!cardNo || cardNo === 'N/A') return 'N/A';
		if (cardNo.length <= 4) return cardNo;
		return '**** **** **** ' + cardNo.slice(-4);
	}
</script>

<svelte:head>
	<title>Admin Command Dashboard - SecureATM</title>
</svelte:head>

<div class="mb-8 flex flex-col md:flex-row md:items-center justify-between gap-4">
	<div>
		<div class="flex items-center gap-2 text-xs font-mono text-brand-400 mb-1">
			<Activity class="w-4 h-4 animate-pulse" />
			<span>LIVE BIOMETRIC TELEMETRY ACTIVE</span>
		</div>
		<h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight">Security Command Dashboard</h1>
		<p class="text-slate-400 text-xs sm:text-sm mt-1">Realtime biometrics statistics, facial verification audits, and transaction metrics.</p>
	</div>
	<div class="flex items-center gap-3">
		<a 
			href="/admin/customers" 
			class="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-600 to-blue-600 hover:from-brand-500 hover:to-blue-500 text-white font-semibold text-xs shadow-lg shadow-brand-500/20 transition-all active:scale-95"
		>
			<Users class="w-4 h-4" />
			<span>Register Customer</span>
		</a>
	</div>
</div>

<!-- Dynamic Stats Grid from Firebase Realtime Database -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
	{#each statsList as stat}
		<div class="bg-slate-900/90 border border-slate-800/80 p-5 rounded-2xl shadow-lg relative overflow-hidden group hover:border-slate-700/80 transition-all">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 mb-1">{stat.name}</p>
					<h3 class="text-2xl font-bold font-mono text-white tracking-tight">{stat.value.toLocaleString()}</h3>
				</div>
				<div class={`w-12 h-12 rounded-2xl border flex items-center justify-center shrink-0 ${stat.bg} ${stat.color} group-hover:scale-110 transition-transform`}>
					<stat.icon class="w-6 h-6" />
				</div>
			</div>
		</div>
	{/each}
</div>

<!-- Recent Security Activity & Service Health Status -->
<div class="grid lg:grid-cols-2 gap-8">
	
	<!-- Recent Security Alerts -->
	<div class="bg-slate-900/90 rounded-2xl border border-slate-800/80 overflow-hidden flex flex-col shadow-xl">
		<div class="p-5 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/50">
			<div class="flex items-center gap-2">
				<ShieldAlert class="w-5 h-5 text-rose-400" />
				<h3 class="text-base font-bold text-slate-100">Recent Security Alerts</h3>
			</div>
			<a href="/admin/security-alerts" class="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1">
				<span>View Monitor</span>
				<ChevronRight class="w-3.5 h-3.5" />
			</a>
		</div>
		<div class="p-0 flex-1 overflow-x-auto">
			<table class="w-full text-left text-xs whitespace-nowrap">
				<thead class="bg-slate-950/60 text-slate-400 uppercase tracking-wider font-mono border-b border-slate-800/80">
					<tr>
						<th class="px-5 py-3 font-medium">Incident ID</th>
						<th class="px-5 py-3 font-medium">Card Number</th>
						<th class="px-5 py-3 font-medium">Event Type</th>
						<th class="px-5 py-3 font-medium">Time</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-800/50 text-slate-300 font-mono">
					{#each data.recentAlerts as alert}
						<tr class="hover:bg-slate-800/40 transition-colors">
							<td class="px-5 py-3.5 font-bold text-brand-400">#{alert.id}</td>
							<td class="px-5 py-3.5 text-slate-400">{maskCard(alert.account)}</td>
							<td class="px-5 py-3.5">
								<span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
									<AlertTriangle class="w-3 h-3" />
									{alert.type}
								</span>
							</td>
							<td class="px-5 py-3.5 text-slate-400 font-sans text-xs">{alert.time}</td>
						</tr>
					{:else}
						<tr>
							<td colspan="4" class="px-5 py-12 text-center text-slate-500 font-sans">
								<ShieldCheck class="w-8 h-8 text-emerald-500/40 mx-auto mb-2" />
								No security incidents recorded. System clear.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Real-Time System Status -->
	<div class="bg-slate-900/90 rounded-2xl border border-slate-800/80 p-6 flex flex-col shadow-xl">
		<div class="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
			<div>
				<h3 class="text-base font-bold text-slate-100">Service Connectivity & Health</h3>
				<p class="text-xs text-slate-400 mt-0.5">Realtime backend integrations monitor</p>
			</div>
			<span class="px-2.5 py-1 rounded-full text-[10px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">HEALTHY</span>
		</div>

		<div class="space-y-4 flex-1">
			
			<div class="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<div class={`w-10 h-10 rounded-xl flex items-center justify-center border ${data.systemStatus.firebaseRtdb ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
						<Database class="w-5 h-5" />
					</div>
					<div>
						<p class="text-xs font-bold text-slate-200">Firebase Realtime Database</p>
						<p class="text-[11px] text-slate-400">{data.systemStatus.firebaseRtdb ? 'Connected & Active' : 'Unavailable'}</p>
					</div>
				</div>
				<span class={`w-2.5 h-2.5 rounded-full ${data.systemStatus.firebaseRtdb ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)]' : 'bg-rose-500'}`}></span>
			</div>
			
			<div class="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<div class={`w-10 h-10 rounded-xl flex items-center justify-center border ${data.systemStatus.firebaseStorage ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
						<HardDrive class="w-5 h-5" />
					</div>
					<div>
						<p class="text-xs font-bold text-slate-200">Firebase Storage (Bucket: face-76a11)</p>
						<p class="text-[11px] text-slate-400">{data.systemStatus.firebaseStorage ? 'Connected & Operational' : 'Unavailable'}</p>
					</div>
				</div>
				<span class={`w-2.5 h-2.5 rounded-full ${data.systemStatus.firebaseStorage ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)]' : 'bg-rose-500'}`}></span>
			</div>
			
			<div class="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80 flex items-center justify-between">
				<div class="flex items-center gap-3">
					<div class={`w-10 h-10 rounded-xl flex items-center justify-center border ${data.systemStatus.fastApiMlService ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 'bg-rose-500/10 text-rose-400 border-rose-500/20'}`}>
						<Fingerprint class="w-5 h-5" />
					</div>
					<div>
						<p class="text-xs font-bold text-slate-200">Facial Recognition API (FastAPI MTCNN / FaceNet)</p>
						<p class="text-[11px] text-slate-400">{data.systemStatus.fastApiMlService ? 'Operational (Port 8000)' : 'Offline'}</p>
					</div>
				</div>
				<span class={`w-2.5 h-2.5 rounded-full ${data.systemStatus.fastApiMlService ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)]' : 'bg-rose-500'}`}></span>
			</div>

		</div>
	</div>

</div>
