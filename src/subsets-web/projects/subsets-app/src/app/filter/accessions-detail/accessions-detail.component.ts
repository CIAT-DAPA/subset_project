import { Component, Inject, OnInit } from '@angular/core';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { ActivatedRoute, Router } from '@angular/router';
import { DialogData } from '../components/form-filter/form-filter.component';
import Map from 'ol/Map';
import View from 'ol/View';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { fromLonLat } from 'ol/proj.js';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import VectorSource from 'ol/source/Vector';
import { Circle as CircleStyle, Fill, Stroke, Icon, Style, Text } from 'ol/style';
import OSM from 'ol/source/OSM';
import * as olProj from 'ol/proj';
import XYZ from 'ol/source/XYZ';
import { defaults as defaultCOntrols } from 'ol/control'

@Component({
  selector: 'alliance-cgiar-org-accessions-detail',
  templateUrl: './accessions-detail.component.html',
  styleUrls: ['./accessions-detail.component.scss']
})
export class AccessionsDetailComponent implements OnInit {
  latitude: number = 18.5204;
  longitude: number = 73.8567;  
  vectorSource: any;
  vectorSourceT: any;
  vectorLayer: any;
  rasterLayer: any;
pointAccession:any;
  map: any;

  constructor(private route: ActivatedRoute,
    private router: Router, @Inject(MAT_DIALOG_DATA) public data:any , private dialogRef: MatDialogRef<AccessionsDetailComponent>,) {
     }

  ngOnInit(): void {
  if (this.data.accession.geo_lon && this.data.accession.geo_lat) {

    this.pointAccession = new Feature({
      geometry: new Point(fromLonLat([this.data.accession.geo_lon, this.data.accession.geo_lat])),
    });

    this.pointAccession.setStyle(new Style({
      image: new CircleStyle({
        radius: 10,
        stroke: new Stroke({
          color: 'orange',
          width: 2
        }),
        fill: new Fill({
          color: 'green'
        })
      }),

    }));

    this.vectorSourceT = new VectorSource({
      features: [this.pointAccession,]
    });

    this.vectorLayer = new VectorLayer({
      source: this.vectorSourceT,

    });

    this.map = new Map({
      target: 'map-detail',
      controls: defaultCOntrols({
        attributionOptions: {
          collapsible: false
        }
      }),
      layers: [
        new TileLayer({
          source: new OSM()
        }), this.vectorLayer
      ],
      view: new View({
        center: olProj.fromLonLat([0, 0]),
        zoom: 1
      })
    });
    
    this.setCenter()
  }    
    
  }

  setCenter() {
    var view = this.map.getView();
    view.setCenter(olProj.fromLonLat([this.data.accession.geo_lon, this.data.accession.geo_lat]));
    view.setZoom(8);
  }

}
