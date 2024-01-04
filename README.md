# cz-senate-votes
Votes CZ Senate

## Analyses

### Data preparation (not ordered!)
- `get_mps.py` - Get MPs from the Senate website.
- `add_mp_ids.py` - Add MP IDs to the data. Note: this script is not used in the pipeline, it is only used to add MP IDs once
- `update.py` - Update the database with the latest data from the web. Updates `data/votes.csv` and `data/vote_events.csv`.

### Data analyses