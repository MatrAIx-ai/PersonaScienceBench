"""Publication boundaries and endpoint policy; synthetic data only."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location('trace_export', Path(__file__).resolve().parents[1] / 'scripts/export_trial1_traces.py')
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


def row(score, status='finished'):
    return {'source': 'bixbench', 'status': status, 'native_results': [
        {'episode_id': 'fixture', 'status': 'scored', 'evaluation': {'metrics': {'correct': score}}}
    ]}


def test_repair_selection_does_not_choose_highest_score():
    original, repair = row(1), row(0)
    chosen, label = exporter.choose_endpoint(original, repair)
    assert chosen is repair and label == 'repaired'
    assert exporter.score(chosen) == 0


def test_failed_repair_preserves_evaluable_original():
    original = row(0)
    chosen, label = exporter.choose_endpoint(original, row(1, 'infrastructure_error'))
    assert chosen is original and label == 'original_fallback'


def test_infrastructure_only_slot_has_no_endpoint():
    assert exporter.choose_endpoint(row(0, 'infrastructure_error'), None) == (None, 'unavailable')


def test_shared_fields_only_no_tool_or_private_payloads():
    events = [
        {'type': 'actor_command_result', 'payload': {'stdout': 'PRIVATE_TOOL_CANARY'}},
        {'type': 'agent_handoff', 'payload': {'answer': 'Shared answer', 'evidence': 'Shared evidence', 'private': 'PRIVATE_FIELD_CANARY'}},
        {'type': 'researcher_reply', 'payload': {'answer': 'Shared reply'}},
    ]
    result = exporter.conversation(events)
    assert [r['event_index'] for r in result] == [1, 2]
    assert 'PRIVATE' not in str(result)
    assert result[0]['fields']['evidence'] == 'Shared evidence'


def test_credentials_redacted_and_message_fences_cannot_escape():
    # Construct a synthetic pattern; no real credential in this fixture.
    token = 'sk-' + 'proj-' + 'A' * 40
    result = exporter.fenced('````\n' + token)
    assert token not in result and '[REDACTED_CREDENTIAL]' in result
    assert result.startswith('`````text\n') and result.endswith('\n`````')
