import {
  Component,
  OnInit,
  ElementRef,
  ViewChild,
  AfterViewInit,
  Input,
  AfterContentInit,
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
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { CustomDataComponent } from '../custom-data/custom-data.component';

/* Start Datepicker */
import {
  NgxMatMomentAdapter,
  NgxMatMomentDateAdapterOptions,
  NGX_MAT_MOMENT_DATE_ADAPTER_OPTIONS,
} from '@angular-material-components/moment-adapter';
import {
  DateAdapter,
  MAT_DATE_FORMATS,
  MAT_DATE_LOCALE,
} from '@angular/material/core';
import { MatDatepicker } from '@angular/material/datepicker';

import * as _moment from 'moment';
import { defaultFormat as _rollupMoment, Moment } from 'moment';
import { listLazyRoutes } from '@angular/compiler/src/aot/lazy_routes';

@Component({
  selector: 'app-form-indicator',
  templateUrl: './form-indicator.component.html',
  styleUrls: ['./form-indicator.component.scss'],
})
export class FormIndicatorComponent implements OnInit, AfterContentInit {
  buttonName: any = 'Show properties advanced';
  advanceproperties: boolean = true;
  params$: any;
  minPts!: number;
  epsilon!: number;
  monthFirt: number;
  monthEnd: number;
  months$!: any[];
  request$: any;
  multiv$: any = [];
  //chips-autocomplete start
  visible: boolean = true;
  selectable: boolean = true;
  removable: boolean = true;
  addOnBlur: boolean = false;
  listValues: any;
  separatorKeysCodes = [ENTER, COMMA];
  fruitCtrl = new FormControl();
  filteredFruits: Observable<any[]>;
  fruits: Array<string> = [
    /* 'Extreme daily precipitation', */
  ];
  allFruits: Array<string> = [
    /*     'Extreme daily precipitation',
        'Consecutive dry days',
        'Total precipitation', */
  ];
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
  /* Test month slider */
  valueM: number = 1;
  highvalueM: number = 1;
  optionsM: Options = {
    floor: 1,
    ceil: 12,
    translate: (value: number, label: LabelType): string => {
      switch (label) {
        case LabelType.Low:
          return '<b>Month initial:</b> ' + value;
        case LabelType.High:
          return '<b>Month final:</b> ' + value;
        default:
          return '' + value;
      }
    },
  };
  /* End month slider */

  minValue: number = 0;
  maxValue: number = 10;
  options: Options = {
    floor: 0,
    ceil: 300,
    showTicksValues: true,
    tickStep: 0.5,
    tickValueStep: 30,
  };

  periods: any = [];
  periodMinValue: number = 1983;
  periodMaxValue: number = 1983;
  periodOptions: Options = {
    floor: 1983,
    ceil: 2017,
    showTicksValues: true,
    tickStep: 1,
    tickValueStep: 30,
  };
  allComplete: boolean = false;
  finalRequest: any = [];
  cellids$: any = [];

  constructor(
    private api: IndicatorService,
    private sharedService: SharedService,
    public dialog: MatDialog
  ) {
    this.monthFirt = 1;
    this.monthEnd = 12;
    this.listValues = [];
    this.filteredFruits = this.fruitCtrl.valueChanges.pipe(
      startWith(null),
      map((fruit: string | null) =>
        fruit ? this._filter(fruit) : this.allFruits.slice()
      )
    );

    this.parameters = {
      month: '',
      value: '',
      indicator: '',
      period: '',
    };
  }

  showAdvanceProperties() {
    if (this.buttonName == 'Show properties advanced') {
      this.advanceproperties = false;
      this.buttonName = 'Hidden properties advanced';
      this.epsilon = 20;
      this.minPts = 10;
    } else {
      this.advanceproperties = true;
      this.buttonName = 'Show properties advanced';
      this.epsilon = 20;
      this.minPts = 10;
    }
  }

  openDialog() {
    let ind: String = this.filterIndicatorsById('Consecutive dry days');
    console.log(this.filterIndicatorPeriodById(ind));
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

  ngAfterContentInit() {}

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
    this.sharedService.sendIndicatorsParObservable.subscribe((data) => {
      this.params$ = data;
      this.getSubsetsOfAccessionAutomatically(this.params$);
    });
    this.sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
    });
    this.getIndicators();
    this.getIndicatorPeriods();
  }

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets);
  }

  setDataIndicator(acce: any) {
    this.sharedService.sendAccession(acce);
  }

  setMultivariableData(mul: any) {
    this.sharedService.sendMultivariable(mul);
  }

  seIndicatorValue(indVal: any) {
    this.sharedService.sendIndicatorValue(indVal);
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data) => {
        this.indicators$ = data;
        this.indicators$.forEach((element: any) => {
          this.allFruits.push(element.name);
          this.allIndicatorsArray.push(element);
        });
      },
      (error) => console.log(error)
    );
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

  setSummary(summ: any) {
    this.sharedService.sendSummary(summ);
  }

  sendIndicatorsParameters(params: any) {
    this.sharedService.sendIndicators(params);
  }

  getSubsetsOfAccession = () => {
    this.periods = [this.periodMinValue, this.periodMaxValue];
    let indicators: String[] = this.fruits;
    let obj: any = {};
    indicators.forEach((props: any, index: any) => {
      obj = {
        indicator: this.filterIndicatorPeriodById(
          this.filterIndicatorsById(props)
        ),
      };
      for (let i = this.monthFirt; i <= this.monthEnd; i++) {
        obj['month' + i] = [
          this.listValues[index].minValue,
          this.listValues[index].highValue,
        ];
      }
      obj['period'] = this.periods;
      this.finalRequest.push(obj);
    });
    this.request$ = {
      data: this.finalRequest,
      passport: this.passportParms,
      analysis: { algorithm: ["dbscan", "hdbscan","agglomerative"] },
    };
    this.sendIndicatorsParameters(this.request$);
    this.api.getSubsetsOfAccessionTest(this.request$).subscribe(
      (data) => {
        this.seIndicatorValue(data.data);
        this.setMultivariableData(data.multivariety_analysis);
        // this.filterMultivariableData();
        obj = {};
        this.request$ = {};
      },
      (error) => {
        console.log(error);
      }
    );
  };

  getSubsetsOfAccessionAutomatically = (prop: any) => {
    this.sendIndicatorsParameters(prop);
    this.api.getSubsetsOfAccessionTest(prop).subscribe(
      (data) => {
        console.log(data);

        /* this.subsets$ = data.data[0]*/
        this.cellids$ = data.data.cellids;
        this.seIndicatorValue(data.data.data);
        this.filterAccessionsByIndicator();
        this.setMultivariableData(data.data.multivariety);
        /* this.seIndicatorValue(data.data[1])
        this.subsets$ = data.data[0] */
      },
      (error) => {
        console.log(error);
      }
    );
  };

  filterAccessionsByIndicator() {
    this.cellids$.forEach((prop: any) => {
      let accesionsfind = this.accessions$.filter(
        (acces: any) => acces.cellid == prop
      );
      for (let vat of accesionsfind) {
        this.accessionsFiltered$.push(vat);
      }
    });
    this.accessions$ = this.accessionsFiltered$;
    this.setSummary(this.accessions$);
    this.drawTable(this.accessions$);
  }

  filterIndicatorsById(indicators: String): String {
    console.log(this.indicators$);
    let indicatorSelected: String = '';
    let indicatorsFind = this.indicators$.filter(
      (prop: any) => prop.name == indicators
    );
    indicatorsFind.forEach((element: any) => {
      if (!indicatorSelected.includes(element.id))
        indicatorSelected = element.id;
    });

    return indicatorSelected;
  }

  filterIndicatorPeriodById(indicators: String): String[] {
    let indicatorPeriodSelected: String[] = [];
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

  add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;

    // Add our fruit
    if ((value || '').trim()) {
      this.fruits.push(value.trim());
    }

    // Reset the input value
    if (input) {
      input.value = '';
    }

    this.fruitCtrl.setValue(null);

    /*     this.fruits.forEach((vars:any) => {
          this.listValues.push({value:0, highValue:1})
        })
        console.log(this.listValues); */
  }

  remove(fruit: string): void {
    const index = this.fruits.indexOf(fruit);

    if (index >= 0) {
      this.fruits.splice(index, 1);
      this.listValues.splice(index, 1);
    }
    console.log(this.fruits);
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    this.fruits.push(event.option.viewValue);
    this.fruitInput.nativeElement.value = '';
    this.fruitCtrl.setValue(null);
    this.listValues.push({ minValue: 0, highValue: 1 });
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();
    return this.allFruits.filter(
      (fruit) => fruit.toLowerCase().indexOf(filterValue) === 0
    );
  }
}
