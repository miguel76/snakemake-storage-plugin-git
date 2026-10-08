import logging
from pathlib import Path

from snakemake_storage_plugin_git import StorageProvider, StorageProviderSettings

REPOSITORY = "https://github.com/SE-UP/snakemake-storage-plugin-git"


def get_provider(tmp_path: Path, **settings) -> StorageProvider:
    # Settings as used in a workflow, i.e. without _is_test
    return StorageProvider(
        local_prefix=tmp_path,
        logger=logging.getLogger(__name__),
        settings=StorageProviderSettings(enable_rate_limits=False, **settings),
        keep_local=True,
        retrieve=False,
    )


def test_exists_clones_repository(tmp_path):
    # exists() may be called without inventory() (e.g. for the inputs of jobs
    # that are not targets), so it has to clone the repository itself
    storage_object = get_provider(tmp_path).object(REPOSITORY)
    assert storage_object.exists()
    assert (Path(storage_object.local_path()) / "pyproject.toml").exists()


def test_exists_not_existing_repository(tmp_path):
    storage_object = get_provider(tmp_path, ignore_errors=True).object(
        "https://github.com/SE-UP/snakemake-storage-plugin-svn"
    )
    assert not storage_object.exists()
