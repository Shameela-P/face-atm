<script lang="ts">
	import { onMount } from 'svelte';
	import { ShieldAlert, AlertTriangle, Home } from '@lucide/svelte';

	let cardNumber = $state('');

	onMount(() => {
		const card = sessionStorage.getItem('atm_card_number');
		if (card) {
			cardNumber = `**** **** **** ${card.slice(-4)}`;
		}
		
		// In a real app, this page would trigger an API call to notify the original user
		// and create a Security Incident record in the database.
	});
</script>

<svelte:head>
	<title>Security Alert - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-900 flex items-center justify-center p-4">
	<div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl border-t-8 border-red-500 relative overflow-hidden">
		
		<div class="w-20 h-20 bg-red-50 text-red-500 rounded-2xl flex items-center justify-center mx-auto mb-6 relative">
			<div class="absolute inset-0 bg-red-400 opacity-20 rounded-2xl animate-ping"></div>
			<ShieldAlert class="w-10 h-10 relative z-10" />
		</div>
		
		<div class="text-center mb-8">
			<h1 class="text-2xl font-bold text-slate-900 mb-2">Verification Failed</h1>
			<p class="text-slate-600">
				We could not verify the identity of the person using this card ({cardNumber}).
			</p>
		</div>

		<div class="bg-red-50 border border-red-100 rounded-2xl p-5 mb-8">
			<h3 class="font-semibold text-red-800 flex items-center gap-2 mb-2">
				<AlertTriangle class="w-5 h-5" />
				Security Protocol Activated
			</h3>
			<ul class="text-sm text-red-700 space-y-2 list-disc list-inside">
				<li>Transaction temporarily blocked</li>
				<li>Account holder has been notified</li>
				<li>Security image captured</li>
				<li>Awaiting account holder authorization</li>
			</ul>
		</div>

		<div class="text-center">
			<p class="text-sm text-slate-500 mb-6">
				Please wait while the original account holder reviews this transaction attempt.
			</p>
			<a
				href="/"
				class="inline-flex items-center justify-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 px-6 py-3 rounded-xl font-medium transition-colors"
			>
				<Home class="w-4 h-4" />
				Return to Home
			</a>
		</div>

	</div>
</div>
