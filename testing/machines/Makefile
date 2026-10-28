GREEN := "\033[0;32m"
NC := "\033[0;0m"

LOG := @sh -c '\
       printf ${GREEN}; \
       echo -e "\n> $$1\n"; \
       printf ${NC}' VALUE

-include .env

MACHINE ?= soak
DESKTOP ?= gnome
BOTROPOLIS ?= ../../botropolis
SOAK_SESSIONS ?= 200
SOAK_PROJECTS ?= 150
PLUGINS := $${XDG_CACHE_HOME:-$$HOME/.cache}/botropolis-machines/plugins

REFS := --robot-user-ref "${ROBOT_USER_REF}" --robot-password-ref "${ROBOT_PASSWORD_REF}" --hcloud-token-ref "${HCLOUD_TOKEN_REF}"
BUCKET := --bucket-url "${BUCKET_URL}" --bucket-write-id-ref "${BUCKET_WRITE_ID_REF}" --bucket-write-secret-ref "${BUCKET_WRITE_SECRET_REF}" --bucket-read-id-ref "${BUCKET_READ_ID_REF}" --bucket-read-secret-ref "${BUCKET_READ_SECRET_REF}"
OPTS := --desktop ${DESKTOP} $(if ${IPV4},--ipv4) $(if ${MAX_HOURS},--max-hours ${MAX_HOURS}) $(if ${KEEP_ON_FAILURE},--keep-on-failure)

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

plan ::
	$(LOG) "Pricing and planning the ${MACHINE} machine; nothing is spent"
	@./machines plan ${MACHINE} ${REFS} ${OPTS}

apply ::
	$(LOG) "Pricing the ${MACHINE} machine, then making it once you approve"
	@./machines apply ${MACHINE} ${REFS} ${OPTS}

# The synthetic history comes from botropolis-demo synth-home (item 248).
run-soak ::
	@[ -n "${PERF_BUILD}" ] || { echo "set PERF_BUILD to a directory holding botropolis and botropolisd"; exit 2; }
	$(LOG) "Choosing the soak box from the plan, booking its own cancellation, soaking ${PERF_BUILD} on it for 8 hours with its report going to the bucket, and cancelling it"
	@work=$$(mktemp -d); trap 'rm -rf "$$work"' EXIT; \
		go -C "${BOTROPOLIS}" build -o "$$work/botropolis-demo" ./cmd/botropolis-demo && \
		"$$work/botropolis-demo" synth-home --home "$$work/synthetic" \
			--sessions ${SOAK_SESSIONS} --projects ${SOAK_PROJECTS} --seed 245 && \
		./machines run soak ${REFS} ${BUCKET} ${OPTS} --build "${PERF_BUILD}" --stager "$$work/botropolis-demo" \
			--corpus "${BOTROPOLIS}/demo" --history "$$work/synthetic/.claude" --soak-flags "${PERF_SOAK_FLAGS}"

run-wayland ::
	@[ -n "${SCRIPT}" ] || { echo "set SCRIPT to the test to run in the ${DESKTOP} session"; exit 2; }
	$(LOG) "Pricing a ${DESKTOP} VM, then running ${SCRIPT} on it and destroying it"
	@./machines run wayland ${REFS} ${OPTS} --script "${SCRIPT}"

destroy ::
	$(LOG) "Destroying the ${MACHINE} machine"
	@./machines destroy ${MACHINE} ${REFS} ${OPTS} $(if ${SERVER},--server ${SERVER})

validate ::
	$(LOG) "Caching the hcloud provider in ${PLUGINS} and validating cloud/ (needs the network, no account)"
	@mkdir -p "${PLUGINS}"; work=$$(mktemp -d); trap 'rm -rf "$$work"' EXIT; \
		TF_PLUGIN_CACHE_DIR="${PLUGINS}" TF_DATA_DIR="$$work" terraform -chdir=cloud init -backend=false -input=false && \
		TF_PLUGIN_CACHE_DIR="${PLUGINS}" TF_DATA_DIR="$$work" terraform -chdir=cloud validate
