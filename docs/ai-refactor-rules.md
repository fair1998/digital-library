# AI Refactor Rules

## Scope

- Refactor only files under `templates/**/**.html`
- Do not modify `templates/dashboard/**/**.html`

## Must Keep

- Django template tags
- URL names
- block structure
- extends/include behavior
- forms and csrf
- variable names and loops unless necessary

## Allowed

- Improve HTML structure
- Add Bootstrap classes
- Add Bootstrap Icons
- Improve spacing/layout/typography
- Improve empty states and headings
- Improve semantic grouping

## Forbidden

- Do not change Python code
- Do not change dashboard templates
- Do not redesign into flashy style
- Do not add custom JS unless truly necessary
- Do not break form behavior
