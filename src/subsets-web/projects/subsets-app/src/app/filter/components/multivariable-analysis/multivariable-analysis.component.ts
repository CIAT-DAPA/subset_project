import {
  Component,
  OnInit,
  AfterContentInit,
  Input,
  OnChanges,
} from '@angular/core';
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
import { IndicatorService } from '../../../indicator/service/indicator.service';

@Component({
  selector: 'app-multivariable-analysis',
  templateUrl: './multivariable-analysis.component.html',
  styleUrls: ['./multivariable-analysis.component.scss'],
})
export class MultivariableAnalysisComponent
  implements OnInit, AfterContentInit, OnChanges {
  latitude: number = 18.5204;
  longitude: number = 73.8567;
  namesResponse: String[] = [];
  palmira: any;
  cali: any;
  map: any;
  @Input('popup') popup!: any;
  @Input() multivariable: any[] = [];
  @Input() timeMultiAna: any;
  @Input() res$: any;
  vectorSource: any;
  vectorSourceT: any;
  vectorLayer: any;
  rasterLayer: any;
  popupOverlay: any;

  @Input() accessions: any = [];
  // multivariable$: any = [];
  lst: any = [];
  lstGrouped: any = [];
  headersTable_1: any[];
  headersTable_2: any[];
  actualPageDbscan: number = 1;
  actualPageHdbscan: number = 1;
  actualPageAgglomerative: number = 1;
  actualPageT2: number = 1;
  resDbscan$: any;
  resHdbscan$: any;
  resAgglomerative$: any;
  resMap$: any;
  summaryReduced: any;
  indicators$: any = [];
  accessionsCombined:any = [];
  cropList: any = [];
  cropSelected: any;
  data:any = []
  dataSummary:any = []
  methodSelected: any;

  constructor(
    private _sharedService: SharedService,
    public dialog: MatDialog,
    private api: IndicatorService
  ) {
    this.headersTable_1 = ['Crop', 'Name', 'Number', 'Cluster'];
    this.headersTable_2 = [
      'Indicator',
      'Crop',
      'Slope',
      'Mean',
      'Standard desviation',
      'Cluster',
      'Methodology',
    ];
  }

  ngOnChanges() {
    if (this.multivariable.length > 0) {
      this.namesResponse = Object.keys(this.multivariable[0]);
      if (this.namesResponse.includes('cluster_dbscan')) {
        this.getSummaryMethodology('dbscan');
      } else if (this.namesResponse.includes('cluster_hdbscan')) {
        this.getSummaryMethodology('hdbscan');
      } else {
        this.getSummaryMethodology('hac');
      }
      console.log(this.multivariable);
      console.log(this.accessions);
      this.seeVar();
    }
  }

  ngOnInit(): void {
    this.getIndicators();
  }

  setSummary(summ: any) {
    this._sharedService.sendSummary(summ);
  }

  filterData(crop:any, methd:any) {
    let lst:any[] = []
    let filtered:any[] = [];
    this.data = []
    this.dataSummary = []
    switch (methd) {
      case 'Dbscan Analysis':
      filtered = this.multivariable.filter((prop:any) => prop.cluster_dbscan >= 0 && prop.crop_name == crop);
      filtered.forEach((element:any) => {
        let accessionByCellid: any[] = this.accessions.filter((prop:any) => prop.crop == crop && prop.cellid == element.cellid)
        accessionByCellid.forEach(e => e.cluster = element.cluster_dbscan);
        lst.push(accessionByCellid)
      });
      this.data = [].concat.apply([], lst);
      this.setDataAdvancedMaps(this.data);
      this.dataSummary = this.res$.filter((prop:any) => prop.crop == crop && prop.method == 'dbscan');
        break;
      case 'Hdbscan Analysis':
          filtered = this.multivariable.filter((prop:any) => prop.cluster_hdbscan >= 0 && prop.crop_name == crop);
          filtered.forEach((element:any) => {
            let accessionByCellid: any[] = this.accessions.filter((prop:any) => prop.crop == crop && prop.cellid == element.cellid)
            accessionByCellid.forEach(e => e.cluster = element.cluster_hdbscan);
            lst.push(accessionByCellid)
          });
          this.data = [].concat.apply([], lst);
          this.setDataAdvancedMaps(this.data);
          this.dataSummary = this.res$.filter((prop:any) => prop.crop == crop && prop.method == 'hdbscan');
            break;
      case 'Agglomerative Analysis':
          filtered = this.multivariable.filter((prop:any) => prop.cluster_hac >= 0 && prop.crop_name == crop);
          filtered.forEach((element:any) => {
            let accessionByCellid: any[] = this.accessions.filter((prop:any) => prop.crop == crop && prop.cellid == element.cellid)
            accessionByCellid.forEach(e => e.cluster = element.cluster_hac);
            lst.push(accessionByCellid)
          });
          this.data = [].concat.apply([], lst);
          this.data = this.data.sort((a: any, b: any) => a.cluster - b.cluster);
          this.setDataAdvancedMaps(this.data);
          this.dataSummary = this.res$.filter((prop:any) => prop.crop == crop && prop.method == 'hac');
            break;
      default:
        break;
    }
  }

  seeVar() {
    const mergeById = (t: any, s: any) =>
      t.map((p: any) =>
        Object.assign(
          {},
          p,
          s.find((q: any) => p.cellid == q.cellid)
        )
      );
    combineLatest([of(this.accessions), of(this.multivariable)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((res: any) => {
        res.forEach((element:any) => {
          if (element.cluster_hac >= -1 || element.cluster_dbscan >= -1 ||element.cluster_hdbscan >= -1) {
            this.accessionsCombined.push(element)
          }
        });
        console.log(this.accessionsCombined)

        let dbscan = this.accessionsCombined.filter((prop: any) => prop.cluster_dbscan >= 0);
        let hdbscan = this.accessionsCombined.filter((prop: any) => prop.cluster_hdbscan >= 0);
        let agglomerative = this.accessionsCombined.filter(
          (prop: any) => prop.cluster_hac >= 0
        );
        this.resDbscan$ = dbscan.sort(
          (a: any, b: any) => a.cluster_dbscan - b.cluster_dbscan
        );
        console.log(this.resDbscan$);
        this.resHdbscan$ = hdbscan.sort(
          (a: any, b: any) => a.cluster_hdbscan - b.cluster_hdbscan
        );
        this.resAgglomerative$ = agglomerative.sort(
          (a: any, b: any) => a.cluster_hac - b.cluster_hac
        );
    //     console.log(res);
    //     this.setMultivariableData(res);
    //     // this.setSummary(this.res$);
      });
  }
  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data: any) => {
        data.forEach((element:any) => {
          element.indicators.forEach((res:any) => {
            this.indicators$.push(res);
          });
        });
        console.log(this.indicators$);
      },
      (error: any) => console.log(error)
    );
  };

  ngAfterContentInit() {
    this._sharedService.sendCropsListObservable.subscribe((res: any) => {
      this.cropList = res;
      this.cropSelected = this.cropList[0];
    });
  }

  downloadJsonFormat(data: any) {
    const blob = new Blob([JSON.stringify(data)], { type: 'application/json' });
    saveAs(blob, 'clusters.json');
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
    saveAs(blob, 'clusters.csv');
  }

  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
  }

  getSummaryMethodology(methd: string) {
    this.summaryReduced = this.res$.filter((met: any) => met.method == methd);
  }

  getIndicatorName(pref: string) {
    let indicatorFiltered = this.indicators$.filter(
      (prop: any) => prop.pref == pref
    );
    return indicatorFiltered[0].name;
  }

  setMultivariableData(mul: any) {
    this._sharedService.sendMultivariable(mul);
  }

  setDataAdvancedMaps(data: any) {
    this._sharedService.sendDataAdvancedMaps(data);
  }
}
