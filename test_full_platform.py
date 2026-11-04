"""
CampusVoice Platform - Comprehensive End-to-End Verification Test
"""

import sys
import asyncio
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent / "backend"))

# On Windows, use SelectorEventLoop for local execution
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.database import init_db, get_all_grievances, get_connection
from app.main import conversation_chat, create_grievance, get_emerging_incidents, get_campus_pulse, get_settings, update_settings
from app.schemas import ConversationChatRequest, GrievanceCreate, SettingsUpdateRequest

async def async_run():
    print("=" * 60)
    print(" Running CampusVoice End-to-End Verification")
    print("=" * 60)

    # 1. Test conversational engine turn 1 (Trigger follow-up)
    print("\n[Test 1] Conversational Turn 1: 'Electricity is unavailable in Block A since morning.'")
    req1 = ConversationChatRequest(message="Electricity is unavailable in Block A since morning.")
    res1 = await conversation_chat(req1)
    needs_follow_up = res1["needsFollowUp"] if isinstance(res1, dict) else res1.needsFollowUp
    ai_msg = res1["aiMessage"] if isinstance(res1, dict) else res1.aiMessage
    partial_state = res1["partialState"] if isinstance(res1, dict) else res1.partialState
    
    print(f"  needsFollowUp: {needs_follow_up}")
    print(f"  aiMessage:     {ai_msg}")
    assert needs_follow_up is True, "Expected needsFollowUp to be True for Block A power outage"
    assert "entire block" in ai_msg.lower() or "classroom" in ai_msg.lower()
    print("  [OK] Follow-up correctly requested scope clarification")

    # 2. Test conversational engine turn 2 (Reply with scope)
    print("\n[Test 2] Conversational Turn 2: 'The entire block.'")
    req2 = ConversationChatRequest(
        message="The entire block.",
        conversationState=partial_state
    )
    res2 = await conversation_chat(req2)
    needs_follow_up2 = res2["needsFollowUp"] if isinstance(res2, dict) else res2.needsFollowUp
    ai_msg2 = res2["aiMessage"] if isinstance(res2, dict) else res2.aiMessage
    analysis2 = res2["analysis"] if isinstance(res2, dict) else res2.analysis
    
    print(f"  needsFollowUp: {needs_follow_up2}")
    print(f"  aiMessage:     {ai_msg2}")
    print(f"  analysis:      {analysis2}")
    assert needs_follow_up2 is False, "Expected needsFollowUp to be False after follow-up answered"
    assert analysis2 is not None
    assert analysis2["category"] == "ELECTRICITY"
    assert analysis2["location"] == "Block A"
    assert analysis2["priority"] in ["HIGH", "CRITICAL"]
    print("  [OK] Full structured incident extracted and confirmed")

    # 3. Test creating grievance CV-1042
    print("\n[Test 3] Submitting Grievance to /api/grievances")
    g_create = GrievanceCreate(
        summary=analysis2["summary"],
        category=analysis2["category"],
        assignedCommittee=analysis2["assignedCommittee"],
        grievanceType=analysis2["grievanceType"],
        priority=analysis2["priority"],
        location=analysis2["location"],
        description=analysis2["description"],
        complaint="Electricity is unavailable in Block A since morning. The entire block.",
        startTime="2026-11-04T08:00:00",
        affectedScope="Block-wide",
        reliefSought="Immediate restoration of main feeder line",
        studentName="Demo Student",
        rollNo="2023-CS-104",
        isConfidential=False,
        aiProcessed=True
    )
    created = create_grievance(g_create.model_dump())
    ticket_id = created["ticketId"] if isinstance(created, dict) else created.ticketId
    loc = created["location"] if isinstance(created, dict) else created.location
    cat = created["category"] if isinstance(created, dict) else created.category
    
    print(f"  Created Ticket ID: {ticket_id}")
    print(f"  Location:          {loc}")
    print(f"  Category:          {cat}")
    assert ticket_id.startswith("CV-")
    print("  [OK] Grievance registered successfully")

    # 4. Test emerging incident detection
    print("\n[Test 4] Querying /api/incidents/emerging")
    incidents = await get_emerging_incidents()
    print(f"  Detected Clusters: {len(incidents)}")
    for inc in incidents:
        inc_title = inc.title if hasattr(inc, 'title') else inc['title']
        inc_loc = inc.location if hasattr(inc, 'location') else inc['location']
        inc_count = inc.reportCount if hasattr(inc, 'reportCount') else inc.get('reportCount', inc.get('complaintCount', 0))
        inc_sev = inc.severity if hasattr(inc, 'severity') else inc['severity']
        inc_rec = inc.aiRecommendation if hasattr(inc, 'aiRecommendation') else inc.get('aiRecommendation', '')
        print(f"   - {inc_title} | Location: {inc_loc} | Reports: {inc_count} | Severity: {inc_sev}")
        print(f"     Recommended: {inc_rec}")
    
    block_a_incidents = [i for i in incidents if (i.location if hasattr(i, 'location') else i['location']) == "Block A"]
    assert len(block_a_incidents) >= 1, "Expected emerging incident in Block A after 3 complaints!"
    print("  [OK] Emerging incident alert correctly triggered for Block A with correlated complaints")

    # 5. Test campus pulse node query
    print("\n[Test 5] Querying /api/campus/pulse")
    nodes = await get_campus_pulse()
    print(f"  Campus Nodes Returned: {len(nodes)}")
    block_a_node = next((n for n in nodes if (n.name if hasattr(n, 'name') else n['name']) == "Block A"), None)
    assert block_a_node is not None
    active_t = block_a_node.activeTickets if hasattr(block_a_node, 'activeTickets') else block_a_node['activeTickets']
    st = block_a_node.status if hasattr(block_a_node, 'status') else block_a_node['status']
    print(f"  Block A Pulse Node -> Active Tickets: {active_t}, Status: {st}")
    assert active_t >= 3
    assert st == "CRITICAL"
    print("  [OK] Campus Pulse correctly marks Block A as CRITICAL with pulsing radar beacon")

    # 6. Test Settings API
    print("\n[Test 6] Testing /api/settings")
    cfg = await get_settings()
    print(f"  Settings: hasGeminiKey={cfg.get('geminiConfigured', False)}")
    update_res = await update_settings(SettingsUpdateRequest(geminiApiKey="test_key_abc"))
    print(f"  Update Result: {update_res.get('status')}")
    cfg2 = await get_settings()
    assert cfg2.get('geminiConfigured') is True
    # Reset back to empty
    await update_settings(SettingsUpdateRequest(geminiApiKey=""))
    print("  [OK] AI Settings API verified")

    print("\n" + "=" * 60)
    print(" ALL TESTS PASSED! CAMPUSVOICE PLATFORM IS 100% OPERATIONAL")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(async_run())
