from wikidataintegrator import wdi_core
import pywikibot
import pickle
import collections
from lxml import html
import requests
import urllib.request, json
LANG = 'en'
def url_formatter(pid, value):

 	urls = pickle.load(open("wikidp/caches/url-formats", "rb"))
 	value = value.strip()
 	if pid in urls: base = urls[pid]
 	else: 
 		try:
 			url = urllib.request.urlopen("https://www.wikidata.org/wiki/Special:EntityData/%s.json"%(pid))
 			base = json.loads(url.read().decode())['entities'][pid]['claims']['P1630'][0]['mainsnak']['datavalue']['value'] 
 			caching_label(pid, base,"url-formats" )
 		except: return "Error: Could not find url format."
 	base = base.replace("$1", value)
 	# print(base)
 	return base
def caching_label(id, label, fileName):
	url = "wikidp/caches/"+fileName
	props = pickle.load(open(url, "rb"))
	props[id] = label
	pickle.dump( props, open( url, "wb" ) )
	# out = pickle.load(open("wikidp/caches/property-labels", "rb"))
	# print ("succesfully cached: ", label, '\n->', out)

def prop_label(pid):
	props = pickle.load(open("wikidp/caches/property-labels", "rb"))
	if pid in props: return props[pid]
	else: 
		try:
			page = requests.get("http://wikidata.org/wiki/Property:"+pid)
			title = html.fromstring(page.content).xpath('//title/text()')
			title = title[0][:-10].title()
			caching_label(pid, title, "props-labels")
			return title
		except: return "Unknown Property Label"
def qid_label(qid):
	labels = pickle.load(open("wikidp/caches/item-labels", "rb"))
	if qid in labels: return labels[qid]
	else:
		try:
			item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata').data_repository(), qid)
			item.get()
			label = item.labels[LANG]
			caching_label(qid, label, "item-labels")
			return label
		except:
			try:
				page = requests.get("http://wikidata.org/wiki/"+qid)
				title = html.fromstring(page.content).xpath('//title/text()')
				title = title[0][:-10]
				caching_label(qid, title, "item-labels")
				return title
			except:
				return "Error Reading QID: "+qid






def search_result(string):
	options = wdi_core.WDItemEngine.get_wd_search_results(string)
	if options == []: return ("n/a", "Could Not Find Item"), [], {}, {}
	item, counts = item_detail_parse(options[0])
	options = [(opt, qid_label(opt)) for opt in options]
	return options[0], options, item, counts

def item_detail_parse(qid):
	item = wdi_core.WDItemEngine(wd_item_id=qid).wd_json_representation
	sub = {'claims':{}, 'refs':{}, 'sitelinks':{}, 'aliases':[], 'ex-ids':{}, 'description':[]}
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
			count += 1
		counts[(clm, label)] = count
	# print (sub['ex-ids'])
	sub['claims'] = collections.OrderedDict(sorted(sub['claims'].items()))
	sub['claims'] = collections.OrderedDict(sorted(sub['claims'].items(), key=sorting) )
	# print (sub['description'])
	# for x in sub['description']: print(x)
	return sub, counts


def sorting(elem):

	return len(elem[0][0])
# item_detail_parse("Q7593")


	# page = requests.get("http://wikidata.org/wiki/Property:"+pid)
	# title = html.fromstring(page.content).xpath('//title/text()')
	# title = title[0][:-10]
	# print( title)
# pickle.dump({}, open("wikidp/caches/url-formats", "wb"))
