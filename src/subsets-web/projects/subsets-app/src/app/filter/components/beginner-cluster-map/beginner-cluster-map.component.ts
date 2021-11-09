import {
  Component,
  OnInit,
  AfterContentInit,
  AfterViewInit,
  Input,
  OnChanges,
} from '@angular/core';
import { combineLatest, of, from, zip } from 'rxjs';
import {
  groupBy,
  map,
  mergeMap,
  reduce,
  switchMap,
  toArray,
} from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';

//
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
import OverlayPositioning from 'ol/OverlayPositioning';
import { toStringHDMS } from 'ol/coordinate';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';
import * as L from 'leaflet';

@Component({
  selector: 'beginner-cluster-map',
  templateUrl: './beginner-cluster-map.component.html',
  styleUrls: ['./beginner-cluster-map.component.scss'],
})
export class BeginnerClusterMapComponent
  implements OnInit, AfterContentInit, AfterViewInit, OnChanges {
  accessions$: any;
  clusters: any = [];
  clustersGrouped$: any;
  analysis$: any = [];
  map: any;
  data: any;
  colorClusters: any = [];
  @Input() showMap = false;
  tested$: any = [];
  listFigures: any[];
  listClusters: any[];
  cropList: any;

  constructor(
    private api: IndicatorService,
    private _sharedService: SharedService,
    public dialog: MatDialog
  ) {
    this.listFigures = [
      'fa-leaf',
      'fa-circle',
      'fa-square',
      'fa-star',
      'fa-certificate',
      'fa-cloud',
      'fa-map-marker',
      'fa-play',
    ];
    this.listClusters = [];
  }

  ngAfterViewInit() {
    // console.log("Hello")
    // this.map = L.map('beginner-map', {
    //   center: [0, 0],
    //   zoom: 3,
    //   zoomControl: false
    // });
    // const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    //   maxZoom: 18,
    //   minZoom: 3,
    //   attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    // });
    // tiles.addTo(this.map);
    // L.control.zoom({
    //   position: 'bottomright'
    // }).addTo(this.map)
    // this.initMap();
  }

  ngOnInit(): void {}

  ngOnChanges() {
    if (this.showMap == true) {
      this.initMap();
    }
  }

  getRandomColor() {
    var letters = '0123456789ABCDEF';
    var color = '#';
    for (var i = 0; i < 6; i++) {
      color += letters[Math.floor(Math.random() * 16)];
    }
    return color;
  }

  mergeCropAndCluster() {
    let colors = [
      'green',
      'blue',
      'yellow',
      'red',
      'brown',
      'gray',
      'brown',
      'black',
      'orange',
      'purple',
    ];
    this.cropList.forEach((crop: any, index: any) => {
      this.listClusters.forEach((cluster: any, indx: any) => {
        let obj = {
          crop: crop,
          cluster: cluster,
          color: colors[index],
          fillColor: this.getRandomColor(),
        };
        this.tested$.push(obj)
      });
    });
  }

  ngAfterContentInit() {
    this._sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessions$ = data;
    });
    this._sharedService.sendMultivariableBeginnerObservable.subscribe(
      (res: any) => {
        this.analysis$ = res.data;
        this.combineData();
      }
    );
    this._sharedService.sendCropsListObservable.subscribe((res: any) => {
      this.cropList = res;
    });
  }

  combineData() {
    const mergeById = (t: any, s: any) =>
      t.map((p: any) =>
        Object.assign(
          {},
          p,
          s.find((q: any) => p.cellid == q.cellid)
        )
      );
    combineLatest([of(this.accessions$), of(this.analysis$)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((res: any) => {
        res.forEach((element: any) => {
          if (element.cluster_hac >= 0) {
            this.listClusters.push(element.cluster_hac);
            // console.log(this.listClusters)
            this.clusters.push(element);
          }
        });
        this.listClusters = [...new Set(this.listClusters)];
        this.mergeCropAndCluster();
        this.clusters = this.clusters.sort(
          (a: any, b: any) => a.cluster - b.cluster
        );

        of(this.clusters)
          .pipe(
            switchMap((data: any) =>
              from(data).pipe(
                groupBy((item: any) => item.cluster_hac),
                mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
                reduce((acc: any, val: any) => acc.concat([val]), [])
              )
            )
          )
          .subscribe((res: any) => {
            this.data = res;
            console.log(this.data);
          });

        // of(this.clusters)
        //   .pipe(
        //     switchMap((data: any) =>
        //       from(data).pipe(
        //         groupBy((item: any) => item.crop),
        //         mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
        //         // reduce((acc: any, val: any) => acc.concat([val]), []),

        //         // map((x:any) => {return x[1]})
        //         mergeMap((array: any) => {
        //           // Take each from above array and group each array by manDate
        //           let newArray: any;
        //           from(array[1])
        //             .pipe(
        //               groupBy((val: any) => val.cluster_hac),
        //               mergeMap((group) => {
        //                 return zip(of(group.key), group.pipe(toArray())); // return the group values as Arrays
        //               }),
        //               reduce((acc: any, val: any) => acc.concat([val]), [])
        //             )
        //             .subscribe((re: any) => {
        //               newArray = re;
        //             });
        //           array[1] = newArray;
        //           // console.log(array)
        //           return [array];
        //         }),
        //         reduce((acc: any, val: any) => acc.concat([val]), [])
        //         // toArray()
        //       )
        //     )
        //   )
        //   .subscribe((res: any) => {
        //     this.tested$ = res;
        //   });
      });
  }

  initMap(): void {
    let colors = [
      'green',
      'blue',
      'yellow',
      'red',
      'brown',
      'gray',
      'brown',
      'black',
      'orange',
      'purple',
    ];

    this.map = L.map('beginner-map', {
      center: [0, 0],
      zoom: 2,
      zoomControl: false,
    });

    const tiles = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 18,
        minZoom: 2,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }
    );

    tiles.addTo(this.map);

    L.control
      .zoom({
        position: 'bottomright',
      })
      .addTo(this.map);

    this.tested$.forEach((element: any) => {
      let filtered:any = this.clusters.filter(
        (prop: any) => prop.crop == element.crop && prop.cluster_hac == element.cluster
      );

      if (filtered.length > 0) {
                this.colorClusters.push({crop:element.crop, cluster: element.cluster, color: element.color, fillColor:element.fillColor})
                filtered.forEach((val: any) => {
            if (val.geo_lon != null && val.geo_lat != null) {
              // const marker = L.marker([val.geo_lat, val.geo_lon], {
              //   icon: MyCustomMarker,
              // }).addTo(this.map);
              const marker = L.circleMarker([val.geo_lat, val.geo_lon], {
                radius: 5,
              });
              marker.addTo(this.map);
              marker.setStyle({ color: element.color, fillColor: element.fillColor });
              marker.bindPopup('Name: ' + val.name + ' Crop: ' + val.crop);
              marker.on('mouseover', function (event) {
                marker.openPopup();
              });
              marker.on('mouseout', function (event) {
                marker.closePopup();
              });
              marker.on('click', () => {
                this.openAccessionDetail(val);
              });
            }
          });
      }
    });

    // Grouped cluster color
    this.clustersGrouped$ = of(this.colorClusters).pipe(
      switchMap((data: any) =>
        from(data).pipe(
          groupBy((item: any) => item.crop),
          mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
          reduce((acc: any, val: any) => acc.concat([val]), [])
        )
      )
    )
    // this.cropList.forEach((element: any, index: any) => {
    //   this.listClusters.forEach((clus: any, indx: any) => {
    //     var MyCustomMarker = L.divIcon({
    //       html:
    //         '<i class="fas ' +
    //         this.listFigures[index] +
    //         ' fa 4x" style="color:' +
    //         colors[indx] +
    //         ';"></i>',
    //       iconSize: [20, 20],
    //       className: 'myDivIcon',
    //     });
    //     let filtered = this.clusters.filter(
    //       (prop: any) => prop.crop == element && prop.cluster_hac == clus
    //     );
    //     if (filtered.length > 0) {
    //       filtered.forEach((val: any) => {
    //         if (val.geo_lon != null && val.geo_lat != null) {
    //           // const marker = L.marker([val.geo_lat, val.geo_lon], {
    //           //   icon: MyCustomMarker,
    //           // }).addTo(this.map);
    //           const marker = L.circleMarker([val.geo_lat, val.geo_lon], {
    //             radius: 5,
    //           });
    //           marker.addTo(this.map);
    //           marker.setStyle({ color: colors[indx] });
    //           marker.bindPopup('Name: ' + val.name + ' Crop: ' + val.crop);
    //           marker.on('mouseover', function (event) {
    //             marker.openPopup();
    //           });
    //           marker.on('mouseout', function (event) {
    //             marker.closePopup();
    //           });
    //           marker.on('click', () => {
    //             this.openAccessionDetail(val);
    //           });
    //         }
    //       });
    //     }
    //   });
    // });

    // this.tested$.forEach((element: any, index: any) => {

    //   element[1].forEach((prop:any, indx:any) => {
    //     var MyCustomMarker = L.divIcon({
    //       html: '<i class="fas ' + this.listFigures[index] +' fa 4x" style="color:'+ colors[indx]+';"></i>',
    //       iconSize: [20, 20],
    //       className: 'myDivIcon'
    //   });
    //     prop[1].forEach((val:any) => {
    //       if (val.geo_lon != null && val.geo_lat != null) {
    //       const marker = L.marker([val.geo_lat, val.geo_lon], { icon: MyCustomMarker }).addTo(
    //         this.map
    //       );
    //       marker.bindPopup('Name: ' + val.name + ' Crop: ' + val.crop);
    //       marker.on('mouseover', function (event) {
    //         marker.openPopup();
    //       });
    //       marker.on('mouseout', function (event) {
    //         marker.closePopup();
    //       });
    //       marker.on('click', () => {
    //         this.openAccessionDetail(val);
    //       });
    //       }
    //     });
    //   });
    // });

    // this.data.forEach((res: any, index: any) => {
    //   // this.colorClusters.push({ cluster: res[0], color: colors[index] });
    //   res[1].forEach((val: any) => {
    //     if (val.geo_lon != null && val.geo_lat != null) {
    //       const marker = L.circleMarker([val.geo_lat, val.geo_lon], {
    //         radius: 5,
    //       });
    //       marker.addTo(this.map);
    //       marker.setStyle({ color: 'black', fillColor: colors[index] });
    //       marker.bindPopup('Name: ' + val.name + ' Crop: ' + val.crop);
    //       marker.on('mouseover', function (event) {
    //         marker.openPopup();
    //       });
    //       marker.on('mouseout', function (event) {
    //         marker.closePopup();
    //       });
    //       marker.on('click', () => {
    //         this.openAccessionDetail(val);
    //       });
    //     }
    //   });
    // });
  }

  onMapReady() {
    setTimeout(() => {
      this.map.invalidateSize();
    }, 0);
  }

  drawMap() {
    let colors = ['green', 'blue', 'yellow', 'red', 'brown', 'gray'];
    // let idMap:any = document.getElementById('map');
    let palmira: any;

    this.map = new Map({
      target: 'map-cluster',
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

    if (this.data)
      this.data.forEach((res: any, index: any) => {
        var coordinates: any = [];
        res[1].forEach((val: any) => {
          if (val.geo_lon != null && val.geo_lat != null) {
            palmira = new Feature({
              geometry: new Point(fromLonLat([val.geo_lon, val.geo_lat])),
              name: val.name,
              crop: val.crop,
              obj: val,
            });
            coordinates.push(palmira);
          }
        });

        // properties
        var iconStyle = new Style({
          image: new CircleStyle({
            radius: 3,
            fill: new Fill({
              color: colors[index],
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

        let vectorSourceT = new VectorSource({
          features: coordinates,
        });

        let vectorLayer = new VectorLayer({
          source: vectorSourceT,
          style: function (feature) {
            labelStyle.getText().setText(feature.get('name'));
            return style;
          },
        });

        this.map.addLayer(vectorLayer);
      });

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
        content.innerHTML = name + ' ' + crop;
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

  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
  }
}
