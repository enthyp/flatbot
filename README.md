### flatbot
Google Firebase Cloud Messaging in service of letting you know about new postings on Gumtree (to be enhanced).
Also, Android app receiver of notifications is not here yet.

#### TODOs:
  * Send updates when someone new tracks?
    * Others can ignore.
  * Remove stale updates.
  * Better error handling - e.g. UniqueViolation upon 2nd tracking request.
  * Cleanup (and correct - Config especially) the tests!
    * Plenty of 'unit' tests are actually integration tests (using DB)...
