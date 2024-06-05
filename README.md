**Work in progress. Don't use.**

# Container-Conductor

[![PyPI - Version](https://img.shields.io/pypi/v/container-conductor.svg)](https://pypi.org/project/container-conductor)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/container-conductor.svg)](https://pypi.org/project/container-conductor)

Turn podman into an app store.

Container Conductor is a Python based CLI app that helps you manage and run
docker-compose files. It reduces mental load when running containers by
wrapping their functionality into a CLI tool with modern shell completion. No
more looking up and remembering information about which volume goes where, what
environment variable has which functionality, and so on. The configurations are
easily shareable. Put the power of containers into hands of people who don't know what a container is.

It is based on podman instead of Docker because podman's rootless containers
are simpler to deal with. Podman-compose is based on Python, which I prefer,
and more targeted towards this scenario.

Container Conductor is considered **MeWare**: fills a need I have and works for
me. Published in the hopes it can be useful for you, but don't expect perfect
polishing. Issues and PRs welcome.

> [!WARNING]
> While containers can be used to limit exposure in case of a breach, don't
> feel too safe. You are still running other people's code on your machine.
> Perhaps Container Conductor will have a permission-based safety concept in
> the future, but not at this point.

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pipx ensurepath
pipx install container-conductor
```

Note that you need to install podman and pipx first using your system's package manager. For Debian/Ubuntu/Kali:

```console
apt install podman pipx
```

For shell completion and smart links to work, add this to your shell's config file:

```shell
# .zshrc
eval "$(cococtl shell-config --shell zsh)"

# .bashrc
eval "$(cococtl shell-config --shell bash)"

# ~/.config/fish/completions/foo-bar.fish

```

## Using and adding coco apps

Container Conductor ("coco" for short) apps consist of single YAML files.

They are located by default in `~/.local/share/coco/apps`, unless you changed your
`XDG_DATA_HOME` variable. You can create or copy the files there (see
`examples` for examples) or use `cococtl add [URL|PATH]` to add them.

To use a coco app, run `coco <APP NAME>`. If that is too verbose for you, you can create a "smart link", which is a symlink to the `coco` executable where the name of the symlink corresponds to the name of the coco app.

For example, if you have a coco app named `typst`, do this:

```console
ln -s $(which coco) ~/.local/bin/typst
```

Now you can call `typst` directly instead of `coco typst`. Alternatively, use
the `cococtl symlink create` command, which will create a link in
`~/.local/share/coco/symlinks`, which must be in your `$PATH`. If you added the
line with `cococtl shell-config` like described above, your `$PATH` will be
adjusted accordingly.


## License

`container-conductor` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
