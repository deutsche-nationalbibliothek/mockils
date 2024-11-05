# MockILS

This is just meant for development and testing, not for production.

A fastapi implementation to mock parts of the ARAS REST API to test [aras-py](https://github.com/deutsche-nationalbibliothek/aras-py) and to perform some item queries in context of the webarchive.


You need to create a directory `data` with the following abstract structure:

```
data:
- repositoryA
  - idn1
    - fileX.txt
    - fileY.gz
  - idn2
  - …
- repositoryB
```

You can create it with `task testdata` if you have [task](https://taskfile.dev/) installed.
