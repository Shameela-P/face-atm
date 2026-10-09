<script lang="ts">
    import { enhance } from '$app/forms';
    import { ShieldCheck, AlertCircle, CheckCircle2, Loader2, ArrowRight } from '@lucide/svelte';

    let { data, form } = $props();
    let loading = $state(false);
</script>

<svelte:head>
    <title>Authorize Transaction - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-4">
    <div class="max-w-lg w-full bg-white rounded-3xl p-8 shadow-xl">
        <div class="text-center space-y-4 mb-8">
            <div class="mx-auto w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center">
                <ShieldCheck class="w-8 h-8" />
            </div>
            <h1 class="text-2xl font-bold text-slate-900">Authorize ATM Access</h1>
            <p class="text-slate-500 text-sm">Review the access attempt details below to securely authorize this transaction.</p>
        </div>

        {#if form?.success}
            <div class="p-6 bg-emerald-50 border border-emerald-200 rounded-2xl text-center space-y-4">
                <CheckCircle2 class="w-12 h-12 text-emerald-500 mx-auto" />
                <h2 class="text-xl font-bold text-emerald-700">Approval Confirmed</h2>
                <p class="text-emerald-600 text-sm">We have sent a one-time OTP to your email address. Please share this OTP securely with the person at the ATM.</p>
                <p class="text-xs text-slate-500 mt-4">You may safely close this window.</p>
            </div>
        {:else if data.request.status === 'PENDING'}
            <div class="space-y-6">
                <div class="bg-slate-50 p-4 rounded-2xl border border-slate-200">
                    <p class="text-xs text-slate-500 font-semibold uppercase mb-2">Attempted Image</p>
                    <img src={data.request.attemptedImageUrl} alt="Attempted Face" class="w-full h-48 object-cover rounded-xl" />
                    
                    <div class="mt-4 space-y-2">
                        <div class="flex justify-between text-sm">
                            <span class="text-slate-500">Card Number:</span>
                            <span class="font-bold text-slate-800 font-mono">{data.request.cardNumber}</span>
                        </div>
                        <div class="flex justify-between text-sm">
                            <span class="text-slate-500">Attempt Time:</span>
                            <span class="text-slate-800">{new Date(data.request.createdAt).toLocaleString()}</span>
                        </div>
                    </div>
                </div>

                {#if form?.error}
                    <div class="p-3 bg-rose-50 border border-rose-200 rounded-xl flex items-center gap-2 text-rose-600 text-xs font-semibold">
                        <AlertCircle class="w-4 h-4 shrink-0" />
                        <p>{form.error}</p>
                    </div>
                {/if}

                <form method="POST" action="?/approve" use:enhance={() => { loading = true; return async ({ update }) => { await update(); loading = false; } }} class="space-y-4">
                    <div>
                        <label class="block text-sm font-semibold text-slate-700 mb-2">Maximum Authorized Amount (₹)</label>
                        <input type="number" name="maxAmount" placeholder="e.g. 5000" min="100" step="100" required class="w-full bg-white border border-slate-300 rounded-xl px-4 py-3 text-slate-900 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all" />
                    </div>
                    <button type="submit" disabled={loading} class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50">
                        {#if loading}
                            <Loader2 class="w-5 h-5 animate-spin" /> Authorizing...
                        {:else}
                            Confirm & Generate OTP <ArrowRight class="w-4 h-4" />
                        {/if}
                    </button>
                </form>
            </div>
        {:else}
            <div class="p-6 bg-slate-50 border border-slate-200 rounded-2xl text-center space-y-2">
                <AlertCircle class="w-8 h-8 text-slate-400 mx-auto" />
                <h3 class="text-lg font-bold text-slate-700">Request No Longer Pending</h3>
                <p class="text-sm text-slate-500">This request has already been {data.request.status.toLowerCase()}.</p>
            </div>
        {/if}
    </div>
</div>
