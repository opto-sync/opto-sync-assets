# opto-sync-assets
Versioned product images, CSS, CDN exports, and static assets; app branding is isolated from marketing sites.

## Integrity manifest

`asset-manifest.json` binds every exported file to its SHA-256 digest, byte length, and image dimensions. `branding/app-logo.png` is the Flutter launcher-icon source: consumers must verify it against the manifest digest before deriving platform launcher assets, and must not substitute GitHub Pages marketing artwork.

`brandApproval` stays `pending` until the product owner approves the logo; changing the image requires updating the digest in the same reviewed change.

Run `python3 scripts/validate.py` before publishing. It fails on digest, size, or dimension drift, a missing or symlinked asset, and any file under `branding/` that is not listed in the manifest.
