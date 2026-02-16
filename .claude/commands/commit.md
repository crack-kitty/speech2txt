Commit changes with automatic semantic version bump.

## Instructions

1. Run `git status` and `git diff` to see all changes (staged and unstaged). If there are no changes, tell the user and stop.

2. Read the `VERSION` file at the project root to get the current version (format: MAJOR.MINOR.PATCH).

3. Determine the version bump type from the user's argument `$ARGUMENTS`:
   - If the argument contains "major" → bump MAJOR, reset MINOR and PATCH to 0
   - If the argument contains "minor" → bump MINOR, reset PATCH to 0
   - If the argument is empty or contains "patch" or anything else → bump PATCH
   - If the argument contains a specific version like "2.0.0" → use that exact version

4. Stage all relevant changed files with `git add` (add specific files, not `git add -A`). Do NOT stage files that contain secrets (.env, credentials, etc).

5. Update the `VERSION` file with the new version number.

6. Stage the updated `VERSION` file.

7. Draft a concise commit message summarizing the changes. Format:
   ```
   v{NEW_VERSION}: {summary of changes}
   ```
   The summary should be 1-2 sentences describing what changed and why.

8. Create the commit. Do NOT include Co-Authored-By lines.

9. Create a git tag `v{NEW_VERSION}` on the new commit.

10. Show the user: old version → new version, the commit message, and remind them to `git push --tags` when ready.

## Rules
- Do NOT push automatically — let the user decide when to push
- Do NOT use `git add -A` or `git add .` — add specific files
- Do NOT include Co-Authored-By lines in the commit message
- Do NOT skip pre-commit hooks (no --no-verify)
- Use a HEREDOC for the commit message to preserve formatting
