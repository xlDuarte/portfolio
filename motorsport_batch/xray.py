"""#105: actual Conv2D training, synthetic radiographic voids and Grad-CAM."""
import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL","2")
import cv2
import numpy as np

def sample(has_void:bool,seed:int,size=64):
    rng=np.random.default_rng(seed)
    image=np.full((size,size),.57,dtype="float32")
    mask=np.zeros((size,size),dtype=np.uint8)
    if has_void:
        radius=int(rng.integers(5,11))
        cx=int(rng.integers(16,48));cy=int(rng.integers(16,48))
        cv2.circle(mask,(cx,cy),radius,1,-1)
        image[mask>0]=.12
    image=np.clip(image+rng.normal(0,.028,image.shape),0,1)
    return image.astype("float32"),mask

def dataset(seed=105,n=120):
    rows=[sample(i%2==0,seed+i) for i in range(n)]
    return np.stack([x for x,_ in rows])[...,None],np.stack([m for _,m in rows]),np.arange(n)%2==0

def evaluate(seed=105,epochs=3):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    x,mask,y=dataset(seed,120)
    # True test samples are produced with unrelated random seeds.
    testrows=[sample(i%2==0,seed+10000+i) for i in range(24)]
    xt=np.stack([x for x,m in testrows])[...,None]
    mt=np.stack([m for x,m in testrows])
    yt=np.arange(24)%2==0
    inp=tf.keras.Input(shape=(64,64,1))
    z=tf.keras.layers.Conv2D(8,3,activation="relu",padding="same")(inp)
    z=tf.keras.layers.MaxPooling2D(2)(z)
    z=tf.keras.layers.Conv2D(12,3,activation="relu",padding="same",name="last_conv")(z)
    z=tf.keras.layers.GlobalAveragePooling2D()(z)
    out=tf.keras.layers.Dense(1,activation="sigmoid")(z)
    model=tf.keras.Model(inp,out)
    model.compile(optimizer=tf.keras.optimizers.Adam(.008),loss="binary_crossentropy",metrics=["accuracy"])
    history=model.fit(x,y.astype("float32"),epochs=epochs,batch_size=24,verbose=0)
    prob=model.predict(xt,verbose=0).reshape(-1)
    grad_model=tf.keras.Model(model.inputs,[model.get_layer("last_conv").output,model.output])
    def cam(img):
        with tf.GradientTape() as tape:
            conv,score=grad_model(img[None,...],training=False)
            target=score[:,0]
        grads=tape.gradient(target,conv)[0]
        pooled=tf.reduce_mean(grads,axis=(0,1))
        heat=tf.nn.relu(tf.reduce_sum(conv[0]*pooled,axis=-1)).numpy()
        heat=cv2.resize(heat,(64,64),interpolation=cv2.INTER_LINEAR)
        return heat/(heat.max()+1e-8)
    heats=[cam(xt[i]) for i in range(0,len(xt),2)]
    ious=[]
    for heat,gt in zip(heats,mt[::2]):
        binary=heat>=max(.4,float(np.quantile(heat,.86)))
        union=np.logical_or(binary,gt>0).sum()
        ious.append(float(np.logical_and(binary,gt>0).sum()/max(union,1)))
    return {"project_id":105,"model":"TensorFlow CNN trained, GradientTape Grad-CAM",
            "train_samples":len(x),"untouched_test_samples":len(xt),
            "test_accuracy":round(float(np.mean((prob>=.5)==yt)),5),
            "loss_last_epoch":round(float(history.history["loss"][-1]),6),
            "gradcam_masks_computed":len(heats),
            "gradcam_mean_iou_on_synthetic_voids":round(float(np.mean(ious)),5),
            "heatmap_shape":[64,64],"example_gradcam_heatmap":np.round(heats[0],4).tolist(),
            "ground_truth_void_mask":mt[0].tolist(),
            "source":"SYNTHETIC radiographs, no actual X-ray NDT validation",
            "production_validated":False}
