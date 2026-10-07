<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { enhance } from '$app/forms';
	import { 
		Camera, ScanFace, ShieldAlert, ShieldCheck, Loader2, AlertCircle, 
		Lock, UserX, Cpu, RefreshCw, XCircle, ArrowLeft
	} from '@lucide/svelte';

	let { data, form } = $props();

	let videoElement: HTMLVideoElement;
	let stream: MediaStream | null = null;
	let photoDataUrl = $state('');
	
	// Real-time camera & ML status pipeline state
	let scanStage = $state<'position' | 'detected' | 'checking_liveness' | 'verifying_facenet' | 'verified' | 'failed'>('position');
	let loading = $state(false);
	let errorMessage = $state('');
	
	onMount(async () => {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: { width: 1280, height: 720 } });
			if (videoElement) {
				videoElement.srcObject = stream;
			}
		} catch (err) {
			console.error("Camera access denied:", err);
			errorMessage = "Unable to access camera. Please check permissions.";
		}
	});

	onDestroy(() => {
		if (stream) {
			stream.getTracks().forEach(track => track.stop());
		}
	});

	function captureAndSubmit(formElement: HTMLFormElement) {
		if (!videoElement) {
			errorMessage = "Camera is offline or denied.";
			return;
		}

		errorMessage = '';
		scanStage = 'detected';

		// Step sequence display simulating backend biometric pipeline feedback
		setTimeout(() => {
			scanStage = 'checking_liveness';
		}, 400);

		setTimeout(() => {
			scanStage = 'verifying_facenet';
		}, 900);

		// Capture live camera frame
		const canvas = document.createElement('canvas');
		canvas.width = videoElement.videoWidth || 640;
		canvas.height = videoElement.videoHeight || 480;
		const ctx = canvas.getContext('2d');
		if (ctx) {
			// Un-mirror canvas when capturing frame
			ctx.translate(canvas.width, 0);
			ctx.scale(-1, 1);
			ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
		}
		photoDataUrl = canvas.toDataURL('image/jpeg', 0.92);

		setTimeout(() => {
			formElement.requestSubmit();
		}, 1200);
	}
</script>

<svelte:head>
	<title>ATM Face Verification - SecureATM</title>
</svelte:head>

