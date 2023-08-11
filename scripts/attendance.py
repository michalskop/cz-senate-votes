"""Voting attendace."""

import pandas as pd

since = '2018-10-13'

mps = pd.read_csv('data/current_mps.csv')
votes = pd.read_csv('data/votes.csv')

# filter out the current MPs and votes since
votes_selected = votes[(votes['date'] > since) & (votes['voter_id'].isin(mps['mp_id']))]
votes_selected['voter_id'] = votes_selected['voter_id'].astype('Int64')

# remove votes from sitting 999 (testing)
vote_events = pd.read_csv('data/vote_events.csv')
votes_selected = votes_selected.merge(vote_events.loc[:, ['vote_event_id', 'sitting']], on='vote_event_id', how='left')
votes_selected = votes_selected[votes_selected['sitting'] != 999]

# ATTENDANCE BY VOTES
# get the number of votes per MP
attendance = pd.pivot_table(votes_selected, index=['voter_id'], columns=['option'], values=['vote_event_id'], aggfunc='count', fill_value=0)
attendance.columns = attendance.columns.droplevel(0)
attendance['possible'] = attendance.sum(axis=1)
attendance['attendance'] = attendance['yes'] + attendance['no'] + attendance['abstain']
attendance['rate'] = attendance['attendance'] / attendance['possible']

# add names
attendance = attendance.merge(mps.loc[:, ['mp_id', 'name', 'party', 'group', 'photo', 'constituency']], left_on='voter_id', right_on='mp_id', how='left')

# correct photo links, add server prefix
attendance['photo'] = 'https://www.senat.cz' + attendance['photo']

# add abbreviations
attendance['group'].unique()
attendance['abbreviation'] = attendance['group'].replace({
  'Občanské demokratické strany a TOP 09': 'ODS a TOP 09',
  'KDU-ČSL a nezávislí': 'KDU-ČSL',
  'ANO a SOCDEM': 'ANO a SOCDEM',
  'Starostové a nezávislí': 'STAN',
  'SEN 21 a Piráti': 'SEN 21 a Piráti',
  'Nezařazení': 'Nezařazení'
})

# add prepared attendance
attendance['účast'] = round(attendance['rate'] * 100)
attendance['účast'] = attendance['účast'].astype('Int64')

# sort
attendance = attendance.sort_values(by=['abbreviation'])

# save
attendance.to_csv('data/attendance.v1.csv', index=False)

# ATTENDANCE BY DAYS
t1 = pd.pivot_table(votes_selected, index=['voter_id', 'name', 'date'], columns=['option'], values=['group'], aggfunc='count', fill_value=0)

t1.columns = t1.columns.droplevel(0)
t1['present'] = ((t1['yes'] + t1['no'] + t1['abstain']) > 0) * 1
t1.reset_index(inplace=True)

attendance_days = pd.pivot_table(t1, index=['voter_id', 'name'], columns=['present'], values=['date'], aggfunc='count', fill_value=0)

attendance_days.columns = attendance_days.columns.droplevel(0)
attendance_days['total'] = attendance_days.sum(axis=1)
attendance_days['present_rate'] = attendance_days[1] / attendance_days['total']
attendance_days['not_present_rate'] = attendance_days[0] / attendance_days['total']
attendance_days.reset_index(inplace=True)
attendance_days.rename(columns={1: 'present', 0: 'not_present'}, inplace=True)

attendance_days = attendance_days.merge(mps.loc[:, ['mp_id',  'party', 'group', 'photo', 'constituency']], left_on='voter_id', right_on='mp_id', how='left')

# add úcast
attendance_days['účast'] = round(attendance_days['present_rate'] * 100)
attendance_days['účast'] = attendance_days['účast'].astype('Int64')

# add abbreviations/home/michal/dev/cz-psp-votes-2021-202x/wpca.py
attendance_days['abbreviation'] = attendance_days['group'].replace({
  'Občanské demokratické strany a TOP 09': 'ODS a TOP 09',
  'KDU-ČSL a nezávislí': 'KDU-ČSL',
  'ANO a SOCDEM': 'ANO a SOCDEM',
  'Starostové a nezávislí': 'STAN',
  'SEN 21 a Piráti': 'SEN 21 a Piráti',
  'Nezařazení': 'Nezařazení'
})

# correct photo links, add server prefix
attendance_days['photo'] = 'https://www.senat.cz' + attendance_days['photo']

# sort
attendance_days = attendance_days.sort_values(by=['group'])

# save
attendance_days.to_csv('data/attendance_days.v1.csv', index=False)

# TEST
votes_selected[(votes_selected['voter_id'] == 368) & (votes_selected['option'] == 'absent')]

t = pd.pivot_table(votes_selected[(votes_selected['voter_id'] == 206)], index=[ 'voter_id', 'date'], columns=['option'], values=['group'], aggfunc='count', fill_value=0)
len(t)


t = pd.pivot_table(votes_selected[(votes_selected['date'] == '2023-08-02')], index=['voter_id', 'name', 'group', 'date'], columns=['option'], values=['sitting_x'], aggfunc='count', fill_value=0)
t.columns = t.columns.droplevel(0)
t['present'] = ((t['yes'] + t['no'] + t['abstain']) > 0) * 1

t[t['present'] == 0]


# pspvotes = pd.read_csv('../cz-psp-votes-2021-202x/data/votes.csv')

# len(pspvotes[pspvotes['date'] > '2018-10-13']['date'].unique())