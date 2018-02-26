# dotfiles

Syncs configuration files in the repository with the user's home directory

```text
./sync.py -h
usage: sync.py [-h] [-s SRCDIR] [-t TARGETDIR] [-v] [--overwrite] [--latest]
               [-d]

Sync user rc files with this repo

optional arguments:
  -h, --help            show this help message and exit
  -s SRCDIR, --srcdir SRCDIR
                        Source directory
  -t TARGETDIR, --targetdir TARGETDIR
                        Target directory, defaults to ~
  -v, --verbose
  --overwrite           Resolve conflicts by overwriting the target
  --latest              Resolve conflicts by picking the latest modified
  -d, --dryrun          Don't actually move any files
```

When comparing existing files, targets modified after their corresponding
source file will be identified as 'conflicts'. These can be resolved either by
overwriting the target with the source, or by updating the repository files
with the latest off-sync changes.
