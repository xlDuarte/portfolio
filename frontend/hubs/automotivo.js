// Automotivo hub: two garages. Left an open-wheel single-seater (Fórmula 1), right a GT car
// (Porsche Cup category). Generic procedural cars, not replicas. Roller doors open in the intro;
// each turntable spins with inertia when dragged (physics.js → Turntable).
import { BoxGeometry, CanvasTexture, Group, Mesh, MeshStandardMaterial, RepeatWrapping, SRGBColorSpace } from "three";
import { mountStage } from "./common.js";
import { studio, bindSpin } from "./studio.js";
import { gtCar, openWheeler } from "../scene/cars.js";
import { C } from "../hero/palette.js";

function rollerDoor(width, height) {
  const c = document.createElement("canvas");
  c.width = 8; c.height = 64;
  const g = c.getContext("2d");
  g.fillStyle = "#d4d9df"; g.fillRect(0, 0, 8, 64);
  g.fillStyle = "#b9c0c8"; g.fillRect(0, 0, 8, 4);
  const tex = new CanvasTexture(c);
  tex.colorSpace = SRGBColorSpace;
  tex.wrapS = tex.wrapT = RepeatWrapping;
  tex.repeat.set(1, 18);
  const door = new Mesh(new BoxGeometry(width, height, 0.08), new MeshStandardMaterial({ map: tex, metalness: 0.5, roughness: 0.45 }));
  door.castShadow = true;
  return door;
}

function garage(env, car, washTint) {
  const s = studio(env, { washTint });
  const holder = new Group();
  holder.position.y = s.plinthTop;
  holder.add(car.root);
  s.scene.add(holder);
  const door = rollerDoor(9.5, 4.2);
  door.position.set(0, 2.1, 4.4);
  s.scene.add(door);
  const lintel = new Mesh(new BoxGeometry(10, 0.5, 0.6), new MeshStandardMaterial({ color: 0x9aa3ad, metalness: 0.6, roughness: 0.4 }));
  lintel.position.set(0, 4.45, 4.4);
  s.scene.add(lintel);
  const doorState = { open: 0 };
  return Object.assign(s, {
    doorState,
    step(dt) {
      holder.rotation.y = s.table.step(dt, s.held?.());
      door.position.y = 2.1 + doorState.open * 4.0;
      door.visible = doorState.open < 0.99;
      lintel.visible = doorState.open < 0.99;
    },
  });
}

export function mount(root) {
  return mountStage(root, {
    split: true,
    build(env) {
      const f1 = garage(env, openWheeler({ paint: C.graphite, accent: C.auto }), C.autoWash);
      const gt = garage(env, gtCar({ paint: 0xd5d9de, accent: C.auto }), C.autoWash);
      gt.state.azimuth = -0.7;
      return [f1, gt];
    },
    onResize() {},
    warmup(views) { for (const v of views) v.doorState.open = 1; },
    intro(tl, views) {
      views.forEach((v, i) => {
        tl.to(v.doorState, { open: 1, duration: 1.6, ease: "power3.inOut" }, 0.2 + i * 0.15);
        v.state.distance = 1.25;
        tl.to(v.state, { distance: 1, duration: 2 }, 0.3);
      });
      const view = root.querySelector(".hub-view");
      views.forEach((v, i) => {
        const half = root.querySelector(`[data-half="${i}"]`);
        const spin = bindSpin(half, v.table, () => view.getBoundingClientRect());
        v.held = spin.held;
      });
    },
  });
}
