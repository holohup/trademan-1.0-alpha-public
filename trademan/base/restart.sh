# Most modren development servers are watching for file changes to auto-restart.
# In this simple script we add a comment to a file in our project and then remove it.
# This tricks development server into restarting, thinking actual changes were made.

# TODO: change myapp/manage.py with any code file in your project

# Add a comment to the end of file
echo "# meow" >> admin.py

# Remove that added comment
sed -i '' -e '$ d' admin.py