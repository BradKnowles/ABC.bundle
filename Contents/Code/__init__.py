NAME = 'ABC'
ART = 'art-default.jpg'
ICON = 'icon-default.jpg'

ALL_SHOWS = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/module/tilegroup/1389461?brand=001&device=002&start=0&size=100'
SHOW_SEASONS = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/layout?brand=001&device=002&type=show&show=%s'
SHOW_EPISODES = 'https://api.pluto.watchabc.go.com/api/ws/pluto/v1/module/tilegroup/1925878?brand=001&device=002&show=%s&season=%s&start=0&size=50'

HTTP_HEADERS = {
	'User-Agent': 'ABC/5.0.3(iPad4,4; cpu iPhone OS 9_3_4 like mac os x; en-nl) CFNetwork/758.5.3 Darwin/15.6.0',
	'appversion': '5.0.0'
}

RE_SECTION_TITLE = Regex('^season (\d+)$', Regex.IGNORECASE)

####################################################################################################
def Start():

	ObjectContainer.title1 = NAME
	HTTP.CacheTime = CACHE_1HOUR

####################################################################################################
@handler('/video/abc', NAME, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	json_obj = JSON.ObjectFromURL(ALL_SHOWS, headers=HTTP_HEADERS)

	for show in json_obj['tiles']:

		title = show['title']
		try:
			id = show['show']['id']
		except:
			id = ""
		thumb = show['images'][0]['value']

		oc.add(DirectoryObject(
			key = Callback(Season, title=title, id=id),
			title = title,
			thumb = thumb
		))

	return oc

####################################################################################################
@route('/video/abc/season')
def Season(title, id):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(SHOW_SEASONS % (id), headers=HTTP_HEADERS)

	for section in json_obj['modules']:

		if 'title' not in section:
			continue

		season = RE_SECTION_TITLE.search(section['title'])

		if season:

			oc.add(DirectoryObject(
				key = Callback(Episodes, title=title, id=id, season=season.group(1)),
				title = 'Season %s' % (season.group(1))
			))

	if len(oc) < 1:
		oc.header = "No episodes available"
		oc.message = "There aren't any episodes available for this show"

	return oc

####################################################################################################
@route('/video/abc/episodes')
def Episodes(title, id, season):

	oc = ObjectContainer(title2=title)
	json_obj = JSON.ObjectFromURL(SHOW_EPISODES % (id, season), headers=HTTP_HEADERS)

	for episode in json_obj['tiles']:

		oc.add(EpisodeObject(
			url = 'abc://%s' % (episode['video']['id']),
			show = episode['video']['show']['title'],
			title = episode['video']['title'],
			summary = episode['video']['longdescription'],
			duration = episode['video']['duration'],
			content_rating = episode['video']['tvrating'],
			originally_available_at = Datetime.ParseDate(episode['video']['airtime']).date(),
			season = int(episode['video']['seasonnumber']),
			index = int(episode['video']['episodenumber']),
			thumb = episode['images'][0]['value']
		))

	return oc
