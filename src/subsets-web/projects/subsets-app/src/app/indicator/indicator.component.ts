import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { IndicatorService } from './service/indicator.service';
import { Options } from '@angular-slider/ngx-slider';
import { Observable } from 'rxjs';
import { SharedService } from '../core/service/shared.service';
import { ThemePalette } from '@angular/material/core';

//chips
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';

export interface Month {
  id: number;
  name: string;
  completed: boolean;
  color: ThemePalette;
  subtasks?: Month[];
}

@Component({
  selector: 'app-indicator',
  templateUrl: './indicator.component.html',
  styleUrls: ['./indicator.component.scss']
})
export class IndicatorComponent implements OnInit {
  parameters: any = {}
  params: any = {}
  subsets$ = []
  accessions$ = []
  crops$: any = []
  accessionsFiltered$: any = []
  indicators: any = []

  //chips
  visible = true;
  selectable = true;
  removable = true;
  addOnBlur = true;
  readonly separatorKeysCodes: number[] = [ENTER, COMMA];
  countries: any = [
    { name: 'Slovakia' },
    { name: 'Ghana' },
  ];

  //checkbox month

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

  allComplete: boolean = false;

  //end checkbox month


  mcpd = [
    { id: 100, name: 'wild' },
    { id: 110, name: 'natural' },
    { id: 120, name: 'semi-natural/wild' },
    { id: 130, name: 'semi-natural/sown' },
    { id: 200, name: 'weedy' },
    { id: 300, name: 'landrace' },
    { id: 400, name: 'breeding' },
  ]

  minValue: number = 0;
  maxValue: number = 10;
  options: Options = {
    floor: 0,
    ceil: 300,
    showTicksValues: true,
    tickStep: 0.5,
    tickValueStep: 30
  };

  constructor(private api: IndicatorService, private sharedService: SharedService) {
    this.parameters = {
      month: "",
      value: "",
      indicator: "",
      period: "",
    }
    this.params = {
      crop_name: "", name: "", country_name: "",
      samp_stat: "", institute_fullname: "", institute_acronym: ""
    }
  }

  ngOnInit(): void {
    this.sharedService.sendSubsetObservable.subscribe(data => {
      this.accessions$ = data
    })
    this.getIndicators()
    this.getCrops()
  }

  drawTable(subsets: any) {
    this.sharedService.sendSubsets(subsets)
  }

  getSubsetsOfAccession = () => {
    this.parameters.month = this.getAllSelected()
    this.api.getSubsetsOfAccession(this.parameters).subscribe(
      (data) => {
        this.subsets$ = data
        this.filterAccessionsByIndicator()
      },
      (error) => {
        console.log(error)
      }
    )
  }

  getAccessions = () => {
    this.api.getAccessions(this.params).subscribe(
      (data) => {
        this.accessions$ = data
        console.log(data);
        this.drawTable(data)

      },
      (error) => (console.log(error)
      )
    )
  }

  getIndicators = () => {
    this.api.getIndicators().subscribe(
      (data) => {
        this.indicators = data
        //console.log(data);
      },
      (error) => (console.log(error)
      )
    )
  }

  getCrops = () => {
    this.api.getCrops().subscribe(
      (data) => {
        this.crops$ = data
        //console.log(data);
      },
      (error) => (console.log(error)
      )
    )
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

  //Chips

  add(event: MatChipInputEvent): void {
    const input = event.input;
    const value = event.value;
    // Add our fruit
    if ((value || '').trim()) {
      this.countries.push({ name: value.trim() });
    }
    // Reset the input value
    if (input) {
      input.value = '';
    }
    console.log(this.countries);

  }

  remove(fruit: any): void {
    const index = this.countries.indexOf(fruit);

    if (index >= 0) {
      this.countries.splice(index, 1);
    }
  }

  //end chips

  //checkbox filter

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

  getAllSelected():any {
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

}
