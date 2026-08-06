# Activation

Source readiness does not modify installed plugins or live persona folders.

Before activating a framework change:

1. Run `bash tests/run-tests.sh`.
2. Review the exact source diff and runtime support declarations.
3. Install or update the plugin through the target runtime's normal plugin
   flow.
4. Test a sanitized persona folder before reconciling an existing persona with
   `personas:persona-update`.
5. Review every persona-local migration separately; preserve ignored `user/`
   context and persona-owned customizations.

Installation, live-folder migration, external connections, and publication are
separate actions and require their own approval.
