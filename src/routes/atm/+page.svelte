<script lang="ts">
	import { enhance } from '$app/forms';
	import { CreditCard, ArrowRight, ShieldCheck, AlertCircle, Loader2 } from '@lucide/svelte';
	
	let { form } = $props();
	let loading = $state(false);
	let cardNumber = $state(form?.cardNumber || '');
</script>

<svelte:head>
	<title>SecureATM - Insert Card</title>
</svelte:head>

<div class="min-h-screen bg-slate-900 flex items-center justify-center p-4">
	<div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl relative overflow-hidden">
		<!-- Decorative bg element -->
		<div class="absolute -right-16 -top-16 w-32 h-32 bg-brand-100 rounded-full blur-2xl opacity-50"></div>
		
		<div class="text-center mb-8 relative z-10">
			<div class="w-16 h-16 bg-brand-50 rounded-2xl flex items-center justify-center mx-auto mb-6 text-brand-600 shadow-sm border border-brand-100">
				<ShieldCheck class="w-8 h-8" />
			</div>
			<h1 class="text-2xl font-bold text-slate-900">Welcome to SecureATM</h1>
			<p class="text-slate-500 mt-2">Please enter your card number to begin</p>
		</div>

		{#if form?.error}
			<div class="mb-6 p-4 bg-red-50 border border-red-100 rounded-xl flex items-start gap-3 text-red-700">
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
			class="space-y-6 relative z-10"
		>
			<div>
				<label for="cardNumber" class="block text-sm font-medium text-slate-700 mb-2">Card Number</label>
				<div class="relative">
					<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
						<CreditCard class="h-5 w-5 text-slate-400" />
					</div>
					<input
						type="text"
						id="cardNumber"
						name="cardNumber"
						bind:value={cardNumber}
						class="block w-full pl-11 pr-4 py-4 border border-slate-200 rounded-xl bg-slate-50 text-lg tracking-widest text-slate-900 placeholder:text-slate-400 focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-all font-mono"
						placeholder="4860 0000 0000 0000"
						maxlength="19"
						autocomplete="off"
					/>
				</div>
			</div>

			<button
				type="submit"
				disabled={loading || !cardNumber.trim()}
				class="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed text-white py-4 rounded-xl font-semibold text-lg transition-all shadow-md shadow-brand-500/20 active:scale-[0.98]"
			>
				{#if loading}
					<Loader2 class="w-5 h-5 animate-spin" />
					Verifying Card...
				{:else}
					Continue
					<ArrowRight class="w-5 h-5" />
				{/if}
			</button>
		</form>
		
		<div class="mt-8 text-center">
			<a href="/" class="text-sm text-slate-500 hover:text-slate-700 transition-colors">Return to Home</a>
		</div>
	</div>
</div>
