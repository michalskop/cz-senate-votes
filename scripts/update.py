"""Update the database with the latest data from the web."""

# import numpy as np
import pandas as pd
import re
from requests_html import HTMLSession

session = HTMLSession()

# Read the existing database
votes = pd.read_csv('data/votes.csv')
vote_events = pd.read_csv('data/vote_events.csv')
mps = pd.read_csv('data/current_mps.csv')

# Get the latest vote event number
latest_vote_event_id = vote_events['vote_event_id'].max()
latest_vote_event_id = max(0, latest_vote_event_id)

# Get the latest vote event from the web
url0 = 'https://www.senat.cz/xqw/xervlet/pssenat/hlasa?O=&S=&K=&H=&N='
r0 = session.get(url0)
table0 = r0.html.find('table', first=True)
trs0 = table0.find('tr')
tds0 = trs0[2].find('td')
href = tds0[5].find('a', first=True).attrs['href']
web_latest_vote_event_id = int(re.search(r'G=(\d+)', href).group(1))

# Get the data
url = 'https://www.senat.cz/xqw/xervlet/pssenat/hlasy?zobraz=tisk&G='

def vote2option(vote):
  """Convert the vote to a popolo standard option."""
  if vote == 'A':
    return 'yes'
  elif vote == 'N':
    return 'no'
  elif vote == 'X':
    return 'abstain'
  elif vote == '0':
    return 'absent'
  elif vote == 'T':
    return 'secret'
  else:
    return 'unknown'

def extract_votes(table, party, vote_event_id):
  """Extract the votes from the table."""
  vs = []
  for row in table.find('tr'):
    tds = row.find('td')
    for td in tds:
      tdtext = td.text.strip().replace('\xa0', ' ')
      tdarr = tdtext.split(' ')
      vote = vote2option(tdarr[0])
      name = ' '.join(tdarr[2:])
      vs.append({'name': name, 'option': vote, 'group': party, 'vote_event_id': vote_event_id})
  return vs

for vote_event_id in range(latest_vote_event_id + 1, web_latest_vote_event_id + 1):
  r = session.get(url + str(vote_event_id))
  if (r.status_code == 200) and (r.html.find('table', first=True) is not None):
    doc = r.html
    sitting_number = int(doc.find('h3')[0].text.split(',')[0].strip().split('.')[0])
    vote_event_number = int(doc.find('h3')[0].text.split(',')[1].strip().split('.')[0])
    
    datet = doc.find('h3')[0].text.split(',')[2].strip().split('.')
    date = f"{datet[2]}-{datet[1]}-{datet[0]}"

    if len(doc.find('b')[0].text.strip().split('\n')) > 1:
      name = doc.find('b')[0].text.strip().split('\n')[0]
      action = doc.find('b')[0].text.strip().split('\n')[1]
    else:
      name = doc.find('b')[0].text.strip().split('\n')[0]
      action = ''

    try:
      resulttext = doc.find('h3')[1].text.lower().strip()
      if 'návrh byl přijat' in resulttext:
        result = 'pass'
      else:
        result = 'fail'
    except:
      result = 'unknown'
    
    try:
      voted = int(doc.find('td')[0].text.split('=')[1])
      quorum = int(doc.find('td')[1].text.split('=')[1])
      yes = int(doc.find('td')[2].text.split('=')[1])
      no = int(doc.find('td')[3].text.split('=')[1])
      abstain = int(doc.find('td')[5].text.split('=')[1])
      try:
        absent = int(doc.find('td')[4].text.split('=')[1])
      except:
        absent = 0
    except:
      voted = pd.NA
      quorum = pd.NA
      yes = pd.NA
      no = pd.NA
      abstain = pd.NA
      absent = pd.NA

    item = {
      'vote_event_id': vote_event_id,
      'date': date,
      'sitting': sitting_number,
      'vote_event_number': vote_event_number,
      'name': name,
      'action': action,
      'result': result,
      'voted': voted,
      'quorum': quorum,
      'yes': yes,
      'no': no,
      'abstain': abstain,
      'absent': absent
    }

    vote_events = pd.concat([vote_events, pd.DataFrame([item])])
    vote_events.to_csv('data/vote_events.csv', index=False)

    if vote_event_id % 10 == 0:
      print(f'Vote event {vote_event_id} saved.')
    
    # Extract party-wise vote counts
    parties = doc.find('h2')

    tables = doc.find('table')
    tables = tables[1:] # first table is the overall result

    for p in parties:
      party = p.text.replace('Senátorský klub', '').strip()
      table = tables[0]
      tables = tables[1:]
      vs = extract_votes(table, party, vote_event_id)
      fsdf = pd.DataFrame(vs)
      fsdf = fsdf.merge(mps.loc[:, ['mp_id', 'name']], on='name', how='left')
      fsdf['voter_id'] = fsdf['mp_id']
      fsdf = fsdf.drop(columns=['mp_id'])
      fsdf['voter_id'] = fsdf['voter_id'].astype('Int64')
      votes = pd.concat([votes, fsdf])
    votes.to_csv('data/votes.csv', index=False)

    # break

  else:
    print(f'Vote event {vote_event_id} not found.')



