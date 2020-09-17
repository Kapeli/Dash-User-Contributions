docset: clean
	curl -L -o source.tgz \
		https://github.com/bulletphysics/bullet3/archive/$(VERSION).tar.gz
	tar -xzvf source.tgz
	mv bullet3-$(VERSION) source
	printf "\n \
		HAVE_DOT = NO \n \
		GENERATE_DOCSET = YES\n \
		DISABLE_INDEX = YES\n \
		SEARCHENGINE = NO\n \
		GENERATE_TREEVIEW = NO\n \
		DOCSET_BUNDLE_ID = org.bulletphysics\n \
		PROJECT_NAME = Bullet\n" >>source/Doxyfile
	cd source && \
		doxygen && \
		cd html && \
		make && \
		plutil -insert DashDocSetKeyword -string bullet \
			org.bulletphysics.docset/Contents/Info.plist && \
		tar --exclude=.DS_Store -czvf ../../org.bulletphysics.docset.tgz \
			org.bulletphysics.docset
	mkdir -p versions/$(VERSION)
	cp org.bulletphysics.docset.tgz versions/$(VERSION)
	make clean

clean:
	rm -fr source source.tgz
