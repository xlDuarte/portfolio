# Industrial Computer Vision #071–#080

**All images are generated entirely with OpenCV and NumPy. They are NOT factory-camera photos, actual operators, vehicles, industrial stamps, or metallographic samples.** The pipelines implement real image computations and (for #071/#080) actual CPU CNN training, but none is homologated for production, safety, purchasing or regulatory purposes.

| ID | Implemented capability | Real technology |
|---|---|---|
| #071 | Helmet-color segmentation, separate TensorFlow CNN fit on 32 fake worker images | OpenCV, NumPy, TensorFlow/Keras Conv2D |
| #072 | Contour shape matching of rendered hand gestures (never activates HMI) | OpenCV matchShapes |
| #073 | Segmentation and bounding boxes for artificial separated forged parts | OpenCV findContours |
| #074 | Synthetic eye aperture tracking and PERCLOS fraction (never claims actual fatigue diagnosis) | OpenCV, NumPy |
| #075 | OCR of artificially printed, high-contrast serial (not embossed/gravity-stamped metal) | OpenCV Otsu, Tesseract OCR |
| #076 | Contrasted artificial surface defects: crack, pores, oxidation | OpenCV contours and HSV |
| #077 | Color/shape recognition for synthetic stop/warning/mandatory sign | OpenCV HSV, polygon approximation |
| #078 | Metal-class classification based on artificial specimen color | OpenCV color histogram |
| #079 | Two non-overlapping moving fake yard objects; nearest centroid data association | OpenCV contours + NumPy |
| #080 | Ferrite/pearlite/martensite-like artificial textures; actual PyTorch Conv2d CNN fit | OpenCV, PyTorch |

**Important:** The portfolio-category list names OpenCV, TensorFlow, PyTorch and NumPy, but *each* project uses the actual subset described above. No model pretrained on genuine photographs is being claimed. The artificial ferrite/pearlite/martensite textures have no established metallographic validity. #072 never sends industrial control commands, and #074 does not interpret facial emotion or record real persons.

## Reproducibility

Requirements for the core:
\`\`\`bash
sudo apt-get install -y tesseract-ocr
python -m pip install -r requirements-vision.txt
python -m unittest discover -s tests -p test_vision_batch.py -v
python -m vision_batch.engine 75 --save
python -m vision_batch.engine 79 --save
\`\`\`

To verify both deep learning frameworks:
\`\`\`bash
python -m pip install -r requirements-vision-deep.txt
python -m unittest discover -s tests -p test_vision_deep.py -v
python -m vision_batch.engine 71 --deep --save
python -m vision_batch.engine 80 --deep --save
\`\`\`

The project entrypoints in \`projetos/08-vision/<ID>-*/main.py\` accept \`--save\` and \`--deep\`. Only #071 and #080 train CNNs with \`--deep\`; other projects are classical image processing. Output is a JSON report and an actual PNG generated from synthetic scene primitives in \`vision_batch/reports/\`.

## Data governance, failures and exclusions

Synthetic shape/color segmentation is easy relative to real plant deployments. No performance estimate against annotated real images, localization mAP, precision/recall across lighting, domain adaptation, validated OCR character-error rate for embossed metal, sign robustness, low-light cameras, multi-target tracking IDF1/HOTA, privacy impact assessment or safety certification is available. False negatives are especially critical in PPE and vigilance. **Do not run these prototypes as an enforcement, employee-monitoring or machine actuation system.** #078 color histograms cannot identify elemental composition; #080 visual texture simulation cannot replace microscopic analysis.

Source images and reports are deterministic synthetic evidence only. Frameworks do not contact external inference APIs and model weights are initialized and fitted locally.
