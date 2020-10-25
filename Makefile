all: clean build

SHELL:=/bin/bash
DIST:=docs


clean:
	rm -rf ${DIST}

build:
	DOCSEARCH_ENABLED=true DOCSEARCH_ENGINE=lunr NODE_PATH="$(npm -g root)" \
	antora --to-dir ${DIST} \
	--generator=./antora-site-generator-example-html-pages \
	--generator antora-site-generator-lunr \
	antora-playbook.yml
	touch ${DIST}/.nojekyll

web: build
	http-server ${DIST}

