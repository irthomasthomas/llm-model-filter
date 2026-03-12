# llm-model-filter

Filter the `llm models` list to show only your favorite "starred" models. Especially useful for LLM agents that need a clean list of available capabilities.

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/):

```bash
llm install llm-model-filter
```

## Usage

### 1. Configure Filtering
By default, the plugin doesn't filter anything. You can enable "starred-only" mode:

```bash
llm models config starred-only
```
To revert:
```bash
llm models config all
```

### 2. Starring Models
Add models to your favorites:

```bash
llm models star gpt-4o
llm models star claude-3.5-sonnet
```

### 3. Viewing Models
When configured to `starred-only`, the standard `llm models` command will only show your favorites:

```bash
llm models
```

To see all models regardless of configuration:
```bash
llm models list --all
```

### 4. Unstarring
Remove models from your favorites:

```bash
llm models unstar gpt-4o
```

## How it works
This plugin wraps the `llm models list` command. It uses a robust callback-modification technique to ensure compatibility with existing flags while providing the filtering logic.

Starred models and configuration are stored in `llm.user_dir() / "models_mod_starred.json"`.

## Plugin directory

This plugin is listed in the [LLM plugin directory](https://llm.datasette.io/en/stable/plugins/directory.html) under **Extra commands**.
