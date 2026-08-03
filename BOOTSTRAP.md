# Bootstrap

This repo deploys to Cloudflare as a Worker with static assets, built with SvelteKit's `adapter-cloudflare` — same setup as [mzywang/site](https://github.com/mzywang/site), whose `BOOTSTRAP.md` this process was copied from. Setup splits into local code changes and Cloudflare dashboard configuration, which has no `wrangler` CLI equivalent.

Prerequisites: Node >= 22 (Wrangler 4 requires it), `gh` CLI authenticated, a Cloudflare account, a GitHub account.

## Local Setup

### Scaffold the Project

```bash
npx sv create groups --template minimal --types ts \
  --add prettier eslint sveltekit-adapter="adapter:cloudflare+cfTarget:workers" \
  --install npm
npm run gen
```

Use `cfTarget:workers`, **not** `cfTarget:pages` — connecting a repo through Workers & Pages now provisions a Worker with static assets, not classic Pages.

### Gitignore the Generated Types

- `.gitignore` — add `/worker-configuration.d.ts`
- `.prettierignore` — add `worker-configuration.d.ts`
- `package.json`:
  ```diff
  - "build": "wrangler types --check && vite build",
  + "build": "vite build",
  - "prepare": "svelte-kit sync || echo ''",
  + "prepare": "svelte-kit sync || echo ''; wrangler types",
  - "check": "wrangler types --check && svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
  + "check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json",
  ```

### Pin the Node Version

```bash
echo 24 > .nvmrc
```

### Disable checkJs for the Compiled Worker Bundle

```diff
- "checkJs": true,
+ "checkJs": false,
```

Sanity-check locally before touching Cloudflare:

```bash
npm run gen && npm run build && npx wrangler deploy --dry-run
```

Should print `env.ASSETS  Assets` under bindings, no errors.

### Add a CI Workflow

`.github/workflows/ci.yml` — same `lint-check-build` job as `site`, so it can be wired up as a required status check once branch protection is added.

### Create the GitHub Repo and Branch Protection

```bash
gh repo create <you>/<repo> --public --source=. --remote=origin
git push -u origin main

gh api repos/<you>/<repo>/rulesets -X POST --input - <<'EOF'
{
  "name": "protect-main",
  "target": "branch",
  "enforcement": "active",
  "conditions": { "ref_name": { "include": ["~DEFAULT_BRANCH"], "exclude": [] } },
  "rules": [
    {
      "type": "pull_request",
      "parameters": {
        "required_approving_review_count": 0,
        "dismiss_stale_reviews_on_push": false,
        "required_reviewers": [],
        "require_code_owner_review": false,
        "require_last_push_approval": false,
        "required_review_thread_resolution": false,
        "allowed_merge_methods": ["squash"]
      }
    },
    {
      "type": "required_status_checks",
      "parameters": {
        "strict_required_status_checks_policy": true,
        "do_not_enforce_on_create": false,
        "required_status_checks": [{ "context": "lint-check-build" }]
      }
    }
  ]
}
EOF
```

This is `site`'s actual live ruleset (fetched via `gh api repos/mzywang/site/rulesets/<id>`), not just the simplified snippet in its `BOOTSTRAP.md` — it also requires the `lint-check-build` CI job to pass before merging, which the doc snippet omits.

## Cloudflare Dashboard

Same as `site` — none of this is exposed via `wrangler` or the Cloudflare API, confirmed the same way `site`'s bootstrap did.

### Connect the Repository

1. **Connect to Git** — Workers & Pages -> Create -> Connect to Git -> pick your repo.
2. **Build command** — `npm run build`
3. **Deploy command** (Production field) — `npx wrangler deploy`
4. **Environment variables** — `NODE_VERSION=24`.
5. **Branch control** — Settings -> Builds -> Branch control. Leave "Builds for non-production branches" unchecked so only `main` ever builds or deploys.
6. **Deploy token** — profile/api-tokens -> "Edit Cloudflare Workers" template, scoped to **Account Resources** (not just Zone Resources). Paste as `CLOUDFLARE_API_TOKEN` in Settings -> Environment variables, encrypted.
7. **First build** — push to `main` to trigger it.

### Add a Custom Domain

```jsonc
"routes": [{ "pattern": "groups.mzywang.dev", "custom_domain": true }],
"workers_dev": false
```

Redeploy (`wrangler deploy`, or push to `main`) to provision DNS + SSL.
