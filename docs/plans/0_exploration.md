# Groups

## Notes

- Designing a primitive for organization on the internet.
- There are groups and subjects. Any human or computer can be a subject. A subject can belong to many groups.
- Subjects express preferences: yes/no on whether a given subject should be in a given group.
  - Self-referential: a subject's preference about their own membership.
  - Third-party: a subject's preference about another subject's membership. Only third-party preferences from a group's current members count toward majority.
- Tick rules (there's a daily tick when group membership changes for all groups):
  - **Join**: a subject joins a group if they want to (self-referential yes) _and_ a majority of the group's current members want them in (third-party yes). Otherwise they don't join.
  - **Leave**: a subject's self-referential preference is decisive — if they want to leave, they leave, regardless of the group's preference.
  - **Expulsion**: if a subject wants to stay but a majority of the _other_ current members (their own vote doesn't count) want them out, they're removed. Multiple subjects can be expelled from a group in the same tick, each evaluated independently against the group's membership at the start of the tick.
  - **Majority**: strictly more than half of the relevant voters; ties don't count. In a 2-person group, majority requires both members to agree.
    - Exception for expulsion: a tie counts as a vote to expel, not a vote to stay. A subject needs strict majority support among the other members to remain; a tie goes against them.
  - **Group size**: leaving/expulsion shrinks a group by one. A group only disbands at 0 members — a group of 1 is a valid, persistent state.
  - **Formation**: any subject can unilaterally form a group of 1 (no one else exists yet to vote). Growth from there uses the ordinary join rule, so joining a group of 1 already requires mutual agreement between the two subjects. This is the only way groups come into existence — including groups that have previously disbanded.
- **Voting is continuous, ticks are periodic**: a subject can set a preference (self-referential or third-party, for any group and any subject) at any time. Once set, it stays valid indefinitely and counts in every future tick until the subject explicitly changes it — there's no need to re-affirm a preference each tick. A subject can hold many standing preferences at once, across every group and subject they care about.
  - Accepted tradeoff: a preference cast once can outlive the voter's actual current opinion, or their activity on the platform entirely ("zombie votes") — there's no expiration or decay. This is a deliberate choice for now, not an oversight.
