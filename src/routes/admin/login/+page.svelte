<script lang="ts">
	import { enhance } from '$app/forms';
	import { Shield, Lock, User, ArrowRight, AlertCircle, Loader2, KeyRound } from '@lucide/svelte';
	
	let { form } = $props();
	let username = $state(form?.username || '');
	let password = $state('');
	let loading = $state(false);
</script>

<svelte:head>
	<title>Admin Authentication - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative overflow-hidden text-slate-100 font-sans">
	<!-- Background Ambient Glow & Grid -->
	<div class="absolute inset-0 bg-radial from-brand-900/20 via-slate-950 to-slate-950 pointer-events-none"></div>
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px]"></div>

	<div class="max-w-md w-full relative z-10 space-y-6">
		<!-- Header -->
		<div class="text-center space-y-3 flex flex-col items-center">
			<div class="w-14 h-14 rounded-2xl bg-brand-500/10 border border-brand-500/20 text-brand-400 flex items-center justify-center shadow-xl shadow-brand-500/10">
				<Shield class="w-8 h-8" />
			</div>
			<div>
				<h1 class="text-3xl font-extrabold text-white tracking-tight">SecureATM Admin Portal</h1>
				<p class="text-slate-400 text-sm mt-1">Biometric Surveillance & ATM Management Console</p>
			</div>
		</div>

		<!-- Error Message -->
		{#if form?.error}
			<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-3 text-rose-400 text-sm animate-in fade-in">
				<AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
				<p class="font-medium leading-relaxed">{form.error}</p>
			</div>
		{/if}

		<!-- Login Form -->
		<form 
			method="POST" 
			use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					await update();
					loading = false;
				};
			}}
			class="bg-slate-900/80 backdrop-blur-xl border border-slate-800 p-8 rounded-2xl shadow-2xl space-y-5"
		>
			<div>
				<label for="username" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Admin Email</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
						<User class="h-4 h-4" />
					</div>
					<input
						type="email"
						id="username"
						name="username"
						bind:value={username}
						class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
						placeholder="sham@gmail.com"
						required
					/>
				</div>
			</div>

			<div>
				<label for="password" class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Password</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
						<Lock class="h-4 h-4" />
					</div>
					<input
						type="password"
						id="password"
						name="password"
						bind:value={password}
						class="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
						placeholder="••••••••"
						required
					/>
				</div>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 text-white py-3.5 rounded-xl font-bold text-sm transition-all shadow-lg shadow-brand-500/20 active:scale-[0.99] disabled:opacity-50"
			>
				{#if loading}
					<Loader2 class="w-5 h-5 animate-spin" />
					Authenticating...
				{:else}
					Authenticate Admin Console
					<ArrowRight class="w-4 h-4" />
				{/if}
			</button>

			<div class="pt-2 text-center text-xs text-slate-500 bg-slate-950/60 p-3 rounded-xl border border-slate-800/80 flex items-center justify-center gap-2">
				<KeyRound class="w-4 h-4 text-brand-400 shrink-0" />
				<span>Authorized personnel access only</span>
			</div>
		</form>
		
		<div class="text-center pt-2">
			<a href="/" class="text-xs font-medium text-slate-500 hover:text-slate-300 transition-colors">&larr; Return to SecureATM Main Portal</a>
		</div>
	</div>
</div>
