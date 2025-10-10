This folder contains the application's localized help files. The canonical (source-of-truth) help text is the Ukrainian master file `uk-UA.md`. All other language files in this folder must be derived from and kept in sync with `uk-UA.md`.

Agent / Translator Guide (English)

Purpose
- Keep localized help documentation accurate and consistent across locales.
- Use `uk-UA.md` as the canonical source. When help content changes, update the master first and then update translations to match.

Quick contract
- Inputs: the latest `uk-UA.md` content and any new strings or UI label changes.
- Outputs: updated locale markdown files (for example `en-US.md`) placed in this same folder.
- Success criteria: translated files preserve structure and code samples from the master and reflect the same user-facing content.

How to work
1. Start from `uk-UA.md` (master)
	- If you are changing the original text, update `uk-UA.md` first.
	- Translators should base their work on the current `uk-UA.md` at the HEAD of the branch they are working on.

2. Create or update the target locale file
	- File name format: `<language-region>.md` (examples: `en-US.md`, `uk-UA.md`).
	- Keep the same headings, section order, code fences, inline code, links and anchors as the master. Translate only the textual content.
	- Do not alter example code, file paths, or configuration snippets unless the content explicitly requires localization.

3. Markdown and formatting rules
	- Use plain Markdown compatible with GitHub/Git renderer.
	- Preserve inline code/backticks and code blocks exactly (only translate comments and user-facing text inside those blocks when appropriate).
	- Keep any localized strings that are UI labels consistent with the UI language files when present.

4. Commit & branch workflow
	- Branch naming: prefer `i18n/<locale>/<short-description>` (for example `i18n/en-US/help-fix`).
	- Commit messages: follow Conventional Commits, for example:
	  - `docs(i18n): update en-US translation for help text`.
	- Include the source commit or a reference to the `uk-UA.md` version in the PR description.

5. Pull requests and review
	- Open a PR targeting the `develop` branch (or the branch requested by the issue/maintainer).
	- In the PR description, state whether you updated only translations or also changed the master.
	- Request review from a reviewer fluent in the target language and from a maintainer if you modified the master file.

6. Style guidance for translators
	- Use simple, clear, user-facing language.
	- Preserve technical terms. When translating a technical term for the first time, choose a consistent translation and add a short note/comment in the PR if the choice is non-obvious.
	- Keep sentences short and instructions actionable.

7. Checklist before merging
	- [ ] Based on the latest `uk-UA.md` (or PR that modified it).
	- [ ] Headings and anchors preserved; section order matches master.
	- [ ] Code blocks and inline code unchanged unless intentionally localized.
	- [ ] Commit message follows Conventional Commits.
	- [ ] A fluent reviewer is assigned.

If you're unsure about a translation choice, or the help text refers to UI labels or code that may also change, open an issue or mention maintainers in the PR so we can coordinate.

Contact / Maintainers
- If in doubt, add a comment to the PR and tag the repository maintainers. It's better to ask than to guess translations for UI terms.

Thank you for keeping the documentation accessible and accurate across languages.
