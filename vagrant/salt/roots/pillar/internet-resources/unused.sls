# -*- mode: yaml -*-

#####################################################
## Not using these resources
#####################################################
mdt-i386_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x86.msi

mdt-amd64_msi:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MicrosoftDeploymentToolkit2013_x64.msi

mdt-docs_zip:
  source: http://download.microsoft.com/download/B/F/5/BF5DF779-ED74-4BEC-A07E-9EB25694C6BB/MDT%202013%20Documentation.zip


win-builds-bundle-zip:
  source: http://win-builds.org/stable/win-builds-bundle-1.3.0.zip
  source_hash: sha256=39452620ad67bb292d6910bba9dd79fcce17ddd5e9774d26c0b27ea8ddec4c5e
  name: win-builds-bundle-1.3.0.zip


vcredist_x86.exe:
  source: http://download.microsoft.com/download/d/d/9/dd9a82d0-52ef-40db-8dab-795376989c03/vcredist_x86.exe
  source_hash: sha256=41f45a46ee56626ff2699d525bb56a3bb4718c5ca5f4fb5b3b38add64584026b
  name: vcredist/vcredist_x86.exe
