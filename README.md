## Municipal Assistant

CLI and API to help a municipal office manage residents, service requests, permits, contacts, and tasks. Data is stored in a local SQLite database at `data/municipal.db`.

### Requirements
- Python 3.10+
- Optional: `uv` for fast env management. Install if needed:

```bash
pip install uv
```

### Setup
Using `uv` (recommended):

```bash
uv sync
source .venv/bin/activate
```

Alternative with `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### CLI usage
After activating the virtual environment:

```bash
municipal-assistant --help
```

Common commands:

```bash
# Residents
municipal-assistant resident add "Jane Doe" --email jane@example.com --phone "+1-555-0100" --address "123 Main St"
municipal-assistant resident list

# Service Requests
municipal-assistant sr open --resident-id 1 --category "Pothole" --description "Large pothole on 5th Ave"
municipal-assistant sr list
municipal-assistant sr update 1 closed

# Permits
municipal-assistant permit apply --resident-id 1 --type "Building"
municipal-assistant permit list
municipal-assistant permit decide --permit-id 1 --outcome approved

# Contacts
municipal-assistant contact add "Public Works" "Alex Smith" --email alex@city.gov --phone "+1-555-0101"
municipal-assistant contact list

# Tasks
municipal-assistant task add "Inspect playground equipment" --due 2025-09-01 --assigned-to "Safety Team"
municipal-assistant task list
municipal-assistant task update 1 done

# Export all data to JSON
municipal-assistant export -o data/export.json
```

You can also run the CLI module directly:

```bash
python -m municipal_assistant --help
```

### API usage
Start the API server:

```bash
uvicorn municipal_assistant.api:app --reload
```

Test a few endpoints:

```bash
curl -X POST http://127.0.0.1:8000/residents \
  -H 'content-type: application/json' \
  -d '{"name":"Jane Doe","email":"jane@example.com"}'

curl http://127.0.0.1:8000/residents
```

### Packaging
- Project metadata and dependencies are managed in `pyproject.toml`.
- An executable script `municipal-assistant` is installed via the `project.scripts` entry point.

### Troubleshooting
- ImportError when running `python municipal_assistant/cli.py`: run as a module or use the installed script instead:

```bash
python -m municipal_assistant
```

- Typer/Click help error (e.g., `Parameter.make_metavar()`): ensure Click is pinned to a compatible version. This project pins `click==8.1.7`. If using `requirements.txt`, install it explicitly:

```bash
pip install 'click==8.1.7'
```

### Data location
- SQLite DB: `data/municipal.db` (auto-created on first run)
- JSON export example: `data/export.json`
