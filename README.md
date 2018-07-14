# soundcloud-recommender
building my own recommendation engine for soundcloud!


**tldr;** some objects you can plug into a `sklearn.pipeline.Pipeline` for processing features out of a pandas DataFrame



**the parts so far include:**
- `aws`: a module for managing a postgresql relational db set up on an AWS EC2 instance
- `sc`: a python wrapper for the soundcloud api
- a remote **webcrawler** than can make individual api requests, identify Users and Tracks to collect in the future, clean and send scraped data to the relational tables on AWS.
- a remote *postgresql* relational db server that houses our collected data (`users`,`tracks`,`favorites`,`manifest`)



| executables | description |
|----|----|
|`data_utils.sc`  | my custom wrapper for interacting with the soundcloud api
|`data_utils.settings`  | a settings file for `sc`.  originally intentioned as an overall settings
|`data_utils.aws`  |  for interacting with data from the aws database mostly uses `sqlalchemy` ORM and MetaData objs
 file but got too big... needs to be condensed with `sc` into its own contained module
|`data_utils.crawl`  | crawler function that can go out and get data from soundcloud and arrange it into our database!
|`data_utils/cron.sh`  |  little script triggered by `crontab` on server which runs our `crawl.py` function and leaves a log

## `sc`: pulling data from the soundcloud API
the module basically leads up to a few main functions which handle our most useful API requests. a few endpoints allow options to pull multiple UIDs but most of them can  only handle one UID at a time, which becomes our bottleneck when collecting the exponentially increasing social relationships as degrees of separation increase: user-to-items-to-more-users-to-even-more-items, etc

||description| ie
|-----|----|---|
|`Resolve.resolve`| translates public-facing URLs to api requests (good way to get internal info from a public username, for example) | api.soundcloud.com/resolve?url="http://soundcloud.com/myuser/"
|`Users.user` | individual request for `users` metadata | api.soundcloud.com/users/{uid}}
|`Users.users` | bulk requests for `users` metadata | api.soundcloud.com/tracks/?ids={string_of_uids_separated_by_commas}
|`Users.favorite` | gets a list of public favorites from a user (in `tracks` format)| api.soundcloud.com/tracks/{uid}/favorites
|`Tracks.track` | individual request for `tracks` metadata | api.soundcloud.com/tracks/{uid}}
|`Tracks.tracks` | bulk requests for `tracks` metadata | api.soundcloud.com/tracks/?ids={string_of_uids_separated_by_commas}
|`Tracks.favoriters` | NOTE: named differently from to explicitly clarify the contextual differences with `Users.favorites` | api.soundcloud.com/tracks/{uid}/favoriters


## The Relational DB: how to store the data in a useful way?
there are four main tables:

|table | description |
|-----|----|
| `users` | our user account metadata |
| `tracks` | our track metadata |
| `favorites` | interaction data between `tracks` and the `users` that "favorited" them.  currently 1 (favorited) or 0 (not favorited) for simplicity
| `manifest` | a list of uids (either `users` or `tracks`) gleaned from every API request that is processed & submitted to the db.  has a "to-do" list of timestamps if a particular API request & DB update/insert has yet to be carried out for that uid (`ref_id`)


## `aws` module
navigates management tasks related to queries to/from the postgresql server.

to do: refactor, cut out cruft, figure out better solutions to temporary measures (step limit) abstract a couple useful things out (like "step" iteration) for better performance/reliability

#### `schema`:
defines our `sqlalchemy` schema both for creation and so that everything we send to the server is in the right format!

#### `table(obj)`,`get()`,`extract()`, and :



## `crawl` and `cron.sh`
