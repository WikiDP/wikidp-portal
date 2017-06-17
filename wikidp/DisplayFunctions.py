from wikidataintegrator import wdi_core
import pywikibot
import pickle
import collections
from lxml import html
import wikidp.lists as LIST
import requests
import urllib.request, json

# Global Variables:
LANG = 'en'
urlCache, pidCache, qidCache = None, None, None


def search_result(string):
	"""Uses wikidataintegrator to generate a list of similar items based on a text search and returns a list of dictionaries containing details about each item"""
	options = wdi_core.WDItemEngine.get_wd_search_results(string)
	if options == []: 
		return ("n/a", "Could Not Find Item"), [], {}, {}
	else:
		options = [(opt, qid_label(opt), item_detail_parse(opt)) for opt in options]
	return options[0], options, None, None

def item_detail_parse(qid):
	"""Uses the JSON representaion of wikidataintegrator to parse the item ID specified (qid) and returns a new dictionary of previewing information and a dictionary of property counts"""
	try:
		item = wdi_core.WDItemEngine(wd_item_id=qid)
	except:
		print ("Error reading: ", qid)
		return None, None
	load_caches()
	global qidCache
	label = item.get_label()
	qidCache[qid] = label
	item = item.wd_json_representation
	outputDict = {'label': [qid, label], 'claims':{}, 'refs':{}, 'sitelinks':{}, 'aliases':[], 'ex-ids':{}, 'description':[], 'categories':[], 'properties':[]}
	countDict = {}
	try:
		outputDict['aliases'] = [x['value'] for x in item['aliases'][LANG]]
	except: 
		pass
	try:
		outputDict['description'] = item['descriptions'][LANG]['value']
	except: 
		pass
	for claim in item['claims']:
		count = 0
		label = pid_label(claim)
		for jsonDetails in item['claims'][claim]:
			reference = []
			refNum = 0
			pattern = ' '
			if jsonDetails['references'] != []:
				refNum = len(jsonDetails['references'][0]['snaks-order'])
				order = jsonDetails['references'][0]['snaks-order']
				for snak in order:
					pid = jsonDetails['references'][0]['snaks'][snak][0]['property']
					reference += [(pid, pid_label(pid),jsonDetails['references'][0]['snaks'][snak][0]['datavalue']['value'] )]
			val = ["error at the "]
			size = 1 
			if 'datavalue' not in jsonDetails['mainsnak']:
				# print ("~~skipping~~~\n", qid,'\n', jsonDetails, '\n~~~~~~~~~~~~~~~')
				pass
			elif jsonDetails['mainsnak']['datavalue']['type'] == 'string':
				val = jsonDetails['mainsnak']['datavalue']['value']
			elif jsonDetails['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
				if jsonDetails['mainsnak']['datavalue']['value']['entity-type'] == 'item':
					val = jsonDetails['mainsnak']['datavalue']['value']['id']
					val = [val, qid_label(val)]
					size = 2
				elif jsonDetails['mainsnak']['datavalue']['value']['entity-type'] == 'property':
					val = 'P'+str(jsonDetails['mainsnak']['datavalue']['value']['numeric-id'])
					val = [val, pid_label(val)]
					size = 2
				else: val = [val[0]+"entity-type level"]
			elif jsonDetails['mainsnak']['datavalue']['type'] == 'time':
				val = [jsonDetails['mainsnak']['datavalue']['value']['time']]
			else: 
				val = [val[0] + "type level " + jsonDetails['mainsnak']['datavalue']['type']]
			try: 
				if jsonDetails['mainsnak']['datatype'] == 'external-id':
					outputDict['ex-ids'][(claim, label, val, url_formatter(claim, val))] += [val]
				else:
					outputDict['claims'][(claim, label,  size)] += [val]
				if refNum > 0:
					outputDict['refs'][(claim, val[0])] = reference
			except:
				if jsonDetails['mainsnak']['datatype'] == 'external-id':
					# print(jsonDetails)
					outputDict['ex-ids'][(claim, label, val, url_formatter(claim, val))] = [val]
				else:
					outputDict['claims'][(claim, label, size)] = [val]
				if refNum > 0:
					outputDict['refs'][(claim, val[0])] = reference
			if claim in ['P31', 'P279']: outputDict['categories']+= [val]
			if claim in ["P18", "P154"]: 
				original = jsonDetails['mainsnak']['datavalue']['value']
				outputDict["claims"][(claim, label, size)] += [image_url(original)]
				outputDict["claims"][(claim, label, size)].remove(original)
			count += 1
		countDict[claim] = count
	outputDict['claims'] = collections.OrderedDict(sorted(outputDict['claims'].items()))
	outputDict['claims'] = collections.OrderedDict(sorted(outputDict['claims'].items(), key=dict_sorting_by_length) )
	outputDict['categories'] = sorted(sorted(outputDict['categories']), key=list_sorting_by_length)
	propList = LIST.Properties()
	for prop in propList:
		instance = [[prop, pid_label(prop)]]
		try:
			instance[0] += [countDict[prop]]
		except:
			instance[0] += [0]
		outputDict['properties'] += instance
	save_caches()
	return outputDict, countDict

def load_caches():
	"""Uses pickle to load all caching files as global variables"""
	global urlCache, pidCache, qidCache
	urlCache = pickle.load(open("wikidp/caches/url-formats", "rb"))
	pidCache = pickle.load(open("wikidp/caches/property-labels", "rb"))
	qidCache = pickle.load(open("wikidp/caches/item-labels", "rb"))

def save_caches():
	"""Uses pickle to save global variables to caching files in order to update"""
	global urlCache, pidCache, qidCache
	pickle.dump( urlCache, open( "wikidp/caches/url-formats", "wb" ) )
	pickle.dump( pidCache, open( "wikidp/caches/property-labels", "wb" ) )
	pickle.dump( qidCache, open( "wikidp/caches/item-labels", "wb" ) )

def qid_label(qid):
	"""Converts item identifier (Q###) to a label and updates the cache"""
	## TO DO: Add step to try using wikidataintegrator as second option
	global qidCache 
	try:
		return qidCache[qid]
	except:
		try:
			item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata').data_repository(), qid)
			item.get()
			label = item.labels[LANG]
			qidCache[qid] = label
			# print("[1] Adding qid to cache {",qid,"}: ", label)
			pickle.dump( qidCache, open( "wikidp/caches/item-labels", "wb" ) )
			# print ('---confirmed->' ,qidCache[qid])
			return label
		except:
			try:
				page = requests.get("http://wikidata.org/wiki/"+qid)
				title = html.fromstring(page.content).xpath('//title/text()')
				title = title[0][:-10]
				qidCache[qid] = title
				# print("[2] Adding qid to cache {",qid,"}: ", label)
				return title
			except:
				print ("Error finding QID label: "+qid)
				return "Unknown Item Label"

def pid_label(pid):
	"""Converts property identifier (P###) to a label and updates the cache"""
	global pidCache 
	try: 
		return pidCache[pid]
	except: 
		try:
			page = requests.get("http://wikidata.org/wiki/Property:"+pid)
			title = html.fromstring(page.content).xpath('//title/text()')
			title = title[0][:-10].title()
			pidCache[pid] = title
			return title
		except:
			print ("Error finding property label: ",pid) 
			return "Unknown Property Label"

def url_formatter(pid, value):
	"""Inputs property identifier (P###) for a given url type, lookes up that pid's url format (P1630) and creates a url with the value using the format"""
	global urlCache
	value = value.strip()
	if pid in urlCache: base = urlCache[pid]
	else:
		try:
			url = urllib.request.urlopen("https://www.wikidata.org/wiki/Special:EntityData/%s.json"%(pid))
			base = json.loads(url.read().decode())['entities'][pid]['claims']['P1630'][0]['mainsnak']['datavalue']['value'] 
			urlCache[pid] = base
 			# print("Adding url format to cache {",pid,"}: ", base)
		except:
 			# print ("Error: Could not find url format. ->", pid, value) 
 			return "unavailable"
	base = base.replace("$1", value)
	return base

def image_url(title):
	"""Converts the title of an image to the url location of that file it describes"""
	# TO DO: Url's do not work with non-ascii characters
	#    For example, the title of the image for Q267193 [Submlime Text] is "Скриншот sublime text 2.png"
	try:
		url = urllib.request.urlopen("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:%s&format=json"%(title.replace(" ", "_")))
		base = json.loads(url.read().decode())["query"]["pages"]
		for x in base:
			out = base[x]["imageinfo"][0]["url"]
		return out
	except:
		# print("Error reading image url: "+title)
		return "Error reading image url: "+title

def list_sorting_by_length(elem):
	"""Auxiliary sorting key function at the list level"""
	return len(elem[0])

def dict_sorting_by_length(elem):
	"""Auxiliary sorting key function at the dictionary level"""
	return len(elem[0][0])

def caching_label(id, label, fileName):
	"""Auxiliary function to cache information {not currently called by any function}"""
	url = "wikidp/caches/"+fileName
	props = pickle.load(open(url, "rb"))
	props[id] = label
	pickle.dump( props, open( url, "wb" ) )
	# out = pickle.load(open("wikidp/caches/property-labels", "rb"))
	# print ("succesfully cached: ", label, '\n->', out)

load_caches()

# Testing function calls/data structure references:
# -------------------------------------------------
# search_result("Debian")
# item_detail_parse("Q7593")
# item_detail_parse("Q131346")
# ('P31', 'Instance of', 2)
# ('P279', 'Subclass of', 2)




