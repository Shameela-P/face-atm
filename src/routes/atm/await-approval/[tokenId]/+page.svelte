<script lang="ts">
    import { enhance } from '$app/forms';
    import { onMount } from 'svelte';
    import { Loader2, AlertCircle, ShieldCheck, Mail, ArrowLeft } from '@lucide/svelte';

    let { data, form } = $props();
    let loading = $state(false);

    // Auto-refresh the page every 3 seconds to check for status changes if still pending
    onMount(() => {
        let timer: any;
        if (data.request.status === 'PENDING') {
            timer = setInterval(() => {
                window.location.reload();
            }, 3000);
        }
        return () => clearInterval(timer);
    });
</script>

<svelte:head>
    <title>Awaiting Approval - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4">
    <div class="max-w-md w-full bg-slate-900 border border-slate-800 rounded-3xl p-8 shadow-2xl relative">
        {#if data.request.status === 'PENDING'}
            <div class="text-center space-y-6">
                <div class="mx-auto w-20 h-20 bg-amber-500/10 rounded-full flex items-center justify-center text-amber-500 border-2 border-amber-500/50">
                    <Loader2 class="w-10 h-10 animate-spin" />
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-white mb-2">Awaiting Approval</h2>
                    <p class="text-slate-400 text-sm">Face verification did not match. An authorization request has been sent to the account owner.</p>
                </div>
                <div class="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs text-slate-500 font-mono">
                    Please wait here. The owner must approve the request and provide you with an OTP.
                </div>
            </div>
        {:else if data.request.status === 'REJECTED'}
            <div class="text-center space-y-6">
                <div class="mx-auto w-20 h-20 bg-rose-500/10 rounded-full flex items-center justify-center text-rose-500 border-2 border-rose-500/50">
                    <AlertCircle class="w-10 h-10" />
                </div>
                <div>
                    <h2 class="text-2xl font-bold text-white mb-2">Transaction Rejected</h2>
                    <p class="text-slate-400 text-sm">The account owner has denied this access request. No transaction was performed.</p>
                </div>
                <a href="/atm" class="inline-flex items-center gap-2 bg-slate-800 text-white px-6 py-2.5 rounded-xl text-sm font-semibold hover:bg-slate-700 transition-colors">
                    <ArrowLeft class="w-4 h-4" /> Return Home
                </a>
            </div>
        {:else if data.request.status === 'APPROVED'}
            <div class="space-y-6">
                <div class="text-center space-y-2">
                    <div class="mx-auto w-16 h-16 bg-emerald-500/10 rounded-full flex items-center justify-center text-emerald-500 mb-4">
                        <ShieldCheck class="w-8 h-8" />
                    </div>
                    <h2 class="text-2xl font-bold text-white">Owner Approved</h2>
                    <p class="text-slate-400 text-sm">The owner has authorized a maximum of ₹{data.request.maxAmount?.toLocaleString()}.</p>
                </div>

                <div class="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl flex items-start gap-3">
                    <Mail class="w-5 h-5 text-emerald-500 shrink-0 mt-0.5" />
                    <p class="text-xs text-emerald-400">An OTP has been sent to the owner's registered email address. Enter it below to proceed.</p>
                </div>

                {#if form?.error}
                    <div class="p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-center gap-2 text-rose-400 text-xs font-semibold">
                        <AlertCircle class="w-4 h-4 shrink-0" />
                        <p>{form.error}</p>
                    </div>
                {/if}

                <form method="POST" action="?/verifyOtp" use:enhance={() => { loading = true; return async ({ update }) => { await update(); loading = false; } }} class="space-y-4">
                    <div>
                        <input 
                            type="text" 
                            name="otp" 
                            placeholder="Enter 6-digit OTP" 
                            pattern="[0-9\\s]*"
                            maxlength="12"
                            required 
                            class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-4 text-center text-3xl font-mono text-white tracking-[0.5em] placeholder:tracking-normal focus:outline-none focus:border-emerald-500 transition-colors"
                        />
                    </div>
                    <button 
                        type="submit" 
                        disabled={loading}
                        class="w-full flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-500 text-white py-3.5 rounded-xl font-bold transition-colors disabled:opacity-50"
                    >
                        {#if loading}
                            <Loader2 class="w-5 h-5 animate-spin" /> Verifying...
                        {:else}
                            Unlock Transaction
                        {/if}
                    </button>
                </form>
            </div>
        {/if}
    </div>
</div>
