"""Add MP IDs to the data."""

# Note: this script is not used in the pipeline, it is only used to add MP IDs once

import janitor
import pandas as pd

mps = pd.read_csv('data/mps.csv')
votes = pd.read_csv('data/votes.csv')
vote_events = pd.read_csv('data/vote_events.csv')

votes = votes.merge(vote_events.loc[:, ['vote_event_id', 'date']], on='vote_event_id', how='left')

votes.merge(mps, on='name', how='left')

# Merge mps into votes 
votes['date'] = pd.to_datetime(votes['date'])
mps['since'] = pd.to_datetime(mps['since'])
mps['until'] = pd.to_datetime(mps['until'])

# conditional join using janitor
df = votes.conditional_join(
  mps.loc[:, ['mp_id', 'name', 'since', 'until']],
  ('name', 'name', '=='),
  ('date', 'since', '>='),
  ('date', 'until', '<='),
  keep='last',
  how='left'
)
df.columns = df.columns.droplevel(0)
# check for duplicates (there are some testing vote events, which have duplicated names | 99 votes)
duplicates = df[df.duplicated(subset=['vote_event_id', 'name'])]
# check for missing MP IDs (there are some vote events with secret votes, where the full names are not available | 242 votes)
df[df['mp_id'].isna()]
# clean up
df['voter_id'] = df['mp_id']
df = df.drop(columns=['mp_id'])
dupes = df.columns.duplicated()
df = df.loc[:, ~dupes]
df = df.drop(columns=['since', 'until'])
df['voter_id'] = df['voter_id'].astype('Int64')

# save
df.to_csv('data/votes.csv', index=False)

# CORRECT DATES
df = pd.read_csv('data/votes.csv')
# delete column dates
df = df.drop(columns=['date'])
# correct voter_id
df['voter_id'] = df['voter_id'].astype('Int64')
# change not_voting to absent
df['option'] = df['option'].replace({'not_voting': 'absent'})
# save
df.to_csv('data/votes.csv', index=False)