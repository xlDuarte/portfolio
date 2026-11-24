// Small, deterministic physics kernels used by the scenes. Pure JavaScript, no three.js,
// SI units unless stated. Each kernel documents its model; unit tests live in physics.test.mjs.

export const G0 = 9.80665;                   // m/s², standard gravity
export const SIGMA = 5.670374419e-8;         // W/(m² K⁴), Stefan–Boltzmann

// ---------------------------------------------------------------------------
// Hot particles (sparks): ballistic flight with quadratic drag, Newtonian convection plus
// radiative cooling, inelastic bounces with Coulomb friction on a height field.
//
//   dv/dt = g - k |v| v,        k = ½ ρ_air C_d A / m            [1/m]
//   dT/dt = -h (T - T_amb) - r (T⁴ - T_amb⁴),  h = h_c A/(m c), r = ε σ A/(m c)
//
// Defaults: 0.2 mm molten-steel droplet (m ≈ 3.3e-8 kg, A ≈ 3.1e-8 m²) → k ≈ 0.27 1/m,
// h ≈ 3.9 1/s, r ≈ 3.5e-13 1/(K³ s). Cooling below `visibleK` ends the particle.
export const STEEL_SPARK = Object.freeze({
  drag: 0.27, convection: 3.9, radiation: 3.5e-13, ambientK: 300, visibleK: 850,
  restitution: 0.38, friction: 0.45, contactCoolingK: 120, maxLife: 3.5,
});

export class SparkField {
  constructor(capacity, params = STEEL_SPARK) {
    this.capacity = capacity;
    this.params = { ...params };
    this.count = 0;
    const f = () => new Float32Array(capacity);
    this.px = f(); this.py = f(); this.pz = f();
    this.vx = f(); this.vy = f(); this.vz = f();
    this.temp = f(); this.age = f();
  }

  emit(x, y, z, vx, vy, vz, tempK) {
    if (this.count >= this.capacity) return false;
    const i = this.count++;
    this.px[i] = x; this.py[i] = y; this.pz[i] = z;
    this.vx[i] = vx; this.vy[i] = vy; this.vz[i] = vz;
    this.temp[i] = tempK; this.age[i] = 0;
    return true;
  }

  /** Advance by dt seconds. `groundY(x, z)` returns the surface height in metres. */
  step(dt, groundY) {
    const p = this.params;
    const sub = Math.max(1, Math.ceil(dt / (1 / 240)));
    const h = dt / sub;
    const cool = Math.exp(-p.convection * h);
    for (let s = 0; s < sub; s++) {
      for (let i = 0; i < this.count; i++) {
        const vx = this.vx[i], vy = this.vy[i], vz = this.vz[i];
        const sp = Math.hypot(vx, vy, vz);
        // Semi-implicit Euler; the drag term is integrated implicitly for stability at high speed.
        const damp = 1 / (1 + p.drag * sp * h);
        this.vx[i] = vx * damp;
        this.vy[i] = (vy - G0 * h) * damp;
        this.vz[i] = vz * damp;
        this.px[i] += this.vx[i] * h;
        this.py[i] += this.vy[i] * h;
        this.pz[i] += this.vz[i] * h;
        const ground = groundY(this.px[i], this.pz[i]);
        if (this.py[i] < ground) {
          this.py[i] = ground;
          const vn = -this.vy[i];
          this.vy[i] = vn * p.restitution;
          // Coulomb friction: tangential speed drops by μ·(1+e)·|v_n|, never reverses.
          const vt = Math.hypot(this.vx[i], this.vz[i]);
          if (vt > 0) {
            const k = Math.max(0, vt - p.friction * (1 + p.restitution) * vn) / vt;
            this.vx[i] *= k; this.vz[i] *= k;
          }
          this.temp[i] -= p.contactCoolingK;
        }
        const T = this.temp[i], Ta = p.ambientK;
        this.temp[i] = Ta + (T - Ta) * cool - p.radiation * (T ** 4 - Ta ** 4) * h;
        this.age[i] += h;
      }
    }
    // Swap-remove dead particles (order is irrelevant for rendering).
    for (let i = 0; i < this.count; ) {
      if (this.temp[i] < p.visibleK || this.age[i] > p.maxLife) this._kill(i); else i++;
    }
  }

  _kill(i) {
    const j = --this.count;
    if (i === j) return;
    for (const a of [this.px, this.py, this.pz, this.vx, this.vy, this.vz, this.temp, this.age]) a[i] = a[j];
  }
}

// ---------------------------------------------------------------------------
// Rigid body, sphere-approximated contact against static axis-aligned boxes.
// Impulse-based response: restitution on the normal, Coulomb friction on the tangent,
// tangential slip converted into spin (solid cube inertia I = m s²/6). Fixed 240 Hz step.
export class RigidBody {
  constructor({ position, velocity = [0, 0, 0], spin = [0, 0, 0], radius, mass = 1, side,
                restitution = 0.25, friction = 0.55, gravity = G0 }) {
    this.p = [...position]; this.v = [...velocity]; this.w = [...spin];
    this.q = [0, 0, 0, 1];            // orientation quaternion (x, y, z, w)
    this.r = radius; this.m = mass; this.e = restitution; this.mu = friction; this.g = gravity;
    const s = side ?? radius * 2;
    this.I = (mass * s * s) / 6;
    this.sleeping = false; this.rest = 0; this.acc = 0;
  }

