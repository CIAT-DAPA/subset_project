import { Component, OnInit, AfterViewInit } from '@angular/core';
import * as L from 'leaflet';
import * as awesome from 'leaflet.awesome-markers';

// import {} from '../../../../assets'

const iconRetinaUrl = '../../../../assets/marker-icon-2x.png';
const iconUrl = 'assets/marker-icon.png';
const shadowUrl = 'assets/marker-shadow.png';
const iconDefault = L.icon({
  iconRetinaUrl,
  iconUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41],
});
L.Marker.prototype.options.icon = iconDefault;

@Component({
  selector: 'alliance-cgiar-org-map-test',
  templateUrl: './map-test.component.html',
  styleUrls: ['./map-test.component.scss'],
})
export class MapTestComponent implements OnInit, AfterViewInit {
  private map: any;

  constructor() {}

  private initMap(): void {
    this.map = L.map('map', {
      center: [39.8282, -98.5795],
      zoom: 3,
    });

    const tiles = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 18,
        minZoom: 3,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }
    );

    tiles.addTo(this.map);

    // let lon = -76.3
    // let lat = 3.517
    // const marker = L.circleMarker([lat, lon],{ radius: 5 });
    // marker.addTo(this.map);
    // marker.setStyle({color: 'green'});
    // Creates a red marker with the coffee icon
    var MyCustomMarker = L.divIcon({
      html: '<i class="fas fa-leaf fa 4x" style="color:red;"></i>',
      iconSize: [20, 20],
      className: 'myDivIcon'
  });

    L.marker([3.517, -76.3], { icon: MyCustomMarker }).addTo(
      this.map
    );
  }

  ngAfterViewInit() {
    this.initMap();
  }

  ngOnInit(): void {}
}
