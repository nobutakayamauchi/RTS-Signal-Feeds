import copy
import unittest

from scripts.discovery_sweep import SweepError, evaluate


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.req = {"sweep_id":"s","subject":"x","frozen_workload_ref":"w","reference_time":"2026-08-14T02:00:00+09:00","source_classes":[{"id":"official","required":True,"max_age_seconds":86400},{"id":"github","required":True,"max_age_seconds":86400}],"policy":{"min_rounds":3,"quiet_rounds_to_saturate":2}}
    def q(self,sid,n,status="SEARCHED",derived=None,at="2026-08-14T01:30:00+09:00"):
        x={"source_class":sid,"query":f"q{n}","status":status,"searched_at":at,"derived_from_candidate_ids":list(derived or [])}
        if status=="SEARCHED": x["evidence_ref"]=f"e{n}-{sid}"
        return x
    def h(self,cid,mat="MATERIAL",follow=False,at="2026-08-14T01:30:00+09:00"):
        return {"candidate_id":cid,"source_class":"github","source_ref":f"gh:{cid}","captured_at":at,"materiality":mat,"relation_types":["competitor"],"followup_required":follow}
    def base(self):
        return {"rounds":[{"round":1,"queries":[self.q("official",1),self.q("github",1)],"hits":[self.h("a",follow=True)]},{"round":2,"queries":[self.q("official",2,derived=["a"]),self.q("github",2,derived=["a"])],"hits":[]},{"round":3,"queries":[self.q("official",3),self.q("github",3)],"hits":[]}]}
    def test_valid(self): self.assertEqual(evaluate(self.req,self.base())["decision"],"SEARCH_SATURATED_UNDER_CURRENT_EVIDENCE")
    def test_empty_round(self):
        e=self.base();e["rounds"][1]["queries"]=[]
        with self.assertRaises(SweepError): evaluate(self.req,e)
    def test_blocked_tail(self):
        e=self.base();e["rounds"][2]["queries"]=[self.q("official",3),self.q("github",3,"BLOCKED")]
        self.assertEqual(evaluate(self.req,e)["decision"],"BLOCKED_COVERAGE_OR_UNKNOWN")
    def test_new_material_resets(self):
        e=self.base();e["rounds"][2]["hits"]=[self.h("b")]
        self.assertEqual(evaluate(self.req,e)["decision"],"CONTINUE_SWEEP")
    def test_stale(self):
        e=self.base();e["rounds"][0]["hits"][0]["captured_at"]="2020-01-01T00:00:00+09:00"
        with self.assertRaises(SweepError): evaluate(self.req,e)
    def test_followup_required(self):
        e=self.base()
        for q in e["rounds"][1]["queries"]:q["derived_from_candidate_ids"]=[]
        self.assertIn("UNRESOLVED_FRONTIER_FOLLOWUP",evaluate(self.req,e)["blocking_states"])
    def test_same_round_not_followup(self):
        e=self.base();e["rounds"][0]["queries"][0]["derived_from_candidate_ids"]=["a"]
        for q in e["rounds"][1]["queries"]:q["derived_from_candidate_ids"]=[]
        self.assertIn("UNRESOLVED_FRONTIER_FOLLOWUP",evaluate(self.req,e)["blocking_states"])
    def test_old_max_new_policy_rejected(self):
        r=copy.deepcopy(self.req);r["policy"]["max_new_material_per_quiet_round"]=1
        with self.assertRaises(SweepError): evaluate(r,self.base())



if __name__ == "__main__":
    unittest.main()
