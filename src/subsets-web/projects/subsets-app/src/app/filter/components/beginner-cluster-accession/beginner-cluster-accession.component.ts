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
  clusters: any = [];
  clustersGrouped$: any;
  analysis$: any = [];
  summary$: any = [];
  headers: any[];
  actualpages: any;
  actualpageSummary: number = 1;
  test$: any;
  indicators$: any = [];
  cropList: any = [];
  headerSummary: any[];
  indicatorsAvailables: any[];
  variableToEvaluate:any[];
  @ViewChild('plots') private plots!: ElementRef;
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
    this.variableToEvaluate = ['Mean', 'Max', 'Min'];
    this.summSelected = this.variableToEvaluate[0];
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
          listTest.push(element.cluster_hac);
        });
        // Set the indicators available
        this.summary$.forEach((element: any) => {
          // if (!this.indicatorsAvailables.includes(element.indicator))
          this.indicatorsAvailables.push(element.indicator);
        });
        listTest = [...new Set(listTest)];
        this.indicatorsAvailables = [...new Set(this.indicatorsAvailables)];
        this.headerSummary = listTest.sort((n1: any, n2: any) => n1 - n2);
        this.seeVar();
        if (this.cropSelected) {
          this.drawPlot(this.cropSelected);
          // this.test$ = [];
        }
      }
    );
  }

  getValueFromClusterAndIndicator(
    indicator: string,
    nCluster: number,
    crop:any,
    summ: any
  ) {
    let result: any;
    let filteredlist: any = this.summary$.filter(
      (prop: any) => prop.indicator == indicator && prop.cluster == nCluster && prop.crop == crop
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
        console.log(data);
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
    let data: any[] = [];
    this.headerSummary.forEach((cluster: any) => {
      let accessionsFiltered: any[] = this.clusters.filter(
        (prop: any) => prop.cluster_hac == cluster && prop.crop == crop
      );
      let regularname = cluster + 1
      let obj: any = {
        label: 'Cluster ' + regularname,
        value: accessionsFiltered.length,
      };
      data.push(obj);
    });

    $(this.plots.nativeElement).append('<div id="plote"><svg></svg></div>');
    nv.addGraph(() => {
      var width = 960,
        height = 700;
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
        this.getAccessionlistByCropAndCluster(e.data.label);
      });

      nv.utils.windowResize(chart.update);
      return chart;
    });
  }

  getAccessionlistByCropAndCluster(cluster: any) {
    let splitVar = cluster.split(' ');
    let realName = splitVar[1] -1
    let accessionFiltered = this.clusters.filter(
      (prop: any) =>
        prop.cluster_hac == realName && prop.crop == this.cropSelected
    );
    this.test$ = of(accessionFiltered);
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
    combineLatest([of(this.accessions$), of(this.analysis$)])
      .pipe(map((res: any) => mergeById(res[0], res[1])))
      .subscribe((res: any) => {
        res.forEach((element: any) => {
          if (element.cluster_hac >= 0) {
            this.clusters.push(element);
          }
        });
        this.clusters = this.clusters.sort(
          (a: any, b: any) => a.cluster - b.cluster
        );
        console.log(this.clusters);
        // this.drawPlot();
        // this.clustersGrouped$ = of(this.clusters).pipe(
        //   switchMap((data: any) =>
        //     from(data).pipe(
        //       groupBy((item: any) => item.cluster_hac),
        //       mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
        //       reduce((acc: any, val: any) => acc.concat([val]), [])
        //     )
        //   )
        // )
        // // .subscribe((res:any) => {
        // //   console.log(res);
        // // })
        // this.test$ = of(this.clusters).pipe(
        //   switchMap((data: any) =>
        //     from(data).pipe(
        //       groupBy((item: any) => item.crop),
        //       mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
        //       // reduce((acc: any, val: any) => acc.concat([val]), []),

        //       // map((x:any) => {return x[1]})
        //       mergeMap((array:any) => {// Take each from above array and group each array by manDate
        //         const newArray = from(array[1]).pipe(groupBy(
        //           (val:any) => val.cluster_hac,
        //           ),
        //           mergeMap(group => {
        //             return zip(of(group.key), group.pipe(toArray())); // return the group values as Arrays
        //           }),
        //           reduce((acc: any, val: any) => acc.concat([val]), []),
        //           )
        //           // .subscribe((re:any) => {
        //           //   newArray = re;
        //           // })
        //           array[1] = newArray;
        //           // console.log(array)
        //           return [array]
        //       }),
        //       reduce((acc: any, val: any) => acc.concat([val]), []),
        //       // toArray()
        //     )
        //   )
        // )
        // .subscribe((res:any) => {
        //   console.log(res)
        // })
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
