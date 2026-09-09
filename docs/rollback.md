# Recovering from a release

Keep framework recovery separate from changes to a live persona's content.

1. Identify the affected release and a known-good published tag or commit.
2. Inspect the known-good source in a separate checkout and run its own test
   gate. Preserve the failing checkout and any persona-local changes.
3. Reinstall the selected version through the runtime's plugin flow, or prepare
   a corrective release through the normal pull-request process.
4. Verify a synthetic persona before reviewing any live-folder reconciliation.

For a failed adapter update, inspect the helper's reported paths and restore
only the affected files from reviewed backups. Preview generation again before
applying it. Private context remains with its existing owner and backup source.
