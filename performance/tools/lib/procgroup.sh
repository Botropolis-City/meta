# shellcheck shell=bash
#
# Keep a perf tool and everything it starts in one process group, and stop that
# whole group when the tool exits or is signalled, so nothing it started is ever
# orphaned (2026-10-22: a timed-out perf-busy-city left a `go build` behind).
#
# Usage, at the top of a tool, before it starts anything:
#
#   . "${here}/lib/procgroup.sh"
#   procgroup_lead "$@"
#   ...
#   procgroup_on_exit cleanup     # instead of `trap cleanup EXIT`
#
# A tool that does not lead its own group (run from make, flock or another
# tool) starts a copy of itself in a new session and stays behind as a small
# launcher: it passes the copy's exit status back, turns INT, TERM and HUP into
# a TERM for the copy's whole group, and if the launcher is killed outright the
# copy notices within a second and stops itself.
#
# Bash defers a trap until a foreground command finishes, so anything long (a
# `go build`) belongs in the background with a `wait` on its pid.

procgroup_cleanup=""

procgroup_lead() {
	if [[ "$(ps -o pgid= -p $$ | tr -d ' ')" != "$$" ]]; then
		procgroup_launch "$@"
	fi
	if [[ -n "${PROCGROUP_LAUNCHER:-}" ]]; then
		local launcher="${PROCGROUP_LAUNCHER}" self=$$
		unset PROCGROUP_LAUNCHER
		(
			trap - TERM
			while kill -0 "${launcher}" 2>/dev/null; do sleep 1; done
			kill -TERM "${self}" 2>/dev/null
		) </dev/null >/dev/null 2>&1 &
		disown
	fi
	trap 'procgroup_finish $?' EXIT
	trap 'procgroup_finish 129' HUP
	trap 'procgroup_finish 130' INT
	trap 'procgroup_finish 143' TERM
}

procgroup_launch() {
	local child status
	{
		trap - INT QUIT
		PROCGROUP_LAUNCHER=$$ exec setsid -w "$0" "$@"
	} &
	child=$!
	trap 'kill -TERM -- "-${child}" 2>/dev/null' HUP INT TERM
	while :; do
		status=0
		wait "${child}" || status=$?
		kill -0 "${child}" 2>/dev/null || break
	done
	exit "${status}"
}

procgroup_on_exit() {
	procgroup_cleanup="$1"
}

procgroup_finish() {
	local status="$1"
	trap - EXIT HUP INT TERM
	if [[ -n "${procgroup_cleanup}" ]]; then
		"${procgroup_cleanup}" || true
	fi
	trap '' TERM
	kill -TERM -- "-$$" 2>/dev/null || true
	trap - TERM
	wait 2>/dev/null || true
	exit "${status}"
}
