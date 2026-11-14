# opto-sync-assets
Versioned product images, CSS, CDN exports, and static assets; app branding is isolated from marketing sites.

## Versioned asset inventory

`branding/manifest.v1.json` is the machine-readable catalog for tracked product
branding assets. Each entry records a stable ID, repository-relative path,
media type, accessible alternative text, and the **Git blob SHA** (not an
independent SHA-256 content hash). Consumers should pin the repository commit
when resolving assets; a mutable branch URL is not a release identifier.

The `Asset manifest integrity` CI gate rejects duplicate IDs/paths, path
traversal, symlinks, mismatched file extensions/media types, and stale Git blob
hashes. Update the manifest in the same PR as an asset change. No CDN upload,
publishing, or external provider mutation is performed by this repository.
