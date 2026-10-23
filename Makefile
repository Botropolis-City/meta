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

perf-busy ::
	@[ -n "${PERF_BUILD}" ] || { echo "set PERF_BUILD to a directory perf-pprof-build made"; exit 2; }
	$(LOG) "Replaying a busy desk against ${PERF_BUILD} (performance/method.md, run 6)"
	@flock /tmp/botropolis-land.lock performance/tools/perf-busy-city ${PERF_BUILD}

publishable :: docs-check
	$(LOG) "Checking nothing unpublishable is in the repository"
	@tools/check-publishable

AGENT = claude --agent $(1) -n "$(2)" $(if ${REMOTE},--remote-control)

roadmap-manager ::
	$(LOG) "Starting the roadmap manager (docs/roles.md)"
	@$(call AGENT,roadmap-manager,roadmap manager)

design-agent ::
	$(LOG) "Starting the design agent (docs/roles.md)"
	@$(call AGENT,design-agent,design agent)

performance-manager ::
	$(LOG) "Starting the performance manager (docs/roles.md)"
	@$(call AGENT,performance-manager,performance manager)

auditor ::
	$(LOG) "Starting the auditor (docs/roles.md)"
	@$(call AGENT,auditor,auditor)

AGENTS_TMUX ?= botropolis
AGENT_WINDOWS := design:design-agent roadmap:roadmap-manager benchmark:performance-manager

agents ::
	$(LOG) "Starting design, roadmap and benchmark in tmux session ${AGENTS_TMUX}, with Remote Control"
	@if ! tmux has-session -t "=${AGENTS_TMUX}" 2>/dev/null; then \
		i=1; \
		for w in ${AGENT_WINDOWS}; do \
			name=$${w%%:*}; role=$${w#*:}; \
			cmd="make -C $(CURDIR) $$role REMOTE=1; exec $$SHELL"; \
			if [ $$i = 1 ]; then \
				tmux new-session -d -s "${AGENTS_TMUX}" -n "$$name" -c "$(CURDIR)" "$$cmd"; \
				[ "$$(tmux display-message -p -t "=${AGENTS_TMUX}:$$name" '#I')" = 1 ] \
					|| tmux move-window -s "=${AGENTS_TMUX}:$$name" -t "=${AGENTS_TMUX}:1"; \
			else \
				tmux new-window -t "=${AGENTS_TMUX}:$$i" -n "$$name" -c "$(CURDIR)" "$$cmd"; \
			fi; \
			i=$$((i + 1)); \
		done; \
		tmux select-window -t "=${AGENTS_TMUX}:1"; \
	fi
	@if [ -n "$$TMUX" ]; then tmux switch-client -t "=${AGENTS_TMUX}"; else tmux attach-session -t "=${AGENTS_TMUX}"; fi

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
