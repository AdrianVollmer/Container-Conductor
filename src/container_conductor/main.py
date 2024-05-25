import click
from container_conductor import click_aux


@click_aux.from_config
def coco(*args, **kwargs):
    pass


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


def __main__(*args, **kwargs):
    cococtl(*args, **kwargs)
