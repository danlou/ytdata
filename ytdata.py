import os
import json
import logging
from collections import OrderedDict

import requests
from clint.textui import puts, progress


API_URL = 'https://www.googleapis.com/youtube/v3'

try:
    API_KEY = os.environ['GOOGLE_API_KEY']
except KeyError:
    # TODO: allow API_KEY to be a class argument for YTData()
    raise SystemExit('Requires environment variable for your Google API key.\n'
                     'Add \'export GOOGLE_API_KEY="<key>"\' to ~/.bashrc.')

# This PARTS dictionary maps part names to their corresponding fields.
# It's used to set the correct 'part' parameter for requests.
#
# For more information about YouTube's API parts and fields visit:
# https://developers.google.com/youtube/v3/docs/videos
PARTS = {}

PARTS['snippet'] = {'channelId', 'channelTitle', 'title', 'description',
                    'position', 'playlistId', 'publishedAt', 'resourceId',
                    'videoId', 'thumbnails'}

PARTS['statistics'] = {'commentCount', 'dislikeCount', 'favoriteCount',
                       'likeCount', 'viewCount'}

PARTS['status'] = {'embeddable', 'license', 'privacyStatus', 'uploadStatus',
                   'publicStatsViewable'}

PARTS['contentDetails'] = {'caption', 'definition', 'dimension', 'duration',
                           'licensedContent', 'projection'}

# TODO: might still be missing relevant parts, look into this.


def filter_fields(part, fields):
    """
    Returns the intersection (set) between a given part's fields and the user
    specified fields.
    """
    return PARTS[part].intersection(fields)


def chunks(list_, size):
    """ Yield successive n-sized chunks from given list. """
    for i in range(0, len(list_), size):
        yield list_[i:i+size]


