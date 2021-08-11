import { Component, Inject, OnInit } from '@angular/core';
import Map from 'ol/Map';
import View from 'ol/View';
import  MousePosition  from 'ol/control/MousePosition'
import  * as coordinate  from 'ol/coordinate'
import { defaults as defaultCOntrols } from 'ol/control'
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import OSM from 'ol/source/OSM';
import * as olProj from 'ol/proj';
import { MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { DialogData } from '../form-filter/form-filter.component';


@Component({
  selector: 'add-point-map',
  templateUrl: './add-point-map.component.html',
  styleUrls: ['./add-point-map.component.scss']
})
export class AddPointMapComponent implements OnInit {
  latitude: number = 18.5204;
  longitude: number = 73.8567;

  map: any;

  constructor(@Inject(MAT_DIALOG_DATA) public data: DialogData, private dialogRef: MatDialogRef<AddPointMapComponent>,) {}

  ngOnInit(): void {

    setTimeout(() => {
      
    var mousePositionControl = new MousePosition({
      coordinateFormat: coordinate.createStringXY(4),
      projection: 'EPSG:4326',
      // comment the following two lines to have the mouse position
      // be placed within the map.
      className: 'custom-mouse-position',
      target: <HTMLElement> document.getElementById('mouse-position'),
      undefinedHTML: '&nbsp;'
    });

    this.map = new Map({
      target: 'map',
      controls: defaultCOntrols({
        attributionOptions: {
          collapsible: false
        }
      }).extend([mousePositionControl]),
      layers: [
        new TileLayer({
          source: new OSM()
        })
      ],
      view: new View({
        center: olProj.fromLonLat([0, 0]),
        zoom: 2
      })
    });

    this.map.on('click', function (args:any) {
      console.log(args.coordinate);
      var lonlat = olProj.transform(args.coordinate, 'EPSG:3857', 'EPSG:4326');
      console.log(lonlat);
      
      var lon = lonlat[0];
      var lat = lonlat[1];
      
    });
    
  }, 100);
  }

  setCenter() {
    var view = this.map.getView();
    view.setCenter(olProj.fromLonLat([this.longitude, this.latitude]));
    view.setZoom(8);
  }

  accept() {
    let dataCoordinate = {
      longitude: this.longitude, latitude: this.latitude
    }
    this.dialogRef.close(dataCoordinate);
  }

  close() {
    this.dialogRef.close();
}

}
