# MunkiCatalogPromote
Promotes pkginfo files from development to testing to production after a certain number of days

## Rationale
If you have a lot of Munki items to move through a development-testing-production process, it can be cumbersome to go into each pkginfo and add a new catalog to the pkginfo, even if you're doing it through a GUI like MunkiAdmin. MunkiCatalogPromote allows you to bulk-promote all your pkginfo files after a certain number of days.

There are actually a bunch of catalog promotion scripts for Munki. Ed Ravin has compiled [a fairly comprehensive list on the Munki Dev mailing list.](https://groups.google.com/d/msg/munki-dev/w5fAMwzeMmM/s_-ri2nGAgAJ)

I wanted to create something simple for what I want, which is just to move every pkginfo through after a certain number of days. I also wanted to practice some more Python, so this script was a good excuse to do so. If this script doesn't do what you want to do, definitely check out any of the other automated options from Ed Ravin's list.

## How to use MunkiCatalogPromote
### General Instructions
* Download the MunkiCatalogPromote.py file to your Munki server.
* Edit the MunkiCatalogPromote.py, being sure to user-defined preferences. You may want to make the days between promotions longer or shorter, or you may have only testing and production catalogs (no development). Definitely be sure check your MUNKI_ROOT_PATH to match that of your server's.
* Move MunkiCatalogPromote.py and the FoundationPlist folder to /usr/local/mcp and make it executable.
* The first time you run MunkiCatalogPromote, it won't seem to do anything, because it's just tagging each pkginfo with a promotion date of now, and then each item's actual promotion will happen after a certain number of days (which you define) the next time you run the script.
* If you find MunkiCatalogPromote working the way you like it, you can automate it using a launch agent (Mac), a cron job (Linux), or a scheduled task (Windows).

### Example of configuration/installation via command line
Your paths may vary, of course, especially if you're using a Windows server

Edit the downloaded file
```
nano ~/Downloads/MunkiCatalogPromote-master/MunkiCatalogPromote.py
```

Create the directory
```
sudo mkdir /usr/local/mcp/
```

Move the files
```
sudo mv ~/Downloads/MunkiCatalogPromote-master/* /usr/local/mcp/
```

Change permissions and ownership
```
sudo chown -R root:wheel /usr/local/mcp
sudo chmod -R 755 /usr/local/mcp
```

## Acknowledgements
Some of the code is lifted/tweaked from [autopromoter](https://github.com/jessepeterson/autopromoter), some from [outset](https://github.com/chilcote/outset/), and some from [munki](https://github.com/munki/munki).
