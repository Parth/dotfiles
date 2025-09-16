test: bootstrap
	./test-runner.sh

bootstrap: test-runner.sh test/assert.sh
clean: remove_test-runner.sh remove_assert.sh
update: update_test-runner.sh update_assert.sh

test/assert.sh:
	echo "fetching assert.sh..." && \
	curl -s -L -o test/assert.sh \
		https://raw.github.com/lehmannro/assert.sh/v1.0.2/assert.sh

remove_assert.sh:
	( \
		test -f "test/assert.sh" && rm "test/assert.sh" && \
		echo "removed test/assert.sh" \
	) || exit 0

update_assert.sh: remove_assert.sh test/assert.sh

test-runner.sh:
	echo "fetching test-runner.sh..." && \
	curl -s -L -o test-runner.sh \
		https://github.com/jimeh/test-runner.sh/raw/master/test-runner.sh && \
	chmod +x test-runner.sh

remove_test-runner.sh:
	( \
		test -f "test-runner.sh" && rm "test-runner.sh" && \
		echo "removed test-runner.sh" \
	) || exit 0

update_test-runner.sh: remove_test-runner.sh test-runner.sh

.SILENT:
.PHONY: test bootstrap clean update \
	remove_test-runner.sh update_test-runner.sh \
	remove_assert.sh update_assert.sh
