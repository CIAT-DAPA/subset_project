import {
  Component,
  OnInit,
  Input,
  AfterContentInit,
  Renderer2,
  OnChanges,
  RendererFactory2,
  ElementRef,
  ViewChild,
  ChangeDetectionStrategy,
  SimpleChanges,
  AfterViewInit
} from '@angular/core';
import Map from 'ol/Map';
import View from 'ol/View';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import { fromLonLat } from 'ol/proj.js';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import VectorSource from 'ol/source/Vector';
import {
  Circle as CircleStyle,
  Fill,
  Stroke,
  Icon,
  Style,
  Text,
} from 'ol/style';
import OSM from 'ol/source/OSM';
import * as olProj from 'ol/proj';
import XYZ from 'ol/source/XYZ';
import Overlay from 'ol/Overlay';
import { Control, defaults as defaultCOntrols } from 'ol/control';
import Select from 'ol/interaction/Select';
import { SharedService } from '../../../core/service/shared.service';
import OverlayPositioning from 'ol/OverlayPositioning';
import { toStringHDMS } from 'ol/coordinate';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';


export const DEFAULT_HEIGHT = '500px';
export const DEFAULT_WIDTH = '500px';
import * as L from 'leaflet';

@Component({
  selector: 'advanced-subset-map',
  templateUrl: './advanced-subset-map.component.html',
  styleUrls: ['./advanced-subset-map.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AdvancedSubsetMapComponent implements OnInit, OnChanges, AfterViewInit {
  @Input() data: any;
  @Input() showMap: any;
  vectorSource: any;
  vectorSourceT: any;
  vectorLayer: any;
  rasterLayer: any;
  popupOverlay: any;
  map!: any;
  constructor(
    private renderer: Renderer2, public dialog: MatDialog, private _sharedService: SharedService
  ) { }

   initMap(): void {
    this.map = L.map('advanced-map', {
      center: [0, 0],
      zoom: 2,
      zoomControl: false 
    });

    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      minZoom: 2,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    });

    tiles.addTo(this.map);

    L.control.zoom({
      position: 'bottomright'
    }).addTo(this.map)


    this.data.data.forEach((val: any, index: any) => {
      if (val.geo_lon != null && val.geo_lat != null) {
        const marker = L.circleMarker([val.geo_lat, val.geo_lon],{ radius: 5 });
        marker.addTo(this.map);
        marker.setStyle({color: 'green'});
        marker.bindPopup( "Name: " + val.name + " Crop: " + val.crop,);
        marker.on('mouseover', function(event){
          marker.openPopup();
        });
        marker.on('mouseout', function(event){
          marker.closePopup();
        });
        marker.on('click', () => {
          this.openAccessionDetail(val)
        });
      }
    });
  }


  
  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
  }

  ngOnInit() {  
    // this.drawMap();
    // this.map = new Map({
    //   target: 'subset-map',
    //   controls: defaultCOntrols({
    //     attributionOptions: {
    //       collapsible: false,
          
    //     },
    //   }),
    //   layers: [
    //     new TileLayer({
    //       source: new OSM(),
    //     }),
    //   ],
    //   view: new View({
    //     center: olProj.fromLonLat([0, 0]),
    //     zoom: 1,
        
    //   }),
    // });
  }

  ngOnChanges(changes: SimpleChanges) {
    if (this.showMap == true)
    this.initMap()
    console.log(this.showMap)
  }

  ngAfterViewInit() {
  }



}
