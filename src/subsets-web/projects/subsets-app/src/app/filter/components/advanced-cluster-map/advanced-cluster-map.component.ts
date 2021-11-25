import { Component, OnInit, AfterContentInit} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { of, zip, from } from 'rxjs';
import { groupBy, mergeMap, reduce, switchMap, toArray } from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import * as L from 'leaflet';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';

@Component({
  selector: 'advanced-cluster-map',
  templateUrl: './advanced-cluster-map.component.html',
  styleUrls: ['./advanced-cluster-map.component.scss']
})
export class AdvancedClusterMapComponent implements OnInit, AfterContentInit {
  data:any;
  dataGrouped:any = [];
  colorClusters: any = [];
  map:any;
  constructor(  private api: IndicatorService,
    private _sharedService: SharedService,
    public dialog: MatDialog) { }

  ngOnInit(): void {
  }

  ngAfterContentInit() {
    this._sharedService.sendDataAdvancedMapObservable.subscribe((res: any) => {
      this.data = res
      console.log(res);
      this.groupDataByCluster();
      if (this.dataGrouped.length > 0 ) {
        setTimeout(() => {
        this.clearDiv();
        this.initMap();
      }, 3000)
      }
    });
  }

  groupDataByCluster() {
    of(this.data)
    .pipe(
      switchMap((data: any) =>
        from(data).pipe(
          groupBy((item: any) => item.cluster),
          mergeMap((group:any) => zip(of(group.key), group.pipe(toArray()))),
          reduce((acc: any, val: any) => acc.concat([val]), [])
        )
      )
    )
    .subscribe((res: any) => {
      console.log(res);
      this.dataGrouped = res;
      this.dataGrouped = this.dataGrouped.sort((a:any, b:any) => a[0] -b[0])
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

    this.map = L.map('advanced-map', {
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
    this.colorClusters = []
    this.dataGrouped.forEach((element: any, index:any) => {

      if (element[1].length > 0) {
        this.colorClusters.push({
          // crop: element.crop,
          cluster: element[0],
          color: colors[index],
          // fillColor: element.fillColor,
        });
        element[1].forEach((val: any) => {
          if (val.geo_lon != null && val.geo_lat != null) {
            // const marker = L.marker([val.geo_lat, val.geo_lon], {
            //   icon: MyCustomMarker,
            // }).addTo(this.map);
            const marker = L.circleMarker([val.geo_lat, val.geo_lon], {
              radius: 5,
            });
            marker.addTo(this.map);
            marker.setStyle({
              color: colors[index]
            });
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

  }

  clearDiv() {
    if (this.map ){
      this.map.eachLayer(function(layer:any){
          layer.remove();
      });
      this.map.remove();
      this.map = null;
  }
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
