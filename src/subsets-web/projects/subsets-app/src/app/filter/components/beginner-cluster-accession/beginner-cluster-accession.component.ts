import {
  Component,
  OnInit,
  AfterContentInit,
  ElementRef,
  Renderer2,
  ViewChild,
} from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
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
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';
import * as d3 from 'd3';
declare var $: any;

@Component({
  selector: 'beginner-cluster-accession',
  templateUrl: './beginner-cluster-accession.component.html',
  styleUrls: ['./beginner-cluster-accession.component.scss'],
})
export class BeginnerClusterAccessionComponent
  implements OnInit, AfterContentInit {
  accessions$: any;
  cropSelected: any;
  summSelected: any;
  clusters: any[];
  clusterSelected: any;
  clustersGrouped$: any;
  analysis$: any = [];
  summary$: any = [];
  headers: any[];
  actualpages: any;
  actualpageSummary: number = 1;
  test$: any[] = [];
  indicators$: any = [];
  cropList: any = [];
  headerSummary: any[];
  indicatorsAvailables: any[];
  variableToEvaluate: any[];
  selectedIndicatorList$: any;
  variablesWithInterpretation: any;
  interpretation: any[] = [];
  @ViewChild('plots_pie') private plots!: ElementRef;
  @ViewChild('summary_table') private summaryTable!: ElementRef;
  constructor(
    private api: IndicatorService,
    private _sharedService: SharedService,
    public dialog: MatDialog,
    public chartElem: ElementRef,
    private renderer: Renderer2
  ) {
    this.headers = ['Number', 'Crop name', 'Taxon', 'Action'];
    this.actualpages = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1];
    this.headerSummary = ['Indicator', 'Mean', 'Min', 'Max', 'Cluster'];
    this.indicatorsAvailables = [];
    this.variableToEvaluate = ['Mean', 'Maximum', 'Minimum'];
    this.summSelected = this.variableToEvaluate[0];
    this.clusters = [];
    this.variablesWithInterpretation = [
      't_rain',
      'ndws',
      'TN',
      'TX',
    ];
  }

  ngAfterContentInit() {
    // Get crop list
    this._sharedService.sendCropsListObservable.subscribe((res: any) => {
      this.cropList = res;
      this.cropSelected = this.cropList[0];
    });
    // Get the accessions data
    this._sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessions$ = data;
    });
    // Get the list of indicators selected
    this._sharedService.sendIndicatorsListObservable.subscribe((res: any) => {
      this.selectedIndicatorList$ = res;
    });

    // Get the clustering analysis from beginner form
    this._sharedService.sendMultivariableBeginnerObservable.subscribe(
      (res: any) => {
        // set clustering analysis data
        this.analysis$ = res.data;
        // Set summary data (Min, Max and Mean)
        this.summary$ = res.summary;
        // Set the clusters available
        let listTest: any = [];
        this.analysis$.forEach((element: any) => {
          if (element.cluster_hac != null) {
            listTest.push(element.cluster_hac);
          }
        });
        // Set the indicators available
        this.summary$.forEach((element: any) => {
          // if (!this.indicatorsAvailables.includes(element.indicator))

          this.indicatorsAvailables.push(element.indicator);
        });
        listTest = [...new Set(listTest)];
        this.indicatorsAvailables = [...new Set(this.indicatorsAvailables)];
        this.headerSummary = listTest.sort((n1: any, n2: any) => n1 - n2);
        this.mergeAccessionsAndCluster();
        if (this.cropSelected) {
          this.drawPlot(this.cropSelected);
          this.setInterpretation(this.cropSelected);
          // this.test$ = [];
        }
      }
    );
  }

  setInterpretation(crop: any) {
    this.interpretation = [];
    this.indicatorsAvailables.forEach((res: any) => {
      if (this.variablesWithInterpretation.includes(res)) {
        let objFiltered = this.summary$.filter(
          (prop: any) => prop.indicator == res && prop.crop == crop
        );
      
        if (res == 'ndws') {
          let maxCluster = objFiltered.reduce((max: any, obj: any) =>
          max.mean > obj.mean ? max : obj
        );
        let NewNameCluster = parseInt(maxCluster.cluster) + 1
          let ob = {
            message:
              'Drought Potential subset ' +NewNameCluster+' is the most exposed to drought, as it has '+ maxCluster.mean.toFixed(2) +' days of drought stress on average per month'
          };
          this.interpretation.push(ob);
        }
        // if (res == 't_rain') {
        //   let ob = {
        //     message:
        //       'Potential subset ' +
        //       NewNameCluster +
        //       ' is the most exposed to drought, as it has XX drought stress days on average per month, and XX mm/month of rain. This potential subset is also the second warmest (or the second coolest), with an average monthly maximum (or minimum) temperature of XX ºC.',
        //   };
        //   this.interpretation.push(ob);
        // }
        if (res == 'TX') {
          let maxCluster = objFiltered.reduce((max: any, obj: any) =>
          max.mean > obj.mean ? max : obj
        );
        let NewNameCluster = maxCluster.cluster + 1
          let ob = {
            message:
            'Heat stress Potential subset '+ NewNameCluster +' is the most exposed to heat stress, with an average monthly maximum temperature of '+maxCluster.mean.toFixed(2)+' ºC.',
          };
          this.interpretation.push(ob);
        }
        if (res == 'TN') {
          let maxCluster = objFiltered.reduce((max: any, obj: any) =>
          max.mean < obj.mean ? max : obj
        );
        let NewNameCluster = maxCluster.cluster + 1
          let ob = {
            message:
              'Cool temperatures Potential subset ' +
              NewNameCluster +
              ' is the "coldest" subset, with an average monthly minimum temperature of ' + maxCluster.mean.toFixed(2) + 'ºC.',
          };
          this.interpretation.push(ob);
        }
      }
    });
    console.log(this.interpretation)
  }

  setTabIndex(indx: number) {
    this._sharedService.setTabSelected(indx);
  }

  sendCandidate(cand:any) {
    this._sharedService.sendCandidate(cand);
    this.setTabIndex(2)
  }

  getIndicatorNameAndUnitByPref(pref: any) {
    let indcatorListFilter = this.selectedIndicatorList$.filter(
      (prop: any) => prop.pref == pref
    );
    let res =
      indcatorListFilter[0].name + ' (' + indcatorListFilter[0].unit + ')';
    return res;
  }

  getClusterListByCrop() {
    let filterByCrop = this.summary$.filter(
      (prop: any) => prop.crop == this.cropSelected
    );
    let listCluster: any[] = [];
    filterByCrop.forEach((element: any) => {
      listCluster.push(parseInt(element.cluster));
    });
    listCluster = [...new Set(listCluster)];
    return listCluster;
  }

  getAccessionByClusterAndCrop(cluster: any, crop: any): number {
    let filterAccessions: any[] = this.clusters.filter(
      (prop: any) => prop.cluster_hac == cluster && prop.crop == crop
    );
    return filterAccessions.length;
  }

  getCellIdsByClusterAndCrop(cluster: any, crop: any): number {
    let filterCell: any[] = this.analysis$.filter(
      (prop: any) => prop.cluster_hac == cluster && prop.crop_name == crop
    );
    return filterCell.length;
  }

  getValueFromClusterAndIndicator(
    indicator: string,
    nCluster: number,
    crop: any,
    summ: any
  ) {
    let result: any;
    let filteredlist: any = this.summary$.filter(
      (prop: any) =>
        prop.indicator == indicator &&
        prop.cluster == nCluster &&
        prop.crop == crop
    );
    switch (summ) {
      case 'Mean':
        result = filteredlist[0].mean;
        break;
      case 'Maximum':
        result = filteredlist[0].max;
        break;
      case 'Minimum':
        result = filteredlist[0].min;
        break;
      default:
        result = filteredlist[0].mean;
        break;
    }
    return result;
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data: any) => {
        data.forEach((element: any) => {
          element.indicators.forEach((res: any) => {
            this.indicators$.push(res);
          });
        });
      },
      (error: any) => console.log(error)
    );
  };

  getIndicatorName(pref: string) {
    let indicatorFiltered = this.indicators$.filter(
      (prop: any) => prop.pref == pref
    );
    return indicatorFiltered[0].name;
  }

  clearDiv() {
    let valueYouWantToPut = '';
    this.renderer.setProperty(
      this.plots.nativeElement,
      'innerHTML',
      valueYouWantToPut
    );
  }

  drawPlot(crop: any) {
    this.clearDiv();
    this.plot(crop);
    window.addEventListener('resize', () => this.plot(crop));
  }

  plot(crop: any) {
    let colors = [
      'green',
      'blue',
      'yellow',
      'red',
      'brown',
      'gray',
      'brown',
      'Silver',
      'orange',
      'purple',
      'salmon',
      'DarkKhaki',
      'violet',
      'magenta',
      'MediumSlateBlue',
      'GreenYellow',
      'LimeGreen',
      'Teal',
      'Aqua',
      'SandyBrown',
    ];
    let data: any[] = [];
    let clust: any[] = this.getClusterListByCrop();
    clust.forEach((cluster: any) => {
      let accessionsFiltered: any[] = this.clusters.filter(
        (prop: any) => prop.cluster_hac == cluster && prop.crop == crop
      );
      let regularname = cluster + 1;
      let obj: any = {
        label: 'Set ' + regularname,
        value: accessionsFiltered.length,
        color: colors[cluster],
      };
      data.push(obj);
    });

    $(this.plots.nativeElement).append('<div id="plote"><svg></svg></div>');
    nv.addGraph(() => {
      var width = 1000,
        height = 800;
      var chart = nv.models
        .pieChart()
        .x(function (d) {
          return d.label;
        })
        .y(function (d) {
          return d.value;
        })
        .showLabels(true);
      d3.select(this.chartElem.nativeElement)
        .select('#plote svg')
        .attr('width', width)
        .attr('height', height)
        .datum(data)
        .transition()
        .duration(350)
        .call(chart);

      chart.pie.dispatch.on('elementClick', (e) => {
        // alert("You've clicked " + e.data.label);
        let splitVar = e.data.label.split(' ');
        let realName = splitVar[1] - 1;
        this.getAccessionlistByCropAndCluster(realName);
      });

      nv.utils.windowResize(chart.update);
      return chart;
    });
  }

  getAccessionlistByCropAndCluster(cluster: any) {
    // let splitVar = cluster.split(' ');
    // let realName = splitVar[1] -1
    console.log(cluster);
    let accessionFiltered = this.clusters.filter(
      (prop: any) =>
        prop.cluster_hac == cluster && prop.crop == this.cropSelected
    );
    // this.test$ = of(accessionFiltered);
    this.test$ = accessionFiltered;
    const container = document.getElementById('table-accessions');
    if (container) container.scrollIntoView();
  }

  sendIndicatorSummary(indSum: any) {
    this._sharedService.sendIndicatorSummary(indSum);
  }

  mergeAccessionsAndCluster() {
    let ls: any[] = [];
    this.analysis$.forEach((element: any) => {
      if (element.cellid > 0) {
        let filtered: any[] = this.accessions$.filter(
          (prop: any) =>
            prop.cellid === element.cellid && prop.crop === element.crop_name
        );
        filtered.forEach((e) => (e.cluster_hac = element.cluster_hac));
        ls.push(filtered);
        this.clusters = [].concat.apply([], ls);
      }
    });
    this.sendIndicatorSummary(this.clusters);
  }

  openAccessionDetail(object: any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object,
      },
      width: '60%',
    });
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

  ngOnInit(): void {
    this.getIndicators();
  }
}
