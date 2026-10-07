<script lang="ts">
	import { page } from '$app/state';
	import { 
		LayoutDashboard, Users, CreditCard, ArrowRightLeft, ShieldAlert, 
		AlertTriangle, Fingerprint, FileText, Settings, LogOut, Menu, X, 
		ShieldCheck, Bell, UserCheck
	} from '@lucide/svelte';

	let { children } = $props();
	let mobileMenuOpen = $state(false);

	function handleLogout() {
		// Clear admin session cookies
		document.cookie = 'admin_auth=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
		window.location.href = '/admin/login';
	}
	
	const navItems = [
		{ name: 'Dashboard', icon: LayoutDashboard, href: '/admin' },
		{ name: 'Customers', icon: Users, href: '/admin/customers' },
		{ name: 'Accounts', icon: CreditCard, href: '/admin/accounts' },
		{ name: 'Transactions', icon: ArrowRightLeft, href: '/admin/transactions' },
		{ name: 'Security Alerts', icon: ShieldAlert, href: '/admin/security-alerts' },
		{ name: 'Face Verification', icon: Fingerprint, href: '/admin/face-verification' },
		{ name: 'Complaints', icon: AlertTriangle, href: '/admin/complaints' },
		{ name: 'Reports', icon: FileText, href: '/admin/reports' },
		{ name: 'Settings', icon: Settings, href: '/admin/settings' },
	];

	let isLoginPage = $derived(page.url.pathname === '/admin/login');

	function toggleMobileMenu() {
		mobileMenuOpen = !mobileMenuOpen;
	}
</script>

{#if isLoginPage}
	{@render children()}
{:else}
	<div class="flex h-screen bg-slate-950 text-slate-100 overflow-hidden font-sans">
		
		<!-- Mobile Backdrop overlay -->
		{#if mobileMenuOpen}
			<div 
				role="button"
				tabindex="0"
				onclick={toggleMobileMenu}
				onkeydown={(e) => e.key === 'Enter' && toggleMobileMenu()}
				class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-40 lg:hidden"
			></div>
		{/if}

		<!-- Persistent Desktop Sidebar / Mobile Drawer -->
		<aside class={`fixed lg:static inset-y-0 left-0 z-50 w-72 bg-slate-900 border-r border-slate-800/80 flex flex-col transition-transform duration-300 ${
			mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
		}`}>
			<!-- Brand Header -->
			<div class="p-6 flex items-center justify-between border-b border-slate-800/80">
				<a href="/admin" class="flex items-center gap-3 text-white group">
					<div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-brand-600 to-blue-500 flex items-center justify-center text-white shadow-lg shadow-brand-500/20 group-hover:scale-105 transition-transform">
						<ShieldCheck class="w-6 h-6" />
					</div>
					<div>
						<span class="text-lg font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent block">SecureATM</span>
						<span class="text-[10px] uppercase font-mono tracking-widest text-slate-500 block -mt-0.5">Biometric Command</span>
					</div>
				</a>
				<button 
					onclick={toggleMobileMenu} 
					class="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden transition-colors"
					aria-label="Close Mobile Navigation"
				>
					<X class="w-5 h-5" />
				</button>
			</div>
			
			<!-- Navigation Links -->
			<nav class="flex-1 overflow-y-auto py-6 px-4 space-y-1">
				<div class="px-3 mb-2 text-[10px] uppercase tracking-wider font-bold text-slate-500">Core Management</div>
				{#each navItems as item}
					{@const isActive = item.href === '/admin' ? page.url.pathname === '/admin' : page.url.pathname.startsWith(item.href)}
					<a 
						href={item.href}
						onclick={() => (mobileMenuOpen = false)}
						class={`flex items-center justify-between px-4 py-3 rounded-2xl transition-all ${
							isActive 
								? 'bg-gradient-to-r from-brand-600 to-blue-600 text-white font-semibold shadow-lg shadow-brand-600/25' 
								: 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
						}`}
					>
						<div class="flex items-center gap-3">
							<item.icon class={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-400'}`} />
							<span class="text-sm">{item.name}</span>
						</div>
						{#if isActive}
							<div class="w-1.5 h-1.5 rounded-full bg-white animate-pulse"></div>
						{/if}
					</a>
				{/each}
			</nav>
			
			<!-- Bottom Admin User Profile & Logout -->
			<div class="p-4 border-t border-slate-800/80 bg-slate-900/50">
				<div class="flex items-center justify-between bg-slate-950/60 border border-slate-800/80 p-3 rounded-2xl mb-3">
					<div class="flex items-center gap-3">
						<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-sm shadow-md">
							A
						</div>
						<div class="overflow-hidden">
							<div class="text-xs font-bold text-slate-200 truncate">System Admin</div>
							<div class="text-[10px] text-slate-500 truncate">sham@gmail.com</div>
						</div>
					</div>
					<span class="px-2 py-0.5 rounded-full text-[9px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">ROOT</span>
				</div>

				<button 
					onclick={handleLogout}
					class="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl transition-all text-xs font-semibold text-red-400 bg-red-500/10 hover:bg-red-500/20 hover:text-red-300 border border-red-500/20"
				>
					<LogOut class="w-4 h-4" />
					<span>Sign Out Admin</span>
				</button>
			</div>
		</aside>

		<!-- Main Workspace Area -->
		<div class="flex-1 flex flex-col h-screen overflow-hidden min-w-0 bg-slate-950">
			<!-- Topbar Header -->
			<header class="h-16 bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 flex items-center px-4 lg:px-8 justify-between shrink-0 z-30">
				<div class="flex items-center gap-3">
					<button 
						onclick={toggleMobileMenu} 
						class="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 lg:hidden transition-colors"
						aria-label="Open Navigation Menu"
					>
						<Menu class="w-6 h-6" />
					</button>
					<div>
						<h1 class="font-bold text-slate-100 text-sm lg:text-base tracking-tight">Security Command Center</h1>
						<p class="text-[10px] text-slate-400 hidden sm:block">Facial Recognition & Liveness Realtime Monitoring System</p>
					</div>
				</div>

				<div class="flex items-center gap-3">
					<div class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50 text-xs text-slate-300 font-mono">
						<span class="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
						<span>ML & RTDB Active</span>
					</div>

					<a 
						href="/admin/security-alerts" 
						class="p-2.5 rounded-xl bg-slate-800/60 hover:bg-slate-800 text-slate-400 hover:text-white border border-slate-700/50 transition-colors relative"
						title="Security Incidents"
					>
						<Bell class="w-4 h-4" />
						<span class="absolute top-2 right-2 w-2 h-2 bg-rose-500 rounded-full"></span>
					</a>
				</div>
			</header>
			
			<!-- Page Content Container -->
			<main class="flex-1 overflow-y-auto p-4 lg:p-8 bg-slate-950">
				<div class="max-w-7xl mx-auto">
					{@render children()}
				</div>
			</main>
		</div>
	</div>
{/if}
