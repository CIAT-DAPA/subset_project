import {
  Component,
  OnInit,
  Input,
  OnChanges,
  ViewChild,
  ElementRef,
  AfterContentInit,
} from '@angular/core';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { Options } from '@angular-slider/ngx-slider';
import { from, Observable, of, zip } from 'rxjs';
import { SharedService } from '../../../core/service/shared.service';
import {
  groupBy,
  map,
  mergeMap,
  reduce,
  startWith,
  switchMap,
  toArray,
} from 'rxjs/operators';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { HttpClient } from '@angular/common/http';

//chips
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';
import { AddPointMapComponent } from '../add-point-map/add-point-map.component';
import { FormControl } from '@angular/forms';
import {
  MatAutocomplete,
  MatAutocompleteSelectedEvent,
} from '@angular/material/autocomplete';
import { NotificationService } from '../../../core/service/notification.service';
import { SpinnerService } from '../../../core/service/spinner.service';
import { ActivatedRoute, Router } from '@angular/router';

export interface DialogData {
  animal: 'panda' | 'unicorn' | 'lion';
}

@Component({
  selector: 'alliance-cgiar-org-form-filter',
  templateUrl: './form-filter.component.html',
  styleUrls: ['./form-filter.component.scss'],
})
export class FormFilterComponent implements OnInit, AfterContentInit {
  /* New get structure */
  properties!: any[];
  amountData: number = 0;
  /* End  New get structure */

  isRunning: boolean = false;
  summary$: any;
  /* Chips Autocomplete var */
  //chips-autocomplete crops start
  visible: boolean = true;
  selectable: boolean = true;
  removable: boolean = true;
  addOnBlur: boolean = false;
  separatorKeysCodes = [ENTER, COMMA];
  CropsCtrl = new FormControl();
  filteredCrops: Observable<any[]>;
  crops: Array<string> = [];
  allCrops: any = [];
  allCropsArray: any = [];
  @ViewChild('fruitInput') fruitInput!: ElementRef<HTMLInputElement>;
  @ViewChild('auto') matAutocomplete!: MatAutocomplete;
  /* Chips Autocomplete finish */
  /* Chips Autocomplete var */
  /* chips-autocomplete countries start */
  countriesCtrl = new FormControl();
  filteredCountries: Observable<any[]>;
  countries: Array<string> = [];
  allCountries: Array<string> = [];
  @ViewChild('countryInput') countryInput!: ElementRef<HTMLInputElement>;
  @ViewChild('countryAuto') matAutocompleteContry!: MatAutocomplete;
  /* Chips Autocomplete finish */

  longitudeAndLatitudeVisible: boolean = true;
  setTabsVisible: boolean = false;

  params: any = {};
  passportParams: any = {};
  cropParams: any = {};
  subsets$ = [];
  accessions$ = [];
  countries$: any = [];
  crops$: any = [];
  accessionsFiltered$: any = [];
  indicators: any = [];
  accessionsIndicator$: any = [];

  allComplete: boolean = false;

  //end checkbox month

  mcpd: any[] = [];

  minValue: number = 0;
  maxValue: number = 10;
  options: Options = {
    floor: 0,
    ceil: 300,
    showTicksValues: true,
    tickStep: 0.5,
    tickValueStep: 30,
  };

  constructor(
    private api: IndicatorService,
    private sharedService: SharedService,
    public dialog: MatDialog,
    private httpClient: HttpClient,
    private notifyService: NotificationService,
    private _spinnerService: SpinnerService,
    private route: ActivatedRoute,
    private router: Router
  ) {
    this.filteredCrops = this.CropsCtrl.valueChanges.pipe(
      startWith(null),
      map((fruit: string | null) =>
        fruit ? this._filter(fruit, this.allCrops) : this.allCrops.slice()
      )
    );

    /* Autocomplete countries */
    this.filteredCountries = this.countriesCtrl.valueChanges.pipe(
      startWith(null),
      map((country: string | null) =>
        country
          ? this._filter(country, this.allCountries)
          : this.allCountries.slice()
      )
    );

    this.passportParams = {
      name: [],
      crop: [],
      country_name: [],
      samp_stat: [],
      institute_fullname: [],
      institute_acronym: [],
      longitude: [],
      latitude: [],
      taxonomy_taxon_name: [],
    };

    this.cropParams = {
      names: [],
    };
  }

  openDialog() {
    const dialogRef = this.dialog.open(AddPointMapComponent, {
      data: {
        animal: 'panda',
      },
    });
    dialogRef.afterClosed().subscribe((data) => {
      if (data) {
        this.params.longitude = data.longitude;
        this.params.latitude = data.latitude;
        this.longitudeAndLatitudeVisible = false;
      }
    });
  }

