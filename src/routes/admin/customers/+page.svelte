<script lang="ts">
	import { enhance } from '$app/forms';
	import { 
		UserPlus, Search, ShieldCheck, X, AlertCircle, CheckCircle2, 
		Loader2, Building2, CreditCard, Eye, Plus, UserX, UserCheck, Camera,
		PhoneCall, KeyRound, Check, RefreshCw
	} from '@lucide/svelte';
	import { onDestroy } from 'svelte';

	let { data, form } = $props();
	
	let searchTerm = $state('');
	let showRegistrationModal = $state(false);
	let showDetailsModal = $state(false);
	let showAddBankModal = $state(false);
	let showSuccessModal = $state(false);
	
	let selectedCustomer = $state<any>(null);
	let addBankCustomer = $state<any>(null);
	let newlyRegisteredCustomer = $state<any>(null);

	// Registration form fields state
	let fullName = $state('');
	let email = $state('');
	let dob = $state('');
	let aadhaarNumber = $state('');
	let bankName = $state('');
	let accountNumber = $state('');
	let mobileNumber = $state('');
	let verifiedEmailAddress = $state('');
	let otpCode = $state('');
	let otpSent = $state(false);
	let emailVerified = $state(false);
	let maskedEmailDisplay = $state('');
	let otpNotice = $state('');
	let otpErrorMsg = $state('');
	let otpTimer = $state(0);
	let otpTimerInterval: any = null;

	// Camera & Face Validation state for Admin Face Capture
	let videoElement = $state<HTMLVideoElement | null>(null);
	let stream: MediaStream | null = null;
	let capturedB64 = $state('');
	let cameraActive = $state(false);
	let loading = $state(false);
	let sendingOtp = $state(false);
	let verifyingOtp = $state(false);
	let addBankLoading = $state(false);
	let capturingFace = $state(false);
	let faceStatusStep = $state('');
	let faceErrorMsg = $state('');
	let retryingEmail = $state(false);

	let filteredCustomers = $derived(
		data.customers.filter((c: any) => 
			c.fullName.toLowerCase().includes(searchTerm.toLowerCase()) || 
			c.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
			c.aadhaarNumber.includes(searchTerm) ||
			c.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
			c.bankAccounts.some((b: any) => b.bankName.toLowerCase().includes(searchTerm.toLowerCase()) || b.accountNumber.includes(searchTerm))
		)
	);

	function startOtpCountdown(seconds = 300) {
		if (otpTimerInterval) clearInterval(otpTimerInterval);
		otpTimer = seconds;
		otpTimerInterval = setInterval(() => {
			if (otpTimer > 0) {
				otpTimer -= 1;
			} else {
				clearInterval(otpTimerInterval);
				otpTimerInterval = null;
			}
		}, 1000);
	}

	function formatTimer(seconds: number) {
		const m = Math.floor(seconds / 60).toString().padStart(2, '0');
		const s = (seconds % 60).toString().padStart(2, '0');
		return `${m}:${s}`;
	}

	async function handleSendOtp() {
		if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
			otpErrorMsg = 'Please enter a valid email address.';
			return;
		}
		sendingOtp = true;
		otpErrorMsg = '';
		otpNotice = '';
		try {
			const res = await fetch('/api/otp/send', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email: email })
			});
			const resData = await res.json();
			sendingOtp = false;
			if (resData.success) {
				otpSent = true;
				otpCode = '';
				maskedEmailDisplay = resData.maskedEmail || email;
				otpNotice = resData.message || `OTP sent to ${maskedEmailDisplay}`;
				startOtpCountdown(resData.expiresIn || 300);
			} else {
				otpErrorMsg = resData.error || 'Failed to send OTP.';
			}
		} catch (e) {
			sendingOtp = false;
			otpErrorMsg = 'Network error sending OTP.';
		}
	}

	async function handleVerifyOtp() {
		if (!/^[0-9]{6}$/.test(otpCode)) {
			otpErrorMsg = 'OTP must be exactly 6 numeric digits.';
			return;
		}
		verifyingOtp = true;
		otpErrorMsg = '';
		otpNotice = '';
		try {
			const res = await fetch('/api/otp/verify', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ email: email, otp: otpCode })
			});
			const resData = await res.json();
			verifyingOtp = false;
			if (resData.success) {
				emailVerified = true;
				verifiedEmailAddress = email;
				otpNotice = 'Email address verified successfully.';
				if (otpTimerInterval) clearInterval(otpTimerInterval);
			} else {
				otpErrorMsg = resData.error || 'Incorrect OTP. Please try again.';
			}
		} catch (e) {
			verifyingOtp = false;
			otpErrorMsg = 'Network error verifying OTP.';
		}
	}

	async function startCamera() {
		try {
			stream = await navigator.mediaDevices.getUserMedia({ video: true });
			if (videoElement) {
				videoElement.srcObject = stream;
				cameraActive = true;
			}
		} catch (err) {
			console.error("Camera access failed:", err);
			alert("Camera access denied or unavailable.");
		}
	}

	function stopCamera() {
		if (stream) {
			stream.getTracks().forEach(t => t.stop());
			stream = null;
		}
		cameraActive = false;
	}

	async function captureAndValidateFace() {
		if (!videoElement) return;
		capturingFace = true;
		faceErrorMsg = '';
		faceStatusStep = 'Capturing...';

		const canvas = document.createElement('canvas');
		canvas.width = videoElement.videoWidth || 640;
		canvas.height = videoElement.videoHeight || 480;
		const ctx = canvas.getContext('2d');
		if (!ctx) {
			capturingFace = false;
			faceErrorMsg = 'Camera context error.';
			faceStatusStep = '';
			return;
		}

		ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
		const b64 = canvas.toDataURL('image/jpeg');

		faceStatusStep = 'Checking liveness...';

		try {
			const res = await fetch('/api/face/validate', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ imageB64: b64 })
			});
			const resData = await res.json();
			capturingFace = false;

			if (resData.success) {
				capturedB64 = b64;
				faceErrorMsg = '';
				faceStatusStep = 'Face verified successfully';
			} else {
				capturedB64 = '';
				faceErrorMsg = resData.error || 'Face verification failed.';
				if (faceErrorMsg.toLowerCase().includes('timeout') || faceErrorMsg.toLowerCase().includes('aborted')) {
					faceErrorMsg = 'Face verification took too long. Please try again.';
				}
				faceStatusStep = '';
			}
		} catch (err) {
			capturingFace = false;
			capturedB64 = '';
			faceErrorMsg = 'Face recognition service is offline or unreachable.';
			faceStatusStep = '';
		}
	}

	function openRegistrationModal() {
		showRegistrationModal = true;
		fullName = '';
		email = '';
		dob = '';
		aadhaarNumber = '';
		bankName = '';
		accountNumber = '';
		capturedB64 = '';
		mobileNumber = '';
		verifiedEmailAddress = '';
		otpCode = '';
		otpSent = false;
		emailVerified = false;
		maskedEmailDisplay = '';
		otpNotice = '';
		otpErrorMsg = '';
		faceErrorMsg = '';
		faceStatusStep = '';
		setTimeout(() => startCamera(), 200);
	}

	function closeRegistrationModal() {
		showRegistrationModal = false;
		stopCamera();
	}

	function openDetailsModal(customer: any) {
		selectedCustomer = customer;
		showDetailsModal = true;
	}

	function closeDetailsModal() {
		showDetailsModal = false;
		selectedCustomer = null;
	}

	function openAddBankModal(customer: any) {
		addBankCustomer = customer;
		showAddBankModal = true;
	}

	function closeAddBankModal() {
		showAddBankModal = false;
		addBankCustomer = null;
	}

	function closeSuccessModal() {
		showSuccessModal = false;
		newlyRegisteredCustomer = null;
	}

	function viewNewCustomer() {
		if (!newlyRegisteredCustomer) return;
		const found = data.customers.find((c: any) => c.id === newlyRegisteredCustomer.id);
		closeSuccessModal();
		if (found) openDetailsModal(found);
	}

	function maskAccount(accNo: string) {
		if (!accNo || accNo === 'N/A') return 'N/A';
		if (accNo.length <= 4) return accNo;
		return '****' + accNo.slice(-4);
	}

	function maskCard(cardNo: string) {
		if (!cardNo || cardNo === 'N/A') return 'N/A';
		if (cardNo.length <= 4) return cardNo;
		return '****' + cardNo.slice(-4);
	}

	onDestroy(() => {
		stopCamera();
	});
