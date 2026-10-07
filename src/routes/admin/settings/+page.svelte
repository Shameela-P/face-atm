<script lang="ts">
	import { enhance } from '$app/forms';
	import { Settings, Shield, Bell, CheckCircle2, AlertCircle, FileText, Loader2, Save } from '@lucide/svelte';

	let { data, form } = $props();

	let loading = $state(false);
</script>

<svelte:head>
	<title>System Settings & Audit Logs - Admin Dashboard</title>
</svelte:head>

<div class="mb-8 flex justify-between items-center">
	<div>
		<h1 class="text-2xl font-bold text-slate-900">System Settings & Audit Logs</h1>
		<p class="text-slate-500 mt-1">Configure security thresholds, ML endpoints, and review administrative audit trails.</p>
	</div>
</div>

{#if form?.message}
	<div class="mb-6 p-4 bg-green-50 border border-green-200 rounded-2xl flex items-center gap-3 text-green-700 font-medium">
		<CheckCircle2 class="w-5 h-5 text-green-600 shrink-0" />
		<p>{form.message}</p>
	</div>
{/if}

{#if form?.error}
	<div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl flex items-center gap-3 text-red-700 font-medium">
		<AlertCircle class="w-5 h-5 text-red-600 shrink-0" />
		<p>{form.error}</p>
	</div>
{/if}

<div class="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
	
	<!-- Configuration Form -->
	<div class="lg:col-span-1 bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
		<h3 class="text-lg font-bold text-slate-900 mb-6 flex items-center gap-2">
			<Settings class="w-5 h-5 text-brand-600" />
			Application Settings
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
				<label for="appName" class="block text-xs font-semibold text-slate-700 mb-1">Application Name</label>
				<input type="text" id="appName" name="appName" value={data.settings.appName} class="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none" />
			</div>

			<div>
				<label for="mlServiceUrl" class="block text-xs font-semibold text-slate-700 mb-1">FastAPI ML Endpoint URL</label>
				<input type="text" id="mlServiceUrl" name="mlServiceUrl" value={data.settings.mlServiceUrl} class="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-sm font-mono focus:border-brand-500 outline-none" />
			</div>

			<div class="grid grid-cols-2 gap-3">
				<div>
					<label for="sessionTimeoutMins" class="block text-xs font-semibold text-slate-700 mb-1">Session (Mins)</label>
					<input type="number" id="sessionTimeoutMins" name="sessionTimeoutMins" value={data.settings.sessionTimeoutMins} class="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none" />
				</div>
				<div>
					<label for="maxFailedAttempts" class="block text-xs font-semibold text-slate-700 mb-1">Max Failed Try</label>
					<input type="number" id="maxFailedAttempts" name="maxFailedAttempts" value={data.settings.maxFailedAttempts} class="w-full px-3 py-2 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none" />
				</div>
			</div>

			<div class="pt-2">
				<label class="flex items-center gap-3 cursor-pointer">
					<input type="checkbox" name="emailAlertsEnabled" checked={data.settings.emailAlertsEnabled} class="w-4 h-4 rounded text-brand-600 focus:ring-brand-500 border-slate-300" />
					<span class="text-xs font-semibold text-slate-700">Enable SMTP Security Email Alerts</span>
				</label>
			</div>

			<div class="pt-4 border-t border-slate-100">
				<button 
					type="submit" 
					disabled={loading}
					class="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 text-white px-4 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-sm"
				>
					{#if loading}<Loader2 class="w-4 h-4 animate-spin" /> Saving...{:else}<Save class="w-4 h-4" /> Save Configuration{/if}
				</button>
			</div>
		</form>
	</div>

	<!-- Admin Audit Logs -->
	<div class="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
		<div class="p-6 border-b border-slate-100 flex justify-between items-center">
			<h3 class="text-lg font-bold text-slate-900 flex items-center gap-2">
				<FileText class="w-5 h-5 text-indigo-600" />
				Admin Security Audit Trail
			</h3>
			<span class="text-xs text-slate-500 font-medium">Recorded in Firebase /adminAuditLogs</span>
		</div>

		<div class="p-0 flex-1 overflow-x-auto">
			<table class="w-full text-left text-sm whitespace-nowrap">
				<thead class="bg-slate-50 text-slate-500">
					<tr>
						<th class="px-6 py-3.5 font-medium">Log ID</th>
						<th class="px-6 py-3.5 font-medium">Action</th>
						<th class="px-6 py-3.5 font-medium">Admin</th>
						<th class="px-6 py-3.5 font-medium">Details</th>
						<th class="px-6 py-3.5 font-medium text-right">Timestamp</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-slate-100">
					{#each data.auditLogs as log}
						<tr class="hover:bg-slate-50/50 transition-colors">
							<td class="px-6 py-3.5 font-mono text-xs font-medium text-slate-900">{log.id}</td>
							<td class="px-6 py-3.5">
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-100">
									{log.action}
								</span>
							</td>
							<td class="px-6 py-3.5 text-xs text-slate-700">{log.admin}</td>
							<td class="px-6 py-3.5 text-xs text-slate-600 max-w-xs truncate">{log.details}</td>
							<td class="px-6 py-3.5 text-right text-xs font-mono text-slate-500">
								{new Date(log.timestamp).toLocaleString()}
							</td>
						</tr>
					{:else}
						<tr>
							<td colspan="5" class="px-6 py-8 text-center text-slate-500">
								No admin audit log entries recorded in Firebase yet.
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	</div>

</div>
