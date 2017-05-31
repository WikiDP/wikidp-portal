from wikidataintegrator import wdi_core
import pywikibot
import pickle
import collections
from lxml import html
import wikidp.lists as LIST
import requests
import urllib.request, json
LANG = 'en'
urlCache, pidCache, qidCache = None, None, None

def load_caches():
	global urlCache, pidCache, qidCache
	urlCache = pickle.load(open("wikidp/caches/url-formats", "rb"))
	pidCache = pickle.load(open("wikidp/caches/property-labels", "rb"))
	qidCache = pickle.load(open("wikidp/caches/item-labels", "rb"))
def save_caches():
	global urlCache, pidCache, qidCache
	pickle.dump( urlCache, open( "wikidp/caches/url-formats", "wb" ) )
	pickle.dump( pidCache, open( "wikidp/caches/property-labels", "wb" ) )
	pickle.dump( qidCache, open( "wikidp/caches/item-labels", "wb" ) )

def url_formatter(pid, value):
 	global urlCache
 	value = value.strip()
 	if pid in urlCache: base = urlCache[pid]
 	else: 
 		print("url try again")
 		try:
 			url = urllib.request.urlopen("https://www.wikidata.org/wiki/Special:EntityData/%s.json"%(pid))
 			base = json.loads(url.read().decode())['entities'][pid]['claims']['P1630'][0]['mainsnak']['datavalue']['value'] 
 			urlCache[pid] = base
 		except: return "Error: Could not find url format."
 	base = base.replace("$1", value)
 	return base

def caching_label(id, label, fileName):
	url = "wikidp/caches/"+fileName
	props = pickle.load(open(url, "rb"))
	props[id] = label
	pickle.dump( props, open( url, "wb" ) )
	# out = pickle.load(open("wikidp/caches/property-labels", "rb"))
	# print ("succesfully cached: ", label, '\n->', out)

def prop_label(pid):
	global pidCache 
	if pid in pidCache: return pidCache[pid]
	else: 
		try:
			page = requests.get("http://wikidata.org/wiki/Property:"+pid)
			title = html.fromstring(page.content).xpath('//title/text()')
			title = title[0][:-10].title()
			pidCache[pid] = title
			return title
		except: return "Unknown Property Label"
def image_url(title):
	try:
		
		url = urllib.request.urlopen("https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:%s&format=json"%(title.replace(" ", "_")))
		base = json.loads(url.read().decode())["query"]["pages"]
		for x in base:
			out = base[x]["imageinfo"][0]["url"]
		return out
	except: return "Error reading image url:"+title

# image_url("Debian-8-desktop-background.png")
def qid_label(qid):
	global qidCache 
	if qid in qidCache: return qidCache[qid]
	else:
		try:
			item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata').data_repository(), qid)
			item.get()
			label = item.labels[LANG]
			print ("pid try again")
			qidCache[qid] = label
			
			return label
		except:
			try:
				page = requests.get("http://wikidata.org/wiki/"+qid)
				title = html.fromstring(page.content).xpath('//title/text()')
				title = title[0][:-10]
				print ("pid try again")
				qidCache[qid] = title
				return title
			except:
				return "Error Reading QID: "+qid






def search_result(string):
	options = wdi_core.WDItemEngine.get_wd_search_results(string)
	if options == []: return ("n/a", "Could Not Find Item"), [], {}, {}
	item, counts = item_detail_parse(options[0])
	options = [(opt, qid_label(opt), item_detail_parse(opt)) for opt in options]
	return options[0], options, item, counts

