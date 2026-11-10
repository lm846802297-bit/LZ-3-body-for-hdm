# Figure assets

The seven PDF figures are part of the original `3body_for_HDM.zip` source package. Their original byte sizes and SHA-256 hashes are listed in [../ASSET_MANIFEST.md](../ASSET_MANIFEST.md).

All seven PDFs are committed here byte-for-byte as extracted from the original archive, so a fresh checkout can run `../build.sh` without restoring anything by hand. The figure names and relative paths must remain unchanged because they are referenced directly by `main.tex`.

Verify the committed bytes against the original archive from `paper-source/`:

```bash
sha256sum -c SHA256SUMS
```

No plots have been redrawn or numerically altered as part of this source import.
