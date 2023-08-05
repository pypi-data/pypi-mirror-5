CHANGELOG
=========

Version 0.1.1

- Bugfix: StormFactory did not flush/commit the store on fixture teardown
  teardown, meaning the store would not be left clean for subsequent operations

Version 0.1

- initial release