<div class="min-h-screen bg-slate-950 flex items-center justify-center p-4 relative font-sans text-slate-100 overflow-hidden">
	<!-- Ambient Glow & Cyber Grid -->
	<div class="absolute inset-0 bg-radial from-cyan-950/30 via-slate-950 to-slate-950 pointer-events-none"></div>
	<div class="absolute inset-0 bg-[linear-gradient(to_right,#1e293b15_1px,transparent_1px),linear-gradient(to_bottom,#1e293b15_1px,transparent_1px)] bg-[size:32px_32px]"></div>

	<div class="max-w-md w-full relative z-10 space-y-4">
		
		<!-- Terminal Frame -->
		<div class="bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-5 backdrop-blur-xl relative overflow-hidden">
			
			<!-- Header Status Bar -->
			<div class="flex items-center justify-between border-b border-slate-800 pb-4">
				<div class="flex items-center gap-2.5">
					<div class="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 flex items-center justify-center">
						<ScanFace class="w-6 h-6" />
					</div>
					<div>
						<h1 class="text-base font-bold text-white">Biometric Terminal</h1>
						<p class="text-xs text-slate-400 font-mono">1:1 Card-Bound Identity</p>
					</div>
				</div>

				<div class="text-right">
					<span class="text-xs font-mono text-slate-400 block">Owner Card</span>
					<span class="text-xs font-mono font-bold text-cyan-400">**** {data.card.slice(-4)}</span>
				</div>
			</div>

			<!-- Dynamic Status Banner -->
			<div class="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-3.5 text-center space-y-1">
				{#if scanStage === 'position'}
					<p class="text-sm font-bold text-white flex items-center justify-center gap-2">
						<Camera class="w-4 h-4 text-cyan-400 animate-pulse" />
						Look directly at the camera frame
					</p>
					<p class="text-[11px] text-slate-400">Position your face inside the scanning target</p>
				{:else if scanStage === 'detected'}
					<p class="text-sm font-bold text-cyan-400 flex items-center justify-center gap-2">
						<ScanFace class="w-4 h-4" />
						Face Detected
					</p>
					<p class="text-[11px] text-slate-400">Aligning 5-point facial landmarks...</p>
				{:else if scanStage === 'checking_liveness'}
					<p class="text-sm font-bold text-amber-400 flex items-center justify-center gap-2">
						<Loader2 class="w-4 h-4 animate-spin" />
						Checking Live Person Anti-Spoofing...
					</p>
					<p class="text-[11px] text-slate-400">Liveness CNN depth texture analysis</p>
				{:else if scanStage === 'verifying_facenet'}
					<p class="text-sm font-bold text-indigo-400 flex items-center justify-center gap-2">
						<Cpu class="w-4 h-4 animate-pulse" />
						Verifying Identity vs Account Owner...
					</p>
					<p class="text-[11px] text-slate-400">Comparing 128-D FaceNet embeddings</p>
				{:else if scanStage === 'verified'}
					<p class="text-sm font-bold text-emerald-400 flex items-center justify-center gap-2">
						<ShieldCheck class="w-4 h-4" />
						Identity Verified — Access Granted
					</p>
				{:else if scanStage === 'failed'}
					<p class="text-sm font-bold text-rose-400 flex items-center justify-center gap-2">
						<ShieldAlert class="w-4 h-4" />
						ACCESS DENIED — Verification Failed
					</p>
				{/if}
			</div>

			<!-- Warning if owner face embedding is missing in RTDB -->
			{#if !data.hasRegisteredEmbedding}
				<div class="p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl text-amber-400 text-xs font-semibold text-center">
					⚠️ Registered owner face template not found in Firebase. Please ask Admin to register customer face first.
				</div>
			{/if}

			<!-- Error Feedback Banner -->
			{#if form?.error || errorMessage}
				<div class="p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl flex items-start gap-3 text-rose-400 text-xs font-medium animate-in fade-in">
					<ShieldAlert class="w-5 h-5 shrink-0 text-rose-400 mt-0.5" />
					<div class="space-y-1">
						<p class="font-bold text-sm text-rose-300">ACCESS DENIED</p>
						<p class="leading-relaxed">{form?.error || errorMessage}</p>
					</div>
				</div>
			{/if}

			<!-- Camera Viewfinder with Laser Scanlines -->
			<div class="relative aspect-[4/3] bg-slate-950 rounded-2xl overflow-hidden border-2 {scanStage === 'verified' ? 'border-emerald-500' : scanStage === 'failed' ? 'border-rose-500' : 'border-slate-800'} transition-all duration-300 shadow-inner">
				
				<!-- Live Video Stream -->
				<!-- svelte-ignore a11y_media_has_caption -->
				<video 
					bind:this={videoElement} 
					autoplay 
					playsinline 
					class="w-full h-full object-cover transform -scale-x-100"
				></video>

				<!-- Subtle Scanning Frame Guidelines -->
				<div class="absolute inset-0 pointer-events-none flex items-center justify-center p-6">
					<div class="w-48 h-48 sm:w-56 sm:h-56 border-2 border-dashed border-cyan-400/40 rounded-full relative flex items-center justify-center">
						<div class="w-full h-full border border-cyan-400/20 rounded-full animate-ping"></div>
						
						<!-- Corner Markers -->
						<div class="absolute -top-1 -left-1 w-4 h-4 border-t-2 border-l-2 border-cyan-400"></div>
						<div class="absolute -top-1 -right-1 w-4 h-4 border-t-2 border-r-2 border-cyan-400"></div>
						<div class="absolute -bottom-1 -left-1 w-4 h-4 border-b-2 border-l-2 border-cyan-400"></div>
						<div class="absolute -bottom-1 -right-1 w-4 h-4 border-b-2 border-r-2 border-cyan-400"></div>

						<!-- Laser Scanline Animation when loading -->
						{#if loading}
							<div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-cyan-400 to-transparent shadow-[0_0_15px_#22d3ee] animate-[scan_1.5s_ease-in-out_infinite]"></div>
						{/if}
					</div>
				</div>

				<!-- Verification Outcome Overlays -->
				{#if scanStage === 'verified'}
					<div class="absolute inset-0 bg-emerald-950/70 backdrop-blur-sm flex flex-col items-center justify-center text-emerald-400 p-4 animate-in fade-in">
						<div class="w-16 h-16 bg-emerald-500/20 rounded-full border border-emerald-500/40 flex items-center justify-center mb-2">
							<ShieldCheck class="w-10 h-10 text-emerald-400" />
						</div>
						<h3 class="text-base font-bold text-white">Identity Verified</h3>
						<p class="text-xs text-emerald-300 mt-1 font-mono">1:1 FaceNet Match Confirmed</p>
					</div>
				{:else if scanStage === 'failed'}
					<div class="absolute inset-0 bg-rose-950/85 backdrop-blur-sm flex flex-col items-center justify-center text-rose-400 p-4 text-center animate-in fade-in">
						<div class="w-16 h-16 bg-rose-500/20 rounded-full border border-rose-500/40 flex items-center justify-center mb-2">
							<UserX class="w-10 h-10 text-rose-400" />
						</div>
						<h3 class="text-base font-bold text-white">ACCESS DENIED</h3>
						<p class="text-xs text-rose-300 mt-1 max-w-xs leading-relaxed">
							Identity verification failed. Attempt recorded & security alert dispatched.
						</p>
					</div>
				{/if}
			</div>

			<!-- Scan Action Form -->
			<form 
				method="POST" 
				action="?/verifyFace"
				use:enhance={() => {
					loading = true;
					return async ({ result, update }) => {
						loading = false;
						if (result.type === 'success' && result.data?.success) {
							scanStage = 'verified';
							setTimeout(() => {
								window.location.href = '/atm/transaction';
							}, 1000);
						} else {
							scanStage = 'failed';
							await update();
						}
					};
				}}
			>
				<input type="hidden" name="image" value={photoDataUrl} />

				{#if !loading && scanStage !== 'verified'}
					<button
						type="button"
						disabled={!data.hasRegisteredEmbedding}
						onclick={(e) => captureAndSubmit(e.currentTarget.form!)}
						class="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-brand-600 to-cyan-600 hover:from-brand-500 hover:to-cyan-500 disabled:opacity-40 text-white py-4 rounded-2xl font-bold text-base transition-all shadow-xl shadow-brand-500/20 active:scale-[0.99]"
					>
						<ScanFace class="w-5 h-5" />
						{scanStage === 'failed' ? 'Retry Face Verification' : 'Authenticate Face'}
					</button>
				{:else if loading}
					<button
						disabled
						class="w-full flex items-center justify-center gap-2 bg-slate-800 text-cyan-400 py-4 rounded-2xl font-bold text-base cursor-wait border border-slate-700"
					>
						<Loader2 class="w-5 h-5 animate-spin" />
						Processing Biometric Pipeline...
					</button>
				{/if}
			</form>
		</div>

		<div class="text-center">
			<a href="/atm" class="text-xs font-medium text-slate-500 hover:text-slate-300 transition-colors inline-flex items-center gap-1">
				<ArrowLeft class="w-3.5 h-3.5" />
				Cancel & Re-enter Card Number
			</a>
		</div>
	</div>
</div>

<style>
	@keyframes scan {
		0%, 100% { top: 10%; }
		50% { top: 90%; }
	}
</style>
