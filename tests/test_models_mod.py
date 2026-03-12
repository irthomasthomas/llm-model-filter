import click
from click.testing import CliRunner
import json
import llm
from llm.cli import cli
import pathlib
import pytest
from llm_models_mod import register_commands

# We need to register the plugin hooks for the tests
class MockPlugin:
    @llm.hookimpl
    def register_commands(self, cli):
        register_commands(cli)

@pytest.fixture
def runner(tmpdir):
    import importlib
    import llm.cli
    # Setup a clean user directory for each test
    user_dir = pathlib.Path(tmpdir) / "user"
    user_dir.mkdir()
    
    # Mock llm.user_dir to return our temp dir
    original_user_dir = llm.user_dir
    llm.user_dir = lambda: user_dir
    
    # Register the plugin hook
    llm.plugins.pm.register(MockPlugin(), name="llm_models_mod")
    
    # Reload CLI to trigger hook registration
    importlib.reload(llm.cli)
    from llm.cli import cli as reloaded_cli
    
    yield CliRunner(env={"LLM_USER_PATH": str(user_dir)}), reloaded_cli
    
    # Cleanup
    llm.plugins.pm.unregister(name="llm_models_mod")
    llm.user_dir = original_user_dir
    importlib.reload(llm.cli)

def test_star_unstar(runner):
    runner, cli = runner
    # Initially none starred
    result = runner.invoke(cli, ["models", "star", "demo-model"])
    if result.exit_code != 0:
        print(result.output)
    assert result.exit_code == 0
    assert "Starred demo-model" in result.output
    
    data_file = llm.user_dir() / "models_mod_starred.json"
    assert data_file.exists()
    data = json.loads(data_file.read_text())
    assert "demo-model" in data["starred"]
    
    result = runner.invoke(cli, ["models", "unstar", "demo-model"])
    assert result.exit_code == 0
    assert "Unstarred demo-model" in result.output
    data = json.loads(data_file.read_text())
    assert "demo-model" not in data["starred"]

def test_config_starred_only(runner):
    runner, cli = runner
    result = runner.invoke(cli, ["models", "config", "starred-only"])
    assert result.exit_code == 0
    assert "Models display set to: starred-only" in result.output
    
    data_file = llm.user_dir() / "models_mod_starred.json"
    data = json.loads(data_file.read_text())
    assert data["starred_only"] is True

def test_filtering_logic(runner):
    runner, cli = runner
    # This test will likely fail until the plugin is implemented
    # We need some models to be registered.
    # For testing, we can use the 'echo' model which is usually available.
    
    # 1. Show all (default)
    result = runner.invoke(cli, ["models"])
    assert "echo" in result.output
    
    # 2. Star nothing, enable starred-only
    runner.invoke(cli, ["models", "config", "starred-only"])
    result = runner.invoke(cli, ["models"])
    assert "No models starred" in result.output
    assert "echo" not in result.output
    
    # 3. Star 'echo'
    runner.invoke(cli, ["models", "star", "echo"])
    result = runner.invoke(cli, ["models"])
    assert "echo" in result.output
    
    # 4. Use --all flag to bypass
    result = runner.invoke(cli, ["models", "list", "--all"])
    assert "echo" in result.output # echo remains, but others should too
