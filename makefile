.PHONY : clean

cv:
	python update_publications.py
	latexmk -xelatex ry_cv.tex

clean:
	latexmk -C
