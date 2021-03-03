import { Component, OnInit, Input, OnChanges } from '@angular/core';
import { IndicatorService } from './service/indicator.service';
import { Options } from '@angular-slider/ngx-slider';
import { Observable } from 'rxjs';
import { SharedService } from '../core/service/shared.service';

//chips
import { COMMA, ENTER } from '@angular/cdk/keycodes';
import { MatChipInputEvent } from '@angular/material/chips';

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
    console.log(this.subsets$);

    this.subsets$.forEach((value: any) => {
      let accesionsfind = this.accessions$.filter((acces: any) => acces.cellid == value.cellid)
      for (let vat of accesionsfind) {
        this.accessionsFiltered$.push(vat)
      }
    });
    this.accessions$ = this.accessionsFiltered$
    this.drawTable(this.accessions$)
    console.log(this.accessions$);
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

}
