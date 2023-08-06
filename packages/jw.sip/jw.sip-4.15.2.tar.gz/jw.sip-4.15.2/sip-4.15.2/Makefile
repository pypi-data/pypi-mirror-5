
all:
	@(cd sipgen; $(MAKE))
	@(cd siplib; $(MAKE))

install:
	@(cd sipgen; $(MAKE) install)
	@(cd siplib; $(MAKE) install)
	@test -d $(DESTDIR)/home/j/Personal/Projects/virtualenv/jw.sip/lib64/python2.7/site-packages || mkdir -p $(DESTDIR)/home/j/Personal/Projects/virtualenv/jw.sip/lib64/python2.7/site-packages
	cp -f sipconfig.py $(DESTDIR)/home/j/Personal/Projects/virtualenv/jw.sip/lib64/python2.7/site-packages/sipconfig.py
	cp -f /home/j/Personal/Projects/virtualenv/jw.sip/sip-4.15.2/sipdistutils.py $(DESTDIR)/home/j/Personal/Projects/virtualenv/jw.sip/lib64/python2.7/site-packages/sipdistutils.py

clean:
	@(cd sipgen; $(MAKE) clean)
	@(cd siplib; $(MAKE) clean)
