# plugins/module_utils/influx_downloads.py
#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
InfluxDB download resolver for Linux tarball installations.

This helper resolves:
- a concrete InfluxDB version (pinned or "latest")
- the corresponding Linux tarball artifact name
- the download URL
- a SHA256 checksum for integrity verification

Supported product lines:
- InfluxDB OSS v2 (download metadata via GitHub Releases notes)
- InfluxDB 3 (core|enterprise; tarball + .sha256 on dl.influxdata.com)

Design goals:
- Linux only
- No OS/distro packages
- No container installation
- Compatibility with different ansible-core versions (fetch_url signatures)
"""

from __future__ import absolute_import, division, print_function

from dataclasses import dataclass
import json
import platform
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url

# --- Regex ---
SEMVER_RE = re.compile(r"^(?P<maj>\d+)\.(?P<min>\d+)\.(?P<pat>\d+)$")
SHA256_RE = re.compile(r"(?i)\b([0-9a-f]{64})\b")

# --- Common types ---
JsonType = Union[Dict[str, Any], List[Any]]


class DownloadNotFoundError(RuntimeError):
    """
    Raised when a requested resource does not exist (HTTP 404), with structured context.

    The `context` dict is intended to be returned as module result fields to improve
    Ansible error output without forcing string parsing.
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.context: Dict[str, Any] = context or {}


@dataclass(frozen=True)
class DownloadInfo:
    """Resolved download information for a specific InfluxDB line/version."""

    major_version: int
    version: str
    edition: Optional[str]
    arch: str
    artifact: str
    url: str
    sha256: str