  sendIndicatorPar(pars: any) {
    this.sharedService.sendIndicatorsPar(pars);
  }

  ngAfterContentInit() {}

  ngOnInit(): void {
    this.mcpd = [
      { id: 100, name: 'wild' },
      { id: 110, name: 'natural' },
      { id: 120, name: 'semi-natural/wild' },
      { id: 130, name: 'semi-natural/sown' },
      { id: 200, name: 'weedy' },
      { id: 300, name: 'landrace' },
      { id: 400, name: 'breeding' },
    ];

    if (this.router.url.includes('filter;passport')) {
      let paramsPassp: any = this.route.snapshot.paramMap.get('passport');
      let paramsInd: any = this.route.snapshot.paramMap.get('indicator');
      let jsonParamsPas = JSON.parse(paramsPassp);
      if (paramsInd) {
        let jsonParamsInd = JSON.parse(paramsInd);
        this.getAccessionsAutomatically(jsonParamsPas, jsonParamsInd);
      }
    }

    this.getCountries();
    this.getCrops();
    // Send accessions to indicators form
    this.sharedService.sendSubsetObservable.subscribe((data) => {
      this.accessions$ = data;
    });
    this.sharedService.sendAccessionsObservable.subscribe((data) => {
      this.accessionsIndicator$ = data;
    });
  }

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets);
  }

  setDataIndicator(acce: any) {
    this.sharedService.sendAccession(acce);
  }

  setSummary(summ: any) {
    this.sharedService.sendSummary(summ);
  }

  sendPassportParameters(params: any) {
    this.sharedService.sendPassport(params);
  }

  getCrops = () => {
    this.api.getCrops().subscribe(
      (data) => {
        this.crops$ = data;
        this.crops$.forEach((prop: any) => {
          this.allCrops.push(prop.name);
          this.allCropsArray.push(prop);
        });
      },
      (error) => console.log(error)
    );
  };

  getCountries() {
    this.httpClient.get('assets/dbs/countries.json').subscribe((data) => {
      this.countries$ = data;
      this.countries$.forEach((element: any) => {
        this.allCountries.push(element.name);
      });
    });
  }

  getAccessions = () => {
    this.passportParams.crop = this.filterCropsById(this.crops);
    this.passportParams.country_name = this.countries;
    this.sendPassportParameters(this.passportParams);
    this.api.getAccessions(this.passportParams).subscribe(
      (data) => {
        if (data.length === 0) {
          this.notifyService.showWarning(
            "The system didn't find data with the entered parameters",
            'Warning'
          );
        } else {
          this.accessions$ = data;
          this.drawTable(data);
          this.setDataIndicator(data);
          this.setSummary(this.accessions$);
        }
      },
      (error) => console.log(error)
    );
  };

  getAccessionsAutomatically = (prop: any, ind: any) => {
    this.api.getAccessions(prop).subscribe(
      (data) => {
        if (data.length === 0) {
          this.notifyService.showWarning(
            "The system didn't find data with the entered parameters",
            'Warning'
          );
        } else {
          this.accessions$ = data;
          this.drawTable(data);
          this.setDataIndicator(data);
          this.setSummary(this.accessions$);
          this.sendIndicatorPar(ind);
        }
      },
      (error) => console.log(error)
    );
  };

  filterAccessionsByIndicator() {
    this.subsets$.forEach((value: any) => {
      let accesionsfind = this.accessions$.filter(
        (acces: any) => acces.cellid == value.cellid
      );
      for (let vat of accesionsfind) {
        this.accessionsFiltered$.push(vat);
      }
    });
    this.accessions$ = this.accessionsFiltered$;
    this.drawTable(this.accessions$);
  }

  filterCropsById(crops: String[]): String[] {
    let cropSelected: String[] = [];
    crops.forEach((value: any) => {
      let cropsFind = this.allCropsArray.filter(
        (prop: any) => prop.name == value
      );
      cropsFind.forEach((element: any) => {
        if (!cropSelected.includes(element.id)) cropSelected.push(element.id);
      });
    });
    return cropSelected;
  }

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

  remove(fruit: string, addedList: any): void {
    const index = addedList.indexOf(fruit);

    if (index >= 0) {
      addedList.splice(index, 1);
    }
  }

  selectedCrop(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.fruitInput.nativeElement.value = '';
    ctrl.setValue(null);
  }

  selectedCountry(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.countryInput.nativeElement.value = '';
    ctrl.setValue(null);
  }

  private _filter(value: string, allitems: any): string[] {
    const filterValue = value.toLowerCase();
    return allitems.filter(
      (item: any) => item.toLowerCase().indexOf(filterValue) === 0
    );
  }
}
