# Snakemake storage plugin: git

This plugin allows you to clone remote Git repositories via SSH and HTTPS.

A specific git ref (tag, branch or commit) can be checked out by appending it to
the URL as fragment, e.g. `https://github.com/user/repo.git#v1.0`. Each ref gets
its own local copy, so that multiple refs of the same repository can be used in
a workflow, also through wildcards:

```python
rule process:
    input:
        storage.git("https://github.com/user/repo.git#{version}"),
    output:
        "results/{version}.txt",
    shell:
        "..."
```

The ref is looked up as a tag, then as a branch (of the remote, so up to date
after fetching), then as any other revision (e.g. a commit id).

An existing local copy is fetched at each run (with `fetch_to_update`, the
default), unless its ref is already there as a tag or a commit id, which cannot
change.
