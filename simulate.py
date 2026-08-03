import math
import random
from dataclasses import dataclass, field
from itertools import count
from typing import Optional


@dataclass
class GroupSystem:
    subjects: set = field(default_factory=set)
    groups: dict = field(default_factory=dict)
    self_prefs: dict = field(default_factory=dict)
    third_party_prefs: dict = field(default_factory=dict)
    _group_ids: count = field(default_factory=count)

    def add_subject(self, subject):
        self.subjects.add(subject)

    def form_group(self, subject) -> int:
        self.add_subject(subject)
        group_id = next(self._group_ids)
        self.groups[group_id] = {subject}
        self.self_prefs[(subject, group_id)] = True
        return group_id

    def set_self_preference(self, subject, group_id, wants_in: bool):
        self.add_subject(subject)
        self.self_prefs[(subject, group_id)] = wants_in

    def set_third_party_preference(self, voter, target, group_id, wants_in: bool):
        self.add_subject(voter)
        self.add_subject(target)
        self.third_party_prefs[(voter, target, group_id)] = wants_in

    def _self_pref(self, subject, group_id) -> Optional[bool]:
        return self.self_prefs.get((subject, group_id))

    def _third_party_votes(self, voters, target, group_id) -> tuple[int, int]:
        yes = no = 0
        for voter in voters:
            vote = self.third_party_prefs.get((voter, target, group_id))
            if vote is True:
                yes += 1
            elif vote is False:
                no += 1
        return yes, no

    def _is_majority_yes(self, voters, target, group_id) -> bool:
        yes, no = self._third_party_votes(voters, target, group_id)
        total = yes + no
        return total > 0 and yes > total / 2

    def tick(self):
        next_groups = {}
        for group_id, snapshot in self.groups.items():
            remaining = set()
            for subject in snapshot:
                if self._self_pref(subject, group_id) is False:
                    continue
                others = snapshot - {subject}
                yes, no = self._third_party_votes(others, subject, group_id)
                if no >= yes and (yes + no) > 0:
                    continue
                remaining.add(subject)

            for applicant in self.subjects - snapshot:
                if self._self_pref(applicant, group_id) is True and \
                        self._is_majority_yes(snapshot, applicant, group_id):
                    remaining.add(applicant)

            if remaining:
                next_groups[group_id] = remaining

        self.groups = next_groups

    def print_state(self, tick_number):
        print(f"tick {tick_number}:")
        if not self.groups:
            print("  (no groups)")
        for group_id, members in sorted(self.groups.items()):
            print(f"  group {group_id}: {sorted(members)}")


def run(system: GroupSystem, ticks: int):
    system.print_state(0)
    for t in range(1, ticks + 1):
        system.tick()
        system.print_state(t)


