"""Get MPs from the Senate website."""

import pandas as pd
import re
from requests_html import HTMLSession

session = HTMLSession()

# Read the existing database
mps = pd.read_csv('data/mps.csv')

# Get the data
for constituency_id in range(1, 82):
  print(constituency_id)
  # get the constituency page
  url = f'https://www.senat.cz/senat/volby/hledani/o_obvodu.php?kod={constituency_id}'
  r = session.get(url)

  # extract links to MPs
  ass = r.html.find('a')  
  selected = []
  for a in ass:
    if re.search('par_3=', a.attrs['href']):
      selected.append(a.attrs['href'])
  selected = selected[1:] # remove duplicate
  
  # read MPs
  for link in selected:
    try:
      url1 = 'https://senat.cz' + link
      r1 = session.get(url1)
      
      match = re.search(r'par_3=([0-9]+)', url1)
      mp_id = int(match.group(1))
      
      title = r1.html.find('title', first=True).text.replace('\xa0', ' ')
      special_titles = ['MBA', 'MPA', 'MUDr']
      for st in special_titles:
        title = title.replace(st, '')
      name = re.sub(r'\w*\.\w*', '', title.split(':')[0]).replace(',', '').strip().replace('  ', ' ')

      
      table = r1.html.find('table.basicInfo', first=True)
      trs = table.find('tr')
      
      tds = trs[2].find('td')
      party = tds[1].text.replace('\xa0', ' ').split('v roce')[0].strip()

      tds = trs[3].find('td')
      sarr = tds[1].text.split('-')[0].strip().split('.')
      since = f'{sarr[2]}-{sarr[1]}-{sarr[0]}'
      uarr = tds[1].text.split('-')[1].strip().split('.')
      until = f'{uarr[2]}-{uarr[1]}-{uarr[0]}'

      item = {
        'mp_id': mp_id,
        'name': name,
        'constituency_id': constituency_id,
        'party': party,
        'since': since,
        'until': until,
        'photo': r1.html.find('img')[1].attrs['src'],
        'link': url1,
      }
      mps = pd.concat([mps, pd.DataFrame([item])], ignore_index=True)
    except:
      print(f'Error: {url1}')

mps.to_csv('data/mps.csv', index=False)