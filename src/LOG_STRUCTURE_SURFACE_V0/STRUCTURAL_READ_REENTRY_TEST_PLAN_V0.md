# STRUCTURAL_READ_REENTRY_TEST_PLAN_V0

Status:
test_plan

## Purpose

Create a small real-user test surface for Structural Read.

The test is not whether users understand the theory.

The test is whether users can regain footing and conduct a basic investigation.

## Test users

Use 2 to 5 fresh users if available.

They do not need technical background.

## Test path

Ask the user to:

1. Open the GitHub repository.
2. Download the ZIP.
3. Extract the ZIP.
4. Open PREVIEW.
5. Open OpenStack.html.
6. Survey the upper/global frame.
7. Select a region.
8. Inspect the lower/local frame.
9. Use the mouse wheel to change lens size.
10. Save at least one card.
11. Move somewhere else.
12. Return using the saved card.
13. Describe what they think the tool helped them do.

## Observe

Record where the user:

- hesitates
- gets lost
- misunderstands a control
- misses a useful feature
- asks what something means
- wants interpretation
- successfully regains footing
- finds something interesting
- saves a card
- returns to a card

## Do not help too early

Let small confusion appear.

Only intervene if the user is blocked.

The goal is to observe footing loss, not prevent it.

## Questions after use

Ask:

- Was it easy to open?
- Was it clear what to do first?
- Did the upper and lower frames make sense?
- Did the mouse wheel behavior make sense?
- Did saving cards make sense?
- Could you return to where you had been?
- What felt useful?
- What felt unclear?
- What instruction would have helped at the start?

## Boundary

No theory explanation.

No product pitch.

No AI claims.

No anomaly claims.

No root-cause claims.

No interpretation.

This is a re-entry and orientation test only.

## Next implementation should be pulled by test observations

Possible future work:

- simpler download instructions
- first-session guide
- preview landing page
- card explanation
- lens-size explanation
- short video
- try-your-own-log wrapper

Do not choose until observations are gathered.

## Compression

Watch where footing is lost.

Then improve only that.
