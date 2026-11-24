// Multi-view WebGL stage: one canvas, several scenes side by side, each with its own
// post-processing chain, plus an adaptive quality controller.
//
// Each view renders into a fixed-size buffer (its widest possible viewport) and the final
// composite shows a centred crop of it. Animating the split therefore wipes between the views
// instead of squeezing them, and never reallocates render targets mid-animation.
import {
  NeutralToneMapping, HalfFloatType, Mesh, OrthographicCamera, PCFShadowMap, PlaneGeometry,
  Scene, ShaderMaterial, SRGBColorSpace, Vector2, WebGLRenderer, WebGLRenderTarget,
} from "three";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { GTAOPass } from "three/addons/postprocessing/GTAOPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

/** Quality tiers, cheapest first. `post` enables the composer chain. */
export const TIERS = [
  { name: "baixa", post: false, ao: false, bloom: false, msaa: 0, dprCap: 1, shadows: 1024 },
  { name: "média", post: true, ao: false, bloom: true, msaa: 0, dprCap: 1.5, shadows: 1024 },
  { name: "alta", post: true, ao: true, bloom: true, msaa: 4, dprCap: 2, shadows: 2048 },
];

// Vignette and a faint film grain, applied after tone mapping (sRGB space).
const FinishShader = {
  uniforms: { tDiffuse: { value: null }, time: { value: 0 }, vignette: { value: 0.07 }, grain: { value: 0.018 } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
  fragmentShader: `
    uniform sampler2D tDiffuse; uniform float time, vignette, grain; varying vec2 vUv;
    float hash(vec2 p){ p = fract(p * vec2(443.897, 441.423)); p += dot(p, p.yx + 19.19); return fract((p.x + p.y) * p.x); }
    void main(){
      vec4 c = texture2D(tDiffuse, vUv);
      vec2 d = vUv - 0.5;
      c.rgb *= 1.0 - vignette * smoothstep(0.25, 0.85, dot(d, d) * 2.2);
      c.rgb += (hash(vUv * 1024.0 + time) - 0.5) * grain;
      gl_FragColor = c;
    }`,
};

const CompositeShader = {
  uniforms: { map: { value: null }, uvScale: { value: new Vector2(1, 1) }, uvOffset: { value: new Vector2(0, 0) } },
  vertexShader: "varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }",
  fragmentShader: "uniform sampler2D map; uniform vec2 uvScale, uvOffset; varying vec2 vUv; void main(){ gl_FragColor = texture2D(map, vUv * uvScale + uvOffset); }",
};

class ViewPipeline {
  constructor(renderer, view, tier) {
    this.view = view;
    this.tier = tier;
    this.composer = null;
    if (!tier.post) return;
    const rt = new WebGLRenderTarget(2, 2, { type: HalfFloatType, samples: tier.msaa });
    const c = new EffectComposer(renderer, rt);
    c.renderToScreen = false;
    c.addPass(new RenderPass(view.scene, view.camera));
    if (tier.ao) {
      this.ao = new GTAOPass(view.scene, view.camera, 2, 2);
      this.ao.updateGtaoMaterial({ radius: view.aoRadius ?? 0.6, thickness: 1, distanceFallOff: 1, scale: 1 });
      this.ao.blendIntensity = view.aoIntensity ?? 0.85;
      c.addPass(this.ao);
    }
    if (tier.bloom) c.addPass(new UnrealBloomPass(new Vector2(2, 2), 0.9, 0.4, 2.6));
    c.addPass(new OutputPass());
    this.finish = new ShaderPass(FinishShader);
    c.addPass(this.finish);
    this.composer = c;
  }

  setSize(w, h, dpr) {
    if (!this.composer) return;
    this.composer.setPixelRatio(dpr);
    this.composer.setSize(w, h);
  }

  dispose() {
    if (!this.composer) return;
    for (const p of this.composer.passes) p.dispose?.();
    this.composer.dispose();
  }
}

export class Stage {
  /**
   * @param canvas  target canvas
   * @param makeViews  (renderer) => [{ scene, camera, frame(aspect), setShadowSize? }]
   * @param opts       { tier: 0..2 | null (auto), adaptive: boolean, onTierChange }
   */
  constructor(canvas, makeViews, opts = {}) {
    this.canvas = canvas;
    this.renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: "high-performance" });
    this.renderer.outputColorSpace = SRGBColorSpace;
    this.renderer.toneMapping = NeutralToneMapping;
    this.renderer.toneMappingExposure = 1.0;
    this.renderer.shadowMap.enabled = true;
    this.renderer.shadowMap.type = PCFShadowMap;
    this.renderer.autoClear = false;
    this.views = makeViews(this.renderer);
    this.adaptive = opts.adaptive !== false && opts.tier == null;
    this.tierIndex = opts.tier ?? Stage.initialTier();
    this.quad = new Mesh(new PlaneGeometry(2, 2), new ShaderMaterial({ ...CompositeShader, depthTest: false, depthWrite: false }));
    this.quadScene = new Scene();
    this.quadScene.add(this.quad);
    this.quadCam = new OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.size = { w: 1, h: 1 };
    this.slow = 0; this.ema = 1 / 60;
    this.onTierChange = opts.onTierChange || (() => {});
    this._build();
  }

  static initialTier() {
    const mobile = matchMedia("(pointer: coarse)").matches || innerWidth < 720;
    const cores = navigator.hardwareConcurrency || 4;
    if (mobile) return cores >= 8 ? 1 : 0;
    return cores >= 8 ? 2 : 1;
  }

  get tier() { return TIERS[this.tierIndex]; }

  _build() {
    this.pipes?.forEach((p) => p.dispose());
    const t = this.tier;
    this.renderer.setPixelRatio(Math.min(devicePixelRatio || 1, t.dprCap));
    for (const v of this.views) v.setShadowSize?.(t.shadows);
    this.pipes = this.views.map((v) => new ViewPipeline(this.renderer, v, t));
    this.resize(this.size.w, this.size.h, this.layout);
    this.onTierChange(this.tierIndex);
  }

  /** layout: { vertical, buffer: [ {w,h} per view ] } in CSS pixels. */
  resize(w, h, layout) {
    this.size = { w, h };
    this.layout = layout;
    this.renderer.setSize(w, h, false);
    if (!layout) return;
    const dpr = this.renderer.getPixelRatio();
    this.pipes.forEach((p, i) => p.setSize(layout.buffer[i].w, layout.buffer[i].h, dpr));
  }

  /** Track frame time and step quality down when the device cannot keep up. */
  observe(dt) {
    if (!this.adaptive || dt <= 0) return;
    this.ema += (dt - this.ema) * 0.05;
    this.slow = this.ema > 1 / 38 ? this.slow + 1 : Math.max(0, this.slow - 2);
    if (this.slow > 90 && this.tierIndex > 0) {
      this.tierIndex -= 1;
      this.slow = 0; this.ema = 1 / 60;
      this._build();
    }
  }

  /**
   * rects: [{ x, y, w, h }] viewport per view in CSS px (y from the bottom).
   * Each view's buffer is centred and cropped to its rect.
   */
  render(rects, time) {
    const r = this.renderer;
    r.setRenderTarget(null);
    r.setScissorTest(false);
    r.clear();
    r.setScissorTest(true);
    this.views.forEach((v, i) => {
      const rect = rects[i];
      const buf = this.layout.buffer[i];
      const pipe = this.pipes[i];
      if (rect.w < 1 || rect.h < 1) return;
      if (!pipe.composer) {
        v.frame(buf.w / buf.h);
        v.camera.setViewOffset(buf.w, buf.h, (buf.w - rect.w) / 2, (buf.h - rect.h) / 2, rect.w, rect.h);
        r.setViewport(rect.x, rect.y, rect.w, rect.h);
        r.setScissor(rect.x, rect.y, rect.w, rect.h);
        r.render(v.scene, v.camera);
        v.camera.clearViewOffset();
        return;
      }
      v.frame(buf.w / buf.h);
      if (pipe.finish) pipe.finish.uniforms.time.value = time % 100;
      pipe.composer.render();
      r.setRenderTarget(null);
      const m = this.quad.material.uniforms;
      m.map.value = pipe.composer.readBuffer.texture;
      m.uvScale.value.set(rect.w / buf.w, rect.h / buf.h);
      m.uvOffset.value.set((1 - rect.w / buf.w) / 2, (1 - rect.h / buf.h) / 2);
      r.setViewport(rect.x, rect.y, rect.w, rect.h);
      r.setScissor(rect.x, rect.y, rect.w, rect.h);
      r.render(this.quadScene, this.quadCam);
    });
  }
}
