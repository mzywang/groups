# Terraform

Managed with [OpenTofu](https://opentofu.org/) (`tofu`).

## Usage

```bash
cd terraform
tofu init
cp terraform.tfvars.example terraform.tfvars
export BW_SESSION=$(bw unlock --raw)
export CLOUDFLARE_API_TOKEN=$(bw get password "Cloudflare Tofu Token")
tofu plan
```

State is local (`terraform.tfstate`), gitignored.
