import { Component, OnInit, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { IndicatorService } from '../../../indicator/service/indicator.service';
import { ThemePalette } from '@angular/material/core';
import { SharedService } from '../../../core/service/shared.service';
import { Options } from '@angular-slider/ngx-slider';

import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { FormControl } from '@angular/forms';
import { MatAutocompleteSelectedEvent, MatAutocomplete } from '@angular/material/autocomplete';
import { MatChipInputEvent } from '@angular/material/chips';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

export interface Month {
  id: number;
  name: string;
  completed: boolean;
  color: ThemePalette;
  subtasks?: Month[];
}

@Component({
  selector: 'app-form-indicator',
  templateUrl: './form-indicator.component.html',
  styleUrls: ['./form-indicator.component.scss']
})
export class FormIndicatorComponent implements OnInit {
  //chips-autocomplete start
  visible: boolean = true;
  selectable: boolean = true;
  removable: boolean = true;
  addOnBlur: boolean = false;

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
  @ViewChild('fruitInput') fruitInput!: ElementRef<HTMLInputElement>;
  @ViewChild('auto') matAutocomplete!: MatAutocomplete;
  //chips-autocomplete finish
  subsets$: any = []
  accessionsFiltered$: any = []
  accessions$: any = []
  indicators: any = []
  parameters: any = {}
  months: Month = {
    id: 0,
    name: 'All',
    completed: false,
    color: 'primary',
    subtasks: [
      { id: 1, name: 'January', completed: false, color: 'primary' },
      { id: 2, name: 'Febrary', completed: false, color: 'primary' },
      { id: 3, name: 'March', completed: false, color: 'primary' },
      { id: 4, name: 'April', completed: false, color: 'primary' },
      { id: 5, name: 'May', completed: false, color: 'primary' },
      { id: 6, name: 'June', completed: false, color: 'primary' },
      { id: 7, name: 'July', completed: false, color: 'primary' },
      { id: 8, name: 'August', completed: false, color: 'primary' },
      { id: 9, name: 'September', completed: false, color: 'primary' },
      { id: 10, name: 'October', completed: false, color: 'primary' },
      { id: 11, name: 'November', completed: false, color: 'primary' },
      { id: 12, name: 'December', completed: false, color: 'primary' },
    ]
  };

  minValue: number = 0;
  maxValue: number = 10;
  options: Options = {
    floor: 0,
    ceil: 300,
    showTicksValues: true,
    tickStep: 0.5,
    tickValueStep: 30
  };
  periods: any = []
  allComplete: boolean = false;

  constructor(private api: IndicatorService, private sharedService: SharedService) {

    this.filteredFruits = this.fruitCtrl.valueChanges.pipe(
      startWith(null),
      map((fruit: string | null) => fruit ? this._filter(fruit) : this.allFruits.slice()));

    this.parameters = {
      month: "",
      value: "",
      indicator: "",
      period: "",
    }
  }

  ngOnInit(): void {
    this.sharedService.sendSubsetObservable.subscribe(data => {
      this.accessions$ = data
    })
    this.getIndicators()
  }

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets)
  }

  setDataIndicator(acce: any) {
    this.sharedService.sendAccession(acce)
  }

  seIndicatorValue(indVal: any) {
    this.sharedService.sendIndicatorValue(indVal)
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data) => {
        this.indicators = data
        this.indicators.forEach((element:any) => {
          this.allFruits.push(element.name)
        });
      },
      (error) => (console.log(error)
      )
    )
  }

  getSubsetsOfAccession = () => {
    this.parameters.month = this.getAllSelected()
    this.parameters.indicator = this.fruits
    this.api.getSubsetsOfAccession(this.parameters).subscribe(
      (data) => {
        console.log(data.data[0]);
        this.seIndicatorValue(data.data[1])
        this.subsets$ = data.data[0]
        this.filterAccessionsByIndicator()
      },
      (error) => {
        console.log(error)
      }
    )
  }

  updateAllComplete() {
    this.allComplete = this.months.subtasks != null && this.months.subtasks.every(t => t.completed);
  }

  someComplete(): boolean {
    if (this.months.subtasks == null) {
      return false;
    }
    return this.months.subtasks.filter(t => t.completed).length > 0 && !this.allComplete;
  }

  setAll(completed: boolean) {
    this.allComplete = completed;
    if (this.months.subtasks == null) {
      return;
    }
    this.months.subtasks.forEach(t => t.completed = completed);
  }

  getAllSelected(): any {
    if (this.months.subtasks != null) {
      let lst: Month[] = []
      let lst_final: any = []
      lst = this.months.subtasks.filter((value: any) => value.completed == true)
      lst.forEach(element => {
        lst_final.push(element.id)
      });
      return lst_final

    }

  }

  filterAccessionsByIndicator() {
    this.subsets$.forEach((value: any) => {
      let accesionsfind = this.accessions$.filter((acces: any) => acces.cellid == value.cellid)
      for (let vat of accesionsfind) {
        this.accessionsFiltered$.push(vat)
      }
    });
    this.accessions$ = this.accessionsFiltered$
    this.drawTable(this.accessions$)
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
  }

  remove(fruit: string): void {
    const index = this.fruits.indexOf(fruit);

    if (index >= 0) {
      this.fruits.splice(index, 1);
    }
  }

  selected(event: MatAutocompleteSelectedEvent): void {
    this.fruits.push(event.option.viewValue);
    this.fruitInput.nativeElement.value = '';
    this.fruitCtrl.setValue(null);
  }

  private _filter(value: string): string[] {
    const filterValue = value.toLowerCase();

    return this.allFruits.filter(fruit => fruit.toLowerCase().indexOf(filterValue) === 0);
  }

}
