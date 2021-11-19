import { Component, OnInit, Input, AfterContentInit } from '@angular/core';
import { SharedService } from '../../core/service/shared.service';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../filter/accessions-detail/accessions-detail.component';
import { IndicatorService } from '../../indicator/service/indicator.service';
import { saveAs } from 'file-saver';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { Observable } from 'rxjs';
import { share } from 'rxjs/operators';
import { T } from '@angular/cdk/keycodes';
import { Options } from '@angular-slider/ngx-slider';

@Component({
  selector: 'app-tabs',
  templateUrl: './tabs.component.html',
  styleUrls: ['./tabs.component.scss'],
})
export class TabsComponent implements OnInit, AfterContentInit {
  accessions$: any[];
  expertNormalMode$:boolean = false;
  headers: any = [];
  ActualPage: number = 1;
  params: any;
  subsets: any;
  quantileData!: any;
  // quantileData!: Observable<any>;
  timeMultiAna: any;
  clusterData: any[];
  minMaxMeanData: any[];
  /* Get accessions by page */
  properties!: any[];
  amountData: number;
  /* End get accessions by page */
  hyperParameters: any;
  algorithmsList: string[];
  /* Advance properties */
  dbscanCheck: boolean;
  hdbscanCheck: boolean;
  agglomerativeCheck: boolean;
  showAdvancedMap = false;
  selectdIndex: number = 0;
  @Input() activeTabs: boolean;
  // agglo
  maxCluster: number;
  minCluster: number;
  clusterSliderOption: Options = {
    floor: 0,
    ceil: 100,
    showTicksValues: true,
    tickStep: 1,
    tickValueStep: 30,
  };
  constructor(
    private _sharedService: SharedService,
    public dialog: MatDialog,
    private api: IndicatorService
  ) {
    this.headers = ['Number', 'Crop name', 'Taxon', 'Action'];
    this.amountData = 0;
    this.clusterData = [];
    this.minMaxMeanData = [];
    this.agglomerativeCheck = true;
    this.dbscanCheck = false;
    this.hdbscanCheck = false;
    this.hyperParameters = {
      minpts: 20,
      epsilon: 10,
      min_cluster_size: 10,
      n_clusters: 5,
      min_cluster:2
    };
    this.algorithmsList = [];
    this.accessions$ = []
    this.activeTabs = true;
    this.maxCluster = 5;
    this.minCluster = 2;
  }

  addAlgorithmsToList() {
    if (this.agglomerativeCheck) {
      this.algorithmsList.push('agglomerative');
    }
    if (this.dbscanCheck) {
      this.algorithmsList.push('dbscan');
    }
    if (this.hdbscanCheck) {
      this.algorithmsList.push('hdbscan');
    }
  }
  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
    /* dialogRef.afterClosed().subscribe(
      data => {
        if (data) {
          this.params.longitude = data.longitude;
          this.params.latitude = data.latitude;
          this.longitudeAndLatitudeVisible = false
        }
      }
    ); */
  }

  tabClick(tab:any) {
    if (tab.index === 2) {
      this.showAdvancedMap = true;
      console.log(this.showAdvancedMap)
    }
  }

  sendIndicatorSummary(indSum: any) {
    this._sharedService.sendIndicatorSummary(indSum);
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

  drawTable(subsets: any) {
    this._sharedService.sendSubsets(subsets);
  }

  setDataIndicator(acce: any) {
    this._sharedService.sendAccession(acce);
  }

  setSummary(summ: any) {
    this._sharedService.sendSummary(summ);
  }

  setMultivariableData(mul: any) {
    this._sharedService.sendMultivariable(mul);
  }

  setSubsetAdvanced(subset: any) {
    this._sharedService.sendSubsetAdvanced(subset);
  }

  setSubsets(accession: any) {
    this._sharedService.sendSubsets(accession);
  }

  ngOnInit(): void {
    this._sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessions$ = data;
      this.amountData = this.accessions$.length;
    });

    this._sharedService.sendexpertNormalObservable.subscribe((data) => {
      this.expertNormalMode$ = data;
    });
  }

  ngAfterContentInit() {
    this._sharedService.sendIndicatorsObservable.subscribe((params: any) => {
      this.params = params;
    });
    this._sharedService.getTabSelected().subscribe((tabIndex: number) => {
      this.selectdIndex = tabIndex;
      console.log(tabIndex);
      if (this.expertNormalMode$ === true) {
        this.buildSubsets();
      }/*  */
    });
  }

  selectedIndexChange(val :number ){
    this.selectdIndex=val;
  }

  buildSubsets = () => {
    this.subsets = {};
    // let sharedChannel = this.api.getSubsets(this.params).pipe(share())
    // this.quantileData = this.api.getSubsets(this.params);
    this.api.getSubsets(this.params).subscribe((res: any) => {
      if (this.subsets) {
        this.activeTabs = false;
      }
      this.subsets = res.univariate;
      this.setSubsets(this.subsets)
      this.quantileData = res.quantile;
      // this.sendIndicatorSummary(this.subsets.data)
    });
  };

  /* buildQuantilePlots = () => {
    this.quantileData = [];
    this.api.getQuantile(this.params).subscribe((res: any) => {
      this.quantileData = res;
    });
  }; */

  buildClusters = () => {
    this.clusterData = [];
    this.algorithmsList = [];
    this.addAlgorithmsToList();
    this.params['analysis'] = {
      algorithm: this.algorithmsList,
      hyperparameter: this.hyperParameters,
      summary: false
    };
    this.api.generateCluster(this.params).subscribe((res: any) => {
      this.clusterData = res.data;
      this.timeMultiAna = res.time
      this.minMaxMeanData = res.calculate
    });
  };
}
