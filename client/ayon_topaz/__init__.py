from qtpy import QtWidgets
import ayon_api

from ayon_core.addon import AYONAddon, click_wrap
from ayon_core.pipeline import anatomy
from .version import __version__
import subprocess
import os


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


def get_input(rep):
    return os.path.normpath(rep.get("attrib").get("path"))


def get_template_data(con, project_name, format_data):
    project_anatomy = anatomy.Anatomy(project_name)
    template = project_anatomy.get_template_item("publish", "topazUpscale")
    return template.format(**format_data)


@cli_main.command()
@click_wrap.option("--project", help="project name", type=str, required=True)
@click_wrap.option("--entity-id", help="entity id", type=str, required=True)
@click_wrap.option("--command", help="ffmpeg command", type=str, required=True)
def upscale(project, entity_id, command):
    con = ayon_api.get_server_api_connection()
    representations = con.get_representations(
        project_name=project, version_ids=[entity_id]
    )
    target = None
    # we need to fetch the correct rep not just using mov this is error prone
    for rep in representations:
        if rep.get("data"):
            if rep.get("data").get("context"):
                if rep.get("data").get("context").get("output") == "ProRes":
                    target = rep

    if target:
        input = get_input(target)
        data = target.get("data")
        format_data = {"data": data["context"]}
        format_data["data"]["output"] = "4k"
        format_data["data"]["representation"] = "4k"
        template_data = get_template_data(con, project, format_data)
        output = template_data["path"]

        command = [
            "ffmpeg",
            "-hide_banner",
            "-i",
            input,
            command,
            output,
        ]
        os.chdir("C:\Program Files\Topaz Labs LLC\Topaz Video AI")
        os.environ["TVAI_MODEL_DIR"] = (
            "C:\ProgramData\Topaz Labs LLC\Topaz Video AI\models"
        )

        try:
            subprocess.run(command, check=True)

        except subprocess.CalledProcessError as e:
            app = QtWidgets.QApplication()
            QtWidgets.QMessageBox.information(
                None,
                "Triggered from AYON Server",
                f"The action was triggered from folder: '{e}'",
            )

        try:
            result = ayon_api.create_representation(
                project_name=project,
                name="4k__",
                version_id=entity_id,
                files=[
                    {"id": ayon_api.utils.create_entity_id(), "path": output}
                ],
                data=data,
                attrib={"path": output},
            )
        except Exception as e:
            app = QtWidgets.QApplication()
            QtWidgets.QMessageBox.information(
                None,
                "Triggered from AYON Server",
                f"'{e}'",
            )