  step(dt, colliders) {
    if (this.sleeping) return;
    this.acc += dt;
    const h = 1 / 240;
    while (this.acc >= h) {
      this.acc -= h;
      this.v[1] -= this.g * h;
      for (let k = 0; k < 3; k++) this.p[k] += this.v[k] * h;
      for (const c of colliders) this._collide(c);
      // Integrate orientation: q += ½ (ω ⊗ q) h, then renormalise.
      const [x, y, z, w] = this.q, [wx, wy, wz] = this.w;
      this.q = [x + 0.5 * h * (wx * w + wy * z - wz * y), y + 0.5 * h * (wy * w + wz * x - wx * z),
                z + 0.5 * h * (wz * w + wx * y - wy * x), w - 0.5 * h * (wx * x + wy * y + wz * z)];
      const n = Math.hypot(...this.q);
      this.q = this.q.map((c) => c / n);
      const moving = Math.hypot(...this.v) > 0.04 || Math.hypot(...this.w) > 0.15;
      this.rest = moving ? 0 : this.rest + h;
      if (this.rest > 0.4) { this.sleeping = true; this.v = [0, 0, 0]; this.w = [0, 0, 0]; return; }
    }
  }

  _collide(box) {
    const cp = [0, 1, 2].map((k) => Math.min(Math.max(this.p[k], box.min[k]), box.max[k]));
    const d = [this.p[0] - cp[0], this.p[1] - cp[1], this.p[2] - cp[2]];
    const dist = Math.hypot(...d);
    if (dist >= this.r || dist === 0) return;
    const n = d.map((c) => c / dist);
    for (let k = 0; k < 3; k++) this.p[k] += n[k] * (this.r - dist);
    // Velocity of the contact point: v + ω × (−r n)
    const rc = n.map((c) => -c * this.r);
    const wxr = [this.w[1] * rc[2] - this.w[2] * rc[1], this.w[2] * rc[0] - this.w[0] * rc[2], this.w[0] * rc[1] - this.w[1] * rc[0]];
    const vc = this.v.map((c, k) => c + wxr[k]);
    const vn = vc[0] * n[0] + vc[1] * n[1] + vc[2] * n[2];
    if (vn >= 0) return;
    const jn = -(1 + this.e) * vn * this.m;
    const vt = vc.map((c, k) => c - vn * n[k]);
    const vtLen = Math.hypot(...vt);
    // Tangential impulse needed to stop slip, capped by the friction cone.
    const effMass = 1 / (1 / this.m + (this.r * this.r) / this.I);
    const jt = Math.min(this.mu * jn, vtLen * effMass);
    const t = vtLen > 1e-9 ? vt.map((c) => c / vtLen) : [0, 0, 0];
    for (let k = 0; k < 3; k++) this.v[k] += (jn * n[k] - jt * t[k]) / this.m;
    // Angular impulse: τ = rc × (−jt t)
    const imp = t.map((c) => -jt * c);
    const tau = [rc[1] * imp[2] - rc[2] * imp[1], rc[2] * imp[0] - rc[0] * imp[2], rc[0] * imp[1] - rc[1] * imp[0]];
    for (let k = 0; k < 3; k++) this.w[k] = (this.w[k] + tau[k] / this.I) * 0.985;
  }

  energy() {
    const ke = 0.5 * this.m * (this.v[0] ** 2 + this.v[1] ** 2 + this.v[2] ** 2);
    const re = 0.5 * this.I * (this.w[0] ** 2 + this.w[1] ** 2 + this.w[2] ** 2);
    return ke + re + this.m * this.g * this.p[1];
  }
}

// ---------------------------------------------------------------------------
// Second-order follower: x'' = ω² (u − x) − 2 ζ ω x'. Used for chassis pitch and roll, which
// respond to measured accelerations like a sprung mass on its suspension.
export class SpringDamper {
  constructor(freqHz = 2, zeta = 0.7, x0 = 0) {
    this.w = 2 * Math.PI * freqHz; this.z = zeta; this.x = x0; this.v = 0;
  }
  step(target, dt) {
    const sub = Math.max(1, Math.ceil(dt / (1 / 240)));
    const h = dt / sub;
    for (let i = 0; i < sub; i++) {
      this.v += (this.w * this.w * (target - this.x) - 2 * this.z * this.w * this.v) * h;
      this.x += this.v * h;
    }
    return this.x;
  }
}

// ---------------------------------------------------------------------------
// Turntable with rotational inertia: I dω/dt = τ_drive − c ω − μ sign(ω) (+ user impulses).
// Viscous (c) and Coulomb (μ) friction stop a free spin in finite time; a small drive torque
// (feed-forward + proportional) settles the table back to `idle` rad/s after a flick.
export class Turntable {
  constructor({ inertia = 1, viscous = 0.35, coulomb = 0.12, idle = 0.18, drive = 0.25 } = {}) {
    Object.assign(this, { I: inertia, c: viscous, mu: coulomb, idle, drive });
    this.theta = 0; this.omega = idle;
  }
  impulse(angularMomentum) { this.omega += angularMomentum / this.I; }
  step(dt, held = false) {
    if (held) return this.theta;
    const sub = Math.max(1, Math.ceil(dt / (1 / 240))), h = dt / sub;
    for (let i = 0; i < sub; i++) {
      // Motor: feed-forward that balances friction at idle, plus a proportional correction.
      const motor = this.c * this.idle + this.mu * Math.sign(this.idle) + this.drive * (this.idle - this.omega);
      const tau = motor - this.c * this.omega;
      const fr = this.mu * Math.sign(this.omega);
      const next = this.omega + ((tau - fr) / this.I) * h;
      // Coulomb friction cannot reverse the motion within one step.
      this.omega = Math.sign(next) !== Math.sign(this.omega) && Math.abs(tau) < this.mu ? 0 : next;
      this.theta += this.omega * h;
    }
    return this.theta;
  }
}
