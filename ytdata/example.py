from ytdata import YTData

# instantiate
cnn_data = YTData('UCupvZG-5ko_eiXAupbDfxWw',  # CNN's YouTube channel
                  fields=['videoId', 'title', 'description',
                          'viewCount', 'duration', 'publishedAt'],
                  max_results=1000,
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