BUILD_FOLDER:=build
LATEX_CC:=pdflatex
MAIN_SRC:=main
OUTPUT_NAME:=main
LATEX_FLAGS:=

all:
	$(LATEX_CC) -quiet -halt-on-error -output-directory=$(BUILD_FOLDER) $(LATEX_FLAGS) $(MAIN_SRC).tex
	$(LATEX_CC) -quiet -halt-on-error -output-directory=$(BUILD_FOLDER) $(LATEX_FLAGS) $(MAIN_SRC).tex
	mv $(BUILD_FOLDER)/$(MAIN_SRC).pdf $(BUILD_FOLDER)/$(OUTPUT_NAME).pdf
	
clean:
	rm -fv $(BUILD_FOLDER)/*
