# CAPABILITY_USE_RULE_V0

Status: BUILD

## Purpose

Define how LLM capability may enter Master Bench work.

## Rule

Capability enters only through a packet.

## Required before capability use

- active packet
- allowed movement
- forbidden movement
- evidence signals
- stop condition
- review boundary

## Capability may do

- draft orientation
- draft bounded text
- propose bounded file content
- inspect supplied context
- perform narrow code tasks when packeted

## Capability may not do

- self-authorize
- widen scope
- decide meaning
- promote status
- edit frozen floors
- replace human review
- create next packets unless explicitly asked

## Review rule

Model output is draft until reviewed.

## Receipt rule

Receipt behavior, not just output.

Record:
- stayed bounded?
- used supplied context?
- invented facts?
- widened scope?
- stopped?
- required correction?

## Boundary

Capability is useful inside bounds.
Capability is not authority.
