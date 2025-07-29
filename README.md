# Blocky's Cloud Cover Segmentation Network

## 📌 Project Description

This project aims to develop an automatic **cloud cover classification system** using an All-Sky Camera mounted on a **Raspberry Pi 5**. The system employs a **Convolutional Neural Network (CNN)** based on the **MobileNetV3** architecture to classify sky images into several categories.

The system supports automated, efficient, and low-cost weather monitoring applications in remote or urban environments.



## 🚀 Key Features

- 📷 Automatic sky image acquisition using a fisheye All-Sky Camera
- 🧠 Image classification using a lightweight MobileNetV3 CNN model
- 🗂️ Automatic labeling based on Total Cloud Cover (TCC) weather data
- 📊 Visualization of predictions and model performance
- ⚙️ Lightweight deployment optimized for Raspberry Pi and edge devices

## 📸 Sample Images & Classification

| Sky Image | Classification |
|-----------|----------------|
| ![Clear](assets/clear_example.jpg) | Clear |
| ![Cloudy](assets/cloudy_example.jpg) | Cloudy |

## 📈 Model Performance

The MobileNetV3 model achieved up to **XX% accuracy** on the test dataset and runs in near real-time on Raspberry Pi 5.

| Metric    | Value |
|-----------|-------|
| Accuracy  | XX%   |
| Precision | XX%   |
| Recall    | XX%   |
| F1-Score  | XX%   |

## Dataset

The dataset was collected using a self-built All-Sky Camera installed at [your location], with labels derived from Total Cloud Cover (TCC) data obtained from weather APIs such as Open-Meteo, ECMWF, or local meteorological sources.

## Author

- [@raftorblocky](https://www.github.com/raftorblocky)

## License

This project is licensed under the MIT License — feel free to use, modify, and distribute it for both academic and commercial purposes.