def scenario_cycle_instability():
    print("=== scenario: rock-paper-scissors non-reciprocal cycle ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.groups[group] = {"A", "B", "C"}
    s.set_self_preference("A", group, True)
    s.set_self_preference("B", group, True)
    s.set_self_preference("C", group, True)
    s.set_third_party_preference("A", "B", group, True)
    s.set_third_party_preference("A", "C", group, False)
    s.set_third_party_preference("B", "C", group, True)
    s.set_third_party_preference("B", "A", group, False)
    s.set_third_party_preference("C", "A", group, True)
    s.set_third_party_preference("C", "B", group, False)
    run(s, 3)
    print()


def scenario_bootstrap_and_join():
    print("=== scenario: bootstrap a group of 1, then grow it ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.set_self_preference("B", group, True)
    s.set_third_party_preference("A", "B", group, True)
    run(s, 1)

    s.set_self_preference("C", group, True)
    s.set_third_party_preference("A", "C", group, False)
    s.set_third_party_preference("B", "C", group, True)
    run(s, 1)
    print()


def scenario_expulsion_overrides_self_preference():
    print("=== scenario: majority expels a member who wants to stay ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.groups[group] = {"A", "B", "C", "D"}
    for subject in ("A", "B", "C", "D"):
        s.set_self_preference(subject, group, True)
    for voter in ("B", "C", "D"):
        s.set_third_party_preference(voter, "A", group, False)
    run(s, 1)
    print()


def scenario_self_veto_to_leave():
    print("=== scenario: self-preference to leave is decisive ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.groups[group] = {"A", "B"}
    s.set_self_preference("A", group, False)
    s.set_self_preference("B", group, True)
    s.set_third_party_preference("B", "A", group, True)
    run(s, 1)
    print()


def scenario_join_tie_fails():
    print("=== scenario: a tied vote fails to admit a new applicant (asymmetric with expulsion) ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.groups[group] = {"A", "B"}
    s.set_self_preference("A", group, True)
    s.set_self_preference("B", group, True)
    s.set_self_preference("C", group, True)
    s.set_third_party_preference("A", "C", group, True)
    s.set_third_party_preference("B", "C", group, False)
    run(s, 1)
    print()


def scenario_cascading_expulsion():
    print("=== scenario: removing one member flips a tie for another member on a later tick ===")
    s = GroupSystem()
    group = s.form_group("A")
    s.groups[group] = {"A", "B", "C", "D"}
    for subject in ("A", "B", "C", "D"):
        s.set_self_preference(subject, group, True)
    s.set_third_party_preference("B", "D", group, False)
    s.set_third_party_preference("C", "D", group, False)
    s.set_third_party_preference("A", "D", group, True)
    s.set_third_party_preference("B", "A", group, False)
    s.set_third_party_preference("C", "A", group, True)
    s.set_third_party_preference("D", "A", group, True)
    run(s, 2)
    print()


def scenario_multi_group_membership():
    print("=== scenario: the same subject can be expelled from one group but stay in another ===")
    s = GroupSystem()
    group1 = s.form_group("A")
    s.groups[group1] = {"A", "B", "C"}
    group2 = s.form_group("A")
    s.groups[group2] = {"A", "D", "E"}
    for subject in ("A", "B", "C", "D", "E"):
        s.set_self_preference(subject, group1, True)
        s.set_self_preference(subject, group2, True)
    s.set_third_party_preference("B", "A", group1, False)
    s.set_third_party_preference("C", "A", group1, False)
    s.set_third_party_preference("D", "A", group2, True)
    s.set_third_party_preference("E", "A", group2, True)
    run(s, 1)
    print()


def scenario_random_stress():
    print("=== scenario: random preferences among 6 subjects, watch for convergence ===")
    import random
    random.seed(7)
    subjects = ["A", "B", "C", "D", "E", "F"]
    s = GroupSystem()
    group = s.form_group(subjects[0])
    s.groups[group] = set(subjects)
    for subject in subjects:
        s.set_self_preference(subject, group, True)
    for voter in subjects:
        for target in subjects:
            if voter != target:
                s.set_third_party_preference(voter, target, group, random.choice([True, False]))
    run(s, 5)
    print()


def scenario_large_population_dynamic(seed, ticks=15):
    import random
    print(f"=== scenario: 100 subjects, 3 groups, evolving preferences, free group formation (seed={seed}) ===")
    random.seed(seed)

    subjects = [f"s{i}" for i in range(100)]
    types = {subj: random.choice([0, 1, 2]) for subj in subjects}
    tolerance = {subj: random.random() for subj in subjects}

    s = GroupSystem()
    initial_groups = [s.form_group(subjects[k]) for k in range(3)]
    remaining = subjects[3:]
    random.shuffle(remaining)
    for i, subj in enumerate(remaining):
        gid = initial_groups[i % 3]
        s.groups[gid].add(subj)
        s.set_self_preference(subj, gid, True)

    def plurality_type(members):
        if not members:
            return None
        counts = {}
        for m in members:
            counts[types[m]] = counts.get(types[m], 0) + 1
        return max(counts, key=counts.get)

    def print_stats(tick_number):
        parts = []
        seen = set()
        for gid, members in sorted(s.groups.items()):
            seen |= members
            counts = [0, 0, 0]
            for m in members:
                counts[types[m]] += 1
            parts.append(f"g{gid}(n={len(members)}, types={counts})")
        parts.append(f"unaffiliated={len(set(subjects) - seen)}")
        print(f"tick {tick_number}: " + ", ".join(parts))

    print_stats(0)
    for t in range(1, ticks + 1):
        for subj in subjects:
            tolerance[subj] = min(1.0, max(0.0, tolerance[subj] + random.uniform(-0.1, 0.1)))

        for gid, members in list(s.groups.items()):
            plurality = plurality_type(members)
            for m in members:
                s.set_self_preference(m, gid, types[m] == plurality)
            for voter in members:
                for target in members:
                    if voter == target:
                        continue
                    same_type = types[voter] == types[target]
                    wants_in = True if same_type else (random.random() < tolerance[voter])
                    s.set_third_party_preference(voter, target, gid, wants_in)

        current_members = set().union(*s.groups.values()) if s.groups else set()
        for subj in subjects:
            if subj in current_members:
                continue
            candidate_gid = next(
                (gid for gid, members in s.groups.items() if plurality_type(members) == types[subj]),
                None,
            )
            if candidate_gid is not None:
                s.set_self_preference(subj, candidate_gid, True)
                for voter in s.groups[candidate_gid]:
                    same_type = types[voter] == types[subj]
                    wants_in = True if same_type else (random.random() < tolerance[voter])
                    s.set_third_party_preference(voter, subj, candidate_gid, wants_in)
            else:
                has_solo = any(subj in members and len(members) == 1 for members in s.groups.values())
                if not has_solo:
                    s.form_group(subj)

        s.tick()
        print_stats(t)
    print()


def scenario_rich_multi_group(seed, ticks=40, population=150, num_attractors=4, membership_cap=None, bootstrap_leniency=1.0):
    cap_label = membership_cap if membership_cap is not None else "none"
    print(
        f"=== scenario: {population} subjects, 2D traits, multi-group membership, {ticks} ticks, "
        f"cap={cap_label}, bootstrap_leniency={bootstrap_leniency} (seed={seed}) ==="
    )
    random.seed(seed)

    subjects = [f"s{i}" for i in range(population)]
    attractors = [(random.random(), random.random()) for _ in range(num_attractors)]
    trait = {}
    for subj in subjects:
        cx, cy = random.choice(attractors)
        trait[subj] = (
            min(1.0, max(0.0, random.gauss(cx, 0.08))),
            min(1.0, max(0.0, random.gauss(cy, 0.08))),
        )
    openness = {subj: random.uniform(0.1, 0.4) for subj in subjects}

    def distance(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def centroid(members):
        xs = [trait[m][0] for m in members]
        ys = [trait[m][1] for m in members]
        return (sum(xs) / len(xs), sum(ys) / len(ys))

    def compatible(voter, target):
        return distance(trait[voter], trait[target]) < openness[voter]

    s = GroupSystem()
    initial_groups = [s.form_group(subjects[k]) for k in range(num_attractors)]
    remaining = subjects[num_attractors:]
    random.shuffle(remaining)
    for i, subj in enumerate(remaining):
        gid = initial_groups[i % len(initial_groups)]
        s.groups[gid].add(subj)
        s.set_self_preference(subj, gid, True)

    def membership_counts():
        counts = {subj: 0 for subj in subjects}
        for members in s.groups.values():
            for m in members:
                counts[m] += 1
        return counts

    def print_summary(tick_number):
        sizes = sorted((len(m) for m in s.groups.values()), reverse=True)
        counts = membership_counts()
        histogram = {}
        for c in counts.values():
            histogram[c] = histogram.get(c, 0) + 1
        print(
            f"tick {tick_number}: groups={len(s.groups)}, sizes={sizes}, "
            f"memberships-per-subject-histogram={dict(sorted(histogram.items()))}"
        )

    print_summary(0)
    for t in range(1, ticks + 1):
        for subj in subjects:
            openness[subj] = min(0.6, max(0.05, openness[subj] + random.uniform(-0.03, 0.03)))

        for gid, members in list(s.groups.items()):
            center = centroid(members)
            for m in members:
                s.set_self_preference(m, gid, distance(trait[m], center) < openness[m])
            for voter in members:
                for target in members:
                    if voter != target:
                        s.set_third_party_preference(voter, target, gid, compatible(voter, target))

        counts = membership_counts()
        pending = {subj: 0 for subj in subjects}
        for subj in subjects:
            for gid, members in list(s.groups.items()):
                if subj in members:
                    continue
                if membership_cap is not None and counts[subj] + pending[subj] >= membership_cap:
                    s.set_self_preference(subj, gid, False)
                    continue
                center = centroid(members)
                wants_in = distance(trait[subj], center) < openness[subj]
                s.set_self_preference(subj, gid, wants_in)
                if wants_in:
                    pending[subj] += 1
                    for voter in members:
                        s.set_third_party_preference(voter, subj, gid, compatible(voter, subj))
            if counts[subj] == 0 and pending[subj] == 0:
                near_miss_gid = next(
                    (
                        gid for gid, members in s.groups.items()
                        if distance(trait[subj], centroid(members)) < openness[subj] * bootstrap_leniency
                    ),
                    None,
                )
                if near_miss_gid is not None:
                    s.set_self_preference(subj, near_miss_gid, True)
                    for voter in s.groups[near_miss_gid]:
                        s.set_third_party_preference(voter, subj, near_miss_gid, compatible(voter, subj))
                else:
                    has_solo = any(subj in members and len(members) == 1 for members in s.groups.values())
                    if not has_solo:
                        s.form_group(subj)

        s.tick()
        if t % 5 == 0 or t == ticks:
            print_summary(t)
    print()


if __name__ == "__main__":
    scenario_cycle_instability()
    scenario_bootstrap_and_join()
    scenario_expulsion_overrides_self_preference()
    scenario_self_veto_to_leave()
    scenario_join_tie_fails()
    scenario_cascading_expulsion()
    scenario_multi_group_membership()
    scenario_random_stress()
    scenario_large_population_dynamic(seed=1)
    scenario_large_population_dynamic(seed=2)
    scenario_rich_multi_group(seed=1, membership_cap=5, bootstrap_leniency=2.0)
    scenario_rich_multi_group(seed=2, membership_cap=5, bootstrap_leniency=2.0)
    scenario_rich_multi_group(seed=3, num_attractors=6, membership_cap=5, bootstrap_leniency=2.0)
