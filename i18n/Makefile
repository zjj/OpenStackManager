all:
	for i in  $$(ls | grep -v Makefile);do \
		msgfmt -o $$i/LC_MESSAGES/messages.{mo,po};\
	done
