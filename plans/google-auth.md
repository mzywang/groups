# Plan: Google sign-in for groups.mzywang.dev

## Goal

Let a real human authenticate to the app via "Sign in with Google," and turn that into a `subject` record (per `exploration.md`'s data model) that later work (the `/preferences` endpoint, group membership) can build on. This plan is scoped to auth only — it does not implement groups, preferences, or ticks.

## Architecture

- **No Firebase / Supabase.** We're already fully on Cloudflare (Workers + D1), and verifying a Google ID token is a small, well-defined operation Workers can do natively (fetch Google's public JWKS, verify the JWT signature, check `aud`/`iss`/`exp`). Adding a second auth vendor just for this would be more moving parts, not less.
- **Client-side**: Google Identity Services (`accounts.google.com/gsi/client`) renders the official "Sign in with Google" button and hands back a signed ID token (JWT) — no popup/redirect flow to manage ourselves.
- **Server-side**: a single `POST /auth/google` endpoint verifies that token, finds-or-creates a `subjects` row keyed by Google's `sub` claim (not email — email can change), and issues a **signed, httpOnly, secure session cookie** (HMAC over `subject_id` + expiry, no session table, no DB read on every request).
- **`hooks.server.ts`** verifies that cookie on each request and populates `event.locals.subject`, so every route (including the future `/preferences` endpoint) gets the caller's identity from the session — never from a client-supplied field, per the API design discussed earlier.
- **Sign-out**: `POST /auth/logout` just clears the cookie — no server-side state to invalidate.

## Current state

- `groups.mzywang.dev` is live, git-connected to Cloudflare Workers Builds, custom domain working.
- A D1 database named `groups` already exists (`wrangler d1 create groups` was run), database id `8da7b16a-dd1f-47a2-b693-b974c1613e75`. Not yet bound in `wrangler.jsonc` or committed.
- A draft migration for a `subjects` table exists locally (stashed, uncommitted) — schema: `id`, `google_sub` (unique), `email`, `display_name`, `created_at`.

## Phases

Each phase lists whether it's a **PR** (code, goes through the normal branch-protected review flow) or a **manual step** (dashboard/CLI action with no code artifact, done by you — or by me where it doesn't touch live/production state).

### Phase 0 — This plan

**PR.** This document.

### Phase 1 — Google OAuth Client ID

**Manual, UI-only — no CLI/API equivalent (same category of limitation as the Cloudflare git-connection step).**

1. [console.cloud.google.com](https://console.cloud.google.com), on the `mzywang@gmail.com` account (not a work account — `gcloud` locally currently has `michael.wang@valon.com` active, don't use that project).
2. Create/select a project (e.g. "groups").
3. **APIs & Services → OAuth consent screen**: External, app name "groups", your email as contact. Default scopes only (`openid`, `email`, `profile`). Publishing status can stay in **Testing**.
4. **APIs & Services → Credentials → Create Credentials → OAuth Client ID**, type **Web application**.
   - Authorized JavaScript origins: `https://groups.mzywang.dev`, `http://localhost:5183`
   - No redirect URIs needed (the Identity Services button flow doesn't use server-side redirects).
5. Copy the Client ID (`xxxx.apps.googleusercontent.com`) — this is a public value, safe to commit/embed in frontend code, not a secret.

### Phase 2 — D1 binding and subjects table

**PR**, plus one manual step for production.

- PR: add `d1_databases` binding to `wrangler.jsonc` (binding name `DB`), add `migrations/0001_subjects.sql` creating the `subjects` table.
- Manual/CLI: apply the migration to the local dev DB (`wrangler d1 migrations apply groups --local` — I can run this, it's local-only) and to production (`wrangler d1 migrations apply groups --remote` — this touches live infra, so it's on you to run or explicitly approve, same as the earlier remote deploy steps).

### Phase 3 — Session secret

**Manual/CLI, no PR** (it's a runtime secret, never committed).

- Local dev: a `SESSION_SECRET` value in `.dev.vars` (gitignored) — I can generate and write this myself, it's local-only.
- Production: `wrangler secret put SESSION_SECRET` with a separately-generated random value — this mutates the live Worker's config, so it's on you to run or approve.

### Phase 4 — Auth endpoint

**PR.**

- `src/lib/server/googleAuth.ts` — verifies an ID token: fetches/caches Google's JWKS, checks signature, `aud` (matches our Client ID), `iss`, `exp`.
- `src/lib/server/session.ts` — signs/verifies the session cookie (HMAC-SHA256 via Web Crypto, using `SESSION_SECRET`).
- `src/routes/auth/google/+server.ts` — `POST`: verify token → find-or-create subject in D1 (by `google_sub`) → set session cookie.
- `src/routes/auth/logout/+server.ts` — `POST`: clear the cookie.
- `src/hooks.server.ts` — reads the session cookie, sets `event.locals.subject` (or `null`).
- Testing: local dev needs D1 + secret bindings available, which `adapter-cloudflare` should expose to plain `vite dev` (via `getPlatformProxy`) — will confirm when building; falls back to `wrangler dev` if not.

### Phase 5 — Frontend

**PR.**

- Add the Google Identity Services script + rendered button to the homepage.
- On successful sign-in, `POST` the credential to `/auth/google`, then refresh.
- A root `+layout.server.ts` exposes `locals.subject` to pages so the homepage can show "signed in as `{email}`" + a sign-out link instead of the button, once authenticated.
- The Client ID from Phase 1 is embedded as a public var (`PUBLIC_GOOGLE_CLIENT_ID` in `wrangler.jsonc`'s `vars`), not a secret.

### Phase 6 — Verify in production

**Manual.** After Phases 2–5 are merged and deployed: confirm the remote D1 migration and `SESSION_SECRET` are in place (Phases 2–3), then actually sign in at `https://groups.mzywang.dev` and confirm a row appears in the production `subjects` table.

## Explicitly out of scope here

The `/preferences` endpoint, group membership, and tick logic from `exploration.md` — this plan only gets us to "a real signed-in subject exists," which those depend on.
