This utility is written for easing moving source code between separated network with mobile storage.

Here are the steps: (sample of .codepackager.yaml can be found in this project)

 1. Put .codepackager.yaml into your home folder and configurate it with your setting.
    The following directive can be ignored in this configuration file:
      * "package-name" and
      * "vcs"
    This would be your local setting. You will need local setting in remote machine, too.

 2. Put .codepackager.yaml into the root folder (where .hg or .git resides) of your repository.
    Only "package-name" is required. This setting ("package-name") will use as packaged file name.
    You can include other directives to customize for certain project if you really need it.
    This would be your project/repository setting.

 3. Add and commit the .codepackager.yaml in your repository.

 4. Run "prep_codepkg.py" in root folder of repository to package the repository (and make backup).

 5. Move mobile storage to remote machine.
    Run "recv_codepkg.py /PATH/TO/PACKAGED_FILE" in repository folder of remote machine.
    This step should bring configuration file to remote machine.

 6. From now on, you can use "recv_codepkg.py" (without path of packaged file) to pull updates from mobile storage.

