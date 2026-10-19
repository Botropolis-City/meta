GREEN := "\033[0;32m"
NC := "\033[0;0m"

LOG := @sh -c '\
       printf ${GREEN}; \
       echo -e "\n> $$1\n"; \
       printf ${NC}' VALUE

-include .env

CHILDREN := botropolis botropolis.city vision
GITHUB_ORG := git@github.com:Botropolis-City

targets ::
	@awk -F'::?[[:space:]]*' '/^[a-zA-Z0-9][^$#\/\t=]*::?([^=]|$$)/ { \
		gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$1); \
		gsub(/^[[:space:]]+|[[:space:]]+$$/, "", $$2); \
		split($$1,A,/ /); \
		target=A[1]; \
		deps=$$2; \
		printf "%s", target; \
		if (deps) printf " → %s", deps; \
		print "" \
	}' $(MAKEFILE_LIST)

docs-check ::
	$(LOG) "Checking the documentation structure"
	@tools/check-docs

test :: test-unit test-acceptance

test-unit ::
	$(LOG) "Running the unit tests"
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tools -p '*_test.py'
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s performance/tools -p '*_test.py'

test-acceptance ::
	$(LOG) "Running the acceptance tests"
	@PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s testing/acceptance -p '*_test.py'

PERF_SECONDS ?= 600

perf-env ::
	@performance/tools/perf-env

perf-daemon ::
	$(LOG) "Sampling botropolisd for ${PERF_SECONDS}s (performance/method.md, run 1)"
	@out=$${XDG_STATE_HOME:-$$HOME/.local/state}/botropolis-perf/daemon-$$(date +%Y%m%d-%H%M%S); mkdir -p "$$out"; \
		performance/tools/perf-env >"$$out/env.txt"; \
		performance/tools/perf-sample --name botropolisd --interval 1 --duration ${PERF_SECONDS} --out "$$out/samples.csv"; \
		performance/tools/perf-report "$$out/samples.csv" | tee "$$out/report.md"

perf-city ::
	$(LOG) "Opening the city and sampling it for ${PERF_SECONDS}s (performance/method.md, run 3)"
	@performance/tools/perf-city --seconds ${PERF_SECONDS}

publishable :: docs-check
	$(LOG) "Checking nothing unpublishable is in the repository"
	@tools/check-publishable

statusline ::
	$(LOG) "Wiring Claude Code's status line into each checked-out repository"
	@tools/wire-statusline

clone ::
	$(LOG) "Cloning the child repositories that are missing"
	@for c in ${CHILDREN}; do \
		if [ -d "$$c/.git" ]; then \
			echo "  $$c: already here"; \
		elif git clone -q --origin github "${GITHUB_ORG}/$$c.git" "$$c" 2>/dev/null; then \
			echo "  $$c: cloned"; \
		else \
			echo "  $$c: NOT cloned — no access, or offline (vision is private)"; \
		fi; \
	done
	@for d in vision/.claude/skills/*/; do \
		[ -d "$$d" ] || continue; n=$$(basename "$$d"); \
		[ -e ".claude/skills/$$n" ] || ln -s "../../$${d%/}" ".claude/skills/$$n"; \
		grep -qxF "/.claude/skills/$$n" .git/info/exclude 2>/dev/null || echo "/.claude/skills/$$n" >> .git/info/exclude; \
		echo "  vision skill $$n: linked here, kept out of git"; \
	done
