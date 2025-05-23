#!/bin/bash

# Create build directory
mkdir -p build

# Copy all documentation files including _sidebar.md
cp -r docs/* build/

# Copy existing markdown documentation files to the docs directory
cp ARCHITECTURE.md DOCKER.md LOGGING.md build/

# Verify that _sidebar.md was copied
if [ -f build/_sidebar.md ]; then
  echo "_sidebar.md copied successfully"
else
  echo "ERROR: _sidebar.md was not copied correctly!"
  exit 1
fi

# Use the template file to create index.html
cat docs/templates/docsify-template.html > build/index.html

echo "Documentation build completed successfully"
