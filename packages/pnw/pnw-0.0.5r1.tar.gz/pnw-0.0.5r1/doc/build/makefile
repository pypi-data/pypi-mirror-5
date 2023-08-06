PROJECT = 2013-pnw
HEUTE = $(shell date +%Y-%m-%d)
MAIN = ../pnw-doc
STY  = ml-gen.cls local.sty
BIB = localbib.bib 
SRC = $(MAIN).pnw makefile __version__
DISTSRC = $(SRC) $(STY) $(BIB) 
#TEMPLATEDIR = 2013-ML-MathTemplate
#export TEXINPUTS=.//:
# export variables to subshells!
export

#hg node stamp
HGNODE=$(shell hg parent --template '{rev}-{node|short}-{date|shortdate}')
VERSION=$(shell python ../../pnw.pnw -v)

viewer  = evince
view-ext =.pdf

.PHONY: all
all: pdf draft arx clean

.PHONY: everything clean
everything: all arxiv dist


.PHONY: pdf
pdf: $(MAIN).pdf

#hginfo.blg: $(SRC) 
#	echo '\\mlSetRCSInfo{$(VERSION)}' > hginfo.blg

hginfo.blg: $(SRC)
	cd ../.. && $(MAKE) ./doc/build/hginfo.blg

__version__: $(SRC)
	echo "2013-pnw c 2005-2013 Matthias Lesch (ml@matthiaslesch.de) $(HGNODE)">__version__

# noweb related
pnw-doc.tex: $(MAIN).pnw ../../pnw.pnw
#	python pynoweb.py -W $(MAIN).nw > $(MAIN).tex
	pnw -Rmain $(MAIN).pnw > $(MAIN).tex

pnw-doc.pdf:  ../../pnw.pnw $(MAIN).tex $(SRC) $(STY) hginfo.blg 
	pdflatex $(MAIN).tex
	#bibtex $(MAIN)
	pdflatex $(MAIN).tex

.PHONY: dist
dist:   $(DISTSRC) 
	tar -zcf $(PROJECT)-dist-$(HGNODE).tgz $(SRC)

clean:
	rm -f *.aux *.log *.toc *.brf *.out

view:   $(MAIN)-draft.pdf
	$(viewer) $(MAIN)-draft.pdf

viewarx: $(MAIN).pdf
	$(viewer) $(MAIN).pdf
