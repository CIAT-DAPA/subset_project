import {
  Component,
  OnInit,
  ElementRef,
  ViewChild,
  AfterViewInit,
  Input,
  AfterContentInit,
  OnChanges,
} from '@angular/core';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { ThemePalette } from '@angular/material/core';
import { SharedService } from '../../../core/service/shared.service';
import { LabelType, Options } from '@angular-slider/ngx-slider';

import { C, COMMA, ENTER } from '@angular/cdk/keycodes';
import { FormControl } from '@angular/forms';
import {
  MatAutocompleteSelectedEvent,
  MatAutocomplete,
} from '@angular/material/autocomplete';
import { MatChipInputEvent } from '@angular/material/chips';
import { Observable, Subject } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { CustomDataComponent } from '../custom-data/custom-data.component';

import { defaultFormat as _rollupMoment, Moment } from 'moment';

import { NotificationService } from '../../../core/service/notification.service';

@Component({
  selector: 'app-form-indicator',
  templateUrl: './form-indicator.component.html',
  styleUrls: ['./form-indicator.component.scss'],
})
export class FormIndicatorComponent implements OnInit, AfterContentInit {
  rangesValues$:any;
  buttonName: any = 'Show properties advanced';
  advanceproperties: boolean = true;
  params$: any;
  monthFirt: number;
  monthEnd: number;
  months$!: any[];
  request$: any;
  multiv$: any = [];
  minAndMax: any;
  /* Advance properties */
  dbscanCheck: boolean;
  hdbscanCheck: boolean;
  agglomerativeCheck: boolean;

  //chips-autocomplete start
  visible: boolean = true;
  selectable: boolean = true;
  removable: boolean = true;
  addOnBlur: boolean = false;
  listValues: any;
  separatorKeysCodes = [ENTER, COMMA];
  fruitCtrl = new FormControl();
  filteredFruits: Observable<any[]>;
  fruits: Array<string> = [];
  allFruits: Array<string> = [];
  allIndicatorsArray: any = [];
  @ViewChild('fruitInput') fruitInput!: ElementRef<HTMLInputElement>;
  @ViewChild('auto') matAutocomplete!: MatAutocomplete;
  @Input() passportParms: any;
  @Input() cropParms: any;
  //chips-autocomplete finish
  subsets$: any = [];
  values: any[] = [];
  accessionsFiltered$: any = [];
  accessions$: any = [];
  indicatorPeriods$: any = [];
  indicators$: any = [];
  parameters: any = {};
  cropList: string[];
  indicatorsPerCrop: any[];
  // filteredPerCrop: Observable<any[]>;
  perCrops: Array<string> = [];
  perCropCtrl = new FormControl();
  @ViewChild('perCropInput') perCropInput!: ElementRef<HTMLInputElement>;
  @ViewChild('perCropauto') perCropmatAutocomplete!: MatAutocomplete;
  cropsAvailable: any[];
  perCropValues: any[];

  minValue: number = 0;
  maxValue: number = 10;
  options: Options = {
    floor: 0,
    ceil: 300,
    showTicksValues: true,
    tickStep: 0.5,
    tickValueStep: 50,
    translate: (value: number, label: LabelType): string => {
      switch (label) {
        case LabelType.Low:
          return '<b>Min:</b> ' + value;
        case LabelType.High:
          return '<b>Max:</b> ' + value;
        default:
          return value.toString();
      }
    },
  };

  periods: any = [];
  periodMinValue: number = 1983;
  periodMaxValue: number = 1983;
  periodOptions: Options = {
    floor: 1983,
    ceil: 2016,
    showTicksValues: true,
    tickStep: 1,
    tickValueStep: 30,
  };
  allComplete: boolean = false;
  finalRequest: any = [];
  cellids$: any = [];
  hyperParameters: any;
  algorithmsList: string[];

