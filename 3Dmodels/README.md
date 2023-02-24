# Referencing 3D models

The script *sumo2czml_3Dmodels.py* links each traffic member (passenger or pedestrian) with a 3D model. For demonstration purposes, the following openly available 3D models are referenced:

- passenger: CesiumMilkTruck.glb [avialable here](https://github.com/CesiumGS/cesium/blob/main/Apps/SampleData/models/CesiumMilkTruck/CesiumMilkTruck.glb).
- pedestrian: Cesium_Man.glb [avialable here](https://github.com/CesiumGS/cesium/blob/main/Apps/SampleData/models/CesiumMan/Cesium_Man.glb).

The script also contains the possibility to create random links for *passengers* to models called [1-16].gltf. In this way 16 different 3D vehicle models with corresponding names can be referenced randomly. The function creating these links can be easily extended to other traffic types and to different 3D models. 

**Note:** Rotations performed in the script to correctly rotate 3D models depend on the position of traffic members (geodetic latitude and longitude) on the local tangent plane of the virtual globe as well as the orientation of 3D models in their local model frame and might need to be adapted according to the placement of 3D models in their local model frame.    