<script lang="ts">
	import { Shield, Fingerprint, Lock, Bell, AlertTriangle } from '@lucide/svelte';
</script>

<svelte:head>
	<title>SecureATM - Secure Banking Starts With You</title>
</svelte:head>

<header class="bg-brand-950 text-white border-b border-brand-800 sticky top-0 z-50">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
		<div class="flex justify-between items-center h-16">
			<div class="flex items-center gap-2">
				<Shield class="w-8 h-8 text-brand-400" />
				<span class="text-xl font-bold tracking-tight">SecureATM</span>
			</div>
			<nav class="hidden md:flex gap-8">
				<a href="#home" class="text-slate-300 hover:text-white transition-colors">Home</a>
				<a href="#how-it-works" class="text-slate-300 hover:text-white transition-colors">How It Works</a>
				<a href="#security" class="text-slate-300 hover:text-white transition-colors">Security</a>
			</nav>
			<div class="flex items-center gap-4">
				<a href="/admin/login" class="text-sm font-medium text-slate-300 hover:text-white">Admin Login</a>
				<a
					href="/atm"
					class="bg-brand-500 hover:bg-brand-400 text-white px-5 py-2 rounded-lg font-medium transition-colors shadow-lg shadow-brand-500/20"
				>
					Get Started
				</a>
			</div>
		</div>
	</div>
</header>

