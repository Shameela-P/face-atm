<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { enhance } from '$app/forms';
	import { Camera, ScanFace, ShieldAlert, ShieldCheck, Loader2, AlertCircle } from '@lucide/svelte';

	let { data, form } = $props();

	let videoElement: HTMLVideoElement;
	let stream: MediaStream | null = null;
	let photoDataUrl = $state('');
	let scanStatus = $state<'idle' | 'detecting' | 'verifying' | 'success' | 'failed'>('idle');
	let loading = $state(false);
	
	onMount(async () => {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: true });
			if (videoElement) {
				videoElement.srcObject = stream;
			}
		} catch (err) {
			console.error("Camera access denied:", err);
		}
	});

	onDestroy(() => {
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
		}
	});

	function captureAndSubmit(formElement: HTMLFormElement) {
		if (!videoElement) {
			alert("Camera is not available.");
			return;
		}

		// Capture live camera frame
		const canvas = document.createElement('canvas');
		canvas.width = videoElement.videoWidth || 640;
		canvas.height = videoElement.videoHeight || 480;
		const ctx = canvas.getContext('2d');
		if (ctx) {
			ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
		}
		photoDataUrl = canvas.toDataURL('image/jpeg');
		scanStatus = 'verifying';
		
		// Trigger server form submission
		setTimeout(() => {
			formElement.requestSubmit();
		}, 100);
	}
</script>

<svelte:head>
	<title>Identity Verification - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-900 flex items-center justify-center p-4">
	<div class="max-w-md w-full bg-white rounded-3xl p-8 shadow-2xl relative overflow-hidden">
		
		<div class="text-center mb-6">
			<h1 class="text-2xl font-bold text-slate-900">Identity Verification</h1>
			<p class="text-slate-500 mt-2">
				{#if scanStatus === 'idle'}
					Verifying Card Owner: <strong class="text-slate-800">{data.ownerName}</strong>
				{:else if scanStatus === 'detecting' || scanStatus === 'verifying'}
					MTCNN Detection & FaceNet Match for {data.ownerName}...
				{:else if scanStatus === 'success'}
					<span class="text-green-600 font-medium">Identity Verified ✓</span>
				{:else if scanStatus === 'failed'}
					<span class="text-red-600 font-medium">Verification Failed!</span>
				{/if}
			</p>
			{#if !data.hasRegisteredEmbedding}
				<div class="mt-2 text-xs font-semibold bg-amber-100 text-amber-800 px-3 py-1.5 rounded-lg">
					⚠️ Owner Face Not Registered in DB (Admin must register owner face first)
				</div>
			{/if}
		</div>

		{#if form?.error}
			<div class="mb-6 p-4 bg-red-50 border border-red-200 rounded-2xl flex items-start gap-3 text-red-700">
				<AlertCircle class="w-5 h-5 shrink-0 mt-0.5" />
				<p class="text-sm font-medium leading-relaxed">{form.error}</p>
			</div>
		{/if}

		<!-- Camera Viewfinder -->
		<div class="relative aspect-[3/4] bg-slate-100 rounded-2xl overflow-hidden border-4 {scanStatus === 'success' ? 'border-green-500' : scanStatus === 'failed' ? 'border-red-500' : 'border-slate-200'} transition-colors duration-500 mb-8">
			<!-- svelte-ignore a11y_media_has_caption -->
			<video 
				bind:this={videoElement} 
				autoplay 
				playsinline 
				class="w-full h-full object-cover transform -scale-x-100"
			></video>
			
			<!-- Overlay Guidelines -->
			<div class="absolute inset-0 pointer-events-none flex items-center justify-center p-8">
				<div class="w-full h-full border-2 border-white/30 rounded-[3rem] relative">
					{#if loading}
						<div class="absolute top-0 left-0 w-full h-1 bg-brand-500 shadow-[0_0_15px_rgba(59,130,246,0.8)] animate-[scan_2s_ease-in-out_infinite]"></div>
					{/if}
				</div>
			</div>
			
			<!-- Status Overlay Icons -->
			{#if scanStatus === 'success'}
				<div class="absolute inset-0 bg-green-500/20 flex items-center justify-center backdrop-blur-sm">
					<div class="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center text-white shadow-xl shadow-green-500/30">
						<ShieldCheck class="w-10 h-10" />
					</div>
				</div>
			{:else if scanStatus === 'failed'}
				<div class="absolute inset-0 bg-red-500/20 flex items-center justify-center backdrop-blur-sm">
					<div class="w-20 h-20 bg-red-500 rounded-full flex items-center justify-center text-white shadow-xl shadow-red-500/30">
						<ShieldAlert class="w-10 h-10" />
					</div>
				</div>
			{/if}
		</div>

		<form 
			method="POST" 
			action="?/verifyFace"
			use:enhance={() => {
				loading = true;
				return async ({ result, update }) => {
					loading = false;
					if (result.type === 'success' && result.data?.success) {
						scanStatus = 'success';
						setTimeout(() => {
							window.location.href = '/atm/transaction';
						}, 1000);
					} else {
						scanStatus = 'failed';
						await update();
					}
				};
			}}
		>
			<input type="hidden" name="image" value={photoDataUrl} />

			{#if scanStatus === 'idle' || scanStatus === 'failed'}
				<button
					type="button"
					disabled={loading || !data.hasRegisteredEmbedding}
					onclick={(e) => captureAndSubmit(e.currentTarget.form!)}
					class="w-full flex items-center justify-center gap-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white py-4 rounded-xl font-semibold text-lg transition-all shadow-md shadow-brand-500/20 active:scale-[0.98]"
				>
					<ScanFace class="w-5 h-5" />
					Start Face Scan
				</button>
			{:else}
				<button
					disabled
					class="w-full flex items-center justify-center gap-2 bg-slate-100 text-slate-500 py-4 rounded-xl font-semibold text-lg cursor-wait"
				>
					<Loader2 class="w-5 h-5 animate-spin" />
					Verifying Live Face vs {data.ownerName}...
				</button>
			{/if}
		</form>

	</div>
</div>

<style>
	@keyframes scan {
		0%, 100% { top: 0%; }
		50% { top: 100%; }
	}
</style>
