import { Component, OnInit, AfterContentInit, Input } from '@angular/core';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { combineLatest, forkJoin, from, Observable, of, zip } from 'rxjs';
import { groupBy, map, mergeMap, switchMap, toArray } from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';

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
import { defaults as defaultCOntrols } from 'ol/control';

@Component({
  selector: 'app-multivariable-analysis',
  templateUrl: './multivariable-analysis.component.html',
  styleUrls: ['./multivariable-analysis.component.scss'],
})
export class MultivariableAnalysisComponent
  implements OnInit, AfterContentInit {
  latitude: number = 18.5204;
  longitude: number = 73.8567;
  namesResponse: String[] = [];
  palmira: any;
  cali: any;
  map: any;
  @Input('popup') popup!: any;
  vectorSource: any;
  vectorSourceT: any;
  vectorLayer: any;
  rasterLayer: any;
  popupOverlay: any;

  accessions$: any = [];
  multivariable$: any = [];
  lst: any = [];
  lstGrouped: any = [];
  headersTable_1: any[];
  headersTable_2: any[];
  actualPageDbscan: number = 1;
  actualPageHdbscan: number = 1;
  actualPageAgglomerative: number = 1;
  actualPageT2: number = 1;
  res$: any;
  resMap$: any;
  test$: any;
  t1: any = of([1, 2, 3, 4, 5]);
  t2: any = of([6, 7, 8, 9, 10]);
  constructor(private _sharedService: SharedService, public dialog: MatDialog) {
    this.headersTable_1 = ['Crop', 'Name', 'Number', 'Cluster'];
    this.headersTable_2 = ['Crop', 'Min', 'Max', 'Avg', 'Indicator', 'Cluster'];
  }

  ngOnInit(): void {}

  setSummary(summ: any) {
    this._sharedService.sendSummary(summ);
  }

  seeVar() {
    /* this.multivariable$.forEach((element: any) => {
      let ncols: number = Object.keys(element).length;
      let names: any = Object.keys(element);
      for (let index = 1; index < ncols; index++) {
        if (names[index].includes('slope')) {
          let ind: any = names[index].split('_');
          if (ind.length == 2) {
            this.lst.push({ cellid: element.cellid, indicator: ind[1],  cluster: element.cluster,
            slope: element["slope_"+ind[1]],
            mean: element["mean_"+ind[1]],
            sd: element["sd_"+ind[1]]});
          }
          if (ind.length == 3) {
            this.lst.push({
              cellid: element.cellid,
              indicator: ind[1] + '_' + ind[2],
              cluster: element.cluster,
              slope: element["slope_"+ind[1] + '_' + ind[2]],
              mean: element["mean_"+ind[1] + '_' + ind[2]],
            sd: element["sd_"+ind[1] + '_' + ind[2]]
            });
          }
        }
      }
    }); */
    const mergeById = (t: any, s: any) =>
      t.map((p: any) =>
        Object.assign(
          {},
          p,
          s.find((q: any) => p.cellid == q.cellid)
        )
      );
    combineLatest([of(this.multivariable$), of(this.accessions$)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((res: any) => {
        this.res$ = res;
        // this.setSummary(this.res$);
      });
  }

  ngAfterContentInit() {
    this._sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
    });

    this._sharedService.sendMultivariableObservable.subscribe((res: any) => {
      this.multivariable$ = res;
      this.seeVar();
      this.namesResponse = Object.keys(this.multivariable$[0]);
      /* Combine */
      /* const mergeById = (t: any, s: any) =>
      t.map((p: any) =>
        Object.assign(
          {},
          p,
          s.find((q: any) => p.cellid == q.cellid)
        )
      );
    combineLatest([of(this.multivariable$), of(this.accessions$)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((prop: any) => {
        console.log(this.accessions$)
        console.log(prop)
      }); */
      this.multivariable$.forEach((element: any) => {
        this.namesResponse.forEach((prop: any) => {
          if (prop.includes('slope')) {
            let ind: any = prop.split('_');
            if (ind.length == 2) {
              this.lst.push({
                cellid: element.cellid,
                indicator: ind[1],
                cluster: element.cluster_aggolmerative,
                slope: element['slope_' + ind[1]],
                mean: element['mean_' + ind[1]],
                sd: element['sd_' + ind[1]],
              });
            }
            if (ind.length == 3) {
              this.lst.push({
                cellid: element.cellid,
                indicator: ind[1] + '_' + ind[2],
                cluster: element.cluster_aggolmerative,
                slope: element['slope_' + ind[1] + '_' + ind[2]],
                mean: element['mean_' + ind[1] + '_' + ind[2]],
                sd: element['sd_' + ind[1] + '_' + ind[2]],
              });
            }
          }
        });
      });
      // Grouped
      this.lstGrouped = of(this.lst)
        .pipe(
          switchMap((data: any) =>
            from(data).pipe(
              groupBy((item: any) => item.cluster),
              mergeMap((group) => {
                return group.pipe(toArray());
              }),
              mergeMap((arr: any) => {
                // Take each from above array and group each array by manDate
                return from(arr).pipe(
                  groupBy((val: any) => val.indicator),
                  mergeMap((group) => {
                    return group.pipe(toArray()); // return the group values as Arrays
                  })
                );
              }),
              /* map((val: any) => {
                return {
                  cellid: val[0].cellid,
                  indicator: val[0].indicator,
                  cluster: val[0].cluster,
                  slope: val[0].slope,
                  mean: val[0].mean,
                  sd: val[0].sd,
                };
              }), */
              groupBy((item: any) => item.indicator),
              mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
              toArray()
            )
          )
        )
        .subscribe((val: any) => console.log(val));
    });
  }

  drawMap(res: any) {
    var coordinates: any = [];
    res.forEach((element: any) => {
      let prop = element[1];
      prop.forEach((val: any) => {
        this.palmira = new Feature({
          geometry: new Point(fromLonLat([val.geo_lon, val.geo_lat])),
          name: val.name,
          obj: val,
        });
        coordinates.push(this.palmira);
      });
    });

    var iconStyle = new Style({
      image: new CircleStyle({
        radius: 10,
        stroke: new Stroke({
          color: 'orange',
          width: 2,
        }),
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
      target: 'maps',
      controls: defaultCOntrols({
        attributionOptions: {
          collapsible: false,
        },
      }),
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
        this.vectorLayer,
      ],
      view: new View({
        center: olProj.fromLonLat([0, 0]),
        zoom: 1,
      }),
    });

    var container = document.getElementById('popups');
    var overlay = new Overlay({
      element: container as HTMLElement,
      autoPan: true,
      autoPanAnimation: {
        duration: 250,
      },
    });
    this.map.addOverlay(overlay);

    var closer: any = document.getElementById('popup-closers');
    closer.onclick = function () {
      overlay.setPosition(undefined);
      closer.blur();
      return false;
    };

    var content: any = document.getElementById('popup-contents');
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
      if (name) {
        var coordinate = evt.coordinate;
        content.innerHTML = name;
        overlay.setPosition(coordinate);
      }
    });

    this.map.on('singleclick', (evt: any) => {
      this.map.forEachFeatureAtPixel(evt.pixel, (layer: any) => {
        var obj = layer.get('obj');
        this.openAccessionDetail(obj);
      });
    });
  }

  getInfoMap() {
    const mergeById = (t: any, s: any) =>
      t.map((p: any) =>
        Object.assign(
          {},
          p,
          s.find((q: any) => p.cellid === q.cellid)
        )
      );
    combineLatest([of(this.accessions$), of(this.multivariable$)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((res: any) => {
        this.resMap$ = res;
      });
    of(this.resMap$)
      .pipe(
        switchMap((data: any) =>
          from(data).pipe(
            groupBy((item: any) => item.cluster),
            mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
            toArray()
          )
        )
      )
      .subscribe((res: any) => {
        this.drawMap(res);
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
}
