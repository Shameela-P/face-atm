<script lang="ts">
	import { enhance } from '$app/forms';
	import { Shield, Lock, User, ArrowRight, AlertCircle, Loader2 } from '@lucide/svelte';
	
	let { form } = $props();
	let username = $state(form?.username || '');
	let password = $state('');
	let loading = $state(false);
</script>

<svelte:head>
	<title>Admin Login - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
	<div class="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
	
	<div class="max-w-md w-full relative z-10">
		<div class="text-center mb-8 flex flex-col items-center">
			<Shield class="w-12 h-12 text-brand-500 mb-4" />
			<h1 class="text-3xl font-bold text-white">SecureATM Admin</h1>
			<p class="text-slate-400 mt-2">Sign in to the management console</p>
		</div>

		{#if form?.error}
			<div class="mb-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl flex items-start gap-3 text-red-400">
				<AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
				<p class="text-sm font-medium leading-relaxed">{form.error}</p>
			</div>
		{/if}

		<form 
			method="POST" 
			use:enhance={() => {
				loading = true;
				return async ({ update }) => {
					await update();
					loading = false;
				};
			}}
			class="bg-slate-800/50 backdrop-blur-xl border border-slate-700 p-8 rounded-3xl shadow-2xl"
		>
			
			<div class="mb-6">
				<label for="username" class="block text-sm font-medium text-slate-300 mb-2">Email Address</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
						<User class="h-5 w-5 text-slate-500" />
					</div>
					<input
						type="email"
						id="username"
						name="username"
						bind:value={username}
						class="block w-full pl-11 pr-4 py-3 border border-slate-600 rounded-xl bg-slate-900/50 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
						placeholder="sham@gmail.com"
						required
					/>
				</div>
			</div>

			<div class="mb-8">
				<label for="password" class="block text-sm font-medium text-slate-300 mb-2">Password</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
						<Lock class="h-5 w-5 text-slate-500" />
					</div>
					<input
						type="password"
						id="password"
						name="password"
						bind:value={password}
						class="block w-full pl-11 pr-4 py-3 border border-slate-600 rounded-xl bg-slate-900/50 text-white placeholder:text-slate-500 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all"
						placeholder="••••••••"
						required
					/>
				</div>
			</div>

			<button
				type="submit"
				disabled={loading}
				class="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 text-white py-3.5 rounded-xl font-semibold transition-all shadow-md shadow-brand-500/20 active:scale-[0.98] disabled:opacity-50"
			>
				{#if loading}
					<Loader2 class="w-5 h-5 animate-spin" />
					Authenticating...
				{:else}
					Login
					<ArrowRight class="w-5 h-5" />
				{/if}
			</button>
			
			<div class="mt-6 text-center text-xs text-slate-500 bg-slate-900/50 p-3 rounded-lg border border-slate-700/50">
				<strong>ADMIN AUTH:</strong> Enter registered Admin credentials.
			</div>
		</form>
		
		<div class="mt-8 text-center">
			<a href="/" class="text-sm text-slate-400 hover:text-white transition-colors">&larr; Back to Home</a>
		</div>
	</div>
</div>
