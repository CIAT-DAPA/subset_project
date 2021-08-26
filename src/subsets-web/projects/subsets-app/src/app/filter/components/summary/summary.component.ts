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
  summary$: any;
  passportParameters$: any;
  indicatorParameters$: any;
  multivariable$: any;
  totalAccessionsDbscan:number = 0;
  totalAccessionsHdbscan:number = 0;
  totalAccessionsAgglomerative:number = 0;
  constructor(
    private _sharedService: SharedService,
    public dialog: MatDialog
  ) {}

  ngAfterContentInit(): void {
    this._sharedService.sendMultivariableObservable.subscribe((res: any) => {
      this.multivariable$ = res;

      this.multivariable$.forEach((element:any) => {
        if (element.cluster_dbscan != -1) {
          this.totalAccessionsDbscan = this.totalAccessionsDbscan + 1;
        }
        if (element.cluster_hdbscan != -1) {
          this.totalAccessionsHdbscan = this.totalAccessionsHdbscan + 1;
        }
        if (element.cluster_aggolmerative != -1) {
          this.totalAccessionsAgglomerative = this.totalAccessionsAgglomerative + 1;
        }
      });
    });
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
