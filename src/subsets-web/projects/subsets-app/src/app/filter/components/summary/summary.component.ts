import { Component, Input, OnInit, AfterContentInit } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { from, of, zip } from 'rxjs';
import { groupBy, mergeMap, reduce, switchMap, toArray } from 'rxjs/operators';
import { SharedService } from '../../../core/service/shared.service';
import { FormSubsetComponent } from '../form-subset/form-subset.component';

@Component({
  selector: 'app-summary',
  templateUrl: './summary.component.html',
  styleUrls: ['./summary.component.scss'],
})
export class SummaryComponent implements OnInit, AfterContentInit {
  username: any;
  summary$: any;
  accessions$: any;
  passportParameters$: any;
  indicatorParameters$: any;
  time$: any;
  @Input() namesResponse: any[];
  multivariable$: any;
  indicatorValue$: any;
  totalAccessionsDbscan: number = 0;
  totalAccessionsHdbscan: number = 0;
  totalAccessionsAgglomerative: number = 0;
  totalClustersAgglomerative: number = 0;
  totalClustersDbscan: number = 0;
  totalClustersHdbscan: number = 0;
  constructor(private _sharedService: SharedService, public dialog: MatDialog) {
    this.namesResponse = [];
    this.username = localStorage.getItem('username');
  }

  getAMountAccessionsByIndicator(crop: string): number {
    if (this.indicatorValue$) {
      let accessions: any = this.indicatorValue$.filter(
        (x: any) => x.crop == crop
      );
      /*     let lstCellids: number[] = []
      accessions.forEach((res:any) => {
        lstCellids.push(res.cellid)
      })
      let lst: number[] = [...new Set(lstCellids)];
      let lstAccessionFiltered: number[] = [];
      lst.forEach((cellid:any) => {
        let accessionsFiltered = this.accessions$.filter((prop:any) => prop.cellid == cellid);
        lstAccessionFiltered.push(...accessionsFiltered);
      }) */

      return accessions.length;
    } else {
      return 0;
    }
  }

  ngAfterContentInit(): void {
    this._sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
      // console.log(data)
    });
    this._sharedService.sendIndicatorsSummaryObservable.subscribe(
      (res: any) => {
        this.indicatorValue$ = res;
      }
    );

    this._sharedService.sendTimeObservable.subscribe((res: any) => {
      this.time$ = res;
      console.log(this.time$);
    });

    this._sharedService.sendMultivariableObservable.subscribe((res: any) => {
      console.log(res);
      this.multivariable$ = res;
    });
  }

  getNumberOfAccessions(crop: string, methd: string): number {
    let count: number = 0;
    let objs = this.multivariable$.filter((res: any) => res.crop_name == crop);
    if (methd == 'aggolmerative') {
      objs.forEach((element: any) => {
        if (element.cluster_aggolmerative >= 0) {
          count++;
        }
      });
    }
    if (methd == 'dbscan') {
      objs.forEach((element: any) => {
        if (element.cluster_dbscan >= 0) {
          count++;
        }
      });
    }
    if (methd == 'hdbscan') {
      objs.forEach((element: any) => {
        if (element.cluster_hdbscan >= 0) {
          count++;
        }
      });
    }
    return count;
  }

  getNumberOfClusters(crop: string, methd: string): number {
    let lstResult: any[] = [];
    let objs = this.multivariable$.filter((res: any) => res.crop_name == crop);
    objs.forEach((element: any) => {
      if (methd == 'aggolmerative') {
        if (element.cluster_aggolmerative >= 0)
          lstResult.push(element.cluster_aggolmerative);
      }
      if (methd == 'hdbscan') {
        if (element.cluster_hdbscan >= 0)
          lstResult.push(element.cluster_hdbscan);
      }
      if (methd == 'dbscan') {
        if (element.cluster_dbscan >= 0) lstResult.push(element.cluster_dbscan);
      }
    });
    let uniqueResult: any[] = [...new Set(lstResult)];

    return uniqueResult.length;
  }

  ngOnInit(): void {
    this._sharedService.sendIndicatorsObservable.subscribe((res: any) => {
      this.indicatorParameters$ = res;
      console.log(res);
    });
    this._sharedService.sendPassportObservable.subscribe((res: any) => {
      this.passportParameters$ = res;
      console.log(res);
    });

    this.summary$ = this._sharedService.sendSummaryObservable.pipe(
      switchMap((data: any) =>
        from(data).pipe(
          groupBy((item: any) => item.crop),
          mergeMap((group) => zip(of(group.key), group.pipe(toArray()))),
          reduce((acc: any, val: any) => acc.concat([val]), [])
        )
      )
    );
  }

  openDialog() {
    const dialogRef = this.dialog.open(FormSubsetComponent, {
      data: {
        passportParams: this.passportParameters$,
        indicatorParams: this.indicatorParameters$,
      },
    });
  }
}
