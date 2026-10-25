variable "desktop" {
  type        = string
  description = "gnome (Fedora Workstation) or kde (Fedora KDE Plasma)"

  validation {
    condition     = contains(["gnome", "kde"], var.desktop)
    error_message = "desktop is gnome or kde."
  }
}

variable "ssh_public_key_file" {
  type        = string
  description = "the public key root on the VM trusts"
}

variable "server_type" {
  type    = string
  default = "cx33"
}

variable "location" {
  type    = string
  default = "nbg1"
}

variable "image" {
  type        = string
  default     = "fedora-42"
  description = "a Fedora with GNOME 48 or later and Plasma 6"
}

variable "ipv4" {
  type        = bool
  default     = false
  description = "a primary IPv4, for a network without IPv6"
}
