# List git submodules
git submodule

The output you've shown indicates that you have submodules initialized in your main repository, but the submodule directories haven't been populated yet, as indicated by the '-' sign before the commit hashes.

Here's how you pull the updates for these submodules:

    Initialize and Clone Submodules

    If this is the first time you're working with these submodules, or if you've cloned the main repository without the submodules, you need to initialize and update them. Run the following command:

git submodule update --init --recursive

This will clone the submodule repositories based on the commit hashes that are currently recorded in the main repository. The --recursive option will also initialize and update any nested submodules within the submodules.

#Pull Changes for Submodules

If you want to pull the latest changes from the remote branches for your submodules, you can do the following:

Update the submodules to the latest commit on their tracking branch (usually master or main):

git submodule update --remote --merge

The --remote flag tells Git to fetch the latest changes from the remote repository. The --merge flag tries to merge the incoming changes with your current submodule state.
#Commit the Submodule Updates

After updating the submodules, you should commit the changes to the main repo to record the new submodule commit hashes:

git add tennisproject/tennis_atp/tennis_data
git add tennisproject/tennis_atp/wta_data/tennis_wta
git commit -m "Update submodules to latest commits"