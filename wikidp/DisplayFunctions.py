from wikidataintegrator import wdi_core
import pywikibot
import pickle
from collections import OrderedDict
from lxml import html
import wikidp.lists as LIST
import requests
import urllib.request, json

# Global Variables:
LANG = 'en'
urlCache, pidCache, qidCache = None, None, None


def search_result(string):
	"""Uses wikidataintegrator to generate a list of similar items based on a text search
	and returns a list of dictionaries containing details about each item"""
	options = wdi_core.WDItemEngine.get_wd_search_results(string)
	if options == []: 
		return ("n/a", "Could Not Find Item"), [], {}, {}
	else:
		options = [(opt, qid_label(opt), item_detail_parse(opt)) for opt in options]
	return options[0], options, None, None

def item_detail_parse(qid):
	"""Uses the JSON representaion of wikidataintegrator to parse the item ID specified (qid)
	and returns a new dictionary of previewing information and a dictionary of property counts"""
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
	outputDict = {'label': [qid, label], 'claims':{}, 'refs':{},
	'sitelinks':{}, 'aliases':[], 'ex-ids':{}, 'description':[], 
	'categories':[], 'properties':[]}
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
			count = parse_claims(claim, label, jsonDetails, count, outputDict)
		countDict[claim] = count
	outputDict['claims'] = OrderedDict(sorted(outputDict['claims'].items()))
	outputDict['claims'] = OrderedDict(sorted(outputDict['claims'].items(), key=dict_sorting_by_length) )
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

def parse_claims(claim, label, jsonDetails, count, outputDict):
	"""Uses the jsonDetails dictionary of a single claim and outputs the parsed data into the outputDict"""
	#Parsing references
	reference = []
	refNum = 0
	if jsonDetails['references'] != []:
		refList = jsonDetails['references'][0]
		for snak in refList['snaks-order']:
			pid = refList['snaks'][snak][0]['property']
			reference += [(pid, pid_label(pid), refList['snaks'][snak][0]['datavalue']['value'] )]
			refNum += 1
	
	val = ["error at the "]
	size = 1 
	#Parsing the statements & values by data taype
	if 'datavalue' in jsonDetails['mainsnak']:
		dataType = jsonDetails['mainsnak']['datavalue']['type']
		dataValue = jsonDetails['mainsnak']['datavalue']['value']
		if dataType == 'string':
			val = dataValue
		elif dataType == 'wikibase-entityid':
			if dataValue['entity-type'] == 'item':
				val = dataValue['id']
				val = [val, qid_label(val)]
				size = 2
			elif dataValue['entity-type'] == 'property':
				val = 'P'+str(dataValue['numeric-id'])
				val = [val, pid_label(val)]
				size = 2
			else: val = [val[0]+"entity-type level"]				
		elif dataType == 'time':
			val = [dataValue['time']]
		else: 
			val = [val[0] + "type level " + dataType]
	try: 
		dataType = jsonDetails['mainsnak']['datatype']
		if dataType == 'external-id':
			outputDict['ex-ids'][(claim, label, val, url_formatter(claim, val))] += [val]
		else:
			outputDict['claims'][(claim, label,  size)] += [val]
		if refNum > 0:
			outputDict['refs'][(claim, val[0])] = reference
	except:
		if dataType == 'external-id':
			# print(jsonDetails)
			outputDict['ex-ids'][(claim, label, val, url_formatter(claim, val))] = [val]
		else:
			outputDict['claims'][(claim, label, size)] = [val]
		if refNum > 0:
			outputDict['refs'][(claim, val[0])] = reference
	#Determining the 'category' of the item from the 'instance of' and 'subclass of' properties
	if claim in ['P31', 'P279']: 
		outputDict['categories']+= [val]
	#In the event the value is a image file, it converts the title to the image's url
	elif claim in ["P18", "P154"]: 
		original = jsonDetails['mainsnak']['datavalue']['value']
		outputDict["claims"][(claim, label, size)] += [image_url(original)]
		outputDict["claims"][(claim, label, size)].remove(original)
	count += 1
	return count

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
	"""Inputs property identifier (P###) for a given url type, lookes up that 
	pid's url format (P1630) and creates a url with the value using the format"""
	global urlCache
	value = value.strip()
	if pid in urlCache: base = urlCache[pid]
	else:
		try:
			url = urllib.request.urlopen("https://www.wikidata.org/wiki/Special:EntityData/%s.json"%(pid))
			base = json.loads(url.read().decode()) 
			urlCache[pid] = base['entities'][pid]['claims']['P1630'][0]['mainsnak']['datavalue']['value']
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
	title = title.replace(" ", "_")
	url = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:%s&format=json"%(title)
	try:
		url = urllib.request.urlopen(url)
		base = json.loads(url.read().decode())["query"]["pages"]
		for x in base:
			out = base[x]["imageinfo"][0]["url"]
		return out
	except:
		# print("Error reading image url: "+title)
		return "https://commons.wikimedia.org/wiki/File:"+title

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
	# print ("succesfully cached: ", label, '\n->', out)

load_caches()

# Testing function calls/data structure references:
# -------------------------------------------------
# search_result("Debian")
# item_detail_parse("Q7593")
# item_detail_parse("Q131346")
# ('P31', 'Instance of', 2)
# ('P279', 'Subclass of', 2)




