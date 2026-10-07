<script lang="ts">
	import { enhance } from '$app/forms';
	import { 
		AlertTriangle, Search, MessageSquare, CheckCircle2, Clock, 
		X, Loader2, LifeBuoy, FileText, User, Filter, ShieldCheck, CornerDownRight
	} from '@lucide/svelte';

	let { data, form } = $props();

	let searchTerm = $state('');
	let statusFilter = $state('ALL');

	let selectedComplaint = $state<any | null>(null);
	let showModal = $state(false);
	let loading = $state(false);

	const complaints = $derived(data.complaints || []);

	const filteredComplaints = $derived(
		complaints.filter((c: any) => {
			const matchesSearch = 
				c.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
				(c.customerName && c.customerName.toLowerCase().includes(searchTerm.toLowerCase())) ||
				(c.subject && c.subject.toLowerCase().includes(searchTerm.toLowerCase())) ||
				(c.category && c.category.toLowerCase().includes(searchTerm.toLowerCase()));
			
			const matchesStatus = statusFilter === 'ALL' || c.status === statusFilter;
			return matchesSearch && matchesStatus;
		})
	);

	const totalTickets = $derived(complaints.length);
	const openCount = $derived(complaints.filter((c: any) => c.status === 'OPEN' || c.status === 'IN_PROGRESS').length);
	const resolvedCount = $derived(complaints.filter((c: any) => c.status === 'RESOLVED' || c.status === 'CLOSED').length);

	function openReviewModal(complaint: any) {
		selectedComplaint = { ...complaint };
		showModal = true;
	}

	function closeModal() {
		showModal = false;
		selectedComplaint = null;
	}
</script>

