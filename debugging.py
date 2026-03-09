import asyncio

from logger import logger
from minecraft import MinecraftAPI, DefaultServer

if __name__ == "__main__":
    logger.info("Fetching versions...")

    latest_version = asyncio.run(MinecraftAPI(DefaultServer.Velocity()).get_latest_version())

    cached_versions = asyncio.run(MinecraftAPI(DefaultServer.Velocity()).get_latest_version())
    cached_mc_versions = [version["version"] for version in cached_versions]

    version = "1.19.3"

    cached_builds = [build for build in cached_versions[version]]

    logger.info("Test installation:")
    logger.info("Versions:")
    logger.info(cached_versions)
    logger.info("Mc versions:")
    logger.info(cached_mc_versions)
    logger.info(f"Builds from {version}:")
    logger.info(cached_builds)