import aiohttp
import re

from pathlib import Path

from logger import logger

class MinecraftServerBase:
    """Base element for Minecraft Server APIs"""
    HEADERS = {"User-Agent": "betterlinuxmc/1.0"}

    def get_name(self) -> str:
        raise NotADirectoryError


    async def _get(self, session: aiohttp.ClientSession, url: str):
        async with session.get(url, headers=self.HEADERS) as resp:
            resp.raise_for_status()
            return await resp.json()

    async def _get_versions(self, session: aiohttp.ClientSession) -> list[str]:
        raise NotImplementedError

    async def _get_builds(self, session: aiohttp.ClientSession, version: str) -> list[int] | None:
        return None

    async def _get_download_url(self, session: aiohttp.ClientSession, version: str, build: int) -> str:
        raise NotImplementedError
    
    async def _get_download_size(self, session: aiohttp.ClientSession, version: str, build: int) -> int:
        raise NotImplementedError
    
    # Coming up in future
    async def _get_download_sha256(self, session: aiohttp.ClientSession, version: str, build: int) -> str:
        return None
    
    async def _get_additional_infos(self, session: aiohttp.ClientSession, version: str, build: int):
        return None

    @staticmethod
    def _version_sort_key(version: str) -> list[int]:
        """convert from '1.20.4' to [1, 20, 4]"""
        return [int(x) for x in re.split(r"\D", version) if x.isdigit()]

    async def get_versions(self, session: aiohttp.ClientSession, only_stable: bool = False) -> list[dict[str, str | list[int]]]:
        """
        Exaple output:
        [
            {"version": "1.20.4", "builds": [100,101]},
            {"version": "1.20.3", "builds": [95,96]},
        ]
        """
        versions = await self._get_versions(session)
        versions_sorted = sorted(versions, key=self._version_sort_key, reverse=True)
        if only_stable:
            versions_sorted = [v for v in versions_sorted if re.fullmatch(r"^\d+(?:\.\d+)*$", v)]

        if not versions_sorted:
            raise ValueError("No versions found!")

        result = []

        for version in versions_sorted:
            builds = await self._get_builds(session, version)
            result.append({"version": version, "builds": builds})
        
        return result

    async def fetch_latest_version(self, session: aiohttp.ClientSession, only_stable: bool = False) -> str:
        versions = await self._get_versions(session)

        versions_sorted = sorted(versions, key=self._version_sort_key, reverse=True)
        if only_stable:
            versions_sorted = [v for v in versions_sorted if re.fullmatch(r"^\d+(?:\.\d+)*$", v)]

        if not versions_sorted:
            raise ValueError("No versions found! Check API config.")
        return versions_sorted[0]


    async def fetch_latest_build(self, session: aiohttp.ClientSession, version: str) -> int | None:
        builds = await self._get_builds(session, version)
        if not builds:
            return None
        return max(builds)
    

