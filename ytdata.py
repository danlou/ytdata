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
    raise SystemExit('Requires environment variable for your Google API key.\n'
                     'Add \'export GOOGLE_API_KEY="<key>"\' to ~/.bashrc.')

# TODO: describe what PARTS is
PARTS = {}
PARTS['snippet'] = set()
PARTS['snippet'].add('channelId')
PARTS['snippet'].add('channelTitle')
PARTS['snippet'].add('title')
PARTS['snippet'].add('description')
PARTS['snippet'].add('position')
PARTS['snippet'].add('playlistId')
PARTS['snippet'].add('publishedAt')
PARTS['snippet'].add('resourceId')
PARTS['snippet'].add('videoId')
PARTS['snippet'].add('thumbnails')

PARTS['statistics'] = set()
PARTS['statistics'].add('commentCount')
PARTS['statistics'].add('dislikeCount')
PARTS['statistics'].add('favoriteCount')
PARTS['statistics'].add('likeCount')
PARTS['statistics'].add('viewCount')

PARTS['status'] = set()
PARTS['status'].add('embeddable')
PARTS['status'].add('license')
PARTS['status'].add('privacyStatus')
PARTS['status'].add('publicStatsViewable')
PARTS['status'].add('uploadStatus')

PARTS['contentDetails'] = set()
PARTS['contentDetails'].add('caption')
PARTS['contentDetails'].add('definition')
PARTS['contentDetails'].add('dimension')
PARTS['contentDetails'].add('duration')
PARTS['contentDetails'].add('licensedContent')
PARTS['contentDetails'].add('projection')


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


class YTData():
    """
    # TODO
    """
    def __init__(self, channel_id, max_results=1000, verbose=True,
                 fields=['title', 'videoId']):

        self.channel_id = channel_id
        self.verbose = verbose
        self.fields = set(fields)

        self.items = OrderedDict()

        self.upload_playlist_id = self.get_upload_playlist_id()

        snippet_fields = filter_fields('snippet', self.fields)
        self.get_snippets(snippet_fields, max_results)

        for part in [part for part in PARTS if part is not 'snippet']:

            relevant_fields = filter_fields(part, self.fields)
            if len(relevant_fields) > 0:
                self.add_part(part, relevant_fields)

    def get_upload_playlist_id(self):
        """
        # TODO
        """
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
            raise SystemExit('Failed to retrieve upload playlist id.')

    def get_snippets(self, snippet_fields, max_results):
        """
        # TODO
        """
        def get_paginated(page_token=None):
            """
            # TODO
            """
            params = {'key': API_KEY,
                      'part': 'snippet',
                      'playlistId': self.upload_playlist_id,
                      'maxResults': min(50, max_results-len(self.items))}

            if page_token is not None:
                params['pageToken'] = page_token

            req = requests.get(API_URL+'/playlistItems', params)

            if req.status_code == 200:
                response = req.json()
                list(map(process_item, response['items']))

                # return if we've maxed out available items
                if response['pageInfo']['totalResults'] == len(self.items):
                    return len(self.items), None

                return len(self.items), response.get('nextPageToken', None)

            else:
                logging.warning(req.status_code, req.url)

        def process_item(item):
            """
            # TODO
            """
            snippet = item['snippet']
            id_ = snippet['resourceId']['videoId']

            # initialize items entry
            self.items[id_] = {}

            # add specified snippet fields
            for field in snippet_fields:
                if field is 'videoId':
                    self.items[id_][field] = id_
                else:
                    self.items[id_][field] = snippet[field]

        if not self.verbose:

            n_results, page_token = 0, None
            while n_results < max_results:
                n_results, next_page_token = get_paginated(page_token)
                if next_page_token is None:
                    break
                else:
                    page_token = next_page_token

        else:
            # same as above with clint output
            puts('Request snippet for: %s' % ', '.join(snippet_fields))

            with progress.Bar(expected_size=max_results) as bar:

                n_results, page_token = 0, None
                while n_results < max_results:
                    n_results, next_page_token = get_paginated(page_token)
                    if next_page_token is None:
                        break
                    else:
                        page_token = next_page_token

                    bar.show(n_results)
            puts()

    def add_part(self, part, relevant_fields, batch_size=32):
        """
        # TODO
        """
        def request_batch(ids):
            """
            # TODO
            """
        def _request_batch(ids):
            params = {'key': API_KEY,
                      'part': part,
                      'id': ','.join(ids)}

            req = requests.get(API_URL+'/videos', params)

            if req.status_code == 200:
                list(map(process_item, req.json()['items']))

            else:
                logging.warning(req.status_code, req.url)

        def process_item(item):
            """
            # TODO
            """
            id_ = item['id']
            for field in relevant_fields:
                self.items[id_][field] = item[part][field]

        video_ids, n_videos = list(self.items.keys()), len(self.items)
        batches = chunks(video_ids, batch_size)

        if not self.verbose:
            # adds specified part fields to batches of items
            list(map(request_batch, batches))

        else:
            # same as above with clint output
            puts('Request %s for: %s' % (part, ', '.join(relevant_fields)))

            with progress.Bar(expected_size=n_videos) as bar:
                for i, batch in enumerate(batches):
                    request_batch(batch)
                    bar.show(min((i+1)*batch_size, n_videos))
            puts()

    def dump(self, output_filepath='ytdata.json'):
        """Performs a pretty-printed JSON dump with the available items.
        """
        if self.verbose:
            puts('Dumping JSON into \'%s\'' % output_filepath)

        with open(output_filepath, 'w') as file_:
            json.dump({'items': list(self._items.values())}, file_,
                      separators=(',', ': '),
                      sort_keys=True,
                      indent=4)


if __name__ == '__main__':

    YTData('UCupvZG-5ko_eiXAupbDfxWw',  # CNN's YouTube channel
           fields=['videoId', 'title', 'description',
                   'viewCount', 'duration', 'publishedAt'],
           max_results=127,
           output='cnn.json',
           verbose=True)
