.PHONY: clean all

all: index.html

clean:
	rm index.html

index.html: $(addprefix src/, index.pug layout.pug past.pug next.pug)
	pug --pretty src/index.pug --out .
