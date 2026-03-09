import shutil
import subprocess
import asyncio
from pathlib import Path
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from minecraft import MinecraftAPI, DefaultServer
from logger import TextBuilder, GradientPreset, GradientMode, Question, logger

# Dependencies check

def check_dependency(package_name: str, exit_on_fail: bool = True, required: bool = True, packet_manager: list = None) -> bool:
    prefix = "Dependencies"

    if packet_manager is None:
        packet_manager = ["apt", "dnf", "yum", "pacman", "zypper", "apk"]

    if shutil.which(package_name):
        logger.info(f"Found ({package_name})!", prefix)
        return True

    logger.warning(f"({package_name}) not found!", prefix)
    if not required:
        logger.info(f"({package_name}) is optional. Continuing without it.", prefix)
        return False
    
    logger.warning(f"({package_name}) is required.")
    logger.plain("Do we try to install it now? (requires sudo privileges) [Y/n]: ", "#", end="")

    if input().strip().lower() not in ["", "y", "yes"]:
        logger.error("User declined installation.", prefix)
        if exit_on_fail:
            exit(1)
        return False

    package_managers = {
        "apt": ["sudo", "apt", "install", "-y", package_name],
        "dnf": ["sudo", "dnf", "install", "-y", package_name],
        "yum": ["sudo", "yum", "install", "-y", package_name],
        "pacman": ["sudo", "pacman", "-S", "--noconfirm", package_name],
        "zypper": ["sudo", "zypper", "--non-interactive", "install", package_name],
        "apk": ["sudo", "apk", "add", package_name],
    }

    for manager in packet_manager:
        if manager in package_managers and shutil.which(manager):
            try:
                logger.info(f"Found ({manager})! Installing ({package_name}) over ({manager})...", prefix)
                if manager == "apt":
                    subprocess.check_call(["sudo", "apt", "update"])
                subprocess.check_call(package_managers[manager])
                logger.info(f"({package_name}) has been installed.", prefix)
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Could not install ({package_name}) using ({manager}). Error: {e}", prefix)

    logger.error(f"No supported package manager found. Please install ({package_name}) manually.", prefix)
    if exit_on_fail:
        exit(1)
    return False

# Run
def check_dependencies():
    logger.info("Checking dependencies...", "Dependencies")
    check_dependency("screen")

# very fancy logo

def print_logo():
    logo = r"""   ____       __  __            __    _                  __  _________
  / __ )___  / /_/ /____  _____/ /   (_)___  __  ___  __/  |/  / ____/
 / __  / _ \/ __/ __/ _ \/ ___/ /   / / __ \/ / / / |/_/ /|_/ / /     
/ /_/ /  __/ /_/ /_/  __/ /  / /___/ / / / / /_/ />  </ /  / / /___   
\____/\___/\__/\__/\___/_/  /_____/_/_/ /_/\__,_/_/|_/_/  /_/\____/   
    """
    color_logo = TextBuilder().gradient(logo, GradientPreset.LAVA, GradientMode.CHARS)
    for line in color_logo.build().split("\n"):
        logger.info(line)

if __name__ == "__main__":
    logger.clear()
    logger.info("Booting up...", "Installer")
    print_logo()
    
    # Checking if screen is installed
    check_dependencies()

    # Server installation
    path = Path("Server")
    start_script = "start.sh"
    installed_alr = Question("Do you already installed a server on this device?").ask_boolean()
    server = "paper"
    version = "latest"
    build = "latest"

    if installed_alr:
        while True:
            user_input = Question("Please enter the path to your server dir (absolute path can avoid issues)").ask(not_empty=True)
            if Path(user_input).is_dir():
                path = Path(user_input)
                break
            logger.error("Please enter a valid path!")
    else:
        path = Path(Question("Please enter a path where you wanne install your server (absolute path can avoid issues)").ask(not_empty=True))
    logger.warning("Auto generating start script I will code later, so you must know how to build a start.sh!")
    start_script = Question("Enter you start script file").ask("start.sh", not_empty=True)

    if not installed_alr:
        logger.info("Now we want to download the server")
        logger.info("Current supported auto install servers:")
        logger.info("Vanilla, Paper, Velocity, Purpur")
        
        server = Question("Enter one server from above or enter custom if you wanna install it manually").ask("paper", ["vanilla", "paper", "velocity", "purpur", "custom"], True).lower()

        if not server == "custom":
            logger.info("Caching server versions... (This may can take a moment)")
        else:
            pass # TODO: add custom server installations questions

        if server == "vanilla":
            latest_version = asyncio.run(MinecraftAPI(DefaultServer.Vanilla()).get_latest_version())

            cached_versions = asyncio.run(MinecraftAPI(DefaultServer.Vanilla()).get_versions())
            cached_mc_versions = [version["version"] for version in cached_versions]

            version = Question("Please enter a Minecraft version").ask(latest_version["version"], cached_mc_versions)

        if server == "paper":
            latest_version = asyncio.run(MinecraftAPI(DefaultServer.Paper()).get_latest_version())

            cached_versions = asyncio.run(MinecraftAPI(DefaultServer.Paper()).get_versions())
            cached_mc_versions = [version["version"] for version in cached_versions]

            version = Question("Please enter a Minecraft version").ask(latest_version["version"], cached_mc_versions)
            cached_builds = [build for build in cached_versions[version]]
            logger.info(cached_builds)

        if server == "velocity":
            latest_version = asyncio.run(MinecraftAPI(DefaultServer.Velocity()).get_latest_version())

            cached_versions = asyncio.run(MinecraftAPI(DefaultServer.Velocity()).get_latest_version())
            cached_mc_versions = [version["version"] for version in cached_versions]

            version = Question("Please enter a Minecraft version").ask(latest_version["version"], cached_mc_versions)
            cached_builds = [build for build in cached_versions[version]]

