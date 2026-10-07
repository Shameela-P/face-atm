<script lang="ts">
	import { enhance } from '$app/forms';
	import { 
		Settings, Shield, Bell, CheckCircle2, AlertCircle, FileText, 
		Loader2, Save, Server, Lock, Cpu, Database, Mail, Phone, Key
	} from '@lucide/svelte';

	let { data, form } = $props();

	let loading = $state(false);

	const auditLogs = $derived(data.auditLogs || []);
</script>

<svelte:head>
	<title>System Settings & Audit Trail - Admin Command Center</title>
</svelte:head>

<div class="space-y-6">
	<!-- Header -->
	<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
		<div>
			<div class="flex items-center gap-2">
				<div class="p-2 rounded-lg bg-slate-800 text-slate-300 border border-slate-700">
					<Settings class="w-6 h-6" />
				</div>
				<div>
					<h1 class="text-2xl font-bold text-white tracking-tight">System Settings & Health Status</h1>
					<p class="text-slate-400 text-sm mt-0.5">Configure security parameters & review safe service connection statuses</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Alert Banners -->
	{#if form?.message}
		<div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-center gap-3 text-emerald-400 text-sm font-medium">
			<CheckCircle2 class="w-5 h-5 text-emerald-400 shrink-0" />
			<p>{form.message}</p>
		</div>
	{/if}

	{#if form?.error}
		<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-3 text-rose-400 text-sm font-medium">
			<AlertCircle class="w-5 h-5 text-rose-400 shrink-0" />
			<p>{form.error}</p>
		</div>
	{/if}

	<!-- Integration Status Safe Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-center gap-3 backdrop-blur-sm">
			<div class="p-3 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
				<Database class="w-5 h-5" />
			</div>
			<div>
				<p class="text-xs text-slate-400 font-medium">Firebase RTDB</p>
				<p class="text-sm font-bold text-emerald-400 flex items-center gap-1.5 mt-0.5">
					<span class="w-2 h-2 rounded-full bg-emerald-400"></span>
					Connected
				</p>
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-center gap-3 backdrop-blur-sm">
			<div class="p-3 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
				<Cpu class="w-5 h-5" />
			</div>
			<div>
				<p class="text-xs text-slate-400 font-medium">FastAPI ML Pipeline</p>
				<p class="text-sm font-bold text-cyan-400 flex items-center gap-1.5 mt-0.5">
					<span class="w-2 h-2 rounded-full bg-cyan-400"></span>
					Active (Port 8000)
				</p>
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-center gap-3 backdrop-blur-sm">
			<div class="p-3 rounded-lg bg-purple-500/10 text-purple-400 border border-purple-500/20">
				<Phone class="w-5 h-5" />
			</div>
			<div>
				<p class="text-xs text-slate-400 font-medium">Twilio SMS Service</p>
				<p class="text-sm font-bold text-purple-400 flex items-center gap-1.5 mt-0.5">
					<span class="w-2 h-2 rounded-full bg-purple-400"></span>
					Configured (4-Digit OTP)
				</p>
			</div>
		</div>

		<div class="bg-slate-900/80 border border-slate-800 rounded-xl p-4 flex items-center gap-3 backdrop-blur-sm">
			<div class="p-3 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
				<Mail class="w-5 h-5" />
			</div>
			<div>
				<p class="text-xs text-slate-400 font-medium">SMTP Email Alerts</p>
				<p class="text-sm font-bold text-blue-400 flex items-center gap-1.5 mt-0.5">
					<span class="w-2 h-2 rounded-full bg-blue-400"></span>
					Configured (Owner Alerts)
				</p>
			</div>
		</div>
	</div>

	<!-- Main Settings Content Grid -->
	<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
		<!-- Configuration Form -->
		<div class="lg:col-span-1 bg-slate-900/80 border border-slate-800 rounded-xl p-6 backdrop-blur-sm space-y-6">
			<h3 class="text-base font-bold text-white flex items-center gap-2">
				<Settings class="w-5 h-5 text-brand-400" />
				System Configuration
			</h3>

			<form 
				method="POST" 
				action="?/updateSettings"
				use:enhance={() => {
					loading = true;
					return async ({ update }) => {
						await update();
						loading = false;
					};
				}}
				class="space-y-4"
			>
				<div>
					<label for="appName" class="block text-xs font-semibold text-slate-400 mb-1">Application Name</label>
					<input 
						type="text" 
						id="appName" 
						name="appName" 
						value={data.settings.appName} 
						class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors" 
					/>
				</div>

				<div>
					<label for="mlServiceUrl" class="block text-xs font-semibold text-slate-400 mb-1">FastAPI ML Endpoint URL</label>
					<input 
						type="text" 
						id="mlServiceUrl" 
						name="mlServiceUrl" 
						value={data.settings.mlServiceUrl} 
						class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm font-mono text-slate-200 focus:outline-none focus:border-brand-500 transition-colors" 
					/>
				</div>

				<div class="grid grid-cols-2 gap-3">
					<div>
						<label for="sessionTimeoutMins" class="block text-xs font-semibold text-slate-400 mb-1">Session (Mins)</label>
						<input 
							type="number" 
							id="sessionTimeoutMins" 
							name="sessionTimeoutMins" 
							value={data.settings.sessionTimeoutMins} 
							class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors" 
						/>
					</div>
					<div>
						<label for="maxFailedAttempts" class="block text-xs font-semibold text-slate-400 mb-1">Max Failed Try</label>
						<input 
							type="number" 
							id="maxFailedAttempts" 
							name="maxFailedAttempts" 
							value={data.settings.maxFailedAttempts} 
							class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-slate-200 focus:outline-none focus:border-brand-500 transition-colors" 
						/>
					</div>
				</div>

				<div class="pt-2">
					<label class="flex items-center gap-3 cursor-pointer">
						<input 
							type="checkbox" 
							name="emailAlertsEnabled" 
							checked={data.settings.emailAlertsEnabled} 
							class="w-4 h-4 rounded text-brand-500 bg-slate-950 border-slate-800 focus:ring-brand-500" 
						/>
						<span class="text-xs font-semibold text-slate-300">Enable Security Alert Emails</span>
					</label>
				</div>

				<div class="pt-4 border-t border-slate-800">
					<button 
						type="submit" 
						disabled={loading}
						class="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-lg shadow-brand-500/20"
					>
						{#if loading}<Loader2 class="w-4 h-4 animate-spin" /> Saving...{:else}<Save class="w-4 h-4" /> Save Settings{/if}
					</button>
				</div>
			</form>
		</div>

		<!-- Admin Audit Logs -->
		<div class="lg:col-span-2 bg-slate-900/80 border border-slate-800 rounded-xl overflow-hidden backdrop-blur-sm flex flex-col">
			<div class="p-5 border-b border-slate-800 flex items-center justify-between">
				<h3 class="text-base font-bold text-white flex items-center gap-2">
					<FileText class="w-5 h-5 text-indigo-400" />
					Admin Action Audit Trail
				</h3>
				<span class="text-xs text-slate-500 font-mono">Firebase /adminAuditLogs</span>
			</div>

			<div class="overflow-x-auto flex-1">
				<table class="w-full text-left text-sm whitespace-nowrap">
					<thead class="bg-slate-950/80 text-slate-400 border-b border-slate-800 uppercase text-[11px] tracking-wider">
						<tr>
							<th class="px-6 py-4 font-semibold">Log ID</th>
							<th class="px-6 py-4 font-semibold">Action</th>
							<th class="px-6 py-4 font-semibold">Admin User</th>
							<th class="px-6 py-4 font-semibold">Details</th>
							<th class="px-6 py-4 font-semibold text-right">Timestamp</th>
						</tr>
					</thead>
					<tbody class="divide-y divide-slate-800 text-slate-300">
						{#each auditLogs as log}
							<tr class="hover:bg-slate-800/40 transition-colors">
								<td class="px-6 py-4 font-mono text-xs font-medium text-slate-200">#{log.id}</td>
								<td class="px-6 py-4">
									<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
										{log.action}
									</span>
								</td>
								<td class="px-6 py-4 text-xs font-medium text-slate-300">{log.admin}</td>
								<td class="px-6 py-4 text-xs text-slate-400 max-w-xs truncate">{log.details}</td>
								<td class="px-6 py-4 text-right text-xs font-mono text-slate-400">
									{new Date(log.timestamp).toLocaleString()}
								</td>
							</tr>
						{:else}
							<tr>
								<td colspan="5" class="px-6 py-12 text-center text-slate-500">
									<div class="flex flex-col items-center justify-center gap-2">
										<FileText class="w-10 h-10 text-slate-700" />
										<p class="text-slate-400 font-medium">No admin audit log entries recorded in Firebase yet.</p>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>
	</div>
</div>