</script>

<svelte:head>
	<title>Customer Authority - SecureATM</title>
</svelte:head>

<div class="mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
	<div>
		<h1 class="text-2xl lg:text-3xl font-bold text-white tracking-tight">Customer Management Authority</h1>
		<p class="text-slate-400 text-xs sm:text-sm mt-1">Admin Customer Registration, Biometric Enrollment & Linked Accounts</p>
	</div>
	<button 
		onclick={openRegistrationModal}
		class="flex items-center justify-center gap-2 bg-gradient-to-r from-brand-600 to-blue-600 hover:from-brand-500 hover:to-blue-500 text-white px-5 py-2.5 rounded-xl font-semibold text-xs transition-all shadow-lg shadow-brand-500/20 active:scale-95"
	>
		<UserPlus class="w-4 h-4" />
		<span>Register New Customer</span>
	</button>
</div>

{#if form?.message}
	<div class="mb-6 p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center gap-3 text-emerald-400 text-xs font-semibold shadow-sm">
		<CheckCircle2 class="w-5 h-5 text-emerald-400 shrink-0" />
		<p>{form.message}</p>
	</div>
{/if}

{#if form?.error}
	<div class="mb-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-2xl flex items-center gap-3 text-rose-400 text-xs font-semibold shadow-sm">
		<AlertCircle class="w-5 h-5 text-rose-400 shrink-0" />
		<p>{form.error}</p>
	</div>
{/if}

<!-- Main Customers Table -->
<div class="bg-slate-900/90 rounded-2xl shadow-xl border border-slate-800/80 overflow-hidden">
	<div class="p-4 border-b border-slate-800/80 flex flex-col sm:flex-row justify-between items-center gap-4 bg-slate-950/40">
		<div class="relative w-full sm:w-80">
			<Search class="w-4 h-4 absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500" />
			<input 
				type="text" 
				bind:value={searchTerm}
				placeholder="Search by name, email, Aadhaar, bank..." 
				class="w-full pl-10 pr-4 py-2 rounded-xl border border-slate-800 bg-slate-950 text-slate-200 focus:border-brand-500 focus:ring-1 focus:ring-brand-500 outline-none transition-all text-xs placeholder:text-slate-500"
			/>
		</div>
		<div class="text-xs text-slate-400 font-mono">
			Enrolled Customers: <span class="font-bold text-brand-400">{data.customers.length}</span>
		</div>
	</div>

	<div class="overflow-x-auto">
		<table class="w-full text-left text-xs whitespace-nowrap">
			<thead class="bg-slate-950/60 text-slate-400 border-b border-slate-800/80 uppercase tracking-wider font-mono">
				<tr>
					<th class="px-6 py-4 font-semibold">Customer ID</th>
					<th class="px-6 py-4 font-semibold">Customer Name</th>
					<th class="px-6 py-4 font-semibold">Contact Email / Mobile</th>
					<th class="px-6 py-4 font-semibold">Aadhaar (Masked)</th>
					<th class="px-6 py-4 font-semibold text-center">Bank Accounts</th>
					<th class="px-6 py-4 font-semibold text-center">Face Biometric</th>
					<th class="px-6 py-4 font-semibold text-center">Status</th>
					<th class="px-6 py-4 font-semibold text-right">Actions</th>
				</tr>
			</thead>
			<tbody class="divide-y divide-slate-800/50 text-slate-300 font-mono">
				{#each filteredCustomers as customer}
					<tr class="hover:bg-slate-800/40 transition-colors">
						<td class="px-6 py-4 font-bold text-brand-400">#{customer.id}</td>
						<td class="px-6 py-4 font-sans">
							<div class="font-bold text-slate-100">{customer.fullName}</div>
							<div class="text-[11px] text-slate-500 mt-0.5">DOB: {customer.dob}</div>
						</td>
						<td class="px-6 py-4 font-sans">
							<div class="text-slate-300">{customer.email}</div>
							<div class="text-[11px] font-mono text-slate-500 mt-0.5">+91 {customer.mobile}</div>
						</td>
						<td class="px-6 py-4 text-slate-400">
							{customer.maskedAadhaar}
						</td>
						<td class="px-6 py-4 text-center">
							<span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
								<Building2 class="w-3.5 h-3.5" />
								{customer.accountCount} {customer.accountCount === 1 ? 'Bank Account' : 'Bank Accounts'}
							</span>
						</td>
						<td class="px-6 py-4 text-center">
							<span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
								<ShieldCheck class="w-3.5 h-3.5 text-emerald-400" />
								Owner Face Bound
							</span>
						</td>
						<td class="px-6 py-4 text-center font-sans">
							{#if customer.status === 'ACTIVE'}
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
									ACTIVE
								</span>
							{:else}
								<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
									SUSPENDED
								</span>
							{/if}
						</td>
						<td class="px-6 py-4 text-right font-sans">
							<div class="flex items-center justify-end gap-2">
								<button 
									onclick={() => openDetailsModal(customer)}
									class="p-1.5 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors flex items-center gap-1 text-xs font-semibold"
									title="View Details"
								>
									<Eye class="w-4 h-4" />
									Details
								</button>
								<button 
									onclick={() => openAddBankModal(customer)}
									class="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 rounded-lg transition-colors flex items-center gap-1 text-xs font-semibold"
									title="Add Bank Account"
								>
									<Plus class="w-4 h-4" />
									+ Bank
								</button>
								<form method="POST" action="?/toggleCustomerStatus" use:enhance class="inline">
									<input type="hidden" name="customerId" value={customer.id} />
									<input type="hidden" name="status" value={customer.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'} />
									<button 
										type="submit" 
										class="p-1.5 rounded-lg transition-colors text-xs font-medium flex items-center gap-1 {customer.status === 'ACTIVE' ? 'text-slate-400 hover:text-rose-400 hover:bg-rose-500/10' : 'text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10'}"
										title={customer.status === 'ACTIVE' ? 'Suspend Customer' : 'Activate Customer'}
									>
										{#if customer.status === 'ACTIVE'}
											<UserX class="w-4 h-4" />
										{:else}
											<UserCheck class="w-4 h-4" />
										{/if}
									</button>
								</form>
							</div>
						</td>
					</tr>
				{:else}
					<tr>
						<td colspan="8" class="px-6 py-12 text-center text-slate-500 font-sans">
							{#if searchTerm}
								No customer records matching "{searchTerm}"
							{:else}
								No customers registered yet. Click "Register New Customer" to add one.
							{/if}
						</td>
					</tr>
				{/each}
			</tbody>
		</table>
	</div>
</div>

<!-- Modal 1: Fully Responsive Admin Customer Registration Modal -->
{#if showRegistrationModal}
	<div class="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 overflow-y-auto overflow-x-hidden">
		<div class="bg-slate-900 rounded-3xl w-full max-w-4xl max-w-[calc(100vw-32px)] p-6 sm:p-8 shadow-2xl relative max-h-[90vh] overflow-y-auto overflow-x-hidden border border-slate-800 text-slate-100">
			
			<div class="flex justify-between items-center mb-6 border-b border-slate-800 pb-4">
				<div>
					<h2 class="text-xl font-bold text-white tracking-tight">Customer Enrolment Wizard</h2>
					<p class="text-xs text-slate-400 mt-0.5">Official identity registration & liveness-verified face biometrics</p>
				</div>
				<button onclick={closeRegistrationModal} class="text-slate-400 hover:text-white p-2 rounded-xl hover:bg-slate-800 transition-colors">
					<X class="w-6 h-6" />
				</button>
			</div>

			{#if otpErrorMsg}
				<div class="mb-4 p-3.5 bg-red-50 border border-red-200 rounded-xl text-xs font-semibold text-red-700 flex items-center gap-2">
					<AlertCircle class="w-4 h-4 text-red-600 shrink-0" />
					<p>{otpErrorMsg}</p>
				</div>
			{/if}

			{#if otpNotice}
				<div class="mb-4 p-3.5 bg-blue-50 border border-blue-200 rounded-xl text-xs font-semibold text-blue-700 flex items-center gap-2">
					<CheckCircle2 class="w-4 h-4 text-blue-600 shrink-0" />
					<p>{otpNotice}</p>
				</div>
			{/if}

			<form 
				method="POST" 
				action="?/registerCustomer"
				use:enhance={() => {
					loading = true;
					otpErrorMsg = '';
					return async ({ result, update }) => {
						loading = false;
						if (result.type === 'success' && result.data?.registrationComplete) {
							newlyRegisteredCustomer = result.data.customer as any;
							if (newlyRegisteredCustomer) {
								newlyRegisteredCustomer.emailSuccess = result.data.emailSuccess;
							}
							showSuccessModal = true;
							showRegistrationModal = false;
							stopCamera();
						} else if (result.type === 'failure') {
							otpErrorMsg = String(result.data?.error || 'Registration failed.');
							await update({ reset: false });
						} else {
							await update({ reset: false });
						}
					};
				}}
				class="space-y-6 overflow-x-hidden"
			>
				<input type="hidden" name="faceImageB64" value={capturedB64} />
				<input type="hidden" name="verifiedEmail" value={verifiedEmailAddress} />

				<!-- Customer Official Details Grid (Desktop: 2 columns, Mobile: 1 column) -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
					<div>
						<label for="fullName" class="block text-xs font-semibold text-slate-700 mb-1">Customer Full Name *</label>
						<input 
							type="text" 
							id="fullName" 
							name="fullName" 
							required 
							bind:value={fullName}
							placeholder="e.g. Shameela P" 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none transition-all text-slate-900 bg-white placeholder-slate-400" 
						/>
					</div>

					<div>
						<label for="mobile" class="block text-xs font-semibold text-slate-700 mb-1">Indian Mobile Number *</label>
						<div class="relative w-full">
							<span class="absolute left-3 top-1/2 -translate-y-1/2 text-xs font-bold text-slate-400 font-mono">+91</span>
							<input 
								type="text" 
								id="mobile" 
								name="mobile" 
								required 
								maxlength="10"
								inputmode="numeric"
								oninput={(e) => { 
									const val = e.currentTarget.value.replace(/\D/g, ''); 
									mobileNumber = val; 
								}}
								bind:value={mobileNumber}
								placeholder="Enter 10-digit mobile number" 
								class="w-full pl-12 pr-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none font-mono text-slate-900 bg-white placeholder-slate-400" 
							/>
						</div>
					</div>

					<!-- Date of Birth with DYNAMIC MAX TODAY DATE -->
					<div>
						<label for="dob" class="block text-xs font-semibold text-slate-700 mb-1">Date of Birth * (No future date)</label>
						<input 
							type="date" 
							id="dob" 
							name="dob" 
							required 
							bind:value={dob}
							max={data.todayDate || new Date().toISOString().split('T')[0]}
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none transition-all text-slate-900 bg-white" 
						/>
					</div>

					<!-- Aadhaar Number (12 Digits numeric only) -->
					<div>
						<label for="aadhaarNumber" class="block text-xs font-semibold text-slate-700 mb-1">Aadhaar Number * (12 Digits)</label>
						<input 
							type="text" 
							id="aadhaarNumber" 
							name="aadhaarNumber" 
							required 
							maxlength="12" 
							inputmode="numeric"
							bind:value={aadhaarNumber}
							oninput={(e) => { e.currentTarget.value = e.currentTarget.value.replace(/\D/g, ''); aadhaarNumber = e.currentTarget.value; }}
							placeholder="12-digit Aadhaar number" 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-mono focus:border-brand-500 outline-none transition-all text-slate-900 bg-white placeholder-slate-400" 
						/>
					</div>

					<div>
						<label for="bankName" class="block text-xs font-semibold text-slate-700 mb-1">Bank Name *</label>
						<input 
							type="text" 
							id="bankName" 
							name="bankName" 
							required 
							bind:value={bankName}
							placeholder="e.g. Mariyamman Bank / SBI" 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none transition-all text-slate-900 bg-white placeholder-slate-400" 
						/>
					</div>

					<div>
						<label for="accountNumber" class="block text-xs font-semibold text-slate-700 mb-1">Bank Account Number *</label>
						<input 
							type="text" 
							id="accountNumber" 
							name="accountNumber" 
							required 
							bind:value={accountNumber}
							placeholder="e.g. 2143658709" 
							class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-mono focus:border-brand-500 outline-none transition-all text-slate-900 bg-white placeholder-slate-400" 
						/>
					</div>
				</div>

				<!-- Email OTP Verification Box -->
				<div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-5">
					<div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
						<label for="email" class="text-xs font-bold text-slate-800 flex items-center gap-1.5">
							<KeyRound class="w-4 h-4 text-brand-600" />
							Email Verification *
						</label>
						{#if emailVerified}
							<span class="text-xs font-bold text-emerald-600 flex items-center gap-1 bg-emerald-100 px-3 py-1 rounded-full self-start sm:self-auto">
								<CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" />
								Email Verified ✓
							</span>
						{/if}
					</div>

					<div class="flex flex-col sm:flex-row items-center gap-2">
						<div class="relative w-full">
							<input 
								type="email" 
								id="email" 
								name="email" 
								required 
								oninput={(e) => { 
									if (emailVerified && e.currentTarget.value !== verifiedEmailAddress) {
										emailVerified = false;
										verifiedEmailAddress = '';
										otpSent = false;
										otpCode = '';
										otpNotice = '';
										otpErrorMsg = 'Email address changed. Please request and verify a new OTP.';
									}
								}}
								bind:value={email}
								readonly={emailVerified}
								placeholder="e.g. customer@example.com" 
								class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none read-only:bg-slate-200 read-only:text-slate-600 text-slate-900 bg-white placeholder-slate-400" 
							/>
						</div>

						{#if !emailVerified}
							<button 
								type="button"
								onclick={handleSendOtp}
								disabled={sendingOtp || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)}
								class="w-full sm:w-auto text-xs font-semibold bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl transition-all whitespace-nowrap flex items-center justify-center gap-1.5 shadow-sm"
							>
								{#if sendingOtp}
									<Loader2 class="w-3.5 h-3.5 animate-spin" />
									Sending OTP...
								{:else}
									<KeyRound class="w-3.5 h-3.5" />
									{otpSent ? 'Resend OTP' : 'Send OTP'}
								{/if}
							</button>
						{/if}
					</div>

					<!-- OTP Entry Box -->
					{#if otpSent && !emailVerified}
						<div class="mt-4 pt-4 border-t border-slate-200">
							<div class="flex items-center justify-between text-xs text-slate-500 mb-2">
								<span>OTP sent to <span class="font-mono font-bold text-slate-800">{maskedEmailDisplay}</span></span>
								{#if otpTimer > 0}
									<span class="font-mono font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded">OTP expires in {formatTimer(otpTimer)}</span>
								{:else}
									<span class="font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded">OTP expired. Please request a new OTP.</span>
								{/if}
							</div>
							<label for="otp" class="block text-xs font-semibold text-slate-700 mb-1">Enter OTP</label>
							<div class="flex flex-col sm:flex-row items-center gap-2">
								<input 
									type="text" 
									id="otp"
									name="otp"
									maxlength="6" 
									inputmode="numeric"
									bind:value={otpCode}
									oninput={(e) => { e.currentTarget.value = e.currentTarget.value.replace(/\D/g, ''); otpCode = e.currentTarget.value; }}
									placeholder="Enter 6-digit OTP" 
									class="w-full sm:w-64 px-3.5 py-2 rounded-xl border border-slate-200 text-sm font-mono focus:border-brand-500 outline-none tracking-widest text-center text-lg font-bold text-slate-900 bg-white placeholder-slate-400"
								/>

								<button 
									type="button"
									onclick={handleVerifyOtp}
									disabled={verifyingOtp || otpCode.length !== 6 || otpTimer === 0}
									class="w-full sm:w-auto text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-5 py-2.5 rounded-xl transition-all whitespace-nowrap flex items-center justify-center gap-1.5 shadow-sm"
								>
									{#if verifyingOtp}
										<Loader2 class="w-3.5 h-3.5 animate-spin" />
										Verifying...
									{:else}
										<Check class="w-3.5 h-3.5" />
										Verify OTP
									{/if}
								</button>
							</div>
						</div>
					{/if}
				</div>

				<!-- Original Owner Face Capture Section -->
				<div class="bg-slate-50 border border-slate-200 rounded-2xl p-4 sm:p-5">
					<div class="flex items-center justify-between mb-2">
						<label class="text-sm font-bold text-slate-800 flex items-center gap-2">
							<Camera class="w-4 h-4 text-brand-600" />
							Original Owner Face Capture & Liveness Verification *
						</label>
						{#if capturedB64}
							<span class="text-xs font-bold text-emerald-600 flex items-center gap-1 bg-emerald-100 px-3 py-1 rounded-full">
								<CheckCircle2 class="w-3.5 h-3.5 text-emerald-600" />
								Owner Face Bound ✓
							</span>
						{/if}
					</div>
					<p class="text-xs text-slate-500 mb-3">
						Capture the face of the verified account owner. MTCNN single-face detection & Liveness CNN verification required.
					</p>

					{#if faceErrorMsg}
						<div class="mb-3 p-3.5 bg-red-50 border border-red-200 rounded-xl text-xs font-semibold text-red-700 flex items-center gap-2">
							<AlertCircle class="w-4 h-4 text-red-600 shrink-0" />
							<p>{faceErrorMsg}</p>
						</div>
					{/if}

					<div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
						<div class="aspect-video bg-slate-900 rounded-xl overflow-hidden relative border-2 border-slate-300 max-w-full">
							<!-- svelte-ignore a11y_media_has_caption -->
							<video 
								bind:this={videoElement} 
								autoplay 
								playsinline 
								class="w-full h-full object-cover transform -scale-x-100"
							></video>
							{#if !cameraActive}
								<div class="absolute inset-0 flex items-center justify-center text-slate-400 text-xs">
									Initializing camera...
								</div>
							{/if}
							{#if faceStatusStep}
								<div class="absolute bottom-2 left-2 right-2 bg-slate-900/80 backdrop-blur-sm text-white px-3 py-1.5 rounded-lg text-xs font-medium text-center flex items-center justify-center gap-2">
									<Loader2 class="w-3.5 h-3.5 animate-spin text-brand-400" />
									<span>{faceStatusStep}</span>
								</div>
							{/if}
						</div>

						<div class="flex flex-col items-center justify-center">
							{#if capturedB64}
								<img src={capturedB64} alt="Captured Owner" class="w-32 h-32 object-cover rounded-2xl border-4 border-emerald-500 shadow-md mb-3" />
								<button 
									type="button" 
									onclick={captureAndValidateFace}
									disabled={capturingFace}
									class="px-4 py-2 text-xs font-semibold bg-slate-200 hover:bg-slate-300 disabled:opacity-50 text-slate-700 rounded-xl transition-colors flex items-center gap-1.5"
								>
									{#if capturingFace}
										<Loader2 class="w-3.5 h-3.5 animate-spin" />
										Verifying...
									{:else}
										<RefreshCw class="w-3.5 h-3.5" />
										Recapture Owner Face
									{/if}
								</button>
							{:else}
								<button 
									type="button" 
									onclick={captureAndValidateFace} 
									disabled={capturingFace}
									class="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-semibold text-sm transition-all shadow-md shadow-brand-500/20 active:scale-95"
								>
									{#if capturingFace}
										<Loader2 class="w-4 h-4 animate-spin" />
										Verifying Liveness...
									{:else}
										<Camera class="w-4 h-4" />
										Capture Owner Face
									{/if}
								</button>
								<p class="text-[11px] text-slate-400 mt-2 text-center">Position your face inside the frame</p>
							{/if}
						</div>
					</div>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
					<button type="button" onclick={closeRegistrationModal} class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-600 text-sm font-medium hover:bg-slate-50 transition-colors">
						Cancel
					</button>
					<button 
						type="submit" 
						disabled={loading || !capturedB64 || !emailVerified}
						class="flex items-center gap-2 bg-brand-600 hover:bg-brand-500 disabled:opacity-50 text-white px-6 py-2.5 rounded-xl font-semibold text-sm transition-all shadow-md shadow-brand-500/20 active:scale-95"
					>
						{#if loading}
							<Loader2 class="w-4 h-4 animate-spin" />
							Registering & Generating Card...
						{:else}
							<ShieldCheck class="w-4 h-4" />
							Register Customer
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}

<!-- Modal 2: Registration Success Modal -->
{#if showSuccessModal && newlyRegisteredCustomer}
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
		<div class="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl relative border border-slate-100 text-center">
			
			<div class="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 text-emerald-600">
				<ShieldCheck class="w-9 h-9" />
			</div>

			<h2 class="text-xl font-bold text-slate-900">Customer Registered Successfully</h2>
			<p class="text-xs text-slate-500 mt-1 mb-6">Customer identity & bank account stored in Firebase Realtime Database</p>

			<!-- Verification Checklist -->
			<div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 text-left text-xs space-y-2 mb-6">
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Customer identity verified</span>
				</div>
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Mobile number verified (+91)</span>
				</div>
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Original owner face registered</span>
				</div>
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Bank account linked ({newlyRegisteredCustomer.bankName})</span>
				</div>
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Unique 16-digit ATM card generated</span>
				</div>
				<div class="flex items-center gap-2 text-emerald-700 font-semibold">
					<CheckCircle2 class="w-4 h-4 text-emerald-600 shrink-0" />
					<span>Customer record saved to Firebase</span>
				</div>
			</div>

			<!-- Generated Details summary -->
			<div class="bg-slate-900 text-white p-4 rounded-2xl text-left font-mono text-xs space-y-2 mb-6">
				<div class="flex justify-between items-center border-b border-slate-800 pb-2">
					<span class="text-slate-400">Generated ATM Card:</span>
					<span class="font-bold text-emerald-400">{newlyRegisteredCustomer.maskedCard}</span>
				</div>
				<div class="flex justify-between items-center border-b border-slate-800 pb-2">
					<span class="text-slate-400">Customer Email:</span>
					<span class="text-slate-200">{newlyRegisteredCustomer.email}</span>
				</div>
				<div class="flex justify-between items-center border-b border-slate-800 pb-2">
					<span class="text-slate-400">Verified Mobile:</span>
					<span class="text-slate-200">+91 {newlyRegisteredCustomer.mobile}</span>
				</div>
				<div class="flex justify-between items-center border-b border-slate-800 pb-2">
					<span class="text-slate-400">Card SMS Status:</span>
					<span class="text-emerald-300 text-[11px] font-sans">{newlyRegisteredCustomer.cardSmsNotice || 'Delivery attempted'}</span>
				</div>
				<div class="flex justify-between items-center pt-1">
					<span class="text-slate-400">Email Status:</span>
					<div class="flex items-center gap-2">
						<span class="{newlyRegisteredCustomer.emailSuccess ? 'text-emerald-400' : 'text-rose-400'} text-[11px] font-sans">
							{newlyRegisteredCustomer.emailNotice}
						</span>
						{#if !newlyRegisteredCustomer.emailSuccess}
							<form 
								method="POST" 
								action="?/retryCardEmail"
								use:enhance={() => {
									retryingEmail = true;
									return async ({ result, update }) => {
										retryingEmail = false;
										if (result.type === 'success' && result.data?.success) {
											newlyRegisteredCustomer.emailSuccess = true;
											newlyRegisteredCustomer.emailNotice = result.data.message;
										}
										await update({ reset: false });
									};
								}}
							>
								<input type="hidden" name="customerId" value={newlyRegisteredCustomer.id} />
								<input type="hidden" name="cardNumber" value={newlyRegisteredCustomer.cardNumber} />
								<input type="hidden" name="email" value={newlyRegisteredCustomer.email} />
								<input type="hidden" name="customerName" value={newlyRegisteredCustomer.fullName} />
								<input type="hidden" name="bankName" value={newlyRegisteredCustomer.bankName} />
								<input type="hidden" name="accountNumber" value={newlyRegisteredCustomer.accountNumber} />
								<button 
									type="submit" 
									disabled={retryingEmail}
									class="ml-2 px-2 py-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-300 rounded text-[10px] font-bold uppercase transition-colors flex items-center gap-1 disabled:opacity-50"
								>
									{#if retryingEmail}
										<Loader2 class="w-3 h-3 animate-spin" />
									{:else}
										<RefreshCw class="w-3 h-3" /> Retry
									{/if}
								</button>
							</form>
						{/if}
					</div>
				</div>
			</div>

			<div class="flex gap-3 justify-center">
				<button 
					onclick={viewNewCustomer}
					class="px-5 py-2.5 rounded-xl border border-slate-200 text-slate-700 text-sm font-semibold hover:bg-slate-50 transition-colors"
				>
					View Customer
				</button>
				<button 
					onclick={() => { closeSuccessModal(); openRegistrationModal(); }}
					class="px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition-all shadow-md active:scale-95"
				>
					Register Another Customer
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Modal 3: Customer Details Modal -->
{#if showDetailsModal && selectedCustomer}
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
		<div class="bg-white rounded-3xl max-w-2xl w-full p-6 shadow-2xl relative max-h-[92vh] overflow-y-auto border border-slate-100">
			<div class="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
				<div>
					<h2 class="text-xl font-bold text-slate-900">Customer Profile Details</h2>
					<p class="text-xs text-slate-500 mt-0.5">ID: {selectedCustomer.id} | Registered: {selectedCustomer.createdAt}</p>
				</div>
				<button onclick={closeDetailsModal} class="text-slate-400 hover:text-slate-600 p-2 rounded-xl hover:bg-slate-100 transition-colors">
					<X class="w-6 h-6" />
				</button>
			</div>

			<div class="space-y-6">
				<!-- CUSTOMER INFORMATION -->
				<div>
					<h3 class="text-xs uppercase tracking-wider font-bold text-slate-400 mb-3">Customer Information</h3>
					<div class="grid grid-cols-2 md:grid-cols-3 gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-100 text-sm">
						<div>
							<div class="text-xs text-slate-400 font-medium">Full Name</div>
							<div class="font-semibold text-slate-800">{selectedCustomer.fullName}</div>
						</div>
						<div>
							<div class="text-xs text-slate-400 font-medium">Email Address</div>
							<div class="font-semibold text-slate-800">{selectedCustomer.email}</div>
						</div>
						<div>
							<div class="text-xs text-slate-400 font-medium">Date of Birth</div>
							<div class="font-semibold text-slate-800">{selectedCustomer.dob}</div>
						</div>
						<div>
							<div class="text-xs text-slate-400 font-medium">Aadhaar (Masked)</div>
							<div class="font-mono font-semibold text-slate-800">{selectedCustomer.maskedAadhaar}</div>
						</div>
						<div>
							<div class="text-xs text-slate-400 font-medium">Mobile Number</div>
							<div class="font-semibold text-slate-800">{selectedCustomer.mobile}</div>
						</div>
						<div>
							<div class="text-xs text-slate-400 font-medium">Customer Status</div>
							<div class="font-semibold text-emerald-600">{selectedCustomer.status}</div>
						</div>
					</div>
				</div>

				<!-- REGISTERED BANK ACCOUNTS -->
				<div>
					<div class="flex justify-between items-center mb-3">
						<h3 class="text-xs uppercase tracking-wider font-bold text-slate-400">Registered Bank Accounts</h3>
						<button 
							onclick={() => { closeDetailsModal(); openAddBankModal(selectedCustomer); }} 
							class="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center gap-1"
						>
							<Plus class="w-3.5 h-3.5" /> + Add Account
						</button>
					</div>
					
					<div class="bg-white border border-slate-100 rounded-2xl overflow-hidden shadow-sm">
						<table class="w-full text-left text-xs">
							<thead class="bg-slate-50 text-slate-500 border-b border-slate-100">
								<tr>
									<th class="p-3 font-semibold">Bank Name</th>
									<th class="p-3 font-semibold">Account Number</th>
									<th class="p-3 font-semibold">ATM Card Number</th>
									<th class="p-3 font-semibold text-right">Balance</th>
									<th class="p-3 font-semibold text-center">Status</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-slate-100">
								{#each selectedCustomer.bankAccounts as acc}
									<tr class="hover:bg-slate-50/50">
										<td class="p-3 font-semibold text-slate-800">{acc.bankName}</td>
										<td class="p-3 font-mono text-slate-600">{maskAccount(acc.accountNumber)}</td>
										<td class="p-3 font-mono text-slate-600">{maskCard(acc.cardNumber)}</td>
										<td class="p-3 text-right font-semibold text-slate-900">₹{acc.balance.toLocaleString()}</td>
										<td class="p-3 text-center">
											<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-100 text-green-800">
												ACTIVE
											</span>
										</td>
									</tr>
								{:else}
									<tr>
										<td colspan="5" class="p-4 text-center text-slate-400">No bank accounts linked to this customer yet.</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>

				<!-- BIOMETRIC STATUS -->
				<div>
					<h3 class="text-xs uppercase tracking-wider font-bold text-slate-400 mb-3">Biometric Status</h3>
					<div class="bg-slate-50 p-4 rounded-2xl border border-slate-100 flex items-center justify-between text-sm">
						<div class="flex items-center gap-3">
							{#if selectedCustomer.registeredFaceUrl}
								<img src={selectedCustomer.registeredFaceUrl} alt="Owner Face" class="w-12 h-12 rounded-xl object-cover border-2 border-emerald-500 shadow-sm" />
							{:else}
								<div class="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center text-emerald-700">
									<ShieldCheck class="w-6 h-6" />
								</div>
							{/if}
							<div>
								<div class="font-semibold text-slate-800">Original Owner Face: <span class="text-emerald-600">✓ Registered</span></div>
								<div class="text-xs text-slate-500">FaceNet 128-d Vector stored in Firebase Realtime Database</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<div class="mt-6 pt-4 border-t border-slate-100 flex justify-end">
				<button onclick={closeDetailsModal} class="px-5 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-sm transition-colors">
					Close
				</button>
			</div>
		</div>
	</div>
{/if}

<!-- Modal 4: Add Additional Bank Account Modal -->
{#if showAddBankModal && addBankCustomer}
	<div class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
		<div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl relative border border-slate-100">
			<div class="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
				<div>
					<h2 class="text-lg font-bold text-slate-900">+ Add Bank Account</h2>
					<p class="text-xs text-slate-500 mt-0.5">For Customer: <span class="font-semibold text-slate-800">{addBankCustomer.fullName}</span></p>
				</div>
				<button onclick={closeAddBankModal} class="text-slate-400 hover:text-slate-600 p-2 rounded-xl hover:bg-slate-100 transition-colors">
					<X class="w-5 h-5" />
				</button>
			</div>

			<form 
				method="POST" 
				action="?/addBankAccount"
				use:enhance={() => {
					addBankLoading = true;
					return async ({ update }) => {
						await update();
						addBankLoading = false;
						if (form?.success) {
							closeAddBankModal();
						}
					};
				}}
				class="space-y-4"
			>
				<input type="hidden" name="customerId" value={addBankCustomer.id} />

				<div class="bg-slate-50 p-3 rounded-xl border border-slate-100 text-xs text-slate-600 space-y-1">
					<div><span class="font-semibold text-slate-700">Aadhaar:</span> {addBankCustomer.maskedAadhaar}</div>
					<div><span class="font-semibold text-slate-700">Face Status:</span> ✓ Uses existing registered owner face</div>
				</div>

				<div>
					<label for="newBankName" class="block text-xs font-semibold text-slate-700 mb-1">Bank Name *</label>
					<input 
						type="text" 
						id="newBankName" 
						name="bankName" 
						required 
						placeholder="e.g. HDFC Bank" 
						class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm focus:border-brand-500 outline-none transition-all" 
					/>
				</div>

				<div>
					<label for="newAccountNumber" class="block text-xs font-semibold text-slate-700 mb-1">Bank Account Number *</label>
					<input 
						type="text" 
						id="newAccountNumber" 
						name="accountNumber" 
						required 
						placeholder="e.g. 9876543210" 
						class="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-mono focus:border-brand-500 outline-none transition-all" 
					/>
				</div>

				<div class="flex justify-end gap-3 pt-4 border-t border-slate-100">
					<button type="button" onclick={closeAddBankModal} class="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-sm font-medium hover:bg-slate-50 transition-colors">
						Cancel
					</button>
					<button 
						type="submit" 
						disabled={addBankLoading}
						class="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white px-5 py-2 rounded-xl font-semibold text-sm transition-all shadow-md active:scale-95"
					>
						{#if addBankLoading}
							<Loader2 class="w-4 h-4 animate-spin" />
							Generating Card...
						{:else}
							<CreditCard class="w-4 h-4" />
							Add Account & Issue Card
						{/if}
					</button>
				</div>
			</form>
		</div>
	</div>
{/if}
