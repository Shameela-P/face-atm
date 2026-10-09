<script lang="ts">
	import { enhance } from '$app/forms';
	import { CreditCard, ArrowRight, ShieldCheck, AlertCircle, Loader2, Lock, Cpu, CheckCircle2 } from '@lucide/svelte';
	
	let { data, form } = $props();
	let loading = $state(false);
	let cardNumber = $state(form?.cardNumber || '');

	function formatCardDisplay(val: string) {
		const clean = val.replace(/\D/g, '').slice(0, 7);
		return clean;
	}

	function handleInput(e: Event) {
		const target = e.target as HTMLInputElement;
		const raw = target.value;
		cardNumber = formatCardDisplay(raw);
	}
</script>

<svelte:head>
	<title>SecureATM Terminal - Card Entry</title>
</svelte:head>

<div class="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative font-sans text-slate-100 overflow-hidden">
	<!-- Ambient Terminal Grid -->
	<div class="absolute inset-0 bg-radial from-brand-950/40 via-slate-950 to-slate-950 pointer-events-none"></div>
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b20_1px,transparent_1px),linear-gradient(to_bottom,#1e293b20_1px,transparent_1px)] bg-[size:32px_32px]"></div>

	<!-- Main ATM Terminal Container -->
	<div class="max-w-md w-full relative z-10 space-y-6">
		
		<!-- Terminal Frame Banner -->
		<div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-2xl space-y-6 backdrop-blur-xl relative overflow-hidden">
			
			<!-- Glowing Header Badge -->
			<div class="flex items-center justify-between border-b border-slate-800 pb-5">
				<div class="flex items-center gap-3">
					<div class="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center shadow-lg shadow-cyan-500/10">
						<ShieldCheck class="w-7 h-7" />
					</div>
					<div>
						<h1 class="text-xl font-extrabold text-white tracking-tight">SecureATM</h1>
						<p class="text-xs text-slate-400 font-mono">Terminal #01 • Biometric Banking</p>
					</div>
				</div>
				<div class="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
					<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
					READY
				</div>
			</div>

			<!-- Screen Header Prompt -->
			<div class="text-center space-y-1 py-2">
				<h2 class="text-lg font-bold text-white">Enter Your ATM Card Number</h2>
				<p class="text-xs text-slate-400">1:1 Biometric Face Verification will follow card identification</p>
			</div>

			<!-- Success Feedback -->
			{#if data.successMessage}
				<div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-start gap-3 text-emerald-400 text-sm animate-in fade-in">
					<CheckCircle2 class="w-5 h-5 shrink-0 mt-0.5" />
					<p class="font-medium leading-relaxed text-xs">{data.successMessage}</p>
				</div>
			{/if}

			<!-- Error Feedback -->
			{#if form?.error}
				<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-start gap-3 text-rose-400 text-sm animate-in fade-in">
					<AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
					<p class="font-medium leading-relaxed text-xs">{form.error}</p>
				</div>
			{/if}

			<!-- Card Form -->
			<form 
				method="POST" 
				use:enhance={() => {
					loading = true;
					return async ({ update }) => {
						await update();
						loading = false;
					};
				}}
				class="space-y-6"
			>
				<div>
					<label for="cardNumber" class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">
						ATM Card Number
					</label>
					<div class="relative">
						<div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
							<CreditCard class="h-5 w-5 text-cyan-400" />
						</div>
						<input
							type="text"
							id="cardNumber"
							name="cardNumber"
							value={cardNumber}
							oninput={handleInput}
							class="w-full bg-slate-950 border border-slate-800 rounded-2xl pl-12 pr-4 py-4 text-xl tracking-widest text-center text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono shadow-inner"
							placeholder="1234567"
							maxlength="7"
							autocomplete="off"
						/>
					</div>
				</div>

				<button
					type="submit"
					disabled={loading || cardNumber.replace(/\s+/g, '').length < 6}
					class="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 disabled:opacity-40 disabled:cursor-not-allowed text-white py-4 rounded-2xl font-bold text-base transition-all shadow-xl shadow-brand-500/20 active:scale-[0.99]"
				>
					{#if loading}
						<Loader2 class="w-5 h-5 animate-spin" />
						Authenticating Card...
					{:else}
						Proceed to Face Verification
						<ArrowRight class="w-5 h-5" />
					{/if}
				</button>
			</form>
			
			<div class="pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500 font-mono">
				<span class="flex items-center gap-1">
					<Lock class="w-3.5 h-3.5 text-cyan-400" />
					256-Bit Encrypted Session
				</span>
				<span class="flex items-center gap-1">
					<Cpu class="w-3.5 h-3.5 text-brand-400" />
					FaceNet AI 1:1
				</span>
			</div>
		</div>

		<div class="text-center">
			<a href="/" class="text-xs font-medium text-slate-500 hover:text-slate-300 transition-colors">&larr; Exit Terminal & Return Home</a>
		</div>
	</div>
</div>
