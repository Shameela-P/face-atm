<script lang="ts">
	import { 
		ShieldAlert, AlertTriangle, Clock, MailCheck, UserX, 
		Search, Eye, ShieldCheck, Camera, X, FileText, Lock
	} from '@lucide/svelte';

	let { data } = $props();

	let searchQuery = $state('');
	let selectedFilter = $state('ALL');
	let selectedIncident = $state<any>(null);

	const incidents = $derived(data.incidents || []);

	const filteredIncidents = $derived(
		incidents.filter((inc: any) => {
			const matchesSearch = 
				inc.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
				inc.card.toLowerCase().includes(searchQuery.toLowerCase()) ||
				(inc.ownerName && inc.ownerName.toLowerCase().includes(searchQuery.toLowerCase()));
			
			if (selectedFilter === 'ALL') return matchesSearch;
			return matchesSearch && inc.status === selectedFilter;
		})
	);

	const totalIncidents = $derived(incidents.length);
	const faceMismatchCount = $derived(incidents.filter((i: any) => i.status?.includes('MISMATCH')).length);
	const spoofCount = $derived(incidents.filter((i: any) => i.status?.includes('SPOOF')).length);

	function maskCard(card: string) {
		if (!card) return '**** **** **** ****';
		const clean = card.replace(/\s+/g, '');
		if (clean.length < 4) return '**** **** **** ' + clean;
		return '**** **** **** ' + clean.slice(-4);
	}

	function openModal(incident: any) {
		selectedIncident = incident;
	}

	function closeModal() {
		selectedIncident = null;
	}
</script>

<svelte:head>
	<title>Security Incidents - Admin Command Center</title>
</svelte:head>

