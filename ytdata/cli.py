import click
from ytdata import YTData


@click.command()
@click.option('--channel', '-c', required=True,
              help='i.e. \'UCupvZG-5ko_eiXAupbDfxWw\' for CNN')
@click.option('--max_results', '-n', default=100,
              help='The maximum number of items to request.')
@click.option('--output_file', '-o', default='results.json',
              help='''Where results will be dumped.\
                    Default is \'results.json\'.''')
@click.argument('fields', nargs=-1, metavar='<fields>')
def main(channel, max_results, output_file, fields):
    """
    Obtain video details for YouTube channels.
    Version 0.1.0.

    Example:

        ytdata -c UCupvZG-5ko_eiXAupbDfxWw -n 250 videoId title description
    """
    channel_data = YTData(channel, max_results, fields, verbose=True)
    channel_data.fetch()
    channel_data.dump(output_file)
