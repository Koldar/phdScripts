prefix = /usr/local

all:
	@echo "compilation done"

install: all
	install hello_there $(DESTDIR)$(prefix)/bin
	install hello_there.1 $(DESTDIR)$(prefix)/share/man/man1
	@echo "Install done"

clean:
	@echo "clean done"