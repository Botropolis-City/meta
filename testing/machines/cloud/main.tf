locals {
  name       = "botropolis-wayland-${var.desktop}"
  public_key = trimspace(file(var.ssh_public_key_file))
}

resource "hcloud_ssh_key" "runner" {
  name       = local.name
  public_key = local.public_key
}

resource "hcloud_firewall" "ssh_only" {
  name = local.name

  rule {
    direction  = "in"
    protocol   = "tcp"
    port       = "22"
    source_ips = ["0.0.0.0/0", "::/0"]
  }
}

resource "hcloud_server" "desktop" {
  name         = local.name
  server_type  = var.server_type
  image        = var.image
  location     = var.location
  ssh_keys     = [hcloud_ssh_key.runner.id]
  firewall_ids = [hcloud_firewall.ssh_only.id]
  user_data = templatefile("${path.module}/cloud-init.yaml.tftpl", {
    desktop    = var.desktop
    public_key = local.public_key
  })

  public_net {
    ipv4_enabled = var.ipv4
    ipv6_enabled = true
  }

  labels = {
    purpose = "botropolis-item-96"
  }
}