<main>
	<!-- Hero Section -->
	<section id="home" class="relative overflow-hidden bg-brand-950 text-white py-20 lg:py-32">
		<div class="absolute inset-0 bg-[url('/grid.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
			<div class="text-center max-w-3xl mx-auto">
				<h1 class="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-tight">
					Secure Banking <span class="text-brand-400">Starts With You</span>
				</h1>
				<p class="text-lg md:text-xl text-slate-300 mb-10 leading-relaxed">
					A secure ATM transaction platform that combines facial recognition, liveness verification, and real-time user authorization to protect every transaction.
				</p>
				<div class="flex flex-col sm:flex-row justify-center gap-4">
					<a
						href="/atm"
						class="flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-400 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all shadow-lg shadow-brand-500/30 hover:-translate-y-0.5"
					>
						Get Started <span aria-hidden="true">&rarr;</span>
					</a>
					<a
						href="/admin/login"
						class="flex items-center justify-center gap-2 bg-white/10 hover:bg-white/20 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all backdrop-blur-sm"
					>
						Admin Login
					</a>
				</div>
			</div>
		</div>
	</section>

	<!-- Security Features Section -->
	<section id="security" class="py-20 bg-slate-50">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-3xl font-bold text-slate-900 mb-4">Enterprise-Grade Security</h2>
				<p class="text-lg text-slate-600 max-w-2xl mx-auto">Multiple layers of protection ensuring your assets remain secure.</p>
			</div>
			
			<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
				<!-- Feature 1 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<Fingerprint class="w-6 h-6" />
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Facial Recognition</h3>
					<p class="text-slate-600">Verify the identity of the person attempting to access the account securely and instantly.</p>
				</div>
				<!-- Feature 2 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<Shield class="w-6 h-6" />
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Liveness Detection</h3>
					<p class="text-slate-600">Help ensure the detected face belongs to a real person rather than a static image or spoof attempt.</p>
				</div>
				<!-- Feature 3 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<Lock class="w-6 h-6" />
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Real-Time Authorization</h3>
					<p class="text-slate-600">If facial verification fails, the original account holder can instantly approve or reject the suspicious attempt.</p>
				</div>
				<!-- Feature 4 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<span class="font-bold text-xl">₹</span>
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Transaction Control</h3>
					<p class="text-slate-600">When an original user approves a suspicious transaction, they control the maximum amount that can be withdrawn.</p>
				</div>
				<!-- Feature 5 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<Bell class="w-6 h-6" />
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Security Alerts</h3>
					<p class="text-slate-600">Suspicious activity is recorded and immediately communicated to the original user for action.</p>
				</div>
				<!-- Feature 6 -->
				<div class="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
					<div class="w-12 h-12 bg-brand-100 text-brand-600 rounded-xl flex items-center justify-center mb-6">
						<AlertTriangle class="w-6 h-6" />
					</div>
					<h3 class="text-xl font-semibold text-slate-900 mb-3">Complaint Management</h3>
					<p class="text-slate-600">Repeated suspicious attempts can be reported and managed through the comprehensive Admin dashboard.</p>
				</div>
			</div>
		</div>
	</section>

	<!-- How It Works Section -->
	<section id="how-it-works" class="py-20 bg-white border-t border-slate-200">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="text-center mb-16">
				<h2 class="text-3xl font-bold text-slate-900 mb-4">How It Works</h2>
				<p class="text-lg text-slate-600 max-w-2xl mx-auto">A seamless blend of physical presence and digital security.</p>
			</div>

			<div class="grid lg:grid-cols-2 gap-16">
				
				<!-- Normal Flow -->
				<div class="bg-slate-50 rounded-3xl p-8 md:p-12 border border-slate-100 relative overflow-hidden">
					<div class="absolute top-0 right-0 p-8 opacity-5">
						<Shield class="w-48 h-48" />
					</div>
					<h3 class="text-2xl font-bold text-slate-900 mb-8 relative z-10">Standard Transaction</h3>
					
					<div class="space-y-8 relative z-10">
						<div class="flex gap-4">
							<div class="flex flex-col items-center">
								<div class="w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold">01</div>
								<div class="w-0.5 h-full bg-brand-200 my-2"></div>
							</div>
							<div class="pb-6">
								<h4 class="font-semibold text-lg text-slate-900">Enter Card</h4>
								<p class="text-slate-600">Insert your ATM card and initiate the transaction.</p>
							</div>
						</div>
						
						<div class="flex gap-4">
							<div class="flex flex-col items-center">
								<div class="w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold">02</div>
								<div class="w-0.5 h-full bg-brand-200 my-2"></div>
							</div>
							<div class="pb-6">
								<h4 class="font-semibold text-lg text-slate-900">Scan Face</h4>
								<p class="text-slate-600">The system scans your face securely at the terminal.</p>
							</div>
						</div>
						
						<div class="flex gap-4">
							<div class="flex flex-col items-center">
								<div class="w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold">03</div>
								<div class="w-0.5 h-full bg-brand-200 my-2"></div>
							</div>
							<div class="pb-6">
								<h4 class="font-semibold text-lg text-slate-900">Verify Identity</h4>
								<p class="text-slate-600">Instant biometric match confirms your identity.</p>
							</div>
						</div>
						
						<div class="flex gap-4">
							<div class="flex flex-col items-center">
								<div class="w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold">04</div>
								<div class="w-0.5 h-full bg-brand-200 my-2"></div>
							</div>
							<div class="pb-6">
								<h4 class="font-semibold text-lg text-slate-900">Authorize Transaction</h4>
								<p class="text-slate-600">Enter PIN and select transaction details.</p>
							</div>
						</div>
						
						<div class="flex gap-4">
							<div class="flex flex-col items-center">
								<div class="w-10 h-10 rounded-full bg-brand-500 text-white flex items-center justify-center font-bold">05</div>
							</div>
							<div>
								<h4 class="font-semibold text-lg text-slate-900">Complete</h4>
								<p class="text-slate-600">Secure transaction finished successfully.</p>
							</div>
						</div>
					</div>
				</div>

				<!-- Suspicious Flow -->
				<div class="bg-brand-950 text-white rounded-3xl p-8 md:p-12 relative overflow-hidden shadow-xl shadow-brand-900/20">
					<div class="absolute top-0 right-0 p-8 opacity-10">
						<AlertTriangle class="w-48 h-48 text-red-500" />
					</div>
					<h3 class="text-2xl font-bold mb-8 relative z-10 flex items-center gap-3">
						<span class="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
						Suspicious Activity Protocol
					</h3>
					
					<div class="space-y-6 relative z-10">
						<div class="flex items-center gap-4 bg-white/5 p-4 rounded-xl border border-white/10">
							<div class="w-10 h-10 rounded-full bg-red-500/20 text-red-400 flex items-center justify-center shrink-0">
								<AlertTriangle class="w-5 h-5" />
							</div>
							<div>
								<h4 class="font-medium text-red-300">Face Mismatch</h4>
								<p class="text-sm text-slate-400">System detects unauthorized user.</p>
							</div>
						</div>
						
						<div class="flex items-center gap-4 bg-white/5 p-4 rounded-xl border border-white/10">
							<div class="w-10 h-10 rounded-full bg-brand-800 text-brand-300 flex items-center justify-center shrink-0">
								<Fingerprint class="w-5 h-5" />
							</div>
							<div>
								<h4 class="font-medium">Capture & Notify</h4>
								<p class="text-sm text-slate-400">Image captured, original user alerted instantly.</p>
							</div>
						</div>
						
						<div class="flex items-center gap-4 bg-white/5 p-4 rounded-xl border border-white/10">
							<div class="w-10 h-10 rounded-full bg-brand-800 text-brand-300 flex items-center justify-center shrink-0">
								<Lock class="w-5 h-5" />
							</div>
							<div>
								<h4 class="font-medium">Owner Decision</h4>
								<p class="text-sm text-slate-400">Original user Approves or Rejects the attempt.</p>
							</div>
						</div>
						
						<div class="flex items-center gap-4 bg-white/5 p-4 rounded-xl border border-white/10">
							<div class="w-10 h-10 rounded-full bg-brand-800 text-brand-300 flex items-center justify-center shrink-0">
								<Shield class="w-5 h-5" />
							</div>
							<div>
								<h4 class="font-medium">OTP & Limits</h4>
								<p class="text-sm text-slate-400">If approved, OTP verified and strict withdrawal limit set.</p>
							</div>
						</div>
					</div>
				</div>

			</div>
		</div>
	</section>
</main>

<footer class="bg-slate-900 text-slate-400 py-12 border-t border-slate-800">
	<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
		<div class="flex items-center gap-2 text-white">
			<Shield class="w-6 h-6 text-brand-500" />
			<span class="font-semibold">SecureATM</span>
		</div>
		<p class="text-sm">© {new Date().getFullYear()} SecureATM. All rights reserved.</p>
	</div>
</footer>