class DefaultServer:
    """Implemented APIs"""
    class Vanilla(MinecraftServerBase):
        MANIFEST = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

        def get_name(self):
            return "Vanilla"

        async def _get_versions(self, session: aiohttp.ClientSession):
            data = await self._get(session, self.MANIFEST)
            return [v["id"] for v in data["versions"]]

        async def _get_download_url(self, session, version, build = None):
            manifest = await self._get(session, self.MANIFEST)
            version_data = next(v for v in manifest["versions"] if v["id"] == version)
            meta = await self._get(session, version_data["url"])
            return meta["downloads"]["server"]["url"]
        
        async def _get_download_size(self, session, version, build = None):
            manifest = await self._get(session, self.MANIFEST)
            version_data = next(v for v in manifest["versions"] if v["id"] == version)
            meta = await self._get(session, version_data["url"])
            return meta["downloads"]["server"]["size"]
        
    class Paper(MinecraftServerBase):
        API = "https://fill.papermc.io/v3/projects/paper"

        def get_name(self):
            return "Paper"

        async def _get_versions(self, session):
            data = await self._get(session, self.API)
            return [version for versions in data["versions"].values() for version in versions]

        async def _get_builds(self, session, version):
            try:
                data = await self._get(session, f"{self.API}/versions/{version}/builds")
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    return []
                raise
            return [build["id"] for build in data]
        
        async def _get_download_url(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[0]

        async def _get_download_size(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[1]

        async def _get_download_sha256(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[2]

        async def _get_additional_infos(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[3]


        async def _get_download_info(self, session, version, build) -> list[str, int, str, str]:
            try:
                data = await self._get(session, f"{self.API}/versions/{version}/builds/{build}")
            except aiohttp.ClientResponseError as e:
                raise ValueError(f"Build {build} for version {version} not found")
            data = data["downloads"]["server:default"]
            return [data["url"], data["size"], data["checksums"]["sha256"], data["name"]]
        
    class Velocity(MinecraftServerBase):
        API = "https://fill.papermc.io/v3/projects/velocity"

        def get_name(self):
            return "Velocity"

        async def _get_versions(self, session):
            data = await self._get(session, self.API)
            return [version for versions in data["versions"].values() for version in versions]

        async def _get_builds(self, session, version):
            try:
                data = await self._get(session, f"{self.API}/versions/{version}/builds")
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    return []
                raise
            return [build["id"] for build in data]
        
        async def _get_download_url(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[0]

        async def _get_download_size(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[1]

        async def _get_download_sha256(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[2]

        async def _get_additional_infos(self, session, version, build):
            data = await self._get_download_info(session, version, build)
            return data[3]


        async def _get_download_info(self, session, version, build) -> list[str, int, str, str]:
            try:
                data = await self._get(session, f"{self.API}/versions/{version}/builds/{build}")
            except aiohttp.ClientResponseError as e:
                raise ValueError(f"Build {build} for version {version} not found")
            data = data["downloads"]["server:default"]
            return [data["url"], data["size"], data["checksums"]["sha256"], data["name"]]
        
    class Purpur(MinecraftServerBase):
        API = "https://api.purpurmc.org/v2/purpur"

        def get_name(self):
            return "Purpur"

        async def _get_versions(self, session):
            data = await self._get(session, self.API)
            return list(data["versions"])

        async def _get_builds(self, session, version):
            try:
                data = await self._get(session, f"{self.API}/{version}")
            except aiohttp.ClientResponseError as e:
                if e.status == 404:
                    return []
                raise
            return data["builds"]["all"]

        async def _get_download_url(self, session, version, build):
            return f"{self.API}/{version}/{build}/download"

        async def _get_download_size(self, session, version, build):
            return None

        async def _get_download_sha256(self, session, version, build):
            return None
    

class MinecraftAPI:
    """Minecraft Server manager"""
    def __init__(self, server: MinecraftServerBase):
        if server is None:
            raise ValueError("Version can not be null!")
        self.server = server

    async def _download_file(self, session, url: str, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        async with session.get(url) as resp:
            resp.raise_for_status()
            with open(path, "wb") as f:
                async for chunk in resp.content.iter_chunked(8192):
                    f.write(chunk)

    async def download(self, version: str = None, build: int | str = None, directory: Path = Path("."), filename: str = None, send_status: bool = True) -> Path:
        async with aiohttp.ClientSession() as session:
            if send_status:
                logger.info("Fetching versions...")

            if version in [None, "last", "latest"]:
                version = await self.server.fetch_latest_version(session)

            if build in [None, "last", "latest"]:
                build = await self.server.fetch_latest_build(session, version)

            url = await self.server._get_download_url(session, version, build)

            if filename is None:
                filename = f"{version}-{build}.jar"

            target_path = directory / filename
            if send_status:
                logger.info(f"Dowloading {self.server.get_name()} {version}{f" {build}" if build is not None else ""}...")
            await self._download_file(session, url, target_path)
            if send_status:
                logger.info(f"Dowloaded to {target_path}")
            return target_path
 
    async def get_versions(self, only_stable: bool = False) -> list[dict[str, str | list[int]]]:
        async with aiohttp.ClientSession() as session:
            return await self.server.get_versions(session, only_stable)
        
    async def get_latest_version(self, only_stable: bool = False, disable_error: bool = False) -> dict | None:
        async with aiohttp.ClientSession() as session:
            version = await self.server.fetch_latest_version(session, only_stable)
            
            if version is None:
                if disable_error:
                    return None
                raise ValueError("Latest version was null... broken api?")
            
            if isinstance(self.server, DefaultServer.Vanilla):
                build = None
            else:
                build = await self.server.fetch_latest_build(session, version)

            return {
                "version": version,
                "build": build
            }
        
    async def get_latest_build(self, version: str, disable_errors: bool = False) -> int | str | None: #TODO
        async with aiohttp.ClientSession() as session:
            if version is None:
                if disable_errors:
                    return None
                raise ValueError("Please input a valid version, not None")
            return await self.server.fetch_latest_build(session, version)