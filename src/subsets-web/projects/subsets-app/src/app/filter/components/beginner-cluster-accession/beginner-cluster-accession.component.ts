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
  headers:any[];
  actualpages:any;
  constructor(
    private api: IndicatorService,
    private _sharedService: SharedService,
    public dialog: MatDialog
  ) {
    this.headers = ['Number', 'Crop name', 'Taxon', 'Action'];
    this.actualpages = [1,1,1,1,1,1,1,1,1,1]
  }

  ngAfterContentInit() {
    this._sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessions$ = data;
      console.log(data);
    });
    this._sharedService.sendMultivariableBeginnerObservable.subscribe((res:any) => {
      this.analysis$ = res.data;
      // this.analysis$.forEach((element:any) => {
      //   element['cluster'] = element["('cluster_aggolmerative', '')"]
      //   delete element["('cluster_aggolmerative', '')"]
      // });
      this.seeVar();
    }) 
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
          if (element.cluster_aggolmerative >= 0) {
            this.clusters.push(element)
          }
        });
        this.clusters = this.clusters.sort(
          (a: any, b: any) => a.cluster - b.cluster
        );
        this.clustersGrouped$ = of(this.clusters).pipe(
          switchMap((data: any) =>
            from(data).pipe(
              groupBy((item: any) => item.cluster_aggolmerative),
              mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
              reduce((acc: any, val: any) => acc.concat([val]), [])
            )
          )
        )
        // .subscribe((res:any) => {
        //   console.log(res);
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


  ngOnInit(): void {

  }
}
