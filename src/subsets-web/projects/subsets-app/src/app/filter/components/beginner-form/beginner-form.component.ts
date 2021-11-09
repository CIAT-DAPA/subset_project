import { Component, Input, OnInit, OnChanges } from '@angular/core';
import { SharedService } from '../../../core/service/shared.service';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { distinctUntilChanged } from 'rxjs/operators';
import { Options } from '@angular-slider/ngx-slider';
import { T } from '@angular/cdk/keycodes';

@Component({
  selector: 'beginner-form',
  templateUrl: './beginner-form.component.html',
  styleUrls: ['./beginner-form.component.scss'],
})
export class BeginnerFormComponent implements OnInit, OnChanges {
  // Observable with the indicators format
  @Input() indicators$: any;
  listCropWithIndicators: any[];
  listCropAvailable: any[] =[];
  @Input() cropList: any = [];
  @Input() formActive: boolean = false;
  // Observable with the indicators period format
  @Input() indicatorPeriods$: any;
  // Var to check all complete
  allComplete: boolean = false;
  // Passport params
  @Input() passportParms: any;
  // Max numbers of clusters
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
    private api: IndicatorService
  ) {
    this.maxCluster = 5;
    this.minCluster = 2;
    this.listCropWithIndicators = [
      'Beans',
      'Cassava',
      'Banana',
      'Wheat',
      'Maize',
      'Potato',
      'Sweet potato',
      'Rice',
      'Barley',
      'Sorghum',
      'Pearl millet',
      'Cowpea',
      'Yam',
      'Soybean',
    ];
  }

  ngOnInit(): void {}

  ngOnChanges() {
    if (this.formActive === false) {
      this.cropList.forEach((element:any) => {
        if (this.listCropWithIndicators.includes(element)) {
          this.listCropAvailable.push(element)
        } 
      });
      this.indicators$.forEach((element: any) => {
        element.checked = false;
        element.indicators.forEach((prop: any) => {
          prop.checked = false;
        });
      });
    }
  }

  setTabIndex(indx: number) {
    this._sharedService.setTabSelected(indx);
  }

  setMultivariableDataBeginner(mb: any) {
    this._sharedService.sendMultivariableBeginner(mb);
  }

  setIndicatorsList(indicator: any) {
    this._sharedService.sendIndicatorList(indicator);
  }

  // Method to update the checked list
  updateAllComplete(obj: any, field: boolean) {
    obj.checked = obj.indicators != null && obj.indicators.every((t: any) => t.checked);
    console.log(obj)
  }

  // Method to check if the users selected some indicators
  someComplete(obj: any): boolean {
    if (obj.indicators == null) {
      return false;
    }
    return (
      obj.indicators.filter((t: any) => t.checked).length > 0 && !obj.checked
    );
  }

  // Set all indicators by category
  setAll(completed: boolean, category:any,  obj: any) {
    obj.checked = completed;
    if (category === 'Crop-specific indicators') {
      obj.indicators.forEach((t: any) => {
      if (this.listCropAvailable.includes(t.crop)) {
        t.checked = completed
      }
    });
    } else {
      obj.indicators.forEach((t:any) => t.checked = completed);
    }
    console.log(obj)
  }

  filterIndicatorPeriodById(indicator: string): string {
    let indicatorPeriodSelected: string = '';
    let summaryPeriod: string = 'mean';
    let indicatorPeriodFiltered = this.indicatorPeriods$.filter(
      (res: any) => res.indicator == indicator && res.period == summaryPeriod
    );
    indicatorPeriodSelected = indicatorPeriodFiltered[0].id;
    return indicatorPeriodSelected;
  }

  buildSubsets() {
    let indicatorsChecked: any = [];
    let selectedIndicatorList: any[] = [];
    let request: any = {};
    let currentTime = new Date();
    let year = currentTime.getFullYear();
    this.indicators$.forEach((element: any) => {
      element.indicators.forEach((prop: any) => {
        if (prop.checked === true) {
          selectedIndicatorList.push(prop);
          let indicator = this.filterIndicatorPeriodById(prop.id);
          let obj = {
            indicator: [indicator],
            name: prop.name,
            crop: prop.crop,
            type: prop.indicator_type,
            period: [year, year],
          };
          indicatorsChecked.push(obj);
        }
      });
    });
    this.setIndicatorsList(selectedIndicatorList);
    request = {
      methd: 'normal',
      data: indicatorsChecked,
      passport: this.passportParms,
      analysis: {
        algorithm: ['agglomerative'],
        hyperparameter: {
          n_clusters: this.maxCluster,
          min_cluster: this.minCluster,
        },
        summary: true,
      },
    };
    console.log(request);
    this.api.generateCluster(request).subscribe((res: any) => {
      console.log(res);
      this.setMultivariableDataBeginner(res);
      this.setTabIndex(1);
    });
  }
}
