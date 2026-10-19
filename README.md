# Lenivis Homebrew tap

Casks for applications by [Lenivis LLC](https://lenivis.com/). Application,
service and website source are private; this repository holds only Homebrew
installation metadata.

## koe

```sh
brew install lenivis/tap/koe
```

koe needs an Apple Silicon Mac running macOS 13 or later and a koe account
(invite-only for now). The first 30 minutes are free, without a card. After that, a paid plan is optional. No provider API key is needed or bundled.
Homebrew may ask you to trust this third-party cask. No installation step
disables Gatekeeper or removes quarantine.

koe updates itself (Sparkle, signed updates from the same public releases), so
the cask is marked `auto_updates` and `brew upgrade` leaves it to the app.
`brew uninstall --cask koe` quits and removes the app; add `--zap` to also remove
its preferences, caches and opt-in local history. Your sign-in stays in Keychain
(service "com.koe.dictation"); remove it in Keychain Access if desired.

- [Website and setup](https://saykoe.com/)
- [Public binary releases](https://github.com/YIPG/koe-releases)

## Maintainer: publish a verified cask

After `YIPG/koe-releases` publishes a real notarized release:

```sh
gh workflow run update-koe.yml --repo lenivis/homebrew-tap -f version=0.9.1
```

The version above is an example. The workflow downloads
the exact public ZIP, `SHA256SUMS` (which also lists the DMG), and generated
`koe.rb` from that release. It checks the checksum, app identity/version and that
the only symbolic links are Sparkle.framework's own, validates the signature and stapled
notarization ticket, assesses Gatekeeper, and exercises the resource diagnostic
before committing the cask. It rejects drafts and prereleases.

No Apple private key, API key, or cross-repository write token is needed here:
the workflow reads public release artifacts and uses this repository's own
GitHub token only to update its cask.

Test the first install, upgrade, and uninstall in an isolated app directory
before announcing availability. Update this README's status after the first
cask lands; do not advertise a working install command while `Casks/koe.rb` is
absent.
