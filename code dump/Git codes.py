




-------------------------------------------

####Git code 

----------- to set up first project  
# Check your current branch
git branch

# If the 'main' branch does not exist, create and switch to it
git checkout -b main

# Stage all files for commit
git add .

# Commit the changes with a message
git commit -m "Initial commit"

# Push the branch to the remote repository
git push -u origin main


------- to update after making changes in code
# Stage all changes for commit
git add .

# Commit the changes with a descriptive message
git commit -m "Update changes"

# Push the changes to the remote repository
git push -u origin main