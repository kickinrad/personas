# Rollback

## Release rollback

Do not alter live persona homes as part of a framework rollback.

1. Stop distribution and identify the affected release source/version.
2. Restore the last published pre-3.0 framework source at
   `d3a0ed1d29177f85df9cdc28f4e51378ed0da8d9`, or select another known-good
   release source revision.
3. Review the restored source in a separate working directory; do not overwrite
   the current worktree or installed cache.
4. Re-run its own documented validation before any separately authorized
   publish/install action.
5. Roll forward rather than editing a released source in place. Re-installing,
   activating, or changing a live persona requires separate approval.

The maintainer-local Mesh recovery reference is
`forge/personas-mesh-extraction` at
`e1f504222883b0fb5823f6cbec2b2305336dbdd4`. It remains deliberately
unpublished pending a separate Mesh review and is not a rollback instruction
for the core product.
