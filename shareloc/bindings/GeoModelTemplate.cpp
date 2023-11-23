/*
!/usr/bin/env python
coding: utf8

Copyright (c) 2023 Centre National d'Etudes Spatiales (CNES).

This file is part of shareloc
(see https://github.com/CNES/shareloc).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

/**
Cpp copy of GeoModelTemplate.py
*/


GeoModelTemplate::GeoModelTemplate() {
    cout<<"GeoModelTemplate : constructor"<<endl;
}
GeoModelTemplate::~GeoModelTemplate() {
    cout<<"GeoModelTemplate : destructor"<<endl;
}

vector<vector<double>> GeoModelTemplate::direct_loc_h(
    vector<double> row, 
    vector<double> col,
    double alt, 
    bool fill_nan){
    cout<<"GeoModelTemplate : direct_loc_h"<<endl;
    vector<vector<double>> vect;
    return vect;
}

vector<vector<double>> GeoModelTemplate::direct_loc_dtm(
    vector<double> row,
    vector<double> col,
    string dtm){
    cout<<"GeoModelTemplate : direct_loc_dtm"<<endl;
    vector<vector<double>> vect;
    return vect;
}

tuple<vector<double>,vector<double>,vector<double>> GeoModelTemplate::inverse_loc(
    vector<double> lon,
    vector<double> lat,
    double alt){
    cout<<"GeoModelTemplate : inverse_loc"<<endl;
    tuple<vector<double>,vector<double>,vector<double>> res;
    return res;
}