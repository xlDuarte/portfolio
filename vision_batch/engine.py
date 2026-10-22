"""Executable industrial computer-vision methods with exclusively synthetic images.

CV results show functioning image operations but have NO external validation,
camera integrations, certified PPE checks, operator monitoring, or safety approval.
Pytorch/TensorFlow models use train-only images and different synthetic test seeds.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import cv2
import numpy as np

ROOT=Path(__file__).resolve().parent
CONFIG={int(k):v for k,v in json.loads((ROOT/"config.json").read_text()).items()}
SIDE=96

def canvas(color=(26,26,26)):
    return np.full((SIDE,SIDE,3),color,np.uint8)

def validate_image(image):
    if not isinstance(image,np.ndarray) or image.ndim!=3 or image.shape[2]!=3 or image.dtype!=np.uint8:
        raise ValueError("Expected uint8 BGR image with three channels")
    if not 24<=image.shape[0]<=4000 or not 24<=image.shape[1]<=4000:
        raise ValueError("Unsupported frame size")
    return image

def render_ppe(helmet:bool,seed:int=2026):
    img=canvas((35,37,40))
    rng=np.random.default_rng(seed)
    shift=int(rng.integers(-3,4))
    cv2.rectangle(img,(29+shift,64),(67+shift,94),(100,85,70),-1)
    cv2.circle(img,(48+shift,48),18,(165,175,200),-1)
    if helmet:
        cv2.ellipse(img,(48+shift,31),(22,13),0,180,360,(15,200,235),-1)
        cv2.rectangle(img,(22+shift,31),(73+shift,37),(15,200,235),-1)
    return img

def render_gesture(kind:str):
    if kind not in ("open","fist","point"):
        raise ValueError("Unknown gesture")
    img=canvas()
    cv2.rectangle(img,(34,47),(62,88),(240,240,240),-1)
    if kind=="open":
        for i in range(5):
            cv2.rectangle(img,(23+i*11,16+abs(i-2)*4),(29+i*11,50),(240,240,240),-1)
    if kind=="point":
        cv2.rectangle(img,(43,10),(52,49),(240,240,240),-1)
    return img

def gestures(image):
    gray=cv2.cvtColor(validate_image(image),cv2.COLOR_BGR2GRAY)
    _,mask=cv2.threshold(gray,150,255,cv2.THRESH_BINARY)
    cnts,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if not cnts: return {"gesture":"unknown","distance":None}
    contour=max(cnts,key=cv2.contourArea)
    matches={}
    for kind in ("open","fist","point"):
        ref=cv2.cvtColor(render_gesture(kind),cv2.COLOR_BGR2GRAY)
        cc,_=cv2.findContours(cv2.threshold(ref,150,255,cv2.THRESH_BINARY)[1],cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        matches[kind]=float(cv2.matchShapes(contour,max(cc,key=cv2.contourArea),cv2.CONTOURS_MATCH_I1,0))
    winner=min(matches,key=matches.get)
    return {"gesture":winner,"distance":round(matches[winner],7),
            "suggested_hmi_action":{"open":"request_menu","point":"request_select","fist":"request_cancel"}[winner],
            "action_executed":False,"method":"OpenCV contour shape matching"}

def parts_scene(count:int):
    if not isinstance(count,int) or not 0<=count<=6: raise ValueError("count 0..6")
    image=canvas()
    locations=[(20,22),(49,22),(78,22),(20,65),(49,65),(78,65)]
    for i,(x,y) in enumerate(locations[:count]):
        if i%2:cv2.rectangle(image,(x-9,y-9),(x+9,y+9),(235,235,235),-1)
        else:cv2.circle(image,(x,y),9,(235,235,235),-1)
    return image

def detect_parts(image):
    gray=cv2.cvtColor(validate_image(image),cv2.COLOR_BGR2GRAY)
    _,mask=cv2.threshold(gray,120,255,cv2.THRESH_BINARY)
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    boxes=[]
    for c in contours:
        if cv2.contourArea(c)<70:continue
        x,y,w,h=cv2.boundingRect(c)
        boxes.append([int(x),int(y),int(w),int(h)])
    return {"count":len(boxes),"bounding_boxes":sorted(boxes),"method":"OpenCV binary segmentation and contours"}

def eye_scene(open_eye:bool):
    image=canvas()
    for x in (29,68):
        cv2.ellipse(image,(x,47),(13,7 if open_eye else 1),0,0,360,(245,245,245),-1)
    return image

def eye_open_ratio(image):
    image=validate_image(image)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    return float(np.mean(gray[40:55,12:86]>180))

def vigilance_sequence(flags:list[bool]):
    if not flags or not all(type(flag) is bool for flag in flags):raise ValueError("Boolean nonempty frame list required")
    ratios=[eye_open_ratio(eye_scene(f)) for f in flags]
    closed=[r<.14 for r in ratios]
    return {"frames":len(flags),"closed_frames":sum(closed),
            "perclos_demo":round(float(np.mean(closed)),5),
            "eye_aperture_fractions":[round(r,5) for r in ratios],
            "fatigue_diagnosis":"NOT VALIDATED: no real fatigue or emotion inference"}

def serial_scene(serial:str):
    if not isinstance(serial,str) or not 2<=len(serial)<=10 or not serial.isascii() or not serial.isalnum():
        raise ValueError("Alphanumeric serial only, 2..10 chars")
    image=np.full((96,360,3),245,np.uint8)
    cv2.putText(image,serial.upper(),(12,64),cv2.FONT_HERSHEY_SIMPLEX,1.7,(20,20,20),3,cv2.LINE_AA)
    return image

def recognize_serial(image):
    import pytesseract
    image=validate_image(image)
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _,mask=cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    txt=pytesseract.image_to_string(mask,config="--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")
    serial="".join(c for c in txt.upper() if c.isascii() and c.isalnum())
    return {"serial":serial,"method":"OpenCV Otsu threshold + Tesseract OCR",
            "real_stamping_validation":False}

def surface_scene(kind:str):
    if kind not in ("clean","crack","porosity","oxidation"):raise ValueError("Unknown synthetic defect")
    im=canvas((165,165,165))
    if kind=="crack":cv2.line(im,(9,14),(84,81),(18,18,18),2)
    elif kind=="porosity":
        for x,y in ((26,29),(61,40),(35,66),(73,76)):
            cv2.circle(im,(x,y),5,(20,20,20),-1)
    elif kind=="oxidation":cv2.rectangle(im,(20,15),(73,76),(20,80,180),-1)
    return im

def analyze_surface(image):
    validate_image(image)
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    orange=cv2.inRange(hsv,(4,80,80),(28,255,255))
    rust_ratio=float(np.mean(orange>0))
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    _,dark=cv2.threshold(gray,50,255,cv2.THRESH_BINARY_INV)
    contours,_=cv2.findContours(dark,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    long_contours=[]
    pores=[]
    for cnt in contours:
        area=float(cv2.contourArea(cnt))
        if area<10:continue
        x,y,w,h=cv2.boundingRect(cnt)
        rotated=cv2.minAreaRect(cnt)
        lengths=sorted(rotated[1])
        elongation=lengths[1]/max(lengths[0],1)
        if elongation>4 and area>40:long_contours.append([x,y,w,h])
        elif .4<area/(w*h)<.95 and 30<area<200:pores.append([x,y,w,h])
    verdict=("oxidation" if rust_ratio>.08 else "crack" if long_contours
             else "porosity" if len(pores)>1 else "clean")
    return {"synthetic_label":verdict,"crack_boxes":long_contours,
            "pore_boxes":pores,"oxidized_pixel_ratio":round(rust_ratio,5),
            "method":"OpenCV HSV and component geometry"}

def sign_scene(kind:str):
    if kind not in ("stop","warning","mandatory"):raise ValueError("Unknown sign")
    img=canvas()
    if kind=="stop":
        pts=np.array([[35,15],[61,15],[80,35],[80,60],[61,80],[35,80],[15,60],[15,35]],np.int32)
        cv2.fillPoly(img,[pts],(20,25,240))
    if kind=="warning":
        cv2.fillPoly(img,[np.array([[48,13],[82,78],[13,78]],np.int32)],(15,220,235))
    if kind=="mandatory":cv2.circle(img,(48,48),30,(235,95,25),-1)
    return img

def recognize_sign(image):
    validate_image(image)
    hsv=cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    masks={"stop":cv2.inRange(hsv,(0,150,130),(8,255,255)),
           "warning":cv2.inRange(hsv,(18,120,130),(40,255,255)),
           "mandatory":cv2.inRange(hsv,(100,120,90),(130,255,255))}
    coverage={k:int(cv2.countNonZero(m)) for k,m in masks.items()}
    label=max(coverage,key=coverage.get)
    if coverage[label]<100:return {"sign":"unknown","geometry":"unknown"}
    cnts,_=cv2.findContours(masks[label],cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    largest=max(cnts,key=cv2.contourArea)
    corners=len(cv2.approxPolyDP(largest,.035*cv2.arcLength(largest,True),True))
    return {"sign":label,"polygon_corners":corners,"colored_area_px":coverage[label],
            "method":"OpenCV HSV + contour polygons","control_action_executed":False}

COLORS={"ferrous":(90,90,90),"aluminum":(210,210,210),"copper":(45,125,205)}
def scrap_scene(kind:str,seed:int=2026):
    if kind not in COLORS:raise ValueError("Unknown metal")
    image=canvas()
    cv2.rectangle(image,(12,12),(83,83),COLORS[kind],-1)
    rng=np.random.default_rng(seed)
    jitter=rng.integers(-12,13,size=(72,72,1),dtype=np.int16)
    region=image[12:84,12:84].astype(np.int16)+jitter
    image[12:84,12:84]=np.clip(region,0,255).astype(np.uint8)
    return image

def classify_scrap(image):
    validate_image(image)
    # Explicit histogram descriptors on segmented specimen region, NOT chemistry identification.
    roi=image[12:84,12:84]
    descriptor=cv2.calcHist([roi],[0,1,2],None,[8,8,8],[0,256,0,256,0,256]).ravel()
    descriptor=descriptor/max(float(np.linalg.norm(descriptor)),1)
    comparisons={}
    for k in COLORS:
        ref=scrap_scene(k)
        hist=cv2.calcHist([ref[12:84,12:84]],[0,1,2],None,[8,8,8],[0,256,0,256,0,256]).ravel()
        hist=hist/max(float(np.linalg.norm(hist)),1)
        comparisons[k]=float(np.dot(hist,descriptor))
    label=max(comparisons,key=comparisons.get)
    return {"category":label,"cosine_histogram":round(comparisons[label],6),
            "method":"OpenCV 3D color histogram comparison",
            "material_certification":False}

def yard_frames(n:int=6):
    if not isinstance(n,int) or not 2<=n<=30:raise ValueError("2 to 30 frames")
    frames=[]
    for t in range(n):
        img=canvas()
        for start,y in ((9,25),(22,68)):
            x=start+4*t
            cv2.rectangle(img,(x,y-9),(x+17,y+9),(242,242,242),-1)
        frames.append(img)
    return frames

def track_yard(frames):
    if not isinstance(frames,list) or not frames:raise ValueError("Provide nonempty frame list")
    trajectories={}
    previous={}
    next_id=1
    for t,img in enumerate(frames):
        boxes=detect_parts(img)["bounding_boxes"]
        centers=sorted([(x+w//2,y+h//2) for x,y,w,h in boxes],key=lambda q:q[1])
        if t==0:
            for center in centers:
                trajectories[next_id]=[list(center)]
                previous[next_id]=center
                next_id+=1
            continue
        unmatched=set(previous)
        current={}
        for center in centers:
            available=[(np.hypot(center[0]-previous[i][0],center[1]-previous[i][1]),i) for i in unmatched]
            if available and min(available)[0] <= 15:
                _,id=min(available)
                unmatched.remove(id)
                current[id]=center
                trajectories[id].append(list(center))
            else:
                current[next_id]=center
                trajectories[next_id]=[list(center)]
                next_id+=1
        previous=current
    return {"unique_tracks":len(trajectories),"track_paths":{str(k):v for k,v in trajectories.items()},
            "frames":len(frames),"method":"OpenCV detections + nearest centroid association",
            "real_vehicle_identity":False}

def texture(kind:str, seed:int=2026):
    if kind not in ("ferrite","pearlite","martensite"):raise ValueError("Unknown texture")
    rng=np.random.default_rng(seed)
    image=canvas((80,80,80))
    if kind=="ferrite":
        for _ in range(24):
            x=int(rng.integers(5,90));y=int(rng.integers(5,90))
            cv2.circle(image,(x,y),int(rng.integers(3,9)),(185,185,185),1)
    elif kind=="pearlite":
        for x in range(5,96,8):cv2.line(image,(x,0),(x+24,95),(205,205,205),2)
    else:
        for _ in range(18):
            x=int(rng.integers(5,90));y=int(rng.integers(5,90))
            cv2.line(image,(x,y),(min(95,x+int(rng.integers(5,23))),max(0,y-15)),(230,230,230),2)
    return image

def train_torch_microstructure(seed=2026,epochs=3):
    import torch
    from torch import nn
    torch.manual_seed(seed)
    torch.set_num_threads(1)
    classes=["ferrite","pearlite","martensite"]
    # Train/test draw differently seeded texture instances with no repeated image.
    x=np.stack([cv2.cvtColor(texture(kind,seed+i),cv2.COLOR_BGR2GRAY)
                for kind in classes for i in range(16)])
    y=np.repeat(np.arange(3),16)
    xt=torch.from_numpy(x).float().unsqueeze(1)/255.
    yt=torch.from_numpy(y).long()
    model=nn.Sequential(nn.Conv2d(1,8,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                        nn.Conv2d(8,8,3,padding=1),nn.ReLU(),nn.AdaptiveAvgPool2d(1),
                        nn.Flatten(),nn.Linear(8,3))
    optimizer=torch.optim.Adam(model.parameters(),lr=.02)
    criterion=nn.CrossEntropyLoss()
    losses=[]
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        loss=criterion(model(xt),yt)
        loss.backward()
        optimizer.step()
        losses.append(float(loss.detach()))
    model.eval()
    test=np.stack([cv2.cvtColor(texture(k,seed+200),cv2.COLOR_BGR2GRAY) for k in classes])
    with torch.no_grad():
        pred=torch.softmax(model(torch.tensor(test).float().unsqueeze(1)/255.),dim=1).numpy()
    return {"architecture":"PyTorch Conv2d CNN (trained CPU)","train_rows":48,
            "unseen_test_rows":3,"training_losses":[round(v,6) for v in losses],
            "heldout_accuracy":round(float(np.mean(np.argmax(pred,axis=1)==np.arange(3))),5),
            "test_probabilities":np.round(pred,5).tolist(),"labels":classes}

def train_tensorflow_ppe(seed=2026,epochs=2):
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL","2")
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    labels=[0,1]
    image=np.stack([cv2.cvtColor(render_ppe(bool(label),seed+i),cv2.COLOR_BGR2GRAY)
                    for label in labels for i in range(16)])
    y=np.repeat(labels,16)
    model=tf.keras.Sequential([
        tf.keras.layers.Input(shape=(96,96,1)),
        tf.keras.layers.Rescaling(1./255),
        tf.keras.layers.Conv2D(4,5,activation="relu",strides=3),
        tf.keras.layers.MaxPooling2D(2),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(2,activation="softmax"),
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(.004),
                  loss="sparse_categorical_crossentropy",metrics=["accuracy"])
    hist=model.fit(image[...,None],y,batch_size=16,epochs=epochs,verbose=0)
    test=np.stack([cv2.cvtColor(render_ppe(bool(label),seed+100),cv2.COLOR_BGR2GRAY)
                   for label in labels])
    probabilities=model.predict(test[...,None],verbose=0)
    return {"architecture":"TensorFlow/Keras Conv2D CNN, trained", "train_rows":32,
            "unseen_test_rows":2,"losses":[round(v,6) for v in hist.history["loss"]],
            "heldout_accuracy":round(float(np.mean(np.argmax(probabilities,axis=1)==labels)),5),
            "test_probabilities":np.round(probabilities,5).tolist(),"labels":["no_helmet","helmet"]}

def run(project:int,seed:int=2026,save:bool=False,deep:bool=False):
    if project not in CONFIG:raise ValueError("Invalid CV project")
    image=None
    if project==71:
        image=render_ppe(True,seed)
        output={"helmet_color_mask":round(float(np.mean(cv2.inRange(cv2.cvtColor(image,cv2.COLOR_BGR2HSV),(15,70,80),(45,255,255))>0)),5),
                "trained_cnn":train_tensorflow_ppe(seed) if deep else "Run --deep for actual TensorFlow training"}
    elif project==72:
        image=render_gesture("open")
        output=gestures(image)
    elif project==73:
        image=parts_scene(5)
        output=detect_parts(image)
    elif project==74:
        image=eye_scene(True)
        output=vigilance_sequence([True,True,False,False,True,False,True,True])
    elif project==75:
        image=serial_scene("AB1234")
        output=recognize_serial(image)
    elif project==76:
        image=surface_scene("crack")
        output=analyze_surface(image)
    elif project==77:
        image=sign_scene("stop")
        output=recognize_sign(image)
    elif project==78:
        image=scrap_scene("copper",seed)
        output=classify_scrap(image)
    elif project==79:
        image=yard_frames(6)[-1]
        output=track_yard(yard_frames(6))
    elif project==80:
        image=texture("pearlite",seed)
        output={"trained_cnn":train_torch_microstructure(seed) if deep else "Run --deep for actual PyTorch training"}
    report={"project_id":project,"name":CONFIG[project]["title"],
            "result":output,"source":"SYNTHETIC OpenCV-rendered images",
            "input_image_real":False,"production_validated":False,
            "limitations":"No field images, production detection metrics or safety certification"}
    if save:
        out=ROOT/"reports"
        out.mkdir(exist_ok=True)
        (out/f"{project:03d}.json").write_text(json.dumps(report,indent=2)+"\n")
        cv2.imwrite(str(out/f"{project:03d}.png"),image)
    return report

def cli(project:int|None=None):
    p=argparse.ArgumentParser(description="Industrial CV demonstration with synthetic images")
    if project is None:p.add_argument("project",type=int,choices=sorted(CONFIG))
    p.add_argument("--save",action="store_true")
    p.add_argument("--deep",action="store_true",help="Train TensorFlow #071 or PyTorch #080 CNN")
    a=p.parse_args()
    print(json.dumps(run(project if project is not None else a.project,save=a.save,deep=a.deep),indent=2))

if __name__=="__main__":
    cli()