def item_detail_parse(qid):
	# print (qid, " "),
	try:
		item = wdi_core.WDItemEngine(wd_item_id=qid)
	except:
		print ("Error reading: ", qid)
		return None, None
	load_caches()
	lab = item.get_label()
	# print (lab)
	item = item.wd_json_representation
	
	sub = {'label': [qid, lab], 'claims':{}, 'refs':{}, 'sitelinks':{}, 'aliases':[], 'ex-ids':{}, 'description':[], 'categories':[], 'properties':[]}

	counts = {}
	# print (item['claims'], '\n\n')
	try:
		sub['aliases'] = [x['value'] for x in item['aliases'][LANG]]
	except: pass
	try:
		sub['description'] = item['descriptions'][LANG]['value']
	except: pass
	for clm in item['claims']:
		
		count = 0
		label = prop_label(clm)
		for det in item['claims'][clm]:
			# print (det['mainsnak'])
			# print (det['references'] , '\n')
			ref = []
			refNum = 0
			pattern = ' '
			if det['references'] != []:
				
				refNum = len(det['references'][0]['snaks-order'])
				order = det['references'][0]['snaks-order']
				for snak in order:
					pid = det['references'][0]['snaks'][snak][0]['property']
					ref += [(pid, prop_label(pid),det['references'][0]['snaks'][snak][0]['datavalue']['value'] )]
				# print (det['references'][0]['snaks-order'] , ref, '\n\n')
			val = ["error at the "]
			size = 1 
			

			if det['mainsnak']['datavalue']['type'] == 'string':
				val = det['mainsnak']['datavalue']['value']
			elif det['mainsnak']['datavalue']['type'] == 'wikibase-entityid':
				if det['mainsnak']['datavalue']['value']['entity-type'] == 'item':
					val = det['mainsnak']['datavalue']['value']['id']
					val = [val, qid_label(val)]
					size = 2
				elif det['mainsnak']['datavalue']['value']['entity-type'] == 'property':
					val = 'P'+str(det['mainsnak']['datavalue']['value']['numeric-id'])
					val = [val, prop_label(val)]
					size = 2
				else: val = [val[0]+"entity-type level"]
			elif det['mainsnak']['datavalue']['type'] == 'time':
				val = [det['mainsnak']['datavalue']['value']['time']]
			else: 
				val = [val[0] + "type level " + det['mainsnak']['datavalue']['type']]
				# print (det['mainsnak']['datavalue'])
			try: 
				if det['mainsnak']['datatype'] == 'external-id':
					sub['ex-ids'][(clm, label, val, url_formatter(clm, val))] += [val]
				else:
					sub['claims'][(clm, label,  size)] += [val]
				if refNum > 0:
					sub['refs'][(clm, val[0])] = ref
			except:
				if det['mainsnak']['datatype'] == 'external-id':
					# print(det)
					sub['ex-ids'][(clm, label, val, url_formatter(clm, val))] = [val]
				else:
					sub['claims'][(clm, label, size)] = [val]
				if refNum > 0:
					sub['refs'][(clm, val[0])] = ref
			if clm in ['P31', 'P279']: sub['categories']+= [val]
			if clm == "P18": 
				titles = sub["claims"][(clm, label, size)]
				num = len(titles)
				x = 0
				while x < num:
					titles[x] = image_url(titles[x])
					x += 1
				sub["claims"][(clm, label, size)] = titles
				# print(sub["claims"][(clm, label, size)])
			count += 1
		counts[clm] = count
	
	# print (sub['ex-ids'])
	sub['claims'] = collections.OrderedDict(sorted(sub['claims'].items()))
	sub['claims'] = collections.OrderedDict(sorted(sub['claims'].items(), key=dict_sorting_by_length) )
	sub['categories'] = sorted(sorted(sub['categories']), key=list_sorting_by_length)
	propList = LIST.Properties()
	
	for prop in propList:
		instance = [[prop, prop_label(prop)]]
		try:
			instance[0] += [counts[prop]]
		except:
			instance[0] += [0]
		# print(instance)
		sub['properties'] += instance
	# print (sub['properties'])
	# for x in sub['description']: print(x)
	save_caches()
	return sub, counts

def list_sorting_by_length(elem):
	return len(elem[0])

def dict_sorting_by_length(elem):
	return len(elem[0][0])
# search_result("Debian")

# item_detail_parse("Q7593")
# ('P31', 'Instance of', 2)
# ('P279', 'Subclass of', 2)

	# page = requests.get("http://wikidata.org/wiki/Property:"+pid)
	# title = html.fromstring(page.content).xpath('//title/text()')
	# title = title[0][:-10]
	# print( title)
# pickle.dump({}, open("wikidp/caches/url-formats", "wb"))