<div class="space-y-6">
	<!-- Page Title Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
					<ShieldAlert class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-2xl font-bold text-white tracking-tight">Cybersecurity Incident Log</h1>
					<p class="text-slate-400 text-sm mt-0.5">Real-time surveillance & unauthorized ATM face verification attempt audit</p>
				</div>
			</div>
		</div>
		<div class="flex items-center gap-2">
			<span class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
				<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
				Live Audit Active
			</span>
		</div>
	</div>

	<!-- Statistics Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 relative overflow-hidden backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Alerts</p>
					<h3 class="text-2xl font-bold text-white mt-1">{totalIncidents}</h3>
				</div>
				<div class="p-3 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/50">
					<ShieldAlert class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-slate-400 flex items-center gap-1.5">
				<Clock class="w-3.5 h-3.5 text-slate-500" />
				All recorded ATM breaches
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 relative overflow-hidden backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Face Mismatches</p>
					<h3 class="text-2xl font-bold text-rose-400 mt-1">{faceMismatchCount}</h3>
				</div>
				<div class="p-3 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
					<UserX class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-rose-400/80 flex items-center gap-1.5">
				<AlertTriangle class="w-3.5 h-3.5" />
				Unauthorized person detected
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 relative overflow-hidden backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Spoofing Attempts</p>
					<h3 class="text-2xl font-bold text-amber-400 mt-1">{spoofCount}</h3>
				</div>
				<div class="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
					<Camera class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-amber-400/80 flex items-center gap-1.5">
				<ShieldCheck class="w-3.5 h-3.5" />
				Liveness CNN photo/screen catch
			</div>
		</div>
	</div>

	<!-- Filter and Search Toolbar -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
		<div class="relative w-full md:w-96">
			<Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
			<input 
				type="text" 
				placeholder="Search by ID, Card, or Owner..."
				bind:value={searchQuery}
				class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2 w-full md:w-auto overflow-x-auto">
			<span class="text-xs text-slate-500 font-medium whitespace-nowrap">Status Filter:</span>
			<button 
				onclick={() => selectedFilter = 'ALL'}
				class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap {selectedFilter === 'ALL' ? 'bg-brand-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}"
			>
				All Alerts
			</button>
			<button 
				onclick={() => selectedFilter = 'FACE_MISMATCH'}
				class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap {selectedFilter === 'FACE_MISMATCH' ? 'bg-rose-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}"
			>
				Face Mismatch
			</button>
			<button 
				onclick={() => selectedFilter = 'SPOOF_DETECTED'}
				class="px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors whitespace-nowrap {selectedFilter === 'SPOOF_DETECTED' ? 'bg-amber-500 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}"
			>
				Spoof Detected
			</button>
		</div>
	</div>

	<!-- Table Container -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm">
				<thead class="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[11px] tracking-wider">
					<tr>
						<th class="px-6 py-4 font-semibold">Incident ID</th>
						<th class="px-6 py-4 font-semibold">Target Account Owner</th>
						<th class="px-6 py-4 font-semibold">ATM Card</th>
						<th class="px-6 py-4 font-semibold">Alert Type</th>
						<th class="px-6 py-4 font-semibold">Incident Timestamp</th>
						<th class="px-6 py-4 font-semibold text-center">Snapshot</th>
						<th class="px-6 py-4 font-semibold text-right">Actions</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-800 text-slate-300">
					{#each filteredIncidents as incident}
						<tr class="hover:bg-slate-800/40 transition-colors">
							<td class="px-6 py-4 font-mono font-medium text-slate-200">
								<span class="text-rose-400">#{incident.id}</span>
							</td>
							<td class="px-6 py-4">
								<div class="font-medium text-white">{incident.ownerName}</div>
								<div class="text-xs text-slate-500 font-mono mt-0.5">{incident.ownerEmail}</div>
							</td>
							<td class="px-6 py-4 font-mono text-slate-400">
								{maskCard(incident.card)}
							</td>
							<td class="px-6 py-4">
								{#if incident.status?.includes('MISMATCH')}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
										<UserX class="w-3.5 h-3.5" />
										FACE MISMATCH
									</span>
								{:else if incident.status?.includes('SPOOF')}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
										<Camera class="w-3.5 h-3.5" />
										SPOOF DETECTED
									</span>
								{:else}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-rose-500/10 text-rose-400 border border-rose-500/20">
										<AlertTriangle class="w-3.5 h-3.5" />
										{incident.status}
									</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-xs font-mono text-slate-400">
								{new Date(incident.createdAt).toLocaleString()}
							</td>
							<td class="px-6 py-4 text-center">
								{#if incident.capturedImage}
									<button 
										onclick={() => openModal(incident)}
										class="relative group inline-block rounded-lg overflow-hidden border border-slate-700 w-10 h-10 bg-slate-950"
									>
										<img src={incident.capturedImage} alt="Attempt" class="w-full h-full object-cover" />
										<div class="absolute inset-0 bg-brand-500/40 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
											<Eye class="w-4 h-4 text-white" />
										</div>
									</button>
								{:else}
									<span class="text-xs text-slate-600 italic">No image</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-right">
								<button 
									onclick={() => openModal(incident)}
									class="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white hover:bg-slate-700 text-xs font-medium inline-flex items-center gap-1.5 transition-colors"
								>
									<Eye class="w-3.5 h-3.5 text-slate-400" />
									View Audit
								</button>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="7" class="px-6 py-12 text-center text-slate-500">
								<div class="flex flex-col items-center justify-center gap-2">
									<ShieldCheck class="w-10 h-10 text-slate-700" />
									<p class="text-slate-400 font-medium">No security incidents match your filters.</p>
									<p class="text-xs text-slate-600">The ATM biometric monitoring system is actively auditing all attempts.</p>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<!-- Incident Details Modal -->
{#if selectedIncident}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
		<div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-6 shadow-2xl relative overflow-hidden animate-in fade-in zoom-in duration-200">
			<!-- Header -->
			<div class="flex items-center justify-between border-b border-slate-800 pb-4">
				<div class="flex items-center gap-3">
					<div class="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
						<ShieldAlert class="w-6 h-6" />
					</div>
					<div>
						<h3 class="text-lg font-bold text-white">Security Breach Inspection</h3>
						<p class="text-xs text-slate-400 font-mono">Incident #{selectedIncident.id}</p>
					</div>
				</div>
				<button 
					onclick={closeModal}
					class="p-2 rounded-lg bg-slate-800 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
				>
					<X class="w-5 h-5" />
				</button>
			</div>

			<!-- Body -->
			<div class="space-y-4">
				<!-- Image Preview -->
				{#if selectedIncident.capturedImage}
					<div class="space-y-2">
						<div class="flex items-center justify-between text-xs text-slate-400">
							<span class="font-semibold text-slate-300 flex items-center gap-1.5">
								<Camera class="w-4 h-4 text-rose-400" />
								Captured Unauthorized Person Snapshot
							</span>
							<span class="font-mono text-slate-500">{new Date(selectedIncident.createdAt).toLocaleString()}</span>
						</div>
						<div class="relative rounded-xl overflow-hidden border border-rose-500/30 bg-slate-950 max-h-64 flex items-center justify-center">
							<img src={selectedIncident.capturedImage} alt="Attempted access biometric snapshot" class="max-h-64 object-contain" />
							<div class="absolute bottom-2 left-2 px-2.5 py-1 rounded bg-slate-950/90 text-[10px] font-mono text-rose-400 border border-rose-500/30">
								CAMERA_FEED_SNAP_VERIFICATION_FAIL
							</div>
						</div>
					</div>
				{/if}

				<!-- Incident Detail Grid -->
				<div class="grid grid-cols-2 gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80 text-sm">
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Alert Type</p>
						<p class="font-bold text-rose-400 mt-0.5">{selectedIncident.status}</p>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">ATM Terminal</p>
						<p class="font-medium text-slate-200 mt-0.5">{selectedIncident.atmId || 'ATM_TERMINAL_01'}</p>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Target Account Owner</p>
						<p class="font-medium text-slate-200 mt-0.5">{selectedIncident.ownerName}</p>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">ATM Card Number</p>
						<p class="font-mono text-slate-300 mt-0.5">{maskCard(selectedIncident.card)}</p>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Owner Alert Email</p>
						<span class="inline-flex items-center gap-1 text-xs text-emerald-400 mt-0.5 font-medium">
							<MailCheck class="w-3.5 h-3.5" />
							Dispatched to {selectedIncident.ownerEmail}
						</span>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Action Taken</p>
						<span class="inline-flex items-center gap-1 text-xs text-rose-400 mt-0.5 font-semibold">
							<Lock class="w-3.5 h-3.5" />
							ATM Access Blocked
						</span>
					</div>
				</div>
			</div>

			<!-- Footer -->
			<div class="flex justify-end pt-2 border-t border-slate-800">
				<button 
					onclick={closeModal}
					class="px-5 py-2 rounded-xl bg-slate-800 text-white font-medium text-sm hover:bg-slate-700 transition-colors"
				>
					Close Audit
				</button>
			</div>
		</div>
	</div>
{/if}