class InfluxDownloads:
    """
    Resolve InfluxDB tarball download information for Linux.

    Public API stability:
      - __init__(module: AnsibleModule) -> None
      - run() -> Dict[str, Any]

    Parameters (module.params):
      - major_version: int (2|3)
      - version: str ("latest" or "x.y.z")
      - influxdb3_edition: str ("core"|"enterprise") [only for v3]
      - download_base: str (default: https://dl.influxdata.com/influxdb/releases)
      - architecture: str (input arch, e.g. "x86_64", "amd64", "aarch64", "arm64")
      - github_token: str (optional; increases GitHub API rate limits)
      - timeout: int (seconds; default 15)
      - validate_certs: bool (default True)
      - user_agent: str (default "ansible-influx-downloads")
    """

    _DEFAULT_DOWNLOAD_BASE = "https://dl.influxdata.com/influxdb/releases"
    _V3_INSTALL_SCRIPT_URL = "https://www.influxdata.com/d/install_influxdb3.sh"
    _GITHUB_RELEASES_URL = "https://api.github.com/repos/influxdata/influxdb/releases"
    _GITHUB_RELEASE_TAG_URL = "https://api.github.com/repos/influxdata/influxdb/releases/tags"

    _ARCH_ALIASES: Dict[str, str] = {
        # amd64
        "x86_64": "amd64",
        "amd64": "amd64",
        # arm64
        "aarch64": "arm64",
        "arm64": "arm64",
        # keep for future / older v2 releases if present
        "armv7l": "armv7",
        "armv7": "armv7",
        "armv6l": "armv6",
        "armv6": "armv6",
    }

    def __init__(self, module: AnsibleModule) -> None:
        """Initialize resolver with an AnsibleModule."""
        self.module = module
        self.module.log("InfluxDownloads::__init__()")

        p = module.params

        self.major_version: int = int(p.get("major_version"))
        self.requested_version: str = str(p.get("version"))
        self.edition: str = str(p.get("influxdb3_edition") or "core")
        self.download_base: str = str(p.get("download_base") or self._DEFAULT_DOWNLOAD_BASE)

        self.github_token: str = str(p.get("github_token") or "")
        self.timeout: int = int(p.get("timeout") or 15)
        self.validate_certs: bool = bool(
            p.get("validate_certs") if p.get("validate_certs") is not None else True
        )
        self.user_agent: str = str(p.get("user_agent") or "ansible-influx-downloads")

        # Normalize architecture (do not rely on platform.machine() here; Ansible passes it in).
        self.architecture: str = self._normalize_arch(str(p.get("architecture") or "x86_64"))

        # Older ansible-core: fetch_url reads validate_certs from module.params (no kwarg).
        self.module.params.setdefault("validate_certs", self.validate_certs)

        self._validate_inputs()

    def run(self) -> Dict[str, Any]:
        """
        Resolve download information.

        Returns:
            Dict[str, Any]: Ansible module style result dict.
        """
        self.module.log("InfluxDownloads::run()")

        try:
            arch = self.architecture

            resolved_version = (
                self._resolve_latest_v3()
                if (self.requested_version == "latest" and self.major_version == 3)
                else self._resolve_latest_v2()
                if (self.requested_version == "latest" and self.major_version == 2)
                else self.requested_version
            )

            if self.major_version == 2:
                artifact, url, sha256 = self._resolve_v2_download(resolved_version, arch)
            else:
                artifact, url = self._build_v3_artifact_and_url(resolved_version, arch)
                sha256 = self._resolve_v3_sha256(
                    version=resolved_version,
                    arch=arch,
                    artifact=artifact,
                    url=url,
                )

            info = DownloadInfo(
                major_version=self.major_version,
                version=resolved_version,
                edition=self.edition if self.major_version == 3 else None,
                arch=arch,
                artifact=artifact,
                url=url,
                sha256=sha256,
            )

            return {
                "failed": False,
                "changed": False,
                "major_version": info.major_version,
                "version": info.version,
                "edition": info.edition,
                "arch": info.arch,
                "download_artifact": info.artifact,
                "download_url": info.url,
                "download_checksum": info.sha256,
            }

        except DownloadNotFoundError as exc:
            ctx = dict(exc.context)
            reason = ctx.pop("reason", "not_found")
            ctx.setdefault("major_version", self.major_version)
            ctx.setdefault("requested_version", self.requested_version)

            return {
                "failed": True,
                "changed": False,
                "reason": reason,
                "msg": str(exc),
                **ctx,
            }

        except Exception as exc:  # noqa: BLE001
            return {
                "failed": True,
                "changed": False,
                "msg": f"{type(exc).__name__}: {exc}",
                "major_version": self.major_version,
                "requested_version": self.requested_version,
            }

    # -------------------------
    # Validation / inputs
    # -------------------------

    def _validate_inputs(self) -> None:
        """Validate parameters early and fail with a clear message."""
        self.module.log("InfluxDownloads::_validate_inputs()")

        if not str(platform.system()).lower().startswith("linux"):
            raise RuntimeError("This resolver supports Linux only.")

        if self.major_version not in (2, 3):
            raise ValueError("major_version must be 2 or 3")

        if self.requested_version != "latest" and not SEMVER_RE.match(self.requested_version):
            raise ValueError("version must be 'latest' or a semver like '2.7.12' / '3.1.0'")

        if self.major_version == 3 and self.edition not in ("core", "enterprise"):
            raise ValueError("influxdb3_edition must be 'core' or 'enterprise'")

        # InfluxDB 3 tarballs are expected for amd64/arm64 only in this helper.
        if self.major_version == 3 and self.architecture not in ("amd64", "arm64"):
            raise ValueError(
                f"Unsupported architecture for InfluxDB 3 tarballs: {self.architecture} "
                "(supported: amd64, arm64)"
            )

    def _normalize_arch(self, arch: str) -> str:
        """
        Normalize architecture strings to Influx artifact naming.

        Args:
            arch: Input arch string (e.g. 'x86_64', 'amd64', 'aarch64', 'arm64').

        Returns:
            str: Canonical arch token used in artifact names (e.g. 'amd64', 'arm64').

        Raises:
            ValueError: If arch cannot be mapped.
        """
        a = (arch or "").strip().lower()
        if a in self._ARCH_ALIASES:
            return self._ARCH_ALIASES[a]
        raise ValueError(f"Unsupported architecture value: {arch}")

    # -------------------------
    # Resolve "latest"
    # -------------------------

    def _resolve_latest_v3(self) -> str:
        """
        Resolve latest InfluxDB 3 version from the official install script.

        Returns:
            str: version "x.y.z"
        """
        self.module.log("InfluxDownloads::_resolve_latest_v3()")

        text = self._http_text(self._V3_INSTALL_SCRIPT_URL, headers={"Accept": "*/*"})
        m = re.search(r'INFLUXDB_VERSION="(\d+\.\d+\.\d+)"', text)
        if not m:
            raise RuntimeError("Could not parse latest InfluxDB 3 version from install script.")
        return m.group(1)

    def _resolve_latest_v2(self) -> str:
        """
        Resolve latest stable InfluxDB 2 version using the GitHub Releases API.

        Returns:
            str: version "x.y.z"
        """
        self.module.log("InfluxDownloads::_resolve_latest_v2()")

        url = f"{self._GITHUB_RELEASES_URL}?per_page=100"
        releases = self._http_json(url, headers=self._github_headers())
        if not isinstance(releases, list):
            raise RuntimeError("Unexpected GitHub API response for releases list (expected JSON array).")

        candidates: List[str] = []
        for r in releases:
            if not isinstance(r, dict):
                continue
            if r.get("draft") is True or r.get("prerelease") is True:
                continue
            tag = str(r.get("tag_name") or "")
            if not tag.startswith("v2."):
                continue
            v = tag[1:]  # drop leading 'v'
            if SEMVER_RE.match(v):
                candidates.append(v)

        if not candidates:
            raise RuntimeError("No stable v2.* releases found via GitHub API.")

        return max(candidates, key=self._semver_key)

    @staticmethod
    def _semver_key(v: str) -> Tuple[int, int, int]:
        """Convert 'x.y.z' into a tuple for stable comparisons."""
        m = SEMVER_RE.match(v)
        if not m:
            return (0, 0, 0)
        return (int(m.group("maj")), int(m.group("min")), int(m.group("pat")))

    # -------------------------
    # v3: artifact/url + sha
    # -------------------------

    def _build_v3_artifact_and_url(self, version: str, arch: str) -> Tuple[str, str]:
        """
        Build v3 artifact filename and download URL.

        Args:
            version: Semver string.
            arch: Canonical arch token ("amd64"|"arm64").

        Returns:
            Tuple[str, str]: (artifact, url)
        """
        self.module.log(f"InfluxDownloads::_build_v3_artifact_and_url(version: {version}, arch: {arch})")

        artifact = f"influxdb3-{self.edition}-{version}_linux_{arch}.tar.gz"
        url = f"{self.download_base.rstrip('/')}/{artifact}"
        return artifact, url

    def _resolve_v3_sha256(self, version: str, arch: str, artifact: str, url: str) -> str:
        """
        Resolve v3 sha256 via '<url>.sha256'.

        Raises:
            DownloadNotFoundError: If the tarball does not exist.
        """
        self.module.log(f"InfluxDownloads::_resolve_v3_sha256(url: {url})")

        self._http_head(
            url,
            headers={"Accept": "*/*"},
            context={
                "reason": "artifact_not_found",
                "major_version": 3,
                "edition": self.edition,
                "version": version,
                "arch": arch,
                "artifact": artifact,
                "url": url,
            },
        )

        sha_text = self._http_text(f"{url}.sha256", headers={"Accept": "*/*"})
        sha = self._extract_first_sha256(sha_text)
        if not sha:
            raise RuntimeError("Could not parse SHA256 for InfluxDB 3 from .sha256 file.")
        return sha.lower()

    # -------------------------
    # v2: parse artifact/url/sha from release body (naming differs across versions)
    # -------------------------

    def _resolve_v2_download(self, version: str, arch: str) -> Tuple[str, str, str]:
        """
        Resolve v2 artifact, download URL and sha256 from GitHub release notes.

        This avoids guessing the filename format (older releases use '-' separators,
        newer releases use '_' separators).

        Raises:
            DownloadNotFoundError: If the release tag is missing or artifact is missing.
        """
        self.module.log(f"InfluxDownloads::_resolve_v2_download(version: {version}, arch: {arch})")

        rel_url = f"{self._GITHUB_RELEASE_TAG_URL}/v{version}"
        rel = self._http_json(
            rel_url,
            headers=self._github_headers(),
            context={
                "reason": "release_tag_not_found",
                "major_version": 2,
                "version": version,
                "tag": f"v{version}",
                "url": rel_url,
            },
        )
        if not isinstance(rel, dict):
            raise RuntimeError("Unexpected GitHub API response for release-by-tag (expected JSON object).")

        body = str(rel.get("body") or "")
        artifact, embedded_url, sha = self._parse_v2_release_body(body, version, arch)

        # Prefer URL from body; fallback to configured base.
        url = embedded_url or f"{self.download_base.rstrip('/')}/{artifact}"

        ctx = {
            "reason": "artifact_not_found",
            "major_version": 2,
            "version": version,
            "arch": arch,
            "artifact": artifact,
        }

        # Validate URL exists; if it fails and we didn't use embedded_url, try embedded_url as fallback.
        try:
            self._http_head(url, headers={"Accept": "*/*"}, context={**ctx, "url": url})
        except RuntimeError:
            if embedded_url and embedded_url != url:
                self._http_head(embedded_url, headers={"Accept": "*/*"}, context={**ctx, "url": embedded_url})
                url = embedded_url
            else:
                raise

        return artifact, url, sha.lower()

    @staticmethod
    def _parse_v2_release_body(body: str, version: str, arch: str) -> Tuple[str, Optional[str], str]:
        """
        Parse GitHub release body for the Linux tarball filename + sha256.

        Args:
            body: GitHub release markdown body.
            version: Semver string.
            arch: Canonical arch token (amd64|arm64|armv7|armv6).

        Returns:
            Tuple[str, Optional[str], str]: (artifact_filename, optional_full_url, sha256)

        Raises:
            RuntimeError: If the expected artifact+sha entry cannot be parsed.
        """
        if not body:
            raise RuntimeError("GitHub release body is empty; cannot parse v2 artifacts.")

        if arch == "amd64":
            arch_tokens = ["amd64", "x86_64"]
        elif arch == "arm64":
            arch_tokens = ["arm64", "aarch64"]
        elif arch == "armv7":
            arch_tokens = ["armv7", "armv7l"]
        elif arch == "armv6":
            arch_tokens = ["armv6", "armv6l"]
        else:
            raise RuntimeError(f"Unsupported arch token for v2 parsing: {arch}")

        arch_group = "|".join(map(re.escape, arch_tokens))

        # Prefer markdown link variant:
        # [influxdb2-2.4.0-linux-amd64.tar.gz](https://dl.influxdata.com/influxdb/releases/influxdb2-2.4.0-linux-amd64.tar.gz) <sha>
        link_re = re.compile(
            rf"(?im)\b(influxdb2-{re.escape(version)}[-_]linux[-_](?:{arch_group})\.tar\.gz)\b"
            rf".*?\((https?://[^)]+/influxdb/releases/\1)\)\s+([0-9a-f]{{64}})\b"
        )
        m = link_re.search(body)
        if m:
            return m.group(1), m.group(2), m.group(3)

        # Fallback: plain filename and sha on same line
        line_re = re.compile(
            rf"(?im)\b(influxdb2-{re.escape(version)}[-_]linux[-_](?:{arch_group})\.tar\.gz)\b"
            rf"[^\n]*?\b([0-9a-f]{{64}})\b"
        )
        m2 = line_re.search(body)
        if m2:
            return m2.group(1), None, m2.group(2)

        raise RuntimeError(
            f"Could not parse v2 linux tarball + sha256 for version={version}, arch={arch} from release body."
        )

    # -------------------------
    # Common helpers
    # -------------------------

    @staticmethod
    def _extract_first_sha256(text: str) -> Optional[str]:
        """Extract the first SHA256 hash from a text blob."""
        m = SHA256_RE.search(text or "")
        return m.group(1) if m else None

    def _fetch(self, url: str, method: str, headers: Optional[Dict[str, str]] = None) -> Tuple[Any, Dict[str, Any]]:
        """
        Wrapper around fetch_url for compatibility across ansible-core versions.

        Newer ansible-core versions accept validate_certs kwarg.
        Older versions read validate_certs from module.params and do not accept the kwarg.
        """
        self.module.log(f"InfluxDownloads::_fetch(url: {url}, method: {method}, headers: {headers})")

        hdrs = headers or {}
        try:
            return fetch_url(
                self.module,
                url,
                method=method,
                timeout=self.timeout,
                headers=hdrs,
                validate_certs=self.validate_certs,
            )
        except TypeError:
            self.module.params.setdefault("validate_certs", self.validate_certs)
            return fetch_url(
                self.module,
                url,
                method=method,
                timeout=self.timeout,
                headers=hdrs,
            )

    def _http_head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Perform a HEAD request and raise on non-2xx.

        Raises:
            DownloadNotFoundError: On HTTP 404 with structured context.
            RuntimeError: For other non-2xx responses.
        """
        self.module.log(f"InfluxDownloads::_http_head(url: {url}, headers: {headers})")

        _, info = self._fetch(url, method="HEAD", headers=headers)
        status = int(info.get("status") or 0)

        if 200 <= status < 300:
            return

        msg = info.get("msg") or ""
        ctx = context or {}

        if status == 404:
            hint = self._latest_hint(ctx.get("major_version"), ctx.get("edition"))
            parts = [
                "Requested InfluxDB artifact not found (HTTP 404).",
                f"major={ctx.get('major_version', self.major_version)}",
                f"version={ctx.get('version', self.requested_version)}",
            ]
            if ctx.get("edition"):
                parts.append(f"edition={ctx['edition']}")
            if ctx.get("arch"):
                parts.append(f"arch={ctx['arch']}")
            if ctx.get("artifact"):
                parts.append(f"artifact={ctx['artifact']}")
            parts.append(f"url={url}")
            if hint:
                parts.append(f"hint={hint}")

            raise DownloadNotFoundError(
                " | ".join(parts),
                context={**ctx, "url": url, "http_status": status},
            )

        raise RuntimeError(f"HEAD {url} returned HTTP {status}: {msg}")

    def _http_text(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        GET a URL and return decoded UTF-8 text.

        Raises:
            DownloadNotFoundError: On HTTP 404 with structured context (if provided).
            RuntimeError: For other non-2xx responses.
        """
        self.module.log(f"InfluxDownloads::_http_text(url: {url}, headers: {headers})")

        resp, info = self._fetch(url, method="GET", headers=headers)
        status = int(info.get("status") or 0)

        if 200 <= status < 300:
            body = resp.read() if resp else b""
            return body.decode("utf-8", errors="replace")

        msg = info.get("msg") or ""
        ctx = context or {}

        if status == 404 and ctx:
            reason = str(ctx.get("reason") or "not_found")
            major = ctx.get("major_version", self.major_version)
            version = ctx.get("version", self.requested_version)
            hint = self._latest_hint(major, ctx.get("edition"))

            if reason == "release_tag_not_found":
                parts = [
                    "Requested InfluxDB GitHub release tag not found (HTTP 404).",
                    f"major={major}",
                    f"version={version}",
                    f"tag={ctx.get('tag')}",
                    f"url={url}",
                ]
                if hint:
                    parts.append(f"hint={hint}")
                raise DownloadNotFoundError(
                    " | ".join([p for p in parts if p and p != "tag=None"]),
                    context={**ctx, "url": url, "http_status": status},
                )

            parts = [
                "Requested resource not found (HTTP 404).",
                f"major={major}",
                f"version={version}",
                f"url={url}",
            ]
            if hint:
                parts.append(f"hint={hint}")
            raise DownloadNotFoundError(
                " | ".join(parts),
                context={**ctx, "url": url, "http_status": status, "reason": reason},
            )

        raise RuntimeError(f"GET {url} returned HTTP {status}: {msg}")

    def _http_json(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> JsonType:
        """
        GET a URL and parse JSON response.

        Raises:
            DownloadNotFoundError: Propagated from _http_text (HTTP 404 with context).
            RuntimeError: If JSON parsing fails.
        """
        self.module.log(f"InfluxDownloads::_http_json(url: {url}, headers: {headers}, context: {context})")

        text = self._http_text(url, headers=headers, context=context)
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"Failed to parse JSON from {url}: {exc}") from exc

    def _github_headers(self) -> Dict[str, str]:
        """Headers suitable for GitHub API requests."""
        self.module.log("InfluxDownloads::_github_headers()")

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/vnd.github+json",
        }
        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"
        return headers

    def _latest_hint(self, major_version: Optional[int], edition: Optional[str]) -> Optional[str]:
        """
        Best-effort hint to improve error messages.

        Returns:
            Optional[str]: A short hint string, or None on any failure.
        """
        self.module.log(f"InfluxDownloads::_latest_hint(major_version: {major_version}, edition: {edition})")

        try:
            mv = int(major_version or self.major_version)
            if mv == 3:
                latest = self._resolve_latest_v3()
                ed = edition or self.edition
                return f"try version=latest (current installer default: {latest}, edition={ed})"
            if mv == 2:
                latest = self._resolve_latest_v2()
                return f"try version=latest (current stable v2: {latest})"
        except Exception:
            return None
        return None


def main() -> None:
    """Module entrypoint."""
    argument_spec = dict(
        major_version=dict(type="int", required=True, choices=[2, 3]),
        version=dict(type="str", required=True),  # "latest" or "x.y.z"
        influxdb3_edition=dict(type="str", default="core", choices=["core", "enterprise"]),
        download_base=dict(type="str", default=InfluxDownloads._DEFAULT_DOWNLOAD_BASE),
        architecture=dict(type="str", required=False, default="x86_64"),
        github_token=dict(type="str", default="", no_log=True),
        timeout=dict(type="int", default=15),
        validate_certs=dict(type="bool", default=True),
        user_agent=dict(type="str", default="ansible-influx-downloads"),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    helper = InfluxDownloads(module)
    result = helper.run()

    if result.get("failed"):
        module.fail_json(**result)
    module.exit_json(**result)


if __name__ == "__main__":
    main()
