resource "cloudflare_workers_custom_domain" "groups" {
  account_id = var.cloudflare_account_id
  zone_id    = var.cloudflare_zone_id
  hostname   = "groups.mzywang.dev"
  service    = "groups"
}
