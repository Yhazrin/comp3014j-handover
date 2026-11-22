# Brightspace group: 25
# Members: Haoze Yang; Fanshu Yu; Heng Zhang (student numbers to be confirmed)
# AI-assisted development is disclosed in the accompanying report.
"""VASH: Volatility-Aware Safety Handover, queue-memory candidate.

Only current device observations and instance-local history are used.
The serving SINR is inferred under a common interference-plus-noise model;
an inconsistent observation falls back to a conservative power-margin rule.
No files, network access, scenario identifiers, external models or randomness.
"""
import math
import statistics


class StudentPolicy:
    def reset(self, config: dict) -> None:
        self.step_ms = max(1.0, float(config.get("delta_t_ms", 200)))
        self.last_request_ms = -1e12
        self.history = {}
        self.recent_queue = 0.0
        self.variance = {}
        self.serving = None
        self.bad_since_ms = None
        # Selected offline on practice seeds 1-6 only.
        self.source_margin = 0.0
        self.target_floor_db = -3.0
        self.target_sigma_weight = 1.0
        self.variance_alpha = 0.15
        self.cooldown_ms = 1000

    def decide(self, observation: dict) -> dict:
        stay = {"action": "stay"}
        # Coarse motion regimes selected on the development split only.
        # Speed is an observation, not a route/mode/scenario identifier.
        speed = float(observation.get("speed_mps") or 0)
        if speed < 3:
            self.source_margin, self.target_floor_db, self.target_sigma_weight = -1.0, -4.0, 0.5
        elif speed < 15:
            self.source_margin, self.target_floor_db, self.target_sigma_weight = 1.0, -2.0, 1.5
        else:
            self.source_margin, self.target_floor_db, self.target_sigma_weight = 0.0, -3.0, 1.0
        serving = observation.get("serving_cell_id")
        power = observation.get("serving_rsrp_dbm")
        now = observation.get("time_ms", 0)
        if serving is None or power is None or not math.isfinite(power):
            return stay
        candidates, totals = [], []
        for c in observation.get("candidates", []):
            p, s = c.get("rsrp_dbm"), c.get("rs_sinr_db")
            if not c.get("eligible", True) or c.get("cell_id") == serving:
                continue
            if p is None or s is None or not math.isfinite(p) or not math.isfinite(s):
                continue
            if abs(p - power) > 150 or abs(s) > 150:
                continue
            candidates.append(c)
            # Normalise powers to the serving power for numerical stability.
            totals.append(10.0 ** ((p - power) / 10) * (1 + 10.0 ** (-s / 10)))
        if not candidates:
            return stay
        total = statistics.median(totals)
        if total <= 1 or max(totals) / min(totals) >= 1.12:
            # No trustworthy SINR reconstruction: do not treat it as ground truth.
            self.history.clear()
            self.variance.clear()
            self.bad_since_ms = None
            best = max(candidates, key=lambda c: (c["rsrp_dbm"], str(c["cell_id"])))
            if (best["rsrp_dbm"] - power > 6 and best["rs_sinr_db"] >= 0
                    and now - self.last_request_ms >= self.cooldown_ms):
                self.last_request_ms = now
                return {"action": "request_handover", "target_cell_id": best["cell_id"]}
            return stay
        serving_sinr = -10 * math.log10(total - 1)
        values = {serving: serving_sinr}
        values.update({c["cell_id"]: c["rs_sinr_db"] for c in candidates})
        new_variance = {}
        for cid, value in values.items():
            old = self.history.get(cid)
            if old is None:
                new_variance[cid] = 1.0
            else:
                elapsed_steps = max(1.0, (now - old[1]) / self.step_ms)
                change_squared = (value - old[0]) ** 2 / elapsed_steps
                new_variance[cid] = ((1 - self.variance_alpha) * self.variance.get(cid, 1.0)
                                     + self.variance_alpha * change_squared)
        self.variance = new_variance
        self.history = {cid: (value, now) for cid, value in values.items()}
        if serving != self.serving:
            self.bad_since_ms = None
            self.serving = serving
        if serving_sinr < -8:
            if self.bad_since_ms is None:
                self.bad_since_ms = now
        elif serving_sinr > -6:
            self.bad_since_ms = None
        prolonged_risk = self.bad_since_ms is not None and now - self.bad_since_ms >= 800
        floor = -6.0 if prolonged_risk else self.target_floor_db
        boundary = -8 + self.source_margin
        # Recent unserved bytes are evidence of demand, even if this tick's queue is empty.
        self.recent_queue = max(float(observation.get("queue_backlog_bytes", 0)), self.recent_queue * 0.95 ** (self.step_ms / 200.0))
        demand = min(1.0, self.recent_queue / 100000)
        boundary += 2.0 * demand
        options = []
        for c in candidates:
            quality = c["rs_sinr_db"] - self.target_sigma_weight * math.sqrt(self.variance[c["cell_id"]])
            if quality >= floor:
                options.append((quality, str(c["cell_id"]), c))
        if not options:
            return stay
        best = max(options, key=lambda item: item[:2])[2]
        strength = best["rs_sinr_db"] - self.target_sigma_weight * math.sqrt(self.variance[best["cell_id"]])
        confidence = max(0.0, min(1.0, strength / 6.0))
        boundary += confidence
        if prolonged_risk:
            boundary = max(boundary, -6.0)
        if (serving_sinr < boundary and best["rs_sinr_db"] - serving_sinr > 3
                and now - self.last_request_ms >= self.cooldown_ms):
            self.last_request_ms = now
            return {"action": "request_handover", "target_cell_id": best["cell_id"]}
        return stay
