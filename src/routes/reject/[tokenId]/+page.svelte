<script lang="ts">
    import { ShieldAlert, CheckCircle2 } from '@lucide/svelte';
    let { data } = $props();
</script>

<svelte:head>
    <title>Transaction Rejected - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-100 flex flex-col items-center justify-center p-4">
    <div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-xl text-center space-y-6">
        <div class="mx-auto w-16 h-16 bg-rose-100 text-rose-600 rounded-full flex items-center justify-center">
            <ShieldAlert class="w-8 h-8" />
        </div>
        
        <h1 class="text-2xl font-bold text-slate-900">Transaction Rejected</h1>
        
        <div class="p-4 bg-slate-50 border border-slate-200 rounded-xl text-sm text-slate-600">
            {data.message}
        </div>
        
        <p class="text-xs text-slate-500">You may safely close this window. If you suspect your card is compromised, please contact customer support immediately.</p>
    </div>
</div>
