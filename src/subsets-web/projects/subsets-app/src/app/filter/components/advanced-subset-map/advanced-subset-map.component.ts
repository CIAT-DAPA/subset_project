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

@Component({
  selector: 'advanced-subset-map',
  templateUrl: './advanced-subset-map.component.html',
  styleUrls: ['./advanced-subset-map.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class AdvancedSubsetMapComponent implements OnInit, OnChanges, AfterViewInit {
  @Input() data: any;
  vectorSource: any;
  vectorSourceT: any;
  vectorLayer: any;
  rasterLayer: any;
  popupOverlay: any;
  map!: Map;
  constructor(
    private renderer: Renderer2, public dialog: MatDialog, private _sharedService: SharedService
  ) { }

  
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
    this.map = new Map({
      target: 'subset-map',
      controls: defaultCOntrols({
        attributionOptions: {
          collapsible: false,
          
        },
      }),
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: olProj.fromLonLat([0, 0]),
        zoom: 1,
        
      }),
    });
  }

  ngOnChanges(changes: SimpleChanges) {
  
  }

  ngAfterViewInit() {
    setInterval( () => {
      this.map.updateSize();
  }, 100);
  }

  drawMap() {
    var coordinates: any = [];
    this.data.data.forEach((val: any, index: any) => {
      if (val.geo_lon != null && val.geo_lat != null) {
        let marker = new Feature({
          geometry: new Point(fromLonLat([val.geo_lon, val.geo_lat])),
          name: val.name,
          crop: val.crop,
          obj: val,
        });
        coordinates.push(marker);
      }
    });

    var iconStyle = new Style({
      image: new CircleStyle({
        radius: 3,
      /*   stroke: new Stroke({
          color: 'orange',
          width: 2,
        }), */
        fill: new Fill({
          color: 'green',
        }),
      }),
    });

    var labelStyle = new Style({
      text: new Text({
        font: '8px Calibri,sans-serif',
        overflow: true,
        fill: new Fill({
          color: '#000',
        }),
        stroke: new Stroke({
          color: '#fff',
          width: 3,
        }),
      }),
    });

    /* let selectSingleClick = new Select(); */

    var style = [iconStyle];

    this.vectorSourceT = new VectorSource({
      features: coordinates,
    });

    this.vectorLayer = new VectorLayer({
      source: this.vectorSourceT,
      style: function (feature) {
        labelStyle.getText().setText(feature.get('name'));
        return style;
      },
    });

    this.map = new Map({
      target: 'subset-map',
      controls: defaultCOntrols({
        attributionOptions: {
          collapsible: false,
          
        },
      }),
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: olProj.fromLonLat([0, 0]),
        zoom: 1,
        
      }),
    });

    this.map.addLayer(
      this.vectorLayer
    )

    var container = document.getElementById('popup');
    var overlay = new Overlay({
      element: container as HTMLElement,
      autoPan: true,
      autoPanAnimation: {
        duration: 250,
      },
    });
    this.map.addOverlay(overlay);

    var closer: any = document.getElementById('popup-closer');
    closer.onclick = function () {
      overlay.setPosition(undefined);
      closer.blur();
      return false;
    };

    var content: any = document.getElementById('popup-content');
    this.map.on('singleclick', function (this: any, evt: any) {
      var name = this.forEachFeatureAtPixel(evt.pixel, function (feature: any) {
        return feature.get('name');
      });
      var coordinate = evt.coordinate;
      content.innerHTML = name;
      overlay.setPosition(coordinate);
    });

    this.map.on('pointermove', function (this: any, evt: any) {
      //this.getTargetElement().style.cursor = this.hasFeatureAtPixel(evt.pixel) ? 'pointer' : '';
      var name = this.forEachFeatureAtPixel(evt.pixel, function (feature: any) {
        return feature.get('name');
      });
      var crop = this.forEachFeatureAtPixel(evt.pixel, function (feature: any) {
        return feature.get('crop');
      });
      if (name) {
        var coordinate = evt.coordinate;
        content.innerHTML = name + " " + crop;
        overlay.setPosition(coordinate);
      }
    });

    this.map.on('singleclick', (evt: any) => {
      this.map.forEachFeatureAtPixel(evt.pixel, (layer: any) => {
        var obj = layer.get('obj');
        this.openAccessionDetail(obj);
      });
    });

    this.map.updateSize();
  }

  setCenter() {
    var view = this.map.getView();
    view.setCenter(olProj.fromLonLat([0, 0]));
    view.setZoom(8);
  }


}
