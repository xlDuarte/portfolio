# F1 Physics Labs

Three independent engineering applications in the F1/Motorsport site:
- /motorsport/active-aero/
- /motorsport/energy-recovery/
- /motorsport/lap-simulator/

## Data
Aero and ERS can load the existing observed Bahrain 2024 OpenF1 recut, session 9472. This is approximately four minutes, **not a single lap**. No fabricated acquisition is generated on failure.
All initial vehicle values are explicitly labeled editable assumptions, not team specifications or regulatory limits.
The application accepts numeric CSV with comma delimiters, or semicolon delimiters with decimal commas, 2–50,000 rows, up to 5 MB. Headers must match. No missing-value substitution.

## FastF1 export
Install Python dependencies:
```sh
python -m pip install -r site/motorsport/physics/requirements.txt
python site/motorsport/physics/export_fastf1.py 2024 Bahrain Q VER --output fastf1-export
```
Import telemetry.csv for aero/ERS and track.csv for laptime. Preserve provenance.json and identify the session in the UI.
The script selects the fastest accurate timed lap and exports native car samples. It derives track curvature from observed decimetre position, smoothing, arc-length resampling and three-point curvature. The derived geometry is not a surveyed track. Rejects nonclosed traces >100 m; inspect smaller closure seams. Review position-derived.csv and repeat with finer discretization. Telemetry extent may not equal timing-line lap duration.
No actual FastF1 download was executed during implementation; live provider availability remains an external dependency. No token or private data required.

## Aerodynamics
Import front_deg,rear_deg,cd,cl_down. All coefficients must use the entered reference area and identical force conventions. Positive cl_down means downforce. Drag and downforce are q*A*C with q=rho*v²/2, integrated using observed timestamps. Compare configurations under fixed observed speed; this does not predict lap improvement. Active control chooses minimum Cd above the user threshold, maximum Cl_down during braking or below threshold minus hysteresis. It assumes instantaneous actuation, without FIA permission logic; exports state, angles and forces per sample.
Download parametric OpenSCAD NACA0012 concept wing pair, with separate front/rear angles. OpenSCAD can export geometry for a meshing workflow. The concept is not an F1 car CAD model and does not derive CFD coefficients.
**External CFD procedure:** inspect/repair geometry; create fluid domain, appropriate ground/wheel conditions and boundary layers; run independent steady-state cases per wing configuration; establish residual/force convergence and at least three mesh levels; document Reynolds number, turbulence model, reference area and force axes; export the coefficient CSV. OpenFOAM/Fluent is not bundled or executed in the browser. No pressure contours or validated CFD results are claimed.

## Energy recovery
Kinetic-energy decrease minus estimated aero drag work supplies brake work only while the left-sample brake flag is active. Regeneration is limited by mechanical kW, charging efficiency and battery space. Deployment meets positive kinetic-energy increments only; constrained by wheel kW, discharge efficiency and charge. Every interval records charge and cumulative energy.
Initial + brake work = final + friction + wheel deployment + conversion losses.
This omits road slope, rolling resistance, rotational inertia, brake distribution, battery thermal behavior, true torque demand and FIA rules. Public brake is binary. SoC is modeled, not measured.

## Laptime
Periodic point-mass forward/backward relaxation, constant wheel power, quadratic drag/downforce, friction-circle longitudinal availability and explicit braking cap. Segment length <=50 m. Convergence threshold 1e-6 m/s, up to 500 sweeps. Independent estimates: no tire load sensitivity, suspension, power map, banking or racing-line optimization. Discretization and solver approximations must be checked against independent data before engineering decisions.
The UI reports +/-10% one-at-a-time sensitivity for six parameters. This is a local comparative study, not a globally optimized design. A/B uses identical input data; changing source clears reference.

## Validation
```sh
node tests/f1_physics_checks.mjs
node --check site/motorsport/physics/app.mjs
python -m py_compile site/motorsport/physics/export_fastf1.py
```
Analytical fixtures test energy conservation, empty/full/tiny battery limits, efficiency and input rejection, quadratic aero force, trapezoidal drag work, circular-track analytic time, periodic closure, refinement consistency, grip/downforce monotonic behavior, sensitivity and CAD validation.
Fixtures are test-only. No claim of vehicle-level or CFD validation.
Browser UI QA is not available in the current environment; automated model/syntax checks do not replace it.

## References
- https://docs.fastf1.dev/
- https://github.com/theOehrly/Fast-F1/blob/main/fastf1/core.py
- https://openf1.org/
- https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/
- https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/