<svelte:head>
	<title>Customer Complaints - Admin Command Center</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
					<LifeBuoy class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-2xl font-bold text-white tracking-tight">Customer Support & Disputes</h1>
					<p class="text-slate-400 text-sm mt-0.5">Manage customer inquiries, dispute tickets, and resolution responses</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Alert Messages -->
	{#if form?.message}
		<div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-3 text-emerald-400 text-sm font-medium">
			<CheckCircle2 class="w-5 h-5 text-emerald-400 shrink-0" />
			<p>{form.message}</p>
		</div>
	{/if}

	{#if form?.error}
		<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm font-medium">
			<AlertTriangle class="w-5 h-5 text-rose-400 shrink-0" />
			<p>{form.error}</p>
		</div>
	{/if}

	<!-- Stats Grid -->
	<div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Support Tickets</p>
					<h3 class="text-2xl font-bold text-white mt-1">{totalTickets}</h3>
				</div>
				<div class="p-3 rounded-lg bg-slate-800 text-slate-400 border border-slate-700/50">
					<MessageSquare class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-slate-400">All customer submissions in Firebase</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active / Open</p>
					<h3 class="text-2xl font-bold text-amber-400 mt-1">{openCount}</h3>
				</div>
				<div class="p-3 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/20">
					<Clock class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-amber-400/80">Awaiting admin resolution</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-5 backdrop-blur-sm">
			<div class="flex items-center justify-between">
				<div>
					<p class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Resolved / Closed</p>
					<h3 class="text-2xl font-bold text-emerald-400 mt-1">{resolvedCount}</h3>
				</div>
				<div class="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
					<ShieldCheck class="w-5 h-5" />
				</div>
			</div>
			<div class="mt-3 text-xs text-emerald-400/80">Completed ticket items</div>
		</div>
	</div>

	<!-- Controls Toolbar -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex flex-col md:flex-row items-center justify-between gap-4">
		<div class="relative w-full md:w-96">
			<Search class="w-4 h-4 text-slate-500 absolute left-3.5 top-1/2 -translate-y-1/2" />
			<input 
				type="text" 
				bind:value={searchTerm}
				placeholder="Search complaint ID, customer, subject..." 
				class="w-full bg-slate-950 border border-slate-800 rounded-lg pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
			/>
		</div>

		<div class="flex items-center gap-2 w-full md:w-auto">
			<span class="text-xs text-slate-500 font-medium whitespace-nowrap">Filter Status:</span>
			<select 
				bind:value={statusFilter}
				class="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors font-medium"
			>
				<option value="ALL">All Statuses</option>
				<option value="OPEN">OPEN</option>
				<option value="IN_PROGRESS">IN_PROGRESS</option>
				<option value="RESOLVED">RESOLVED</option>
				<option value="CLOSED">CLOSED</option>
			</select>
		</div>
	</div>

	<!-- Complaints Table -->
	<div class="bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-sm">
		<div class="overflow-x-auto">
			<table class="w-full text-left text-sm whitespace-nowrap">
				<thead class="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[11px] tracking-wider">
					<tr>
						<th class="px-6 py-4 font-semibold">Ticket ID</th>
						<th class="px-6 py-4 font-semibold">Customer</th>
						<th class="px-6 py-4 font-semibold">Subject / Category</th>
						<th class="px-6 py-4 font-semibold text-center">Priority</th>
						<th class="px-6 py-4 font-semibold text-center">Status</th>
						<th class="px-6 py-4 font-semibold text-right">Action</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-800 text-slate-300">
					{#each filteredComplaints as c}
						<tr class="hover:bg-slate-800/40 transition-colors">
							<td class="px-6 py-4 font-mono font-medium text-slate-200">
								<span class="text-brand-400">#{c.id}</span>
							</td>
							<td class="px-6 py-4">
								<div class="font-medium text-white">{c.customerName || 'Customer'}</div>
								<div class="text-xs text-slate-500 font-mono mt-0.5">{c.email || 'N/A'}</div>
							</td>
							<td class="px-6 py-4 max-w-xs truncate">
								<div class="font-medium text-slate-200 truncate">{c.subject}</div>
								<div class="text-xs text-slate-500 truncate">{c.category || 'General Support'}</div>
							</td>
							<td class="px-6 py-4 text-center">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold {
									c.priority === 'URGENT' || c.priority === 'HIGH' 
										? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' 
										: 'bg-slate-800 text-slate-400 border border-slate-700'
								}">
									{c.priority || 'NORMAL'}
								</span>
							</td>
							<td class="px-6 py-4 text-center">
								{#if c.status === 'RESOLVED' || c.status === 'CLOSED'}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
										<CheckCircle2 class="w-3.5 h-3.5" />
										{c.status}
									</span>
								{:else if c.status === 'IN_PROGRESS'}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
										<Clock class="w-3.5 h-3.5" />
										IN_PROGRESS
									</span>
								{:else}
									<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20">
										<Clock class="w-3.5 h-3.5" />
										OPEN
									</span>
								{/if}
							</td>
							<td class="px-6 py-4 text-right">
								<button 
									onclick={() => openReviewModal(c)}
									class="px-3 py-1.5 rounded-lg bg-brand-500/10 text-brand-400 hover:bg-brand-500/20 border border-brand-500/20 text-xs font-semibold transition-colors"
								>
									Review & Respond
								</button>
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="6" class="px-6 py-12 text-center text-slate-500">
								<div class="flex flex-col items-center justify-center gap-2">
									<LifeBuoy class="w-10 h-10 text-slate-700" />
									<p class="text-slate-400 font-medium">No customer complaints recorded.</p>
								</div>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>
</div>

<!-- Complaint Review Modal -->
{#if showModal && selectedComplaint}
	<div class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
		<div class="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 space-y-6 shadow-2xl relative">
			<div class="flex justify-between items-center border-b border-slate-800 pb-4">
				<div class="flex items-center gap-3">
					<div class="p-2 rounded-lg bg-brand-500/10 text-brand-400 border border-brand-500/20">
						<MessageSquare class="w-5 h-5" />
					</div>
					<div>
						<h3 class="text-lg font-bold text-white">Review Complaint #{selectedComplaint.id}</h3>
						<p class="text-xs text-slate-400">Customer: {selectedComplaint.customerName} ({selectedComplaint.email})</p>
					</div>
				</div>
				<button onclick={closeModal} class="text-slate-400 hover:text-white p-1.5 rounded-lg hover:bg-slate-800 transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<form 
				method="POST" 
				action="?/updateComplaint"
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
				<input type="hidden" name="complaintId" value={selectedComplaint.id} />

				<!-- Inquiry Card -->
				<div class="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-3">
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Subject</p>
						<p class="text-sm font-bold text-white mt-0.5">{selectedComplaint.subject}</p>
					</div>
					<div>
						<p class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Description</p>
						<p class="text-sm text-slate-300 mt-0.5 whitespace-pre-wrap leading-relaxed">{selectedComplaint.description}</p>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label for="status" class="block text-xs font-semibold text-slate-400 mb-1.5">Update Status</label>
						<select id="status" name="status" bind:value={selectedComplaint.status} class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors">
							<option value="OPEN">OPEN</option>
							<option value="IN_PROGRESS">IN_PROGRESS</option>
							<option value="RESOLVED">RESOLVED</option>
							<option value="CLOSED">CLOSED</option>
						</select>
					</div>

					<div>
						<label for="priority" class="block text-xs font-semibold text-slate-400 mb-1.5">Update Priority</label>
						<select id="priority" name="priority" bind:value={selectedComplaint.priority} class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors">
							<option value="LOW">LOW</option>
							<option value="MEDIUM">MEDIUM</option>
							<option value="HIGH">HIGH</option>
							<option value="URGENT">URGENT</option>
						</select>
					</div>
				</div>

				<div>
					<label for="adminResponse" class="block text-xs font-semibold text-slate-400 mb-1.5">Admin Resolution Note</label>
					<textarea 
						id="adminResponse" 
						name="adminResponse" 
						rows="3"
						placeholder="Enter notes or customer resolution message..."
						class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3.5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
					>{selectedComplaint.adminResponse || ''}</textarea>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-800">
					<button type="button" onclick={closeModal} class="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 hover:text-white text-sm font-medium transition-colors">
						Cancel
					</button>
					<button type="submit" disabled={loading} class="flex items-center gap-2 bg-brand-500 hover:bg-brand-600 text-white px-5 py-2 rounded-xl text-sm font-semibold shadow-lg shadow-brand-500/20 transition-all">
						{#if loading}<Loader2 class="w-4 h-4 animate-spin" /> Saving...{:else}Save Resolution{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
