import { Component, OnInit, AfterContentInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { combineLatest, of, from, zip } from 'rxjs';
import { groupBy, map, mergeMap, reduce, switchMap, toArray } from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { AccessionsDetailComponent } from '../../accessions-detail/accessions-detail.component';

@Component({
  selector: 'beginner-cluster-accession',
  templateUrl: './beginner-cluster-accession.component.html',
  styleUrls: ['./beginner-cluster-accession.component.scss'],
})
export class BeginnerClusterAccessionComponent implements OnInit, AfterContentInit {
  accessions$:any
  clusters:any = [];
  clustersGrouped$:any;
  analysis$:any = [];
  summary$:any = [];
  headers:any[];
  actualpages:any;
  actualpageSummary:number = 1;
  test$:any;
  indicators$:any = [];
  headerSummary:any[];
  constructor(
    private api: IndicatorService,
    private _sharedService: SharedService,
    public dialog: MatDialog
  ) {
    this.headers = ['Number', 'Crop name', 'Taxon', 'Action'];
    this.actualpages = [1,1,1,1,1,1,1,1,1,1]
    this.headerSummary = [
      'Indicator',
      'Mean',
      'Min',
      'Max',
      'Cluster',
    ];
  }

  ngAfterContentInit() {
    this._sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessions$ = data;
      console.log(data);
    });
    this._sharedService.sendMultivariableBeginnerObservable.subscribe((res:any) => {
      this.analysis$ = res.data;
      this.summary$ = res.summary
      // this.analysis$.forEach((element:any) => {
      //   element['cluster'] = element["('cluster_hac', '')"]
      //   delete element["('cluster_hac', '')"]
      // });
      this.seeVar();
    }) 
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data: any) => {
        data.forEach((element:any) => {
          element.indicators.forEach((res:any) => {
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
        res.forEach((element:any) => {
          if (element.cluster_hac >= 0) {
            this.clusters.push(element)
          }
        });
        this.clusters = this.clusters.sort(
          (a: any, b: any) => a.cluster - b.cluster
        );
        this.clustersGrouped$ = of(this.clusters).pipe(
          switchMap((data: any) =>
            from(data).pipe(
              groupBy((item: any) => item.cluster_hac),
              mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
              reduce((acc: any, val: any) => acc.concat([val]), [])
            )
          )
        )
        // .subscribe((res:any) => {
        //   console.log(res);
        // })
        this.test$ = of(this.clusters).pipe(
          switchMap((data: any) =>
            from(data).pipe(
              groupBy((item: any) => item.crop),
              mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
              // reduce((acc: any, val: any) => acc.concat([val]), []),

              // map((x:any) => {return x[1]})
              mergeMap((array:any) => {// Take each from above array and group each array by manDate
                const newArray = from(array[1]).pipe(groupBy(
                  (val:any) => val.cluster_hac,
                  ),
                  mergeMap(group => {
                    return zip(of(group.key), group.pipe(toArray())); // return the group values as Arrays
                  }),
                  reduce((acc: any, val: any) => acc.concat([val]), []),
                  )
                  // .subscribe((re:any) => {
                  //   newArray = re;
                  // })
                  array[1] = newArray;
                  // console.log(array)
                  return [array]
              }),
              reduce((acc: any, val: any) => acc.concat([val]), []),
              // toArray()
            )
          )
        )
        // .subscribe((res:any) => {
        //   console.log(res)
        // })
      });
  }

  openAccessionDetail(object:any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object
      },
      width: '60%'
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
