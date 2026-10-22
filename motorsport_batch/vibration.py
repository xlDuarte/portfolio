"""#104: genuinely trained Keras LSTM autoencoder, time-aligned synthetic vibrations."""
import os
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL","2")
import numpy as np
from sklearn.metrics import precision_recall_fscore_support

def sequences(seed=104,n_normal=200,n_fault=72,width=32):
    rng=np.random.default_rng(seed)
    def one(i,fault):
        t=np.arange(width,dtype=float)
        phase=float(rng.uniform(0,2*np.pi))
        fundamental=2.0*np.sin(2*np.pi*t/width*3+phase)
        modulation=.36*np.sin(2*np.pi*t/width*7+phase)
        anomaly=(1.35*np.sin(2*np.pi*t/width*12+phase)+.8)*(int(fault))
        return (fundamental+modulation+anomaly+rng.normal(0,.15,width)).astype("float32")
    normal=np.stack([one(i,False) for i in range(n_normal)])
    faulty=np.stack([one(i,True) for i in range(n_fault)])
    return normal,faulty

def evaluate(seed=104,epochs=3):
    import tensorflow as tf
    tf.keras.utils.set_random_seed(seed)
    tf.config.threading.set_intra_op_parallelism_threads(1)
    tf.config.threading.set_inter_op_parallelism_threads(1)
    normal,faulty=sequences(seed)
    train=normal[:144]
    valid=normal[144:172]
    test=np.concatenate([normal[172:],faulty],axis=0)
    truth=np.array([0]*(len(normal)-172)+[1]*len(faulty))
    mean,std=train.mean(),train.std()
    def toinput(x):return ((x-mean)/max(std,1e-6))[...,None]
    model=tf.keras.Sequential([
        tf.keras.layers.Input(shape=(train.shape[1],1)),
        tf.keras.layers.LSTM(12,return_sequences=False),
        tf.keras.layers.RepeatVector(train.shape[1]),
        tf.keras.layers.LSTM(12,return_sequences=True),
        tf.keras.layers.TimeDistributed(tf.keras.layers.Dense(1))
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(.005),loss="mse")
    history=model.fit(toinput(train),toinput(train),epochs=epochs,batch_size=24,verbose=0,
                      validation_data=(toinput(valid),toinput(valid)))
    scores=lambda x:np.mean((model.predict(toinput(x),verbose=0)-toinput(x))**2,axis=(1,2))
    cutoff=float(np.quantile(scores(valid),.95))
    predicted=(scores(test)>cutoff).astype(int)
    baseline_signal=np.sqrt(np.mean(train**2,axis=1))
    rms_cutoff=float(np.quantile(baseline_signal,.95))
    baseline=(np.sqrt(np.mean(test**2,axis=1))>rms_cutoff).astype(int)
    def metric(pred):
        p,r,f,_=precision_recall_fscore_support(truth,pred,average="binary",zero_division=0)
        return {"precision":round(float(p),5),"recall":round(float(r),5),"f1":round(float(f),5)}
    return {"project_id":104,"architecture":"TensorFlow/Keras trainable LSTM sequence autoencoder",
            "train_normal_sequences":len(train),"validation_normal_sequences":len(valid),
            "untouched_test_normal":int((truth==0).sum()),"untouched_test_fault":int(truth.sum()),
            "trained_epoch_count":epochs,"last_train_loss":float(history.history["loss"][-1]),
            "threshold_calibrated_on_validation_only":round(cutoff,5),
            "lstm":metric(predicted),"rms_threshold_baseline":metric(baseline),
            "data_origin":"synthetic vibration sinusoids, not sensor observations",
            "production_validated":False}