class YTData(object):
    """
    # TODO

    :param channel_id: the id for the channel to pull videos from.
    :param max_results: the maximum number of results to be retrieved.
    :param fields: the fields to be extracted for each video.
    :param verbose: output mode flag. set True for progress information.
    """
    def __init__(self, channel_id, max_results=99, fields=['title', 'videoId'],
                 verbose=True):

        self.channel_id = channel_id
        self.max_results = max_results
        self.verbose = verbose
        self.fields = set(fields)  # cast for set operations (filter_fields())

        # The self._items dict contains the data extracted for each video.
        # It's indexed by videoId for easier reference when adding part fields.
        # It's an OrderedDict() because we want to preserve the ordering from
        # the API results, which are ordered by publish date by default.
        # This data should be accessed externally using the items @property.
        self._items = OrderedDict()

        # We'll need to know the playlist id for uploaded videos to request
        # all videos for the channel.
        self.upload_playlist_id = None

    def fetch(self):
        """Performs GET requests to API and extracts relevant fields.
        Data is aggregated in the self._items dictionary, indexed by videoId.
        """
        self.upload_playlist_id = self.get_upload_playlist_id()

        # the playlist id is required to proceed, exit if None
        if self.upload_playlist_id is None:
            raise SystemExit('Failed to retrieve upload playlist id.')

        snippet_fields = filter_fields('snippet', self.fields)
        self.get_snippets(snippet_fields)

        for part in [part for part in PARTS if part is not 'snippet']:

            relevant_fields = filter_fields(part, self.fields)
            if len(relevant_fields) > 0:
                self.add_part(part, relevant_fields)

    def get_upload_playlist_id(self):
        """Returns the id for the channel's upload playlist."""
        params = {'key': API_KEY,
                  'part': 'contentDetails',
                  'id': self.channel_id}

        req = requests.get(API_URL+'/channels', params)

        if req.status_code == 200:
            response = req.json()

            details = response['items'][0]['contentDetails']
            return details['relatedPlaylists']['uploads']

        else:
            logging.critical(req.status_code, req.url)
            return None

    def get_snippets(self, snippet_fields):
        """
        Requests 'snippets' part for every channel video.
        Uses 'videos' resource with 'playlistId' set to the uploaded playlist.
        Results are paginated until items are exhausted or given max_results is
        reached. Responsible for initializing the video entries in self._items.

        :param snippet_fields: list with fields to keep for the snippets part
        """
        def _request_paginated(page_token=None):
            params = {'key': API_KEY,
                      'part': 'snippet',
                      'playlistId': self.upload_playlist_id,
                      'maxResults': min(50, self.max_results-len(self._items))}

            if page_token is not None:
                params['pageToken'] = page_token

            req = requests.get(API_URL+'/playlistItems', params)

            if req.status_code == 200:
                response = req.json()
                list(map(_select_fields, response['items']))

                # return if we've maxed out available items
                if response['pageInfo']['totalResults'] == len(self._items):
                    return len(self._items), None

                return len(self._items), response.get('nextPageToken', None)

            else:
                logging.warning(req.status_code, req.url)

        def _select_fields(item):
            snippet = item['snippet']
            id_ = snippet['resourceId']['videoId']

            # initialize items entry
            self._items[id_] = {}

            # add relevant (specified) snippet fields
            for field in snippet_fields:
                if field is 'videoId':  # videoId is nested deeper, exception
                    self._items[id_][field] = id_
                else:
                    self._items[id_][field] = snippet[field]

        if not self.verbose:
            # request results, keep paginating
            n_results, page_token = 0, None
            while n_results < self.max_results:
                n_results, next_page_token = _request_paginated(page_token)
                if next_page_token is None:
                    break
                else:
                    page_token = next_page_token

        else:
            # same as above with clint output
            puts('Request \'snippet\' for: %s' % ', '.join(snippet_fields))

            with progress.Bar(expected_size=self.max_results) as bar:

                n_results, page_token = 0, None
                while n_results < self.max_results:
                    n_results, next_page_token = _request_paginated(page_token)
                    if next_page_token is None:
                        break
                    else:
                        page_token = next_page_token

                    bar.show(n_results)
            puts()

    def add_part(self, part, relevant_fields, batch_size=32):
        """
        Requests given part for every channel video. Must belong to PARTS keys.
        Adds given fields to respective entries in self._items.
        Results are requested with batches of video ids for better efficiency.

        :param relevant_fields: list with fields to keep for the given part
        :param batch_size: size of batch ids to be sent with each request
        """
        def _request_batch(ids):
            # pre-process fields parameter, work in progress
            # fields_ = 'items(%s)' % ','.join([part+'/'+field
            #                                   for field in relevant_fields])

            params = {'key': API_KEY,
                      'part': part,
                      'id': ','.join(ids)}

            req = requests.get(API_URL+'/videos', params)

            if req.status_code == 200:
                list(map(_select_fields, req.json()['items']))

            else:
                logging.warning(req.status_code, req.url)

        def _select_fields(item):
            id_ = item['id']
            for field in relevant_fields:
                self._items[id_][field] = item[part][field]

        video_ids, n_videos = list(self._items.keys()), len(self._items)
        batches = chunks(video_ids, batch_size)

        if not self.verbose:
            # adds specified part fields to batches of items
            list(map(_request_batch, batches))

        else:
            # same as above with clint output
            puts('Request \'%s\' for: %s' % (part, ', '.join(relevant_fields)))

            with progress.Bar(expected_size=n_videos) as bar:
                for i, batch in enumerate(batches):
                    _request_batch(batch)
                    bar.show(min((i+1)*batch_size, n_videos))
            puts()

    def dump(self, output_filepath='ytdata.json'):
        """Performs a pretty-printed json.dump() with the available items.
        """
        if self.verbose:
            puts('Dumping JSON into \'%s\'' % output_filepath)

        with open(output_filepath, 'w') as file_:
            json.dump({'items': self.items}, file_,
                      separators=(',', ': '),
                      sort_keys=True,
                      indent=4)

    @property
    def items(self):
        """Returns a list of dictionaries with fields extracted for each item.
        List entries are ordered by published date.
        """
        return list(self._items.values())


def main():
    """Usage example on Python."""

    # instantiate
    cnn_data = YTData('UCupvZG-5ko_eiXAupbDfxWw',  # CNN's YouTube channel
                      fields=['videoId', 'title', 'categoryId',
                              'viewCount', 'duration', 'publishedAt'],
                      max_results=128,
                      verbose=True)

    # request and select
    cnn_data.fetch()

    # peek
    print('Most recent videos:')
    for i, item in enumerate(cnn_data.items[:10]):
        print('  %d. %s' % (i+1, item['title']))
    print()

    # store
    cnn_data.dump('cnn.json')

if __name__ == '__main__':
    # TODO: CLI support and usage example
    # TODO: Look more into API support for field filters (multi-part support?)
    #       https://developers.google.com/youtube/v3/getting-started#fields
    main()
