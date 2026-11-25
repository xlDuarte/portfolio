"""Rolling-element bearing kinematics: characteristic defect frequencies from the geometry.

For n rolling elements of diameter d on pitch diameter D with contact angle φ, and the inner race
turning at f_r with the outer race fixed (Harris, *Rolling Bearing Analysis*; Randall and Antoni,
MSSP 25, 2011):

    FTF  = f_r/2 · (1 − d/D·cos φ)                 cage
    BPFO = n · FTF                                  outer-race defect
    BPFI = n·f_r/2 · (1 + d/D·cos φ)                inner-race defect
    BSF  = D·f_r/(2d) · (1 − (d/D·cos φ)²)          ball spin; a ball defect strikes both races,
                                                    so the impact rate is 2·BSF

These assume rolling without slip. Real bearings slip by 1–2 %, which is why every frequency
search below has a tolerance band rather than an exact bin.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians

INCH = 0.0254


@dataclass(frozen=True)
class Bearing:
    name: str
    n_balls: int
    ball_d: float          # m
    pitch_d: float         # m
    contact_deg: float = 0.0

    @property
    def ratio(self) -> float:
        return self.ball_d / self.pitch_d * cos(radians(self.contact_deg))

    def orders(self) -> dict[str, float]:
        """Defect frequencies as multiples of the shaft frequency."""
        g = self.ratio
        ftf = 0.5 * (1 - g)
        return {"FTF": ftf, "BPFO": self.n_balls * ftf, "BPFI": 0.5 * self.n_balls * (1 + g),
                "BSF": self.pitch_d / (2 * self.ball_d) * (1 - g * g), "2BSF": self.pitch_d / self.ball_d * (1 - g * g)}

    def frequencies(self, fr: float) -> dict[str, float]:
        return {k: v * fr for k, v in self.orders().items()}


# Drive-end bearing of the CWRU rig: SKF 6205-2RS JEM deep-groove ball bearing (CWRU data center).
SKF_6205 = Bearing("SKF 6205-2RS JEM", 9, 0.3126 * INCH, 1.537 * INCH, 0.0)

# Defect frequency that each fault class excites (ball faults: two impacts per ball revolution).
FAULT_FREQ = {"OR": "BPFO", "IR": "BPFI", "B": "2BSF"}
