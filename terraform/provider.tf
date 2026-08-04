provider "cloudflare" {
  # Reads the API token from the CLOUDFLARE_API_TOKEN env var — never store
  # the token in .tf/.tfvars files. Use the same "Edit Cloudflare Workers"
  # token template documented in BOOTSTRAP.md, scoped to Account Resources,
  # plus D1:Edit if it isn't already covered by that template.
}
