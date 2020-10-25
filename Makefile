all: a clean build serve

SHELL:=/bin/bash
DIST:=docs

a:
	@echo "Using $$0"

clean:
	rm -rf ${DIST}

dev:
	antora --stacktrace --to-dir ${DIST} --title development \
	--require asciidoctor-chart antora-playbook.yml
	make serve

build:
	antora --to-dir ${DIST} \
	--stacktrace antora-playbook.yml
	touch ${DIST}/.nojekyll
	# DOCSEARCH_ENABLED=true DOCSEARCH_ENGINE=lunr NODE_PATH="$(npm -g root)" \
	# --generator=./antora-site-generator-example-html-pages \
	# --generator antora-site-generator-lunr \

serve:
	http-server ${DIST}

new:

