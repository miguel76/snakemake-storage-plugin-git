import logging

import pygit2

from snakemake_storage_plugin_git import StorageProvider, StorageProviderSettings

REPOSITORY = "https://github.com/SE-UP/snakemake-storage-plugin-git"
# A commit preceding the head of the default branch
COMMIT = "5e82c2bf6a195b20d1452e4a2559be5ddcc80d4c"


def test_custom_head_checked_out_after_clone(tmp_path):
    provider = StorageProvider(
        local_prefix=tmp_path,
        logger=logging.getLogger(__name__),
        settings=StorageProviderSettings(
            enable_rate_limits=False,
            custom_heads={REPOSITORY: {"commit": COMMIT}},
            _is_test=True,
        ),
        keep_local=True,
        retrieve=False,
    )
    storage_object = provider.object(REPOSITORY)
    # First access: the repository is cloned
    assert storage_object.exists()
    repo = pygit2.Repository(str(storage_object.local_path()))
    assert str(repo.head.target) == COMMIT
    assert not repo.status()
