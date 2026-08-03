<svelte:head>
	<title>groups.mzywang.dev</title>
</svelte:head>

<main>
	<h1>groups</h1>
	<hr />
	<dl>
		<div>
			<dt>users</dt>
			<dd>0</dd>
		</div>
		<div>
			<dt>groups</dt>
			<dd>0</dd>
		</div>
	</dl>
</main>

<style>
	main {
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		min-height: 100svh;
		width: 100%;
		max-width: 24rem;
		padding: 2rem 1.25rem;
	}

	h1 {
		font-size: 1.1rem;
		font-weight: 400;
		margin: 0;
	}

	hr {
		width: 100%;
		height: 0;
		border: none;
		border-top: 1px dashed var(--ink-dim);
		margin: 0.9rem 0 1.6rem;
	}

	dl {
		display: flex;
		flex-direction: column;
		gap: 0.35rem;
		margin: 0;
		width: 100%;
	}

	dl div {
		display: flex;
		justify-content: space-between;
	}

	dt {
		color: var(--ink-dim);
	}

	dd {
		margin: 0;
	}
</style>
