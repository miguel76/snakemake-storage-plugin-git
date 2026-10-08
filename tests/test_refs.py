import logging

import pygit2
import pytest
from snakemake_interface_common.exceptions import WorkflowError

from snakemake_storage_plugin_git import StorageProvider, StorageProviderSettings

REPOSITORY = "https://github.com/SE-UP/snakemake-storage-plugin-git"
TAG = "v0.1.0"
TAG_COMMIT = "2a712a06a20374cef2e3338f5a9e7bfe641f28bc"
# A commit preceding the head of the default branch
COMMIT = "5e82c2bf6a195b20d1452e4a2559be5ddcc80d4c"


@pytest.fixture
def provider(tmp_path):
    return StorageProvider(
        local_prefix=tmp_path,
        logger=logging.getLogger(__name__),
        settings=StorageProviderSettings(enable_rate_limits=False),
        keep_local=True,
        retrieve=False,
    )


def checked_out(storage_object) -> str:
    assert storage_object.exists()
    repo = pygit2.Repository(str(storage_object.local_path()))
    assert not repo.status()
    return str(repo.head.target)


def test_tag(provider):
    assert checked_out(provider.object(f"{REPOSITORY}#{TAG}")) == TAG_COMMIT


def test_commit(provider):
    assert checked_out(provider.object(f"{REPOSITORY}#{COMMIT}")) == COMMIT


def test_branch(provider):
    head = checked_out(provider.object(f"{REPOSITORY}#main"))
    repo = pygit2.Repository(str(provider.object(f"{REPOSITORY}#main").local_path()))
    assert head == str(repo.revparse_single("refs/remotes/origin/main").id)


def test_ref_after_fetch(provider):
    # The ref is checked out also when an existing clone is updated
    storage_object = provider.object(f"{REPOSITORY}#{COMMIT}")
    checked_out(storage_object)
    provider.done_queries.clear()
    assert checked_out(storage_object) == COMMIT


def test_local_copy_for_each_ref(provider):
    tag_object = provider.object(f"{REPOSITORY}#{TAG}")
    commit_object = provider.object(f"{REPOSITORY}#{COMMIT}")
    assert tag_object.local_path() != commit_object.local_path()
    assert str(tag_object.local_path()).endswith(f"@{TAG}")
    assert checked_out(tag_object) == TAG_COMMIT
    assert checked_out(commit_object) == COMMIT


def test_unknown_ref(provider):
    # (exists() would raise the same error, after retrying)
    with pytest.raises(WorkflowError, match="no-such-ref not found"):
        provider.object(f"{REPOSITORY}#no-such-ref")._clone_or_pull()
