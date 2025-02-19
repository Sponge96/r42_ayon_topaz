from qtpy import QtWidgets
import ayon_api

from ayon_core.addon import AYONAddon, click_wrap
from .version import __version__


class TopazAddon(AYONAddon):
    label = "Topaz"
    name = "topaz"
    version = __version__

    def cli(self, click_group):
        # Convert `cli_main` command to click object and add it to parent group
        click_group.add_command(cli_main.to_click_obj())


@click_wrap.group(TopazAddon.name, help="My Addon cli commands.")
def cli_main():
    pass


@cli_main.command()
@click_wrap.option("--project", help="project name", type=str, required=False)
@click_wrap.option("--entity-id", help="entity id", type=str, required=False)
def show_selected_path(project, entity_id):
    """Display a dialog showing the folder path from which the action was triggered."""
    con = ayon_api.get_server_api_connection()
    entity = con.get_folder_by_id(project, entity_id)
    folder_path = f"{project}{entity['path']}"

    app = QtWidgets.QApplication()
    QtWidgets.QMessageBox.information(
        None,
        "Triggered from AYON Server",
        f"The action was triggered from folder: '{folder_path}'",
    )


@cli_main.command()
@click_wrap.option("--project", help="project name", type=str, required=False)
@click_wrap.option("--entity-id", help="entity id", type=str, required=False)
def launch_topaz(project, entity_id):
    con = ayon_api.get_server_api_connection()
    entity = con.get_version_by_id(project, entity_id)

    app = QtWidgets.QApplication()
    QtWidgets.QMessageBox.information(None, "Test", f"{entity}")
