/* Real GLB helmet with the user-supplied portrait. Dependencies are pinned in the import map. */
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {DRACOLoader} from 'three/addons/loaders/DRACOLoader.js';
import {RGBELoader} from 'three/addons/loaders/RGBELoader.js';
import {mergeGeometries} from 'three/addons/utils/BufferGeometryUtils.js';

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
  // Base color, normal, ORM remain inherited from actual GLB materials.
  const wireGroups=[];
  for(const mesh of meshes){
   const old=mesh.material,mat=old.clone();
   mat.transparent=true;mat.depthWrite=false;mat.side=THREE.FrontSide;
   mat.envMap=env;mat.envMapIntensity=1.3;
   mat.onBeforeCompile=s=>{
     s.uniforms.uIntro=uniforms.uIntro;
     s.uniforms.uTime=uniforms.uTime;
     s.uniforms.uPace=uniforms.uPace;
     s.uniforms.uResolution=uniforms.uResolution;
     s.uniforms.uTrail=uniforms.uTrail;s.uniforms.uTrailCount=uniforms.uTrailCount;
     s.uniforms.uNoise={value:tex['noise.webp']};
     s.vertexShader=s.vertexShader.replace('#include <common>','#include <common>\nvarying vec2 vHelmetUv;');
     s.vertexShader=s.vertexShader.replace('#include <uv_vertex>','#include <uv_vertex>\nvHelmetUv=uv;');
     s.fragmentShader=s.fragmentShader.replace('#include <common>',[
      '#include <common>',
      'varying vec2 vHelmetUv;',
      'uniform float uIntro;uniform float uTime;uniform float uPace;',
      'uniform vec2 uResolution;uniform vec2 uTrail[72];uniform int uTrailCount;uniform sampler2D uNoise;',
      'float capsule2(vec2 a,vec2 b,vec2 p,float r){vec2 ab=b-a;float q=clamp(dot(p-a,ab)/max(dot(ab,ab),.0001),0.,1.);return 1.-smoothstep(r*.8,r,length(p-a-q*ab));}'
     ].join('\n'));
     s.fragmentShader=s.fragmentShader.replace('#include <dithering_fragment>',[
      'float n=texture2D(uNoise,vHelmetUv*vec2(3.,3.)+vec2(uTime*.03)).r;',
      'float h=mix(1.-gl_FragCoord.y/max(uResolution.y,1.),n,.45);',
      'float b=smoothstep(.14,1.,uIntro);float intact=1.-smoothstep(h-.02,h+.02,b);',
      'vec2 uv=gl_FragCoord.xy/max(uResolution,vec2(1.));',
      'float mask=0.;',
      'for(int i=0;i<71;i++){if(i>=uTrailCount-1)break;float f=float(i)/float(uTrailCount-1);float radius=.46*mix(.28,1.,uPace)*pow(1.-f,mix(3.04,1.9,uPace));',
      'vec2 warp=vec2(texture2D(uNoise,uv*2.9+vec2(uTime*.1)).r-.5,texture2D(uNoise,uv*2.9-vec2(uTime*.12)).g-.5)*.023;',
      'mask=max(mask,capsule2(uTrail[i]+warp,uTrail[i+1]+warp,uv,radius));}',
      'mask*=smoothstep(.06,.21,uPace);',
      'float alpha=mix(intact,smoothstep(.075,.085,mask),step(.999,uIntro));',
      'gl_FragColor.rgb+=vec3(0.,.82,.9)*4.*intact*(1.-intact);',
      'gl_FragColor.a*=alpha;if(gl_FragColor.a<.012)discard;',
      '#include <dithering_fragment>'
     ].join('\n'));
   };
   mesh.material=mat;
   // Unmerged fallback if geometry carries different attribute layouts.
   const geom=new THREE.WireframeGeometry(mesh.geometry);
   const scan=new THREE.ShaderMaterial({
    vertexShader:'varying float vY;void main(){vY=position.y;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
    fragmentShader:'precision highp float;varying float vY;uniform float uTime;uniform float uIntro;void main(){float w=exp(-pow((vY-(1.4-mod(uTime,3.1)/3.1*2.8))/.15,2.));gl_FragColor=vec4(.88,.96,.98,w*.09*smoothstep(.3,.9,uIntro));}',
    uniforms,transparent:true,depthWrite:false
   });
   const lines=new THREE.LineSegments(geom,scan);
   lines.position.copy(mesh.position);lines.rotation.copy(mesh.rotation);lines.scale.copy(mesh.scale);
   mesh.parent.add(lines);wireGroups.push(lines);
  }
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
    wireGroups.forEach(o=>o.visible=tier.outline);
  };
  draco.dispose();environment.dispose();pmrem.dispose();
  return {update,reference};
 }catch(e){draco.dispose();try{environment?.dispose()}catch(_){}throw e}
}
