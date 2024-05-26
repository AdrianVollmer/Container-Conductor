import click


def coco():
    from container_conductor import click_aux

    click_aux.main()


@click.group()
def cococtl():
    # TODO:
    # * get
    # * update
    # * list
    # * remove
    # * shell-completion
    # * update-cache
    # * create-link
    pass


def __main__():
    cococtl()
