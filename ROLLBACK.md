# Rollback

## Release rollback

Do not alter live persona homes as part of a framework rollback.

1. Stop distribution and identify the affected release source/version.
2. Restore the pre-renewal framework source from
   `archive/pre-linear-renewal-main` at
   `424237a2597b95ddc59a34443e32d6351e80d4fb`, or select a known-good release
   source revision.
3. Review the restored source in a separate working directory; do not overwrite
   the current worktree or installed cache.
4. Re-run its own documented validation before any separately authorized
   publish/install action.
5. Roll forward rather than editing a released source in place. Re-installing,
   activating, or changing a live persona requires separate approval.

The Mesh recovery reference is `forge/personas-mesh-extraction` at
`e1f504222883b0fb5823f6cbec2b2305336dbdd4`; it is not a rollback instruction
for the core product.