  constructor(
    private api: IndicatorService,
    private sharedService: SharedService,
    public dialog: MatDialog,
    private notifyService: NotificationService
  ) {
    this.agglomerativeCheck = true;
    this.dbscanCheck = false;
    this.hdbscanCheck = false;
    this.monthFirt = 1;
    this.monthEnd = 12;
    this.listValues = [];
    this.cropList = [];
    this.indicatorsPerCrop = [];
    this.cropsAvailable = [];
    this.perCropValues = [];

    this.filteredFruits = this.fruitCtrl.valueChanges.pipe(
      startWith(null),
      map((fruit: string | null) =>
        fruit ? this._filter(fruit, this.allFruits) : this.allFruits
      )
    );

    this.parameters = {
      month: '',
      value: '',
      indicator: '',
      period: '',
    };

    this.hyperParameters = {
      minpts: 20,
      epsilon: 10,
      min_cluster_size: 10,
      n_clusters: 5,
    };
    this.algorithmsList = [];
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

  showAdvanceProperties() {
    if (this.buttonName == 'Show properties advanced') {
      this.advanceproperties = false;
      this.buttonName = 'Hidden properties advanced';
      // this.epsilon = 20;
      // this.minPts = 10;
    } else {
      this.advanceproperties = true;
      this.buttonName = 'Show properties advanced';
      // this.epsilon = 20;
      // this.minPts = 10;
    }
  }

  openDialog() {
    const dialogRef = this.dialog.open(CustomDataComponent, {
      data: {
        animal: 'panda',
      },
    });
    /*     dialogRef.afterClosed().subscribe(
          data => {
            this.params.longitude = data.longitude;
            this.params.latitude = data.latitude;
            this.longitudeAndLatitudeVisible = false
          }
        ); */
  }

  ngAfterContentInit() {
    this.sharedService.sendCropsListObservable.subscribe((res: any) => {
      this.cropList = res;
    });
    this.sharedService.sendRangeValuesObservable.subscribe((res:any) => {
      this.rangesValues$ = res;
    })
    this.sharedService.sendIndicatorsListObservable.subscribe(
      (ind: string[]) => {
        this.fruits = ind;
      }
    );
  }

  getDate() {
    let indicator = ['p95'];
    let monthi: number = 9;
    let monthf: number = 3;
    let yeari: number = 2000;
    let yearf: number = 2001;
    let obj: any = {};
    let list: any = [];
    let periods = [1983, 1985];
    if (monthi > monthf) {
      for (let y = periods[0]; y <= periods[1]; y++) {
        const element = y;
        for (let j = 0; j < indicator.length; j++) {
          obj = { period: element, indicator_period: indicator[j] };

          for (let index = monthi; index <= 12; index++) {
            obj['month_' + index] = 1;
          }
          list.push(obj);
        }
        for (let j = 0; j < indicator.length; j++) {
          obj = { period: element + 1, indicator_period: indicator[j] };
          for (let i = 1; i <= monthf; i++) {
            obj['month_' + i] = 2;
          }
          list.push(obj);
        }
      }
      console.log(list);
    }
  }

  ngOnInit(): void {
    /* this.sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
    }); */
    this.getIndicators();
    this.getIndicatorPeriods();
  }

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets);
  }

  /*  setDataIndicator(acce: any) {
    this.sharedService.sendAccession(acce);
  } */

  sendIndicatorSummary(indSum: any) {
    this.sharedService.sendIndicatorSummary(indSum);
  }

  sendTime(tim: any) {
    this.sharedService.sendTimes(tim);
  }

  setMultivariableData(mul: any) {
    this.sharedService.sendMultivariable(mul);
  }

  setIndicatorsList(indicator: any) {
    this.sharedService.sendIndicatorList(indicator);
  }

  seIndicatorValue(indVal: any) {
    this.sharedService.sendIndicatorValue(indVal);
  }

  setTabIndex(indx: number) {
    this.sharedService.setTabSelected(indx);
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data) => {
        this.indicators$ = data;
        this.indicators$.forEach((element: any) => {
          if (element.indicator_type == 'generic') {
            this.allIndicatorsArray.push(element);
            this.allFruits.push(element.name);
          } else if (element.indicator_type == 'specific') {
            this.cropsAvailable = element.crop;
            this.indicatorsPerCrop.push(element.name);
          }
        });
      },
      (error) => console.log(error)
    );
  };

  getIndicatorType(indicator: string): string {
    let indicatorType = this.indicators$.filter(
      (prop: any) => prop.name == indicator
    );
    return indicatorType[0].indicator_type;
  }

  /* Get Indicators by crop (indicators specific) */
  getIndicatorsAllByCrop(crop: string) {
    let indicatorsFiltered: any = this.indicators$.filter(
      (prop: any) => prop.crop == crop
    );
    let lstIndicatorsByCrop: any = [];
    let indicatorsByCropObservable$: Observable<any[]>;
    indicatorsFiltered.forEach((element: any) => {
      lstIndicatorsByCrop.push(element.name);
    });
    indicatorsByCropObservable$ = this.perCropCtrl.valueChanges.pipe(
      startWith(null),
      map((crop: string | null) =>
        crop ? this._filter(crop, lstIndicatorsByCrop) : lstIndicatorsByCrop
      )
    );

    return indicatorsByCropObservable$;
  }

  getIndicatorsByCrop(crop: string): any[] {
    let indicatorsFiltered: any = this.indicators$.filter(
      (prop: any) => prop.crop == crop
    );
    return indicatorsFiltered;
  }

  /* Get indicator periods objects */
  getIndicatorPeriods = () => {
    this.api.getIndicatorPeriod().subscribe(
      (data) => {
        this.indicatorPeriods$ = data;
      },
      (error) => console.log(error)
    );
  };

  setSummary(summ: any) {
    this.sharedService.sendSummary(summ);
  }

  sendIndicatorsParameters(params: any) {
    this.sharedService.sendIndicators(params);
  }

  getSubsetsOfAccession = () => {
    let obj: any = {};
    this.request$ = {};
    this.finalRequest = [];
    this.setIndicatorsList(this.fruits);
    this.periods = [this.periodMinValue, this.periodMaxValue];
    // let indicators: String[] = this.fruits;
    this.listValues.forEach((props: any, index: any) => {
      obj = {
        name: props.indicator,
        indicator: this.filterIndicatorPeriodById(
          this.filterIndicatorsById(props.indicator, props.crop, props.type), 'subsets'
        ),
      };
      for (let i = this.monthFirt; i <= this.monthEnd; i++) {
        obj['month' + i] = [props.minValue, props.highValue];
      }
      obj['type'] = props.type;
      obj['crop'] = props.crop;
      obj['period'] = this.periods;
      this.finalRequest.push(obj);
    });
    this.request$ = {
      data: this.finalRequest,
      passport: this.passportParms,
    };
    console.log(this.request$);
    this.sendIndicatorsParameters(this.request$);
    this.setTabIndex(1);
  };

  filterIndicatorsById(indicators: String, crop: string, typ: string): String {
    let indicatorSelected: String = '';
    let indicatorsFind: any = [];
    if (typ === 'generic' || typ === 'extracted') {
      indicatorsFind = this.indicators$.filter(
        (prop: any) => prop.name == indicators
      );
      indicatorSelected = indicatorsFind[0].id;
    } else if (typ === 'specific') {
      indicatorsFind = this.indicators$.filter(
        (prop: any) => prop.name == indicators && prop.crop == crop
      );
      indicatorSelected = indicatorsFind[0].id;
    }
    return indicatorSelected;
  }

  filterIndicatorPeriodById(indicators: String, filterBy:any): String[] {
    let indicatorPeriodSelected: String[] = [];

    if (filterBy === 'subsets') {

      for (
        let index = this.periodMinValue;
        index <= this.periodMaxValue;
        index++
      ) {
        let indicatorsFind = this.indicatorPeriods$.filter(
          (prop: any) =>
            prop.indicator == indicators && prop.period == index.toString()
        );
        indicatorsFind.forEach((element: any) => {
          if (!indicatorPeriodSelected.includes(element.id))
            indicatorPeriodSelected.push(element.id);
        });
    }
    } else {
      console.log('ranges')
      let lstMinMax = ['min', 'max']
      lstMinMax.forEach((element:any) => {
      let indicatorsFind = this.indicatorPeriods$.filter(
          (prop: any) =>
            prop.indicator == indicators && prop.period == element
        );
        indicatorsFind.forEach((element: any) => {
          if (!indicatorPeriodSelected.includes(element.id))
            indicatorPeriodSelected.push(element.id);
        });  
      })
    }

    return indicatorPeriodSelected;
  }

  filterMultivariableData() {
    let multivFiltered: any = [];
    this.accessionsFiltered$.forEach((prop: any) => {
      let accesionsfind = this.multiv$.filter(
        (acces: any) => acces.cellid == prop.cellid
      );
      for (let vat of accesionsfind) {
        multivFiltered.push(vat);
      }
    });
    this.setMultivariableData(multivFiltered);
  }

  //chips autocomplete-methods

  add(event: MatChipInputEvent, addList: any, ctrl: any): void {
    const input = event.input;
    const value = event.value;

    // Add our item
    if ((value || '').trim()) {
      addList.push(value.trim());
    }
    // Reset the input value
    if (input) {
      input.value = '';
    }
    ctrl.setValue(null);
  }

  remove(fruit: string, addedList: any, valueList: any[]): void {
    const index = addedList.indexOf(fruit);

    if (index >= 0) {
      addedList.splice(index, 1);
      valueList.splice(index, 1);
    }
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    this.fruits.push(event.option.viewValue);
    this.fruitInput.nativeElement.value = '';
    this.fruitCtrl.setValue(null);
    let typ = this.getIndicatorType(event.option.viewValue)
    let minMax = this.rangesValues$.filter((prop:any) => prop.indicator == event.option.viewValue)

        this.listValues.push({
          minValue: minMax[0].min,
          highValue: minMax[0].max,
          type: typ,
          indicator: event.option.viewValue,
          floor: minMax[0].min,
          ceil: minMax[0].max,
        });
        this.fruitInput.nativeElement.blur();

  
  }

  selectedPerCrop(event: MatAutocompleteSelectedEvent, crop: string): void {
    this.fruits.push(event.option.viewValue);
    this.perCropInput.nativeElement.value = '';
    this.perCropCtrl.setValue(null);
    this.listValues.push({
      minValue: 0,
      highValue: 1,
      type: this.getIndicatorType(event.option.viewValue),
      crop: crop,
      indicator: event.option.viewValue,
    });
    this.fruitInput.nativeElement.blur();
  }

  private _filter(value: string, allitems: any): string[] {
    const filterValue = value.toLowerCase();
    return allitems.filter((item: any) =>
      item.toLowerCase().includes(filterValue)
    );
  }
}
