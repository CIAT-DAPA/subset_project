import { Component, OnInit, AfterContentInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';
import * as L from 'leaflet';
import { SharedService } from '../../../core/service/shared.service';

@Component({
  selector: 'candidate-subset',
  templateUrl: './candidate-subset.component.html',
  styleUrls: ['./candidate-subset.component.scss']
})
export class CandidateSubsetComponent implements OnInit, AfterContentInit {
  data:any = [];
  headers:any = ['Number', 'Crop name', 'Taxon', 'Action'];
  actualpage:number = 1
  map:any
  constructor(public dialog: MatDialog, private _sharedService: SharedService) {

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

   ngAfterContentInit() {
    this._sharedService.sendCandidateObservable.subscribe(
      (res:any) => {
        this.data = res
        this.clearDiv();
      setTimeout(() => {
        this.initMap();
  
      }, 4000)
      }
    );
   }

  ngOnInit(): void {
  }

  downloadJsonFormat(data: any) {
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    saveAs(blob, 'accessions.json');
  }

  downloadCsvFormat(data: any) {
    const replacer = (key: any, value: any) => (value === null ? '' : value); // specify how you want to handle null values here
    const header = Object.keys(data[0]);
    let csv = data.map((row: any) =>
      header
        .map((fieldName) => JSON.stringify(row[fieldName], replacer))
        .join(',')
    );
    csv.unshift(header.join(','));
    let csvArray = csv.join('\r\n');

    var blob = new Blob([csvArray], { type: 'text/csv' });
    saveAs(blob, 'accessions.csv');
  }

  
  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
  }

  private initMap(): void {
    this.map = L.map('map_candidate', {
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


    this.data.forEach((val: any, index: any) => {
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


}
