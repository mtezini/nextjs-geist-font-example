#!/bin/bash
# Script to export the current project directory into a zip file

zip -r project_export.zip . -x "*.git*" "*.vscode*" "node_modules/*" "export_project.sh"
echo "Project exported to project_export.zip"
