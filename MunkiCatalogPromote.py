#!/usr/local/munki/munki-python

import datetime
import logging
import os
import plistlib
import subprocess

##### User-defined preferences -- this could be a .plist, but keeping it in the .py makes it simpler

days_between_promotions = 4
promotion_order = ['development', 'testing', 'production']
MUNKI_ROOT_PATH = '/Users/Shared/munki_repo'

# If you're using a standard Munki setup, these variables will likely remain unchanged
makecatalogs = '/usr/local/munki/makecatalogs'
MUNKI_PKGSINFO_DIR_NAME = 'pkgsinfo'

##### End of user-defined preferences

# Stolen from offset's offset to set up a log file
if not os.path.exists(os.path.expanduser('~/Library/Logs')):
    os.makedirs(os.path.expanduser('~/Library/Logs'))
log_file = os.path.expanduser('~/Library/Logs/MunkiAutopromote.log')

logging.basicConfig(format = '%(asctime)s - %(levelname)s: %(message)s',
                        datefmt = '%m/%d/%Y %I:%M:%S %p',
                        level = logging.DEBUG,
                        filename = log_file)

def main():
    # Join paths based on what's user-defined
    pkgsinfo_path = os.path.join(MUNKI_ROOT_PATH, MUNKI_PKGSINFO_DIR_NAME)

    # Check that the path for the pkgsinfo exists
    if not os.path.isdir(pkgsinfo_path):
        logging.error("Your pkgsinfo path is not valid. Please check your MUNKI_ROOT_PATH and MUNKI_PKGSINFO_DIR_NAME values.")
    else:
        # Get the current date into a variable
        current_date=datetime.date.today()
        
        # Get the threshold date to compare
        threshold_date = datetime.date.today() + datetime.timedelta(days =- days_between_promotions)

        # Initialize test variable for running makecatalogs
        anything_changed = False

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
                logging.info("Now processing {}".format(file))
                try:
                    f = open(fullfile, 'rb')
                except:
                    logging.error("Unable to open {}".format(file))
                    continue
                try:
                    pkginfo = plistlib.load(f)
                except:
                    logging.error("Unable to read XML from {}".format(file))
                    continue
                f.close()
                # In most cases, there should be a catalogs key, but double-check
                if 'catalogs' not in pkginfo.keys():
                    pkginfo['catalogs'] = []
                # Get the existing catalogs into a variable
                existing_catalogs = pkginfo['catalogs']

                # Test variable for this particular pkginfo
                pkginfo_changed = False

                # Check for _metadata key stolen from Jesse Peterson's https://github.com/jessepeterson/autopromoter/blob/master/autopromoter.py
                if '_metadata' not in pkginfo.keys():
                    # create _metadata key if it doesn't exist. this is to catch older
                    # pkginfos that didn't automatically generate this field
                    pkginfo['_metadata'] = {}
                    logging.info("Creating _metadata dictionary for {}".format(file))
                    pkginfo_changed = True
                # Either way, also make sure there is a promotion date that exists, too
                # The idea here is that if MunkiAutopromote didn't already put in a promotion date, we should put one in now and then it'll be caught the next time around
                if 'catalog_promotion_date' not in pkginfo['_metadata']:
                    pkginfo['_metadata']['catalog_promotion_date'] = str(current_date)
                    logging.info("Creating promotion date of {} for {}".format(current_date, file))
                    pkginfo_changed = True
                # No point checking if it was X days ago if we just put it in
                else:
                    # See if the last promotion date was days_between_promotion days ago or more
                    last_catalog_promotion_date = datetime.datetime.strptime(pkginfo['_metadata']['catalog_promotion_date'], "%Y-%m-%d").date()
                    # In addition to comparing dates, we also don't want to bother with any pkginfo files that have the full set of catalogs already
                    if last_catalog_promotion_date <= threshold_date and sorted(existing_catalogs) != sorted(promotion_order):
                        logging.info("Last promotion date was more than {} days ago for {}".format(days_between_promotions, file))
                        # Promote!
                        for catalog in promotion_order:
                            if catalog not in existing_catalogs:
                                logging.info("Adding {} catalog for {}".format(catalog, file))
                                # Add the catalog to the list of existing ones
                                pkginfo['catalogs'].append(catalog)
                                # Update the promotion date
                                pkginfo['_metadata']['catalog_promotion_date'] = str(current_date)
                                pkginfo_changed = True
                                # Check the general test variable
                                if not anything_changed:
                                    anything_changed = True
                                # Break the for loop; otherwise, it will promote beyond just this one
                                break
                if pkginfo_changed:
                    # Write the changes back
                    logging.info("Writing changes back to {}".format(file))
                    try:
                        f = open(fullfile, 'wb')
                    except:
                        logging.error("Unable to open {}".format(file))
                        continue
                    try:
                        pkginfo = plistlib.dump(pkginfo, f)
                    except:
                        logging.error("Unable to write XML back to {}".format(file))
                        continue
                    f.close()

        # If there were any changes made, run makecatalogs
        if anything_changed:
            if os.path.exists(makecatalogs):
                logging.info("Running makecatalogs")
                subprocess.call(makecatalogs)
            else:
                logging.error("{} could not be found. When you have a chance, run makecatalogs on your Munki repo to have the changes reflected".format(makecatalogs))
        else:
            logging.info("No pkginfo files changed, so not running makecatalogs")

if __name__ == '__main__':
    main()
