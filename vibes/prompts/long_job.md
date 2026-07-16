=== Long-run discipline (read first; obey strictly) ===

MISSION_DURATION_SECS=18000

At the very first action, run:
  START_EPOCH="$(date +%s)"
and write that value to /tmp/long_run_start_epoch.txt with the Write tool
(or a single bash redirect). At any later check, compute:
  ELAPSED="$(($(date +%s) - $(cat /tmp/long_run_start_epoch.txt)))"
  REMAINING="$((MISSION_DURATION_SECS - ELAPSED))"
and report ELAPSED in your next user-facing message.

HARD RULES:

1. While ELAPSED < MISSION_DURATION_SECS you are FORBIDDEN from:
   - writing a "Final summary" / "Mission complete" / "All done" message,
   - claiming the work is finished,
   - emptying your TodoWrite list and stopping,
   - asking the user "what would you like next?",
   - producing the closing paragraph-form commit message for the whole run.
   The ONLY allowed loop is: pick next queue item → execute → commit →
   recheck ELAPSED → if still < MISSION_DURATION_SECS, pick next item.

2. If your TodoWrite list reaches zero pending items AND
   ELAPSED < MISSION_DURATION_SECS, you MUST add at least 5 new items
   from the pre-seeded queue below before doing anything else. If the
   pre-seeded queue is exhausted, you MUST scan the repo (tech debt
   log, TODO/FIXME grep, open ADR action items, failing tests) for new
   work and add at least 5 items.

3. If you find yourself drafting a sentence that contains any of:
   "in summary", "to wrap up", "this completes", "final commit", "all
   patches landed", "summary writeup", "good stopping point",
   "transitioning to cleanup", BEFORE
   ELAPSED >= MISSION_DURATION_SECS, stop drafting that sentence,
   pick the next queue item, and execute it instead.

4. Time-check cadence: at the START of every 4th tool-using response
   (or sooner), run a single `date +%s` bash and print
   "ELAPSED: Xs / MISSION_DURATION_SECS — continuing with [task]".
   Do not let more than ~6 responses pass without a time check.

5. After ELAPSED >= MISSION_DURATION_SECS, transition to wrap-up:
   finish the in-flight patch, run validation, write the final summary.
   Do NOT keep starting large new tasks once past the threshold.

6. Stop conditions BEFORE the threshold are limited to genuine
   filesystem errors (permission denied, disk full, repo missing,
   corrupted required file). Compile errors, test failures, design
   uncertainty, and "I'm not sure what to do next" are NOT stop
   conditions — they are the next work item.

7. FAILURE MODE TO RECOGNIZE: declaring victory after a long time has passed.
   If your inner sense says "I'm at a clean stopping point" and ELAPSED <
   MISSION_DURATION_SECS, that sense is wrong. Add 5 queue items and continue.

Pre-seeded queue (work top-to-bottom, append more from the list at the
bottom of this message when this section runs short):

  COMPLETE TASKS FROM TODO.md
  WORK AUTONOMOUSLY.
  DO NOT ASK JON FOR INPUT. 

=== End long-run discipline ===
