#!/usr/bin/python

import datetime
import FoundationPlist
import logging
import os
import sys

##### User-defined preferences -- this could be a .plist, but keeping it in the .py makes it simpler and cross-platform (Mac, Linux, Windows)

days_between_promotions=4
promotion_order=['development', 'testing', 'production']
MUNKI_ROOT_PATH='/Users/Shared/munki_repo'

# If you're using a standard Munki setup, these variables will likely remain unchanged
makecatalogs='/usr/local/munki/makecatalogs'
MUNKI_PKGSINFO_DIR_NAME = 'pkgsinfo'

##### End of user-defined preferences

# Stolen from offset's offset to set up a log file
if not os.path.exists(os.path.expanduser('~/Library/Logs')):
   os.makedirs(os.path.expanduser('~/Library/Logs'))
log_file = os.path.expanduser('~/Library/Logs/MunkiAutopromote.log')

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.DEBUG,
                    filename=log_file)

# Function that checks paths are writable
def check_folder_writable(checkfolder):
   if not os.access(checkfolder, os.W_OK):
      logging.error("You don't have access to %s" % checkfolder)
      sys.exit(1)

def main():
   # Join paths based on what's user-defined
   pkgsinfo_path=os.path.join(MUNKI_ROOT_PATH, MUNKI_PKGSINFO_DIR_NAME)

   # Check that the path for the pkgsinfo exists
   if not os.path.isdir(pkgsinfo_path):
      logging.error("Your pkgsinfo path is not valid. Please check your MUNKI_ROOT_PATH and MUNKI_PKGSINFO_DIR_NAME values.")
   else:
      # Make sure the relevant folder is writable
      check_folder_writable(pkgsinfo_path)
      
      # Get the current date into a variable
      current_date=datetime.date.today()
      
      # Get the threshold date to compare
      threshold_date=datetime.date.today() + datetime.timedelta(days=-days_between_promotions)
      
      ## Loop through all the pkginfo files and see if they need to be promoted
      for root, dirs, files in os.walk(pkgsinfo_path):
         for dir in dirs:
            # Skip directories starting with a period
            if dir.startswith("."):
               dirs.remove(dir)
         for file in files:
            # Skip files that start with a period
            if file.startswith("."):
               continue
            fullfile = os.path.join(root, file)
            logging.info("Now processing %s" % fullfile)
            pkginfo = FoundationPlist.readPlist(fullfile)
            existing_catalogs = pkginfo['catalogs']
            
            # Test variable for this particular pkginfo
            pkginfo_changed=False
            
            # Check for _metadata key stolen from Jesse Peterson's https://github.com/jessepeterson/autopromoter/blob/master/autopromoter.py
            if '_metadata' not in pkginfo.keys():
               # create _metadata key if it doesn't exist. this is to catch older
               # pkginfos that didn't automatically generate this field
               pkginfo['_metadata'] = {}
               logging.info("Creating _metadata dictionary for %s" % fullfile)
               pkginfo_changed=True
            # Either way, also make sure there is a promotion date that exists, too
            # The idea here is that if MunkiAutopromote didn't already put in a promotion date, we should put one in now and then it'll be caught the next time around
            if 'catalog_promotion_date' not in pkginfo['_metadata']:
               pkginfo['_metadata']['catalog_promotion_date'] = str(current_date)
               logging.info("Creating promotion date of %s for %s" % (current_date, fullfile))
               pkginfo_changed=True
            # No point checking if it was X days ago if we just put it in
            else:
               # See if the last promotion date was days_between_promotion days ago or more
               last_catalog_promotion_date=datetime.datetime.strptime(pkginfo['_metadata']['catalog_promotion_date'], "%Y-%m-%d").date()
               # In addition to comparing dates, we also don't want to bother with any pkginfo files that have the full set of catalogs already
               if last_catalog_promotion_date <= threshold_date and sorted(existing_catalogs)!=sorted(promotion_order):
                  logging.info("Last promotion date was more than %s days ago for %s" % (days_between_promotions, fullfile))
                  # Promote!
                  for catalog in promotion_order:
                     if catalog not in existing_catalogs:
                        logging.info("Adding %s catalog for %s" % (catalog, fullfile))
                        # Add the catalog to the list of existing ones
                        pkginfo['catalogs'].append(catalog)
                        # Update the promotion date
                        pkginfo['_metadata']['catalog_promotion_date']=str(current_date)
                        pkginfo_changed=True
                        # Break the for loop; otherwise, it will promote beyond just this one
                        break
            if pkginfo_changed:
               # Write the changes back
               FoundationPlist.writePlist(pkginfo, fullfile)

      # I guess we could have a variable that checks to see if there were any changes before running makecatalogs. For now, it really doesn't hurt to run it, even if there weren't any changes.
      if os.path.exists(makecatalogs):
         logging.info("Running makecatalogs")
         os.system(makecatalogs)
      else:
         logging.error("%s could not be found. When you have a chance, run makecatalogs on your Munki repo to have the changes reflected." % makecatalogs)

if __name__ == '__main__':
    main()
