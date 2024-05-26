import click
from container_conductor import click_aux


def coco():
    click_aux.main()


@click.group()
def cococtl():
    # TODO:
    # * get
    # * update
    # * list
    # * remove
    # * update-cache
    # * create-link
    pass


def __main__():
    cococtl()
