import { Component, Input, OnInit, AfterContentInit } from '@angular/core';
import { Router } from '@angular/router';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';

@Component({
  selector: 'switch-toggle',
  templateUrl: './switch-toggle.component.html',
  styleUrls: ['./switch-toggle.component.scss']
})
export class SwitchToggleComponent implements OnInit, AfterContentInit {
  isChecked = false;
   // Observable with the indicators format
   indicators$: any;
   indicatorsa$: any;
   // Observable with the indicators period format
   indicatorPeriods$: any = [];
   // Var to check all complete
   @Input() passportParms: any;
   rangesValues$:any;
   @Input() cropList:any = []
   @Input() accessions:any = [];
  constructor(
    private _sharedService: SharedService,
    private api: IndicatorService,
    private router: Router
  ) {
    this.getIndicatorsList();
    this.getIndicatorPeriods();
   }

   setExpertNormalMode(en:any) {
     this._sharedService.sendExpertNormal(en)
   }

   setTabIndex(indx: number) {
    this._sharedService.setTabSelected(indx);
  }

    // Method to get the indicators list for each category
    getIndicatorsList = () => {
      this.api.getIndicators().subscribe((res:any) => {
        this.indicators$ = res;
        this.indicatorsa$ = res;
      });
    };
      /* Get indicator periods objects */
      getIndicatorPeriods = () => {
        this.api.getIndicatorPeriod().subscribe(
          (data) => {
            this.indicatorPeriods$ = data;
          },
          (error) => console.log(error)
        );
      };
  ngOnInit(): void {
  }

  ngAfterContentInit() {
    this._sharedService.sendRangeValuesObservable.subscribe((res:any) => {
      this.rangesValues$ = res;
    })

    // this._sharedService.sendCropsListObservable.subscribe((res: any) => {
    //   this.cropList = res;
    //   console.log(this.cropList);
    // });
  }

}
