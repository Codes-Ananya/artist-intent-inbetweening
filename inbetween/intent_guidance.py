"""Preregistered temporal intent mapping; no image or oracle access."""
EVENTS = frozenset(('path_turn', 'timing_change', 'pose_extremum', 'visibility_change'))
REPRESENTATIVES = {'early': 2, 'middle': 3, 'late': 5}


def phase_at(k, count=6):
    if count != 6 or not 1 <= k <= count:
        raise ValueError('Milestone 6 requires N=6 and k=1..6')
    t = k / (count + 1)
    return 'early' if t < 1/3 else 'middle' if t <= 2/3 else 'late'


def decide_intent(events):
    """Return ambiguity handling plus a separately labelled forced-choice ablation."""
    reason = None
    admitted = set()
    if not isinstance(events, list) or not events:
        reason = 'missing_intent'
    elif len(events) > 2 or any(not isinstance(e, dict) or set(e) != {'event', 'phase'}
                              or not isinstance(e['event'], str) or not isinstance(e['phase'], str)
                              or e['event'] not in EVENTS
                              or e['phase'] not in (*REPRESENTATIVES, 'unspecified') for e in events):
        reason = 'unsupported_intent'
    else:
        for event in events:
            admitted.update(REPRESENTATIVES.values() if event['phase'] == 'unspecified'
                            else [REPRESENTATIVES[event['phase']]])
        if len(admitted) > 1:
            reason = 'unspecified_phase' if any(e['phase'] == 'unspecified' for e in events) else 'conflicting_event_phases'
    return {'label': 'pre-registered method outputs', 'status': 'abstained' if reason else 'answered',
            'recommended_k': None if reason else min(admitted), 'abstention_reason': reason,
            'admitted_positions': sorted(admitted),
            'forced_choice_ablation_k': min(admitted) if admitted else 3}
