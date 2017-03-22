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

# store
cnn_data.dump('cnn.json')
```

### Setup and CLI Demonstration

[<img src="https://i.ytimg.com/vi/RAT3J-tBb10/maxresdefault.jpg">](https://www.youtube.com/watch?v=RAT3J-tBb10)
[YouTube link](https://www.youtube.com/watch?v=RAT3J-tBb10)

### Installation notes

ytdata is available as a pip package and can be installed with:
```sh
$ pip install ytdata
```

It expects a valid Google API Key stored in an environment variable called GOOGLE_API_KEY.
If you don't already have one, you can follow these instructions (you'll want a server key):
https://developers.google.com/youtube/registering_an_application#Create_API_Keys

After you get your key, you can add the environment variable by opening your ~/.bashrc (or ~/.zshrc, if you're on zsh) on your editor of choice and append the following line:
```sh
export GOOGLE_API_KEY="<Your_Private_Key>"
```

### How to find the channel id ?

The simplest way to find the channel id is to visit the YouTube page for a video belonging to the channel of interest and extract the id from the page's meta tags. Just open the console on your browser and enter:

```js
console.log(document.querySelector('meta[itemprop="channelId"]')['content']);
```

### Fields

You can request several fields to be returned with each video result. Here are the fields currently supported.

| FIELD | EXAMPLE |
| ------ | ------ |
| channelId | "UCAuUUnT6oDeKwE6v1NGQxug" |
| channelTitle | "TED" |
| title | "I grew up in the Westboro Baptist Church. Here's why I left | Megan Phelps-Roper" |
| description | "What's it like to grow up within a group of people who exult in demonizing ..." |
| position | 0 |
| publishedAt | "2017-03-06T17:10:02.000Z" |
| videoId | "bVV2Zk88beY" |
| viewCount | "871757" |
| favoriteCount | "0" |
| commentCount | TODO |
| likeCount | "2408" |
| dislikeCount | "229" |
| embeddable | true |
| license | "youtube" |
| privacyStatus | "public" |
| uploadStatus | "processed" |
| publicStatsViewable | true |
| caption | "false" |
| definition | "hd" |
| dimension | "2d" |
| duration | "PT15M18S" |
| licensedContent | true |
| projection | "rectangular" |
