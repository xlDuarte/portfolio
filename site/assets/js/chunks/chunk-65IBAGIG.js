import{a as Pe,b as ht}from"./chunk-ZHD2AXXY.js";import{b as ut,d as Ce}from"./chunk-Z5E3FPK4.js";import{d as C}from"./chunk-RGCLR3M6.js";import{$ as tt,Ca as dt,D as j,E as Ze,Ea as ft,G as u,Ga as ie,I as te,Ja as pt,K as $e,La as ae,M as Ee,Ma as se,N as he,O as et,P as oe,Q as Ue,R as De,S as me,T as we,U as H,Y as I,aa as nt,e as Ae,ga as V,ha as Be,ia as ot,la as it,oa as at,pa as st,qa as Le,ra as rt,ta as N,xa as ct,ya as lt}from"./chunk-IGBBPGQH.js";var mt=new oe,xe=new u,J=class extends ft{constructor(){super(),this.isLineSegmentsGeometry=!0,this.type="LineSegmentsGeometry";let e=[-1,2,0,1,2,0,-1,1,0,1,1,0,-1,0,0,1,0,0,-1,-1,0,1,-1,0],o=[-1,2,1,2,-1,1,1,1,-1,-1,1,-1,-1,-2,1,-2],i=[0,2,1,2,3,1,2,4,3,4,5,3,4,6,5,6,7,5];this.setIndex(i),this.setAttribute("position",new De(e,3)),this.setAttribute("uv",new De(o,2))}applyMatrix4(e){let o=this.attributes.instanceStart,i=this.attributes.instanceEnd;return o!==void 0&&(o.applyMatrix4(e),i.applyMatrix4(e),o.needsUpdate=!0),this.boundingBox!==null&&this.computeBoundingBox(),this.boundingSphere!==null&&this.computeBoundingSphere(),this}setPositions(e){let o;e instanceof Float32Array?o=e:Array.isArray(e)&&(o=new Float32Array(e));let i=new ie(o,6,1);return this.setAttribute("instanceStart",new H(i,3,0)),this.setAttribute("instanceEnd",new H(i,3,3)),this.instanceCount=this.attributes.instanceStart.count,this.computeBoundingBox(),this.computeBoundingSphere(),this}setColors(e){let o;e instanceof Float32Array?o=e:Array.isArray(e)&&(o=new Float32Array(e));let i=new ie(o,6,1);return this.setAttribute("instanceColorStart",new H(i,3,0)),this.setAttribute("instanceColorEnd",new H(i,3,3)),this}fromWireframeGeometry(e){return this.setPositions(e.attributes.position.array),this}fromEdgesGeometry(e){return this.setPositions(e.attributes.position.array),this}fromMesh(e){return this.fromWireframeGeometry(new at(e.geometry)),this}fromLineSegments(e){let o=e.geometry;return this.setPositions(o.attributes.position.array),this}computeBoundingBox(){this.boundingBox===null&&(this.boundingBox=new oe);let e=this.attributes.instanceStart,o=this.attributes.instanceEnd;e!==void 0&&o!==void 0&&(this.boundingBox.setFromBufferAttribute(e),mt.setFromBufferAttribute(o),this.boundingBox.union(mt))}computeBoundingSphere(){this.boundingSphere===null&&(this.boundingSphere=new me),this.boundingBox===null&&this.computeBoundingBox();let e=this.attributes.instanceStart,o=this.attributes.instanceEnd;if(e!==void 0&&o!==void 0){let i=this.boundingSphere.center;this.boundingBox.getCenter(i);let r=0;for(let p=0,l=e.count;p<l;p++)xe.fromBufferAttribute(e,p),r=Math.max(r,i.distanceToSquared(xe)),xe.fromBufferAttribute(o,p),r=Math.max(r,i.distanceToSquared(xe));this.boundingSphere.radius=Math.sqrt(r),isNaN(this.boundingSphere.radius)&&console.error("THREE.LineSegmentsGeometry.computeBoundingSphere(): Computed radius is NaN. The instanced position data is likely to have NaN values.",this)}}toJSON(){}};ae.line={worldUnits:{value:1},linewidth:{value:1},resolution:{value:new Ze},dashOffset:{value:0},dashScale:{value:1},dashSize:{value:1},gapSize:{value:1}};se.line={uniforms:Le.merge([ae.common,ae.fog,ae.line]),vertexShader:`
		#include <common>
		#include <color_pars_vertex>
		#include <fog_pars_vertex>
		#include <logdepthbuf_pars_vertex>
		#include <clipping_planes_pars_vertex>

		uniform float linewidth;
		uniform vec2 resolution;

		attribute vec3 instanceStart;
		attribute vec3 instanceEnd;

		attribute vec3 instanceColorStart;
		attribute vec3 instanceColorEnd;

		#ifdef WORLD_UNITS

			varying vec4 worldPos;
			varying vec3 worldStart;
			varying vec3 worldEnd;

			#ifdef USE_DASH

				varying vec2 vUv;

			#endif

		#else

			varying vec2 vUv;

		#endif

		#ifdef USE_DASH

			uniform float dashScale;
			attribute float instanceDistanceStart;
			attribute float instanceDistanceEnd;
			varying float vLineDistance;

		#endif

		float trimSegmentAlpha( const in vec4 start, const in vec4 end ) {

			// compute the interpolation factor needed to trim the segment so it terminates
			// between the camera plane and the near plane

			// conservative estimate of the near plane
			float a = projectionMatrix[ 2 ][ 2 ]; // 3nd entry in 3th column
			float b = projectionMatrix[ 3 ][ 2 ]; // 3nd entry in 4th column

			// we need different nearEstimate formula for reversed and default depth buffer
			// a is positive with a reversed depth buffer so it can be used for controlling the code flow
			float nearEstimate = ( a > 0.0 ) ? ( - b / ( a + 1.0 ) ) : ( - 0.5 * b / a );

			return ( nearEstimate - start.z ) / ( end.z - start.z );

		}

		void main() {

			#ifdef USE_COLOR

				vColor.xyz = ( position.y < 0.5 ) ? instanceColorStart : instanceColorEnd;

			#endif

			float aspect = resolution.x / resolution.y;

			// camera space
			vec4 start = modelViewMatrix * vec4( instanceStart, 1.0 );
			vec4 end = modelViewMatrix * vec4( instanceEnd, 1.0 );

			#ifdef USE_DASH

				float lineDistanceStart = dashScale * instanceDistanceStart;
				float lineDistanceEnd = dashScale * instanceDistanceEnd;

			#endif

			#ifdef WORLD_UNITS

				worldStart = start.xyz;
				worldEnd = end.xyz;

			#else

				vUv = uv;

			#endif

			// special case for perspective projection, and segments that terminate either in, or behind, the camera plane
			// clearly the gpu firmware has a way of addressing this issue when projecting into ndc space
			// but we need to perform ndc-space calculations in the shader, so we must address this issue directly
			// perhaps there is a more elegant solution -- WestLangley

			bool perspective = ( projectionMatrix[ 2 ][ 3 ] == - 1.0 ); // 4th entry in the 3rd column

			if ( perspective ) {

				if ( start.z < 0.0 && end.z >= 0.0 ) {

					float alpha = trimSegmentAlpha( start, end );
					end.xyz = mix( start.xyz, end.xyz, alpha );

					#ifdef USE_DASH

						lineDistanceEnd = mix( lineDistanceStart, lineDistanceEnd, alpha );

					#endif

				} else if ( end.z < 0.0 && start.z >= 0.0 ) {

					float alpha = trimSegmentAlpha( end, start );
					start.xyz = mix( end.xyz, start.xyz, alpha );

					#ifdef USE_DASH

						lineDistanceStart = mix( lineDistanceEnd, lineDistanceStart, alpha );

					#endif

				}

			}

			#ifdef USE_DASH

				vLineDistance = ( position.y < 0.5 ) ? lineDistanceStart : lineDistanceEnd;
				vUv = uv;

			#endif

			// clip space
			vec4 clipStart = projectionMatrix * start;
			vec4 clipEnd = projectionMatrix * end;

			// ndc space
			vec3 ndcStart = clipStart.xyz / clipStart.w;
			vec3 ndcEnd = clipEnd.xyz / clipEnd.w;

			// direction
			vec2 dir = ndcEnd.xy - ndcStart.xy;

			// account for clip-space aspect ratio
			dir.x *= aspect;
			dir = normalize( dir );

			#ifdef WORLD_UNITS

				vec3 worldDir = normalize( end.xyz - start.xyz );
				vec3 tmpFwd = perspective ? normalize( mix( start.xyz, end.xyz, 0.5 ) ) : vec3( 0.0, 0.0, - 1.0 );
				vec3 worldUp = normalize( cross( worldDir, tmpFwd ) );
				vec3 worldFwd = cross( worldDir, worldUp );
				worldPos = position.y < 0.5 ? start: end;

				// height offset
				float hw = linewidth * 0.5;
				worldPos.xyz += position.x < 0.0 ? hw * worldUp : - hw * worldUp;

				// don't extend the line if we're rendering dashes because we
				// won't be rendering the endcaps
				#ifndef USE_DASH

					// cap extension
					worldPos.xyz += position.y < 0.5 ? - hw * worldDir : hw * worldDir;

					// add width to the box
					worldPos.xyz += worldFwd * hw;

					// endcaps
					if ( position.y > 1.0 || position.y < 0.0 ) {

						worldPos.xyz -= worldFwd * 2.0 * hw;

					}

				#endif

				// project the worldpos
				vec4 clip = projectionMatrix * worldPos;

				// shift the depth of the projected points so the line
				// segments overlap neatly
				vec3 clipPose = ( position.y < 0.5 ) ? ndcStart : ndcEnd;

				// only shift the depth of vertices in front of the camera (#35137)
				if ( clip.w > 0.0 ) clip.z = clipPose.z * clip.w;

			#else

				vec2 offset = vec2( dir.y, - dir.x );
				// undo aspect ratio adjustment
				dir.x /= aspect;
				offset.x /= aspect;

				// sign flip
				if ( position.x < 0.0 ) offset *= - 1.0;

				// endcaps
				if ( position.y < 0.0 ) {

					offset += - dir;

				} else if ( position.y > 1.0 ) {

					offset += dir;

				}

				// adjust for linewidth
				offset *= linewidth;

				// adjust for clip-space to screen-space conversion // maybe resolution should be based on viewport ...
				offset /= resolution.y;

				// select end
				vec4 clip = ( position.y < 0.5 ) ? clipStart : clipEnd;

				// back to clip space
				offset *= clip.w;

				clip.xy += offset;

			#endif

			gl_Position = clip;

			vec4 mvPosition = ( position.y < 0.5 ) ? start : end; // this is an approximation

			#include <logdepthbuf_vertex>
			#include <clipping_planes_vertex>
			#include <fog_vertex>

		}
		`,fragmentShader:`
		uniform vec3 diffuse;
		uniform float opacity;
		uniform float linewidth;

		#ifdef USE_DASH

			uniform float dashOffset;
			uniform float dashSize;
			uniform float gapSize;

		#endif

		varying float vLineDistance;

		#ifdef WORLD_UNITS

			varying vec4 worldPos;
			varying vec3 worldStart;
			varying vec3 worldEnd;

			#ifdef USE_DASH

				varying vec2 vUv;

			#endif

		#else

			varying vec2 vUv;

		#endif

		#include <common>
		#include <color_pars_fragment>
		#include <fog_pars_fragment>
		#include <logdepthbuf_pars_fragment>
		#include <clipping_planes_pars_fragment>

		vec2 closestLineToLine(vec3 p1, vec3 p2, vec3 p3, vec3 p4) {

			float mua;
			float mub;

			vec3 p13 = p1 - p3;
			vec3 p43 = p4 - p3;

			vec3 p21 = p2 - p1;

			float d1343 = dot( p13, p43 );
			float d4321 = dot( p43, p21 );
			float d1321 = dot( p13, p21 );
			float d4343 = dot( p43, p43 );
			float d2121 = dot( p21, p21 );

			float denom = d2121 * d4343 - d4321 * d4321;

			float numer = d1343 * d4321 - d1321 * d4343;

			mua = numer / denom;
			mua = clamp( mua, 0.0, 1.0 );
			mub = ( d1343 + d4321 * ( mua ) ) / d4343;
			mub = clamp( mub, 0.0, 1.0 );

			return vec2( mua, mub );

		}

		void main() {

			float alpha = opacity;
			vec4 diffuseColor = vec4( diffuse, alpha );

			#include <clipping_planes_fragment>

			#ifdef USE_DASH

				if ( vUv.y < - 1.0 || vUv.y > 1.0 ) discard; // discard endcaps

				if ( mod( vLineDistance + dashOffset, dashSize + gapSize ) > dashSize ) discard; // todo - FIX

			#endif

			#ifdef WORLD_UNITS

				float len;

				if ( isOrthographic ) {

					// View rays are parallel to the z axis so the distance reduces to camera-space XY
					vec2 lineDir = worldEnd.xy - worldStart.xy;
					float t = clamp( dot( worldPos.xy - worldStart.xy, lineDir ) / dot( lineDir, lineDir ), 0.0, 1.0 );
					len = length( worldStart.xy + lineDir * t - worldPos.xy );

				} else {

					// Find the closest points on the view ray and the line segment
					vec3 rayEnd = normalize( worldPos.xyz ) * 1e5;
					vec3 lineDir = worldEnd - worldStart;
					vec2 params = closestLineToLine( worldStart, worldEnd, vec3( 0.0, 0.0, 0.0 ), rayEnd );

					vec3 p1 = worldStart + lineDir * params.x;
					vec3 p2 = rayEnd * params.y;
					vec3 delta = p1 - p2;
					len = length( delta );

				}

				float norm = len / linewidth;

				#ifndef USE_DASH

					#ifdef USE_ALPHA_TO_COVERAGE

						float dnorm = fwidth( norm );
						alpha = 1.0 - smoothstep( 0.5 - dnorm, 0.5 + dnorm, norm );

					#else

						if ( norm > 0.5 ) {

							discard;

						}

					#endif

				#endif

			#else

				#ifdef USE_ALPHA_TO_COVERAGE

					// artifacts appear on some hardware if a derivative is taken within a conditional
					float a = vUv.x;
					float b = ( vUv.y > 0.0 ) ? vUv.y - 1.0 : vUv.y + 1.0;
					float len2 = a * a + b * b;
					float dlen = fwidth( len2 );

					if ( abs( vUv.y ) > 1.0 ) {

						alpha = 1.0 - smoothstep( 1.0 - dlen, 1.0 + dlen, len2 );

					}

				#else

					if ( abs( vUv.y ) > 1.0 ) {

						float a = vUv.x;
						float b = ( vUv.y > 0.0 ) ? vUv.y - 1.0 : vUv.y + 1.0;
						float len2 = a * a + b * b;

						if ( len2 > 1.0 ) discard;

					}

				#endif

			#endif

			#include <logdepthbuf_fragment>
			#include <color_fragment>

			gl_FragColor = vec4( diffuseColor.rgb, alpha );

			#include <tonemapping_fragment>
			#include <colorspace_fragment>
			#include <fog_fragment>
			#include <premultiplied_alpha_fragment>

		}
		`};var Q=class extends rt{constructor(e){super({type:"LineMaterial",uniforms:Le.clone(se.line.uniforms),vertexShader:se.line.vertexShader,fragmentShader:se.line.fragmentShader,clipping:!0}),this.isLineMaterial=!0,this.setValues(e)}get color(){return this.uniforms.diffuse.value}set color(e){this.uniforms.diffuse.value=e}get worldUnits(){return"WORLD_UNITS"in this.defines}set worldUnits(e){e===!0!==this.worldUnits&&(this.needsUpdate=!0),e===!0?this.defines.WORLD_UNITS="":delete this.defines.WORLD_UNITS}get linewidth(){return this.uniforms.linewidth.value}set linewidth(e){this.uniforms.linewidth&&(this.uniforms.linewidth.value=e)}get dashed(){return"USE_DASH"in this.defines}set dashed(e){e===!0!==this.dashed&&(this.needsUpdate=!0),e===!0?this.defines.USE_DASH="":delete this.defines.USE_DASH}get dashScale(){return this.uniforms.dashScale.value}set dashScale(e){this.uniforms.dashScale.value=e}get dashSize(){return this.uniforms.dashSize.value}set dashSize(e){this.uniforms.dashSize.value=e}get dashOffset(){return this.uniforms.dashOffset.value}set dashOffset(e){this.uniforms.dashOffset.value=e}get gapSize(){return this.uniforms.gapSize.value}set gapSize(e){this.uniforms.gapSize.value=e}get opacity(){return this.uniforms.opacity.value}set opacity(e){this.uniforms&&(this.uniforms.opacity.value=e)}get resolution(){return this.uniforms.resolution.value}set resolution(e){this.uniforms.resolution.value.copy(e)}get alphaToCoverage(){return"USE_ALPHA_TO_COVERAGE"in this.defines}set alphaToCoverage(e){this.defines&&(e===!0!==this.alphaToCoverage&&(this.needsUpdate=!0),e===!0?this.defines.USE_ALPHA_TO_COVERAGE="":delete this.defines.USE_ALPHA_TO_COVERAGE)}};var Te=new te,wt=new u,xt=new u,v=new te,S=new te,O=new te,Ie=new u,Oe=new $e,b=new pt,gt=new u,ge=new oe,ye=new me,G=new te,W,Z;function yt(d,e,o){return G.set(0,0,-e,1).applyMatrix4(d.projectionMatrix),G.multiplyScalar(1/G.w),G.x=Z/o.width,G.y=Z/o.height,G.applyMatrix4(d.projectionMatrixInverse),G.multiplyScalar(1/G.w),Math.abs(Math.max(G.x,G.y))}function Bt(d,e){let o=d.matrixWorld,i=d.geometry,r=i.attributes.instanceStart,p=i.attributes.instanceEnd,l=Math.min(i.instanceCount,r.count);for(let c=0,h=l;c<h;c++){b.start.fromBufferAttribute(r,c),b.end.fromBufferAttribute(p,c),b.applyMatrix4(o);let z=new u,M=new u;W.distanceSqToSegment(b.start,b.end,M,z),M.distanceTo(z)<Z*.5&&e.push({point:M,pointOnLine:z,distance:W.origin.distanceTo(M),object:d,face:null,faceIndex:c,uv:null,uv1:null})}}function Lt(d,e,o){let i=e.projectionMatrix,p=d.material.resolution,l=d.matrixWorld,c=d.geometry,h=c.attributes.instanceStart,z=c.attributes.instanceEnd,M=Math.min(c.instanceCount,h.count),m=-e.near;W.at(1,O),O.w=1,O.applyMatrix4(e.matrixWorldInverse),O.applyMatrix4(i),O.multiplyScalar(1/O.w),O.x*=p.x/2,O.y*=p.y/2,O.z=0,Ie.copy(O),Oe.multiplyMatrices(e.matrixWorldInverse,l);for(let w=0,x=M;w<x;w++){if(v.fromBufferAttribute(h,w),S.fromBufferAttribute(z,w),v.w=1,S.w=1,v.applyMatrix4(Oe),S.applyMatrix4(Oe),v.z>m&&S.z>m)continue;if(v.z>m){let P=v.z-S.z,T=(v.z-m)/P;v.lerp(S,T)}else if(S.z>m){let P=S.z-v.z,T=(S.z-m)/P;S.lerp(v,T)}v.applyMatrix4(i),S.applyMatrix4(i),v.multiplyScalar(1/v.w),S.multiplyScalar(1/S.w),v.x*=p.x/2,v.y*=p.y/2,S.x*=p.x/2,S.y*=p.y/2,b.start.copy(v),b.start.z=0,b.end.copy(S),b.end.z=0;let _=b.closestPointToPointParameter(Ie,!0);b.at(_,gt);let q=j.lerp(v.z,S.z,_),k=q>=-1&&q<=1,$=Ie.distanceTo(gt)<Z*.5;if(k&&$){b.start.fromBufferAttribute(h,w),b.end.fromBufferAttribute(z,w),b.start.applyMatrix4(l),b.end.applyMatrix4(l);let P=new u,T=new u;W.distanceSqToSegment(b.start,b.end,T,P),o.push({point:T,pointOnLine:P,distance:W.origin.distanceTo(T),object:d,face:null,faceIndex:w,uv:null,uv1:null})}}}var re=class extends I{constructor(e=new J,o=new Q({color:Math.random()*16777215})){super(e,o),this.isLineSegments2=!0,this.type="LineSegments2"}computeLineDistances(){let e=this.geometry,o=e.attributes.instanceStart,i=e.attributes.instanceEnd,r=new Float32Array(2*o.count);for(let l=0,c=0,h=o.count;l<h;l++,c+=2)wt.fromBufferAttribute(o,l),xt.fromBufferAttribute(i,l),r[c]=c===0?0:r[c-1],r[c+1]=r[c]+wt.distanceTo(xt);let p=new ie(r,2,1);return e.setAttribute("instanceDistanceStart",new H(p,1,0)),e.setAttribute("instanceDistanceEnd",new H(p,1,1)),this}raycast(e,o){let i=this.material.worldUnits,r=e.camera;if(r===null&&!i&&console.error('LineSegments2: "Raycaster.camera" needs to be set in order to raycast against LineSegments2 while worldUnits is set to false.'),i===!1&&(this.material.resolution.x===0||this.material.resolution.y===0))return;let p=e.params.Line2!==void 0&&e.params.Line2.threshold||0;W=e.ray;let l=this.matrixWorld,c=this.geometry,h=this.material;Z=h.linewidth+p,c.boundingSphere===null&&c.computeBoundingSphere(),ye.copy(c.boundingSphere).applyMatrix4(l);let z;if(i)z=Z*.5;else{let m=Math.max(r.near,ye.distanceToPoint(W.origin));z=yt(r,m,h.resolution)}if(ye.radius+=z,W.intersectsSphere(ye)===!1)return;c.boundingBox===null&&c.computeBoundingBox(),ge.copy(c.boundingBox).applyMatrix4(l);let M;if(i)M=Z*.5;else{let m=Math.max(r.near,ge.distanceToPoint(W.origin));M=yt(r,m,h.resolution)}ge.expandByScalar(M),W.intersectsBox(ge)!==!1&&(i?Bt(this,o):Lt(this,r,o))}onBeforeRender(e){let o=this.material.uniforms;o&&o.resolution&&(e.getViewport(Te),this.material.uniforms.resolution.value.set(Te.z,Te.w))}};var A={trackScale:1/100,elevation:4,trackWidth:3,carScale:2.6,trailSeconds:6,pitchDegPerG:1.2,rollDegPerG:1},D={x:0,y:1,z:2,speed:3,gear:4,throttle:5,brake:6,lap:7,alat:8,along:9,disc:10},Ct=Object.freeze({drag:.35,convection:1.6,radiation:2e-13,ambientK:300,visibleK:1100,restitution:.45,friction:.35,contactCoolingK:60,maxLife:1.2});function Pt(d){let e=new Ee,o=new Ee,i=new N({color:d,roughness:.32,metalness:.35}),r=new N({color:1711393,roughness:.5,metalness:.2}),p=new N({color:1382170,roughness:.85}),l=(m,w,x,E,_,q=0)=>{let k=new I(m,w);return k.position.set(x,E,_),k.rotation.z=q,o.add(k),k};l(new V(.34,.09,.13),i,0,.07,0),l(new V(.2,.05,.22),i,-.05,.06,0),l(new ot(.045,.22,10),i,.27,.06,0,-Math.PI/2),l(new V(.05,.012,.26),r,.37,.025,0),l(new V(.05,.05,.2),r,-.2,.15,0),l(new V(.06,.07,.02),r,-.19,.11,0),l(new V(.42,.01,.2),r,0,.012,0);let c=[],h=[],z=new Be(.045,.045,.05,16),M=new Be(.026,.026,.052,14);for(let[m,w]of[[.2,!0],[-.17,!1]])for(let x of[-.12,.12]){let E=new I(z,p);if(E.rotation.x=Math.PI/2,E.position.set(m,.045,x),e.add(E),c.push(E),w){let _=new I(M,new N({color:2236962,emissive:0,roughness:.6}));_.rotation.x=Math.PI/2,_.position.set(m,.045,x),e.add(_),h.push(_)}}return e.add(o),e.traverse(m=>{m.isMesh&&(m.castShadow=!0)}),{g:e,body:o,discs:h}}function Zt(d,e){let o=new et;o.environment=e,o.background=new he(C.wash);let i=new lt(26,1,1,2e3);o.add(new ct(16777215,14672872,.95));let r=new dt(16777215,2);r.position.set(-18,120,30),r.castShadow=!0,Object.assign(r.shadow.camera,{left:-75,right:75,top:75,bottom:-75,near:10,far:260}),r.shadow.bias=-6e-4,r.shadow.normalBias=.05,o.add(r);let p=new I(new it(400,400),new st({opacity:.1}));p.rotation.x=-Math.PI/2,p.receiveShadow=!0,o.add(p);let l=d.track.extent_dm,c=new I(new V(l[0]/100+9,.9,l[1]/100+9),new N({color:16251130,roughness:.55}));c.position.y=.45,c.castShadow=c.receiveShadow=!0,o.add(c);let h=A.trackScale,z=A.elevation,M=1.2,m=n=>new u(n[0]*h,M+n[2]*h*z,-n[1]*h),w=d.track.points.map(m),x=w.length,E=[],_=[];for(let n=0;n<x;n++){let s=w[(n-1+x)%x],t=w[(n+1)%x],a=new u(t.x-s.x,0,t.z-s.z).normalize(),f=new u(-a.z,0,a.x).multiplyScalar(A.trackWidth/2);E.push(w[n].clone().add(f)),_.push(w[n].clone().sub(f))}let q=[],k=[];for(let n=0;n<x;n++)q.push(...E[n].toArray(),..._[n].toArray());for(let n=0;n<x;n++){let s=(n+1)%x,t=2*n,a=2*n+1,f=2*s,g=2*s+1;k.push(t,a,g,t,g,f)}let $=new we;$.setAttribute("position",new Ue(new Float32Array(q),3)),$.setIndex(k),$.computeVertexNormals();let P=new I($,new N({color:C.asphalt,roughness:.82,metalness:.05,side:Ae}));P.castShadow=P.receiveShadow=!0,o.add(P);let T=[];for(let n of[E,_])for(let s=0;s<x;s++){let t=n[s],a=n[(s+1)%x];T.push(t.x,t.y,t.z,a.x,a.y,a.z,a.x,.9,a.z,t.x,t.y,t.z,a.x,.9,a.z,t.x,.9,t.z)}let ve=new we;ve.setAttribute("position",new Ue(new Float32Array(T),3)),ve.computeVertexNormals();let Se=new I(ve,new N({color:C.resin,roughness:.6,side:Ae}));Se.castShadow=Se.receiveShadow=!0,o.add(Se);let vt=new tt({color:16777215,transparent:!0,opacity:.55});for(let n of[E,_]){let s=n.map((t,a)=>t.clone().lerp(w[a],.12).setY(t.y+.02));o.add(new nt(new we().setFromPoints([...s,s[0]]),vt))}let Ge=d.cars[0],St=Ge.samples.slice(0,Math.round(97*d.sample_hz)),ce=w.map((n,s)=>{let t=d.track.points[s],a=1/0,f=0;for(let g of St){let y=(g[0]-t[0])**2+(g[1]-t[1])**2;y<a&&(a=y,f=g[D.speed])}return f}),be=Math.min(...ce),We=Math.max(...ce),ke=n=>{let s=j.clamp((n-be)/(We-be),0,1);return C.slow.map((t,a)=>t+(C.fast[a]-t)*s)},Fe=[],Re=[];for(let n=0;n<x;n++){let s=w[n],t=w[(n+1)%x];Fe.push(s.x,s.y+.03,s.z,t.x,t.y+.03,t.z),Re.push(...ke(ce[n]),...ke(ce[(n+1)%x]))}let je=new Q({vertexColors:!0,linewidth:4,worldUnits:!1});o.add(new re(new J().setPositions(Fe).setColors(Re),je));let He=[C.auto,C.graphite,C.slate],Ve=d.cars.map((n,s)=>{let t=Pt(He[s]);t.g.scale.setScalar(A.carScale),o.add(t.g);let a=Math.round(A.trailSeconds*d.sample_hz*2),f=new J().setPositions(new Float32Array(a*6)).setColors(new Float32Array(a*6)),g=new re(f,new Q({vertexColors:!0,linewidth:3,worldUnits:!1,transparent:!0}));g.frustumCulled=!1,o.add(g);let y=new ut(260,Ct),R=new ht(y,A.carScale/10,{intensity:1.6,refK:1800,size:2.6});return R.addTo(o),{car:n,model:t,trail:g,tGeo:f,segs:a,colour:new he(He[s]),sparks:y,sparkView:R,pitch:new Ce(2.2,.65),roll:new Ce(2.6,.7),emitAcc:0}}),le=Ge.samples.length/d.sample_hz-.6;function de(n,s){let t=n.samples,a=s*d.sample_hz,f=Math.min(Math.floor(a),t.length-2),g=a-f,y=t[f],R=t[f+1],L=K=>y[K]+(R[K]-y[K])*g;return{x:L(D.x)*h,y:M+L(D.z)*h*z+.02,z:-L(D.y)*h,speed:Math.round(L(D.speed)),gear:y[D.gear],lap:y[D.lap],throttle:L(D.throttle),brake:y[D.brake],aLat:L(D.alat),aLong:L(D.along),disc:L(D.disc)}}let F=0,fe=[],bt=new u,zt=new u,pe=[0,0,0],ue=[];function Mt(n){F=((F+n)%le+le)%le,fe.length=0;for(let t of Ve){let a=de(t.car,F),f=de(t.car,Math.min(F+.25,le)),g=-Math.atan2(f.z-a.z,f.x-a.x);t.model.g.position.set(a.x,a.y,a.z),t.model.g.rotation.y=g;let y=t.pitch.step(j.degToRad(A.pitchDegPerG*a.aLong),n),R=t.roll.step(j.degToRad(A.rollDegPerG*a.aLat),n);t.model.body.rotation.set(R,0,y);let L=a.disc+273.15;Pe.sample(L,pe);let K=Math.max(0,Pe.radiance(L,1e3)-.08)*3.2;for(let U of t.model.discs)U.material.emissive.setRGB(pe[0]*K,pe[1]*K,pe[2]*K);if(n>0&&a.speed>265&&a.throttle>97){let U=.5+.5*Math.sin(F*13.7+t.car.number)*Math.sin(F*5.3);t.emitAcc+=n*140*Math.max(0,U);let Y=A.carScale/10,Me=(f.x-a.x)/.25/Y,ne=(f.z-a.z)/.25/Y,X=bt.set(-.18,.004,0).applyEuler(t.model.g.rotation).multiplyScalar(A.carScale).add(t.model.g.position);for(;t.emitAcc>=1;){t.emitAcc-=1;let ee=.55+Math.random()*.25;t.sparks.emit(X.x/Y,X.y/Y,X.z/Y,Me*ee+(Math.random()-.5)*3,1+Math.random()*2.5,ne*ee+(Math.random()-.5)*3,2300+Math.random()*400)}}let Et=(a.y-.02)/(A.carScale/10);t.sparks.step(n,()=>Et),t.sparkView.update();let Ut=t.tGeo.attributes.instanceStart.data.array,Dt=t.tGeo.attributes.instanceColorStart.data.array;for(let U=0;U<t.segs;U++){let Y=Math.max(0,F-A.trailSeconds*(1-U/t.segs)),Me=Math.max(0,F-A.trailSeconds*(1-(U+1)/t.segs)),ne=de(t.car,Y),X=de(t.car,Me);Ut.set([ne.x,ne.y+.06,ne.z,X.x,X.y+.06,X.z],U*6);let ee=U/t.segs,_e=(U+1)/t.segs;Dt.set([1-(1-t.colour.r)*ee,1-(1-t.colour.g)*ee,1-(1-t.colour.b)*ee,1-(1-t.colour.r)*_e,1-(1-t.colour.g)*_e,1-(1-t.colour.b)*_e],U*6)}t.tGeo.attributes.instanceStart.data.needsUpdate=!0,t.tGeo.attributes.instanceColorStart.data.needsUpdate=!0,fe.push({code:t.car.code,...a,world:zt.set(a.x,a.y+1.1,a.z).clone()})}let s=fe[0];s&&(ue.push([s.aLat,s.aLong]),ue.length>180&&ue.shift())}let _t=[je,...Ve.map(n=>n.trail.material)],Ne=l[0]/200+4.5,qe=l[1]/200+4.5,Ke=[];for(let n of[-Ne,Ne])for(let s of[0,3])for(let t of[-qe,qe])Ke.push(new u(n,s,t));let ze=new u,Ye=new u(0,1.5,0),B={distance:1,elevation:42,azimuth:1.15,fit:.8,parallax:[0,0],pan:[0,0]},Xe=new u,Je=new u;function Qe(n,s,t){i.position.set(Math.sin(t)*Math.cos(s)*n,Math.sin(s)*n,Math.cos(t)*Math.cos(s)*n),i.lookAt(Ye),i.updateMatrixWorld()}function At(n){i.aspect=n,i.updateProjectionMatrix();let s=j.degToRad(B.elevation+B.parallax[1]*3),t=B.azimuth+B.parallax[0]*.08,a=200;for(let f=0;f<3;f++){Qe(a,s,t);let g=0,y=0;for(let R of Ke)ze.copy(R).project(i),g=Math.max(g,Math.abs(ze.x)),y=Math.max(y,Math.abs(ze.y));a*=Math.max(g/(.93*B.fit),y/.93)}if(Qe(a*B.distance,s,t),B.pan[0]||B.pan[1]){let f=Math.tan(j.degToRad(i.fov/2))*i.position.distanceTo(Ye);Xe.setFromMatrixColumn(i.matrixWorld,0).multiplyScalar(B.pan[0]*f*i.aspect),Je.setFromMatrixColumn(i.matrixWorld,1).multiplyScalar(B.pan[1]*f),i.position.add(Xe).add(Je),i.updateMatrixWorld()}}return{scene:o,camera:i,step:Mt,frame:At,setShadowSize:n=>{r.shadow.mapSize.set(n,n),r.shadow.map?.dispose(),r.shadow.map=null},tint:n=>o.background.setHex(C.wash).lerp(new he(C.autoWash),n),lines:_t,readout:fe,history:ue,state:B,speedRange:[be,We],aoRadius:4,aoIntensity:.8}}export{A as a,Zt as b};
