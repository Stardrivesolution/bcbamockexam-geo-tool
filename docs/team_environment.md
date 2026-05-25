# Team Environment And Secrets

This project should be easy for two developers to run locally without sharing
private secrets through Git.

## Rule

Commit `.env.example`.

Do not commit `.env`.

`.env.example` shows which variables are required. Each developer creates their
own local `.env` file.

## Why

Environment variables usually contain private or machine-specific values:

- LLM API keys
- database URLs
- crawl limits
- model names
- debug flags
- third-party API keys

If `.env` is committed, secrets can leak into Git history. Even deleting the
file later does not reliably remove it from old commits.

## Local Setup

```bash
cp .env.example .env
```

Then each developer edits `.env` locally.

## Recommended Sharing Method

For two-person internal development:

1. Keep `.env.example` in Git.
2. Share real secrets through a password manager, not through Git or chat.
3. When a new variable is added, update `.env.example` with a placeholder.
4. Tell the teammate which new variable was added.

Good options:

- 1Password shared vault
- Bitwarden organization vault
- iCloud Keychain shared password group
- company password manager

## Example

`.env.example`:

```env
APP_NAME="GEO Internal Tool"
APP_ENV="local"
APP_DEBUG=true
DATABASE_URL="sqlite:///./geo_internal_tool.db"
OPENAI_API_KEY=""
DEFAULT_LLM_MODEL="gpt-4.1-mini"
```

Local `.env`:

```env
APP_NAME="GEO Internal Tool"
APP_ENV="local"
APP_DEBUG=true
DATABASE_URL="sqlite:///./geo_internal_tool.db"
LLM_PROVIDER="deepseek"
LLM_API_KEY="real-key-goes-here"
LLM_BASE_URL="https://api.deepseek.com"
LLM_MODEL="deepseek-chat"
LLM_TIMEOUT_SECONDS=60
```

## Development vs Production

Local development can use SQLite:

```env
DATABASE_URL="sqlite:///./geo_internal_tool.db"
```

Production or shared staging should use PostgreSQL:

```env
DATABASE_URL="postgresql+psycopg://user:password@host:5432/geo"
```

## Practical Team Workflow

When developer A adds a new environment variable:

1. Add it to `.env.example` with an empty or safe placeholder value.
2. Add code that reads it from `app/core/config.py`.
3. Commit the code and `.env.example`.
4. Share the real secret through the password manager.
5. Developer B pulls the code and updates their local `.env`.
