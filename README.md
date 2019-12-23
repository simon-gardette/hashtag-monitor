# hashtag-monitor
Does what it says.
Monitor specifics hashtags or brand names.
Just an exercise atm.

It will heavily rely on docker images for most of the work cause I'm a lazy ass.

## TO DO

- Define Brand (). Store hashtags for a brand (or any other denominator)
- Collect Response for the hashtag on a serie of different platforms:
    - facebook (Not sure it works anymore)
    - twitter
    - instagram
    - google alerts ?
- Automatise it (airflow / papermill)
- store it in an SQL database. ( Maybe elastic could prove efficient. Dunno, depending on volume.)
- Transform
    - langage detection
    - sentiment analysis
    - normalize interactions
    - anlyze Images ? (later)
- Aggregate and score the whole thing
- Display it (jupyter then flask)

## TO USE

- Postgresql
- airflow
- celery
- redis
- flask
- jupyter 
-
