.PHONY: clean all

all: index.html

clean:
	rm index.html

index.html: $(addprefix src/, index.pug layout.pug next.pug upcoming.pug past.pug) Seminars.csv render.py
	python render.py -u Seminars.csv
	pug --doctype html --pretty src/index.pug --out .
