import click


def coco():
    from container_conductor import click_aux

    click_aux.main()


@click.group()
def cococtl():
    # TODO:
    # * get
    # * update
    # * ls
    # * remove
    # * shell-completion
    # * update-cache
    # * symlink create
    # * symlink delete
    # * symlink ls
    pass


def __main__():
    cococtl()
