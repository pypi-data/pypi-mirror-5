# Makefile for Sphinx documentation
#

# You can set these variables from the command line.
BUILDDIR      = built_docs

all: devman installman userman 

help:
	@echo "Builds all PyBill documentation in HTML and PDF formats."
	@echo "  This makefile uses the Sphinx makefiles in the child "
	@echo "  directories."

clean:
	-rm -rf $(BUILDDIR)

devman:
	@echo
	@echo "****** Building documentation for developper manual (dev-manual)"
	@echo
	mkdir -p $(BUILDDIR)
	@echo "*** Building HTML documentation"
	cd dev-manual ; make html
	mv dev-manual/_build/html $(BUILDDIR)/pybill_dev_manual
	@echo "*** Cleaning source directory"
	cd dev-manual ; make clean

installman:
	@echo
	@echo "****** Building documentation for installation manual (install-manual)"
	@echo
	mkdir -p $(BUILDDIR)
	@echo "*** Building HTML documentation"
	cd install-manual ; make html
	mv install-manual/_build/html $(BUILDDIR)/pybill_install_manual
	@echo "*** Cleaning source directory"
	cd install-manual ; make clean

userman:
	@echo
	@echo "****** Building documentation for user manual (user-manual)"
	@echo
	mkdir -p $(BUILDDIR)
	@echo "*** Building HTML documentation"
	cd user-manual ; make html
	mv user-manual/_build/html $(BUILDDIR)/pybill_user_manual
	@echo "*** Cleaning source directory"
	cd user-manual ; make clean
