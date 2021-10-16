import os

files = []
for root, dirnames, filenames in os.walk(os.getcwd()):
    for filename in filenames:
        if filename.endswith('.html'):
            files.append((root,filename))

for htmlFile in files:
    remove = False
    with open(htmlFile[0]+"/"+htmlFile[1], "r+") as f:
        contents = f.readlines()
        f.seek(0)
        for i in contents:
            if not remove:
                if "<div class=\"main-grid\">" in i:
                    remove = True
                f.write(i)
            else:
                if "<main class=\"grid-item\" role=\"main\">" in i:
                    remove = False
                    f.write(i)
        f.truncate()

