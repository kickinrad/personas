# Recovering from a release

If a release causes trouble, you can return to a known-good version without
rewriting your persona. Keep a backup of any local changes before you begin.

1. Find the affected release and a published tag or commit that worked.
2. Check out the working version in a separate folder and run its test suite.
   Keep the failing checkout and your persona's local changes for comparison.
3. Reinstall the chosen version through your runtime's plugin flow. If you're
   maintaining Personas, you can instead prepare a fix through a pull request.
4. Test with a disposable persona before changing a persona you rely on.

If only an agent or profile update failed, check the paths in the helper's
output and restore only the affected files from your reviewed backups. Run
the preview again before applying it. Your private context doesn't need to
move or change as part of recovery.
