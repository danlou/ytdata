# ytdata - Obtain video details for YouTube channels

ytdata is a minimalistic Python3 library that allows you to simply specify the channel and video fields that matter to you and let it make the right calls to YouTube's Data API (v3) to obtain that data.

### Why?

YouTube can be an amazing source of data, but it's API isn't the most straightforward. In many cases, you'll need to perform several requests to get a few details on a single video. 

There's no endpoint to simply get all the videos for a given channel and let you specify which fields you want for the videos. That's where ytdata comes in.

### Python Example

```python
from ytdata import YTData

cnn_data = YTData(channel_id='UCupvZG-5ko_eiXAupbDfxWw',  # CNN's YouTube channel
                  fields=['videoId', 'title', 'description',
                          'viewCount', 'duration', 'publishedAt'],
                  max_results=250,
                  verbose=False)
cnn_data.fetch()

# peek, nothing's nested
print('Most recent videos:')
for i, item in enumerate(cnn_data.items[:10]):
    print('  %d. %s' % (i+1, item['title']))
print()

# store
cnn_data.dump('cnn.json')
```

### CLI Example

TODO

### Setup

ytdata expects a valid Google API Key stored in an environment variable called GOOGLE_API_KEY.
If you don't already have one, you can follow these instructions (you'll want a server key):
https://developers.google.com/youtube/registering_an_application#Create_API_Keys

After you get your key, you can add the environment variable by opening your ~/.bashrc (or ~/.zshrc, if you're on zsh) on your editor of choice and append the following line:
```sh
export GOOGLE_API_KEY="<Your_Private_Key>"
```

Then, install dependencies with:
```sh
$ pip install -r requirements.txt
```

### Fields

You can request several fields to be returned with each video result. Here are the fields currently supported.

| FIELD | EXAMPLE |
| ------ | ------ |
| channelId | TODO |
| channelTitle | TODO |
| title | TODO |
| description | TODO |
| position | TODO |
| playlistId | TODO |
| publishedAt | TODO |
| resourceId | TODO |
| videoId | TODO |
| thumbnails | TODO |
| commentCount | TODO |
| dislikeCount | TODO |
| favoriteCount | TODO |
| likeCount | TODO |
| viewCount | TODO |
| embeddable | TODO |
| license | TODO |
| privacyStatus | TODO |
| uploadStatus | TODO |
| publicStatsViewable | TODO |
| caption | TODO |
| definition | TODO |
| dimension | TODO |
| duration | TODO |
| licensedContent | TODO |
| projection | TODO |
