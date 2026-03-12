import llm
import click
import json
import textwrap

def get_storage_path():
    return llm.user_dir() / "models_mod_starred.json"

def load_data():
    path = get_storage_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            pass
    return {"starred": [], "starred_only": False}

def save_data(data):
    get_storage_path().write_text(json.dumps(data, indent=4))

@llm.hookimpl
def register_commands(cli):
    models_group = cli.commands.get("models")
    if not isinstance(models_group, click.Group):
        return

    # 1. Add 'star' subcommand
    @models_group.command(name="star")
    @click.argument("model_ids", nargs=-1)
    def star(model_ids):
        """Star one or more models to add to favourites."""
        data = load_data()
        for mid in model_ids:
            if mid not in data["starred"]:
                data["starred"].append(mid)
                click.echo(f"Starred {mid}")
        save_data(data)

    # 2. Add 'unstar' subcommand
    @models_group.command(name="unstar")
    @click.argument("model_ids", nargs=-1)
    def unstar(model_ids):
        """Remove one or more models from favourites."""
        data = load_data()
        for mid in model_ids:
            if mid in data["starred"]:
                data["starred"].remove(mid)
                click.echo(f"Unstarred {mid}")
        save_data(data)

    # 3. Add 'config' subcommand
    @models_group.command(name="config")
    @click.argument("setting", type=click.Choice(["starred-only", "all"]))
    def config_cmd(setting):
        """Configure 'llm models' display mode."""
        data = load_data()
        data["starred_only"] = (setting == "starred-only")
        save_data(data)
        click.echo(f"Models display set to: {setting}")

    # 4. Wrap the 'list' command (Monkey-Patching)
    if "list" in models_group.commands:
        list_cmd = models_group.commands["list"]
        
        # Add the --all option if not already present
        if not any(p.name == "show_all_starred" for p in list_cmd.params):
            list_cmd.params.append(click.Option(["--all", "show_all_starred"], is_flag=True, help="Force show all models"))

        original_callback = list_cmd.callback

        def wrapped_list_callback(**kwargs):
            show_all = kwargs.pop("show_all_starred", False)
            data = load_data()
            if data.get("starred_only") and not show_all:
                starred = data.get("starred", [])
                if starred:
                    current_ids = kwargs.get("model_ids") or []
                    if not current_ids:
                        kwargs["model_ids"] = tuple(starred)
                    else:
                        # Filter user-provided IDs by starred list
                        kwargs["model_ids"] = tuple(set(current_ids).intersection(starred))
                else:
                    click.echo("No models starred. Use 'llm models star <id>' first.")
                    return
            return original_callback(**kwargs)

        list_cmd.callback = wrapped_list_callback
        # Re-register to ensure any caching in DefaultGroup is bypassed
        models_group.add_command(list_cmd, name="list")
