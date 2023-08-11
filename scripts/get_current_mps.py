"""filter out the current MPs from the list of all MPs."""

import datetime
import pandas as pd

mps = pd.read_csv('data/mps.csv')

current_mps = mps[mps['until'] > datetime.datetime.now().strftime('%Y-%m-%d')]

# get current groups
votes = pd.read_csv('data/votes.csv')
last_vote_event_id = votes['vote_event_id'].max()
last_vote_event = votes[votes['vote_event_id'] == last_vote_event_id]

# add current groups to current mps
last_vote_event['voter_id'] = last_vote_event['voter_id'].astype('Int64')
current_mps = current_mps.merge(last_vote_event.loc[:, ['voter_id', 'group']], left_on='mp_id', right_on='voter_id', how='left')
current_mps = current_mps.drop(columns=['voter_id'])

# add constituencies
constituencies = pd.read_csv('data/constituencies.csv')
current_mps = current_mps.merge(constituencies.loc[:, ['constituency_id', 'constituency']], on='constituency_id', how='left')
                  
current_mps.to_csv('data/current_mps.csv', index=False)