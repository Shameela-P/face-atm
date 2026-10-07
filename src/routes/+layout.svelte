<script lang="ts">
	import '../app.css';
	let { children } = $props();
</script>

<div class="min-h-screen flex flex-col font-sans">
	{@render children()}
</div>
