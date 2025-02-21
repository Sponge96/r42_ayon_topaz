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
def upscale_1080p(project, entity_id):
    con = ayon_api.get_server_api_connection()
    representations = con.get_representations(
        project_name=project, version_ids=[entity_id]
    )
    target = None
    for rep in representations:
        if rep.get("context").get("ext") == "mov":
            target = rep

    if target:
        input = os.path.normpath(target.get("attrib").get("path"))
        output = os.path.normpath("Z:/_TEMP/Jack.P/test_area/test.mov")
        command = [
            "ffmpeg",
            "-hide_banner",
            "-i",
            input,
            "-sws_flags",
            "spline+accurate_rnd+full_chroma_int",
            "-color_trc",
            "2",
            "-colorspace",
            "2",
            "-color_primaries",
            "2",
            "-filter_complex",
            "tvai_up=model=prob-3:scale=0:w=1920:h=1080:preblur=0:noise=0.02:details=0.1:halo=0.02:blur=0.05:compression=0.1:blend=0.1:device=0:vram=1:instances=1,"
            "scale=w=1920:h=1080:flags=lanczos:threads=0",
            "-c:v",
            "prores_ks",
            "-profile:v",
            "3",
            "-vendor",
            "apl0",
            "-quant_mat",
            "hq",
            "-bits_per_mb",
            "1350",
            "-pix_fmt",
            "yuv422p10le",
            "-an",
            "-map_metadata",
            "0",
            "-map_metadata:s:v",
            "0:s:v",
            "-movflags",
            "use_metadata_tags+write_colr",
            "-metadata",
            "videoai=Enhanced using prob-3; mode: manual; revert compression at 10; recover details at 10; "
            "sharpen at 5; reduce noise at 2; dehalo at 2; anti-alias/deblur at 0; focus fix Off; "
            "and recover original detail at 10. Changed resolution to 1920x1080",
            output,
        ]

        upscale(command)


@cli_main.command()
@click_wrap.option("--project", help="project name", type=str, required=False)
@click_wrap.option("--entity-id", help="entity id", type=str, required=False)
def upscale_4k(project, entity_id):
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
        try:
            input = get_input(target)
            data = target.get("data")
            format_data = {"data": data["context"]}
            format_data["data"]["output"] = "4k"
            format_data["data"]["representation"] = "4k"
            template_data = get_template_data(con, project, format_data)
            output = template_data["path"]
        except Exception as e:
            app = QtWidgets.QApplication()
            QtWidgets.QMessageBox.information(
                None,
                "Triggered from AYON Server",
                f"'{e}'",
            )

    try:
        result = ayon_api.create_representation(
            project_name=project,
            name="4k__",
            version_id=entity_id,
            files=[{"id": ayon_api.utils.create_entity_id(), "path": output}],
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


# command = [
#     "ffmpeg",
#     "-hide_banner",
#     "-i",
#     input,
#     "-sws_flags",
#     "spline+accurate_rnd+full_chroma_int",
#     "-color_trc",
#     "2",
#     "-colorspace",
#     "2",
#     "-color_primaries",
#     "2",
#     "-filter_complex",
#     "tvai_up=model=ghq-5:scale=0:w=3840:h=2160:device=0:vram=1:instances=1,scale=w=3840:h=2160:flags=lanczos:threads=0",
#     "-c:v",
#     "prores_ks",
#     "-profile:v",
#     "3",
#     "-vendor",
#     "apl0",
#     "-quant_mat",
#     "hq",
#     "-bits_per_mb",
#     "1350",
#     "-pix_fmt",
#     "yuv422p10le",
#     "-an",
#     "-map_metadata",
#     "0",
#     "-map_metadata:s:v",
#     "0:s:v",
#     "-movflags",
#     "use_metadata_tags+write_colr",
#     "-metadata",
#     "videoai=Enhanced using ghq-5. Changed resolution to 3840x2160",
#     output,
# ]
# upscale(command)


def get_input(rep):
    return os.path.normpath(rep.get("attrib").get("path"))


def get_template_data(con, project_name, format_data):
    project_anatomy = anatomy.Anatomy(project_name)
    template = project_anatomy.get_template_item("publish", "topazUpscale")
    return template.format(**format_data)


def upscale(command):
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
