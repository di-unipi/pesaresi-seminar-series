.PHONY: clean all

all: index.html

clean:
	rm index.html

index.html: $(addprefix src/, index.pug layout.pug next.pug upcoming.pug past.pug) Seminars.csv
	python render.py Seminars.csv
	pug --pretty src/index.pug --out .
