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
import { saveAs } from 'file-saver';

//chips
import { COMMA, ENTER, T } from '@angular/cdk/keycodes';
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
  filteredCrops: Observable<string[]>;
  crops: Array<string> = [];
  allCrops: any = [];
  allCropsArray: any = [];
  @ViewChild('fruitInput') fruitInput!: ElementRef<HTMLInputElement>;
  @ViewChild('chipList') chipList!: ElementRef<HTMLInputElement>;
  @ViewChild('auto') auto!: MatAutocomplete;
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

  /* Taxon autocomplete start */
  taxonCtrl = new FormControl();
  filteredTaxon: Observable<any[]>;
  taxon: Array<string> = [];
  allTaxon: Array<string> = [];
  @ViewChild('taxonInput') taxonInput!: ElementRef<HTMLInputElement>;
  @ViewChild('taxonAuto') matAutocompleteTaxon!: MatAutocomplete;
  /* Taxon autocomplete end */
  /* Taxon autocomplete start */
  instituteCtrl = new FormControl();
  filteredInstitute: Observable<any[]>;
  institutes: Array<string> = [];
  allInstitutes: Array<string> = [];
  @ViewChild('instituteInput') instituteInput!: ElementRef<HTMLInputElement>;
  @ViewChild('instituteAuto') matAutocompleteInstitute!: MatAutocomplete;
  /* Taxon autocomplete end */

  /* biological status autocomplete start */
  biostatusCtrl = new FormControl();
  filteredBioStatus: Observable<any[]>;
  biologicalStatus: Array<string> = [];
  allBiologicalStatus: Array<string> = [
    'wild',
    'natural',
    'semi-natural/wild',
    'semi-natural/sown',
    'weedy',
    'landrace',
    'breeding',
  ];
  @ViewChild('bioStatusInput') bioStatusInput!: ElementRef<HTMLInputElement>;
  @ViewChild('bioStatusAuto') matAutocompleteBioStatus!: MatAutocomplete;
  /* biological status autocomplete end */

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
        fruit ? this._filter(fruit, this.allCrops) : this.allCrops
      )
    );

    /* Autocomplete countries */
    this.filteredCountries = this.countriesCtrl.valueChanges.pipe(
      startWith(null),
      map((country: string | null) =>
        country ? this._filter(country, this.allCountries) : this.allCountries
      )
    );

    /* Autocomplete taxon */
    this.filteredTaxon = this.taxonCtrl.valueChanges.pipe(
      startWith(null),
      map((country: string | null) =>
        country ? this._filter(country, this.allTaxon) : this.allTaxon
      )
    );
    /* Autocomplete institute */
    this.filteredInstitute = this.instituteCtrl.valueChanges.pipe(
      startWith(null),
      map((inst: string | null) =>
        inst ? this._filter(inst, this.allInstitutes) : this.allInstitutes
      )
    );

    /* Autocomplete biological status */
    this.filteredBioStatus = this.biostatusCtrl.valueChanges.pipe(
      startWith(null),
      map((inst: string | null) =>
        inst
          ? this._filter(inst, this.allBiologicalStatus)
          : this.allBiologicalStatus
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
    console.log(pars);
    this.sharedService.sendIndicatorsPar(pars);
  }

  setTabIndex(indx: number) {
    this.sharedService.setTabSelected(indx);
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
      let jsonParamsInd = JSON.parse(paramsInd);
        this.getAccessionsAutomatically(jsonParamsPas, jsonParamsInd);
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

  sendIndicatorSummary(indSum: any) {
    this.sharedService.sendIndicatorSummary(indSum);
  }

  setMultivariableData(mul: any) {
    this.sharedService.sendMultivariable(mul);
  }

  seIndicatorValue(indVal: any) {
    this.sharedService.sendIndicatorValue(indVal);
  }

  setAccession(accession: any) {
    this.sharedService.sendAccession(accession);
  }

  setCropList(crop: any) {
    this.sharedService.sendCropList(crop);
  }

  setIndicatorsList(indicator: any) {
    this.sharedService.sendIndicatorList(indicator);
  }

  setDataIndicator(acce: any) {
    this.sharedService.sendAccession(acce);
  }

  setRangeValues(rv:any) {
    this.sharedService.sendRangeValues(rv);
  }

  setSummary(summ: any) {
    this.sharedService.sendSummary(summ);
  }


  sendPassportParameters(params: any) {
    this.sharedService.sendPassport(params);
  }

  getAmountOfAccessions(crop:string) {
    let cropFiltered = this.crops$.filter((prop:any) => prop.name == crop)

    return cropFiltered[0].count_accessions
  }

  getCrops = () => {
    this.api.getCrops().subscribe(
      (data) => {
        this.crops$ = data.crops;
        this.allTaxon = data.taxs;
        this.allInstitutes = data.institute;
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
    this.passportParams.crop = this.filterCrops(this.crops, 'name');
    this.setCropList(this.crops);
    this.passportParams.country_name = this.countries;
    this.passportParams.institute_fullname = this.institutes;
    this.passportParams.taxonomy_taxon_name = this.taxon;
    this.passportParams.samp_stat = this.filterBiologicalStatusByName(
      this.biologicalStatus,
      'name'
    );
    this.sendPassportParameters(this.passportParams);
    this.api.getAccessions(this.passportParams).subscribe(
      (data) => {
        if (data.length === 0) {
          this.notifyService.showWarning(
            "The system didn't find data with the entered parameters",
            'Warning'
          );
        } else {
          this.accessions$ = data.accessions;
          this.setAccession(data.accessions);
          // this.setDataIndicator(data);
          this.setSummary(this.accessions$);
          this.setRangeValues(data.min_max)
          this.setTabIndex(0);
        }
      },
      (error) => console.log(error)
    );
  };

  downloadFile(data: any) {
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
    saveAs(blob, 'myFile.csv');
  }

  getAccessionsAutomatically = (prop: any, ind:any) => {
    this.api.getAccessions(prop).subscribe(
      (data) => {
        if (data.length === 0) {
          this.notifyService.showWarning(
            "The system didn't find data with the entered parameters",
            'Warning'
          );
        } else {
          /* Props */
          this.countries = prop.country_name;
          console.log(this.filterCrops(prop.crop, 'id'))
          this.crops = this.filterCrops(prop.crop, 'id');
          this.taxon = prop.taxonomy_taxon_name;
          this.institutes = prop.institute_fullname;
          this.biologicalStatus = this.filterBiologicalStatusByName(
            prop.samp_stat,
            'id'
          );
          /* End props */
          this.accessions$ = data.accessions;
          this.setAccession(data.accessions);
          this.setSummary(this.accessions$);
          this.setRangeValues(data.min_max)
          if (ind) {
            let lstIndicators: any = [];
            ind.data.forEach((element:any) => {
              lstIndicators.push(element.name)
            });
            this.setIndicatorsList(lstIndicators);
            this.getSubsetsOfAccessionAutomatically(ind);
          }
        }
      },
      (error) => console.log(error)
    );
  };

  getSubsetsOfAccessionAutomatically = (prop: any) => {
    console.log(prop);
    this.sendIndicatorsParameters(prop);
    this.setTabIndex(1);
  };

  sendIndicatorsParameters(params: any) {
    this.sharedService.sendIndicators(params);
  }

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
    this.setAccession(this.accessions$);
  }

  filterBiologicalStatusByName(lst: any[], filterBy: string) {
    let bioStatusFiltered: any = [];
    if (filterBy === 'name') {
      lst.forEach((element: any) => {
        let filtered = this.mcpd.filter((prop: any) => prop.name == element);
        filtered.forEach((res: any) => {
          bioStatusFiltered.push(res.id);
        });
      });
    } else {
      lst.forEach((element: any) => {
        let filtered = this.mcpd.filter((prop: any) => prop.id == element);
        filtered.forEach((res: any) => {
          bioStatusFiltered.push(res.name);
        });
      });
    }

    return bioStatusFiltered;
  }

  filterCrops(crops: string[], filterBy: string): string[] {
    console.log(this.allCropsArray)
    console.log(crops)
    let cropSelected: string[] = [];
    if (filterBy === 'name') {
      crops.forEach((value: any) => {
        let cropsFind = this.allCropsArray.filter(
          (prop: any) => prop.name == value
        );
        cropsFind.forEach((element: any) => {
          if (!cropSelected.includes(element.id)) cropSelected.push(element.id);
        });
      });
    } else {
      crops.forEach((value: any) => {
        let cropsFind = this.allCropsArray.filter(
          (prop: any) => prop.id == value
        );
        cropsFind.forEach((element: any) => {
          if (!cropSelected.includes(element.name))
            cropSelected.push(element.name);
        });
      });
    }
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
    let cropSplit = event.option.viewValue.split(' - ')
    addList.push(cropSplit[0]);
    this.fruitInput.nativeElement.value = '';
    this.CropsCtrl.setValue(null);
    this.fruitInput.nativeElement.blur();
  }

  selectedCountry(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.countryInput.nativeElement.value = '';
    ctrl.setValue(null);
    this.countryInput.nativeElement.blur();
  }

  selectedTaxon(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.taxonInput.nativeElement.value = '';
    ctrl.setValue(null);
    this.taxonInput.nativeElement.blur();
  }

  selectedInstitute(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.instituteInput.nativeElement.value = '';
    ctrl.setValue(null);
    this.instituteInput.nativeElement.blur();
  }

  selectedBiologicalStatus(
    event: MatAutocompleteSelectedEvent,
    addList: any,
    ctrl: any
  ): void {
    addList.push(event.option.viewValue);
    this.bioStatusInput.nativeElement.value = '';
    ctrl.setValue(null);
    this.bioStatusInput.nativeElement.blur();
  }

  private _filter(value: string, allitems: any): string[] {
    const filterValue = value.toLowerCase();
    return allitems.filter((item: any) =>
      item.toLowerCase().includes(filterValue)
    );
  }
}
