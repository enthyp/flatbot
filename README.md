### flatbot
Google Firebase Cloud Messaging in service of letting you know about new postings on Gumtree (to be enhanced).

#### TODOs:
  * Use Postgres instead of YAML files!
    * Requires changes in:
      * authorization policy
      * scrape results storage
  * Move all config (including paths) to Config class.
  * Turn Scheduler into ChannelManager.
  * Better task separation in Channel?