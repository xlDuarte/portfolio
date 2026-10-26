/* Real GLB geometry with a custom Red Bull livery and the user-supplied portrait.
 * Red Bull mark: https://www.logo.wine/logo/Red_Bull (cropped SVG viewBox).
 * Team trademarks belong to Red Bull; this is a portfolio livery, not an official driver replica.
 * Dependencies are pinned in the import map.
 */
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';

export async function activateAssetScene(THREE,opts){
 const {scene,renderer,pivot,procedural,portrait,uniforms,error} = opts;
 const reference=false;
 const base='https://storage.getlayers.ai/assets/kimi-04a9449ab2/hero/scene/';
 const files=['helmet3.glb','studio-light.hdr','noise.webp','person-diffuse.webp'];
 const urls=Object.fromEntries(files.map(f=>[f,base+f]));
 urls['person-diffuse.webp']=new URL('./assets/gabriel-racing.webp',import.meta.url).href;
 const textureLoader=new THREE.TextureLoader();
 const gltfLoader=new GLTFLoader();
 const draco=new DRACOLoader();
 draco.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.185.0/examples/jsm/libs/draco/gltf/');
 gltfLoader.setDRACOLoader(draco);
 const hdrLoader=new RGBELoader();
 const load=(url,fn)=>fn(url).catch(e=>{error(url,e);throw e});
 let loaded,environment;
 try{
  const results=await Promise.all([
   load(urls['helmet3.glb'],url=>gltfLoader.loadAsync(url)),
   load(urls['studio-light.hdr'],url=>hdrLoader.loadAsync(url)),
   ...files.slice(2).map(f=>load(urls[f],url=>textureLoader.loadAsync(url)))
  ]);
  loaded=results[0];environment=results[1];
  const tex=Object.fromEntries(files.slice(2).map((f,i)=>[f,results[i+2]]));
  tex['noise.webp'].wrapS=THREE.RepeatWrapping;tex['noise.webp'].wrapT=THREE.RepeatWrapping;
  tex['person-diffuse.webp'].colorSpace=THREE.SRGBColorSpace;
  const redBull=await load(new URL('./assets/red-bull.svg',import.meta.url).href,url=>textureLoader.loadAsync(url));
  redBull.colorSpace=THREE.SRGBColorSpace;
  const erase={uEraseCenter:{value:new THREE.Vector3(-1000,-1000,-1000)},uEraseActive:{value:0},uEraseRadius:{value:.62},uPixelRatio:{value:renderer.getPixelRatio()}};
  const pmrem=new THREE.PMREMGenerator(renderer);
  const env=pmrem.fromEquirectangular(environment).texture;
  const model=loaded.scene;
  const meshes=[];
  model.traverse(o=>{if(o.isMesh)meshes.push(o)});
  if(!meshes.length)throw new Error('GLB contained no renderable helmet geometry');
  model.updateMatrixWorld(true);
  let box=new THREE.Box3().setFromObject(model);
  const sz=box.getSize(new THREE.Vector3()),center=box.getCenter(new THREE.Vector3());
  const ratio=3.15/sz.y;
  model.scale.setScalar(ratio);model.position.copy(center).multiplyScalar(-ratio);
  model.position.y+=.14;model.position.z+=.35;
  model.rotation.y=.40;
  // Replace every baked Mercedes material with a custom Red Bull livery.
  // Object-space projection avoids inheriting the source model's packed UV artwork.
  for(const mesh of meshes){
   const mat=new THREE.MeshStandardMaterial({color:0xffffff,roughness:.32,metalness:.28,
     envMap:env,envMapIntensity:1.1,transparent:true,depthWrite:true,side:THREE.FrontSide});
   mat.onBeforeCompile=s=>{
     Object.assign(s.uniforms,erase,{uRedBull:{value:redBull}});
     s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec3 vHelmetPosition; varying vec3 vHelmetWorld;');
     s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nvHelmetPosition=position;vHelmetWorld=(modelMatrix*vec4(position,1.)).xyz;');
     s.fragmentShader=s.fragmentShader.replace('#include <common>',`
      #include <common>
      varying vec3 vHelmetPosition; varying vec3 vHelmetWorld;
      uniform sampler2D uRedBull;
      uniform vec3 uEraseCenter;
      uniform float uEraseActive,uEraseRadius,uPixelRatio;
     `);
     s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>',`
      #include <color_fragment>
      vec3 p=vHelmetPosition;
      vec3 navy=vec3(.009,.018,.065),red=vec3(.72,.008,.026),gold=vec3(1.,.58,.008);
      vec3 paint=navy;
      float stripe=abs(p.x);
      if(stripe<.20&&p.y>.64)paint=red;
      if(stripe>.20&&stripe<.235&&p.y>.64)paint=gold;
      // Dark mirrored visor and yellow seal on the front half of the shell.
      float visorTop=.22,visorBottom=-.12;
      if(p.z>.35&&p.y>visorBottom-.025&&p.y<visorTop+.025)paint=gold;
      if(p.z>.35&&p.y>visorBottom&&p.y<visorTop)paint=vec3(.012,.019,.032);
      // Project the authentic bulls + sun mark onto the forehead and chin.
      vec2 logoUV=vec2(p.x/.88+.5,(p.y-.44)/.35+.5);
      if(p.y<-.15)logoUV=vec2(p.x/.85+.5,(p.y+.43)/.34+.5);
      if(p.z>.25&&all(greaterThanEqual(logoUV,vec2(0.)))&&all(lessThanEqual(logoUV,vec2(1.)))){
        vec4 logo=texture2D(uRedBull,logoUV);
        paint=mix(paint,logo.rgb,logo.a);
      }
      diffuseColor.rgb=paint;
     `);
     s.fragmentShader=s.fragmentShader.replace('#include <dithering_fragment>',`
      // A sphere intersects the actual surface at the raycast hit point.
      float distanceToPointer=length(vHelmetWorld-uEraseCenter);
      float eraseMask=(1.-smoothstep(uEraseRadius*.72,uEraseRadius,distanceToPointer))*uEraseActive;
      gl_FragColor.a*=1.-eraseMask;
      if(gl_FragColor.a<.012)discard;
      #include <dithering_fragment>
     `);
   };
   mesh.material=mat;
  }
  let pointerFrame=0;
  const drawPointer=()=>{
    if(!pointerFrame)pointerFrame=requestAnimationFrame(()=>{pointerFrame=0;renderer.render(scene,opts.camera)});
  };
  const clearPointer=()=>{pointerInside=false;erase.uEraseActive.value=0;drawPointer()};
  const raycaster=new THREE.Raycaster(),pointerNdc=new THREE.Vector2();
  let pointerInside=false;
  const updateHit=()=>{
    if(!pointerInside){erase.uEraseActive.value=0;return}
    scene.updateMatrixWorld(true);
    raycaster.setFromCamera(pointerNdc,opts.camera);
    const hit=raycaster.intersectObjects(meshes,false)[0];
    erase.uEraseActive.value=hit?1:0;
    if(hit)erase.uEraseCenter.value.copy(hit.point);
    erase.uEraseRadius.value=.62*pivot.scale.x;
  };
  const onPointer=e=>{
    const r=renderer.domElement.getBoundingClientRect();
    const x=e.clientX-r.left,y=e.clientY-r.top;
    pointerInside=x>=0&&x<=r.width&&y>=0&&y<=r.height;
    pointerNdc.set(x/r.width*2-1,1-y/r.height*2);
    updateHit();drawPointer();
  };
  // Listen above the non-interactive canvas; HTML labels overlay the hero.
  window.addEventListener('pointermove',onPointer,{passive:true});
  document.documentElement.addEventListener('pointerleave',clearPointer);
  window.addEventListener('blur',clearPointer);
  window.addEventListener('scroll',clearPointer,{passive:true});
  window.addEventListener('resize',clearPointer,{passive:true});
  window.addEventListener('pointerup',e=>{if(e.pointerType!=='mouse')clearPointer()},{passive:true});
  pivot.add(model);
  const image=new THREE.Mesh(new THREE.PlaneGeometry(4.65,6.2),new THREE.ShaderMaterial({
    vertexShader:'varying vec2 vUv;void main(){vUv=uv;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:`varying vec2 vUv;uniform sampler2D diffuse;uniform vec2 uPointer;
    void main(){vec2 uv=vUv+(uPointer-.5)*.005;vec4 c=texture2D(diffuse,uv);
    float edge=smoothstep(0.,.16,uv.x)*smoothstep(0.,.16,1.-uv.x)*smoothstep(0.,.16,1.-uv.y);
    gl_FragColor=vec4(c.rgb,edge);
    #include <tonemapping_fragment>
    #include <colorspace_fragment>
    }`,
    uniforms:{uPointer:uniforms.uPointer,diffuse:{value:tex['person-diffuse.webp']}},transparent:true,depthWrite:false
  }));
  image.position.copy(portrait.position);image.scale.copy(portrait.scale);image.position.z=-1.1;
  scene.add(image);
  if(renderer.compileAsync)await renderer.compileAsync(scene,opts.camera);
  renderer.initTexture(tex['noise.webp']);
  renderer.render(scene,opts.camera);
  procedural.forEach(x=>x.visible=false);
  portrait.visible=false;
  const update=(tier)=>{
    image.position.x=portrait.position.x;image.position.y=portrait.position.y;
    image.scale.copy(portrait.scale);
    updateHit();
  };
  draco.dispose();environment.dispose();pmrem.dispose();
  return {update,reference};
 }catch(e){draco.dispose();try{environment?.dispose()}catch(_){}throw e}
}
