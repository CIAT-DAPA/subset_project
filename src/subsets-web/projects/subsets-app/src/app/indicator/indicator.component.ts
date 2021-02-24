import { Component, OnInit } from '@angular/core';
import { IndicatorService } from './service/indicator.service';

@Component({
  selector: 'app-indicator',
  templateUrl: './indicator.component.html',
  styleUrls: ['./indicator.component.scss']
})
export class IndicatorComponent implements OnInit {

  parameters: any = {}
  subsets = []
  constructor(private api: IndicatorService) {
    this.parameters = {
      month: "",
      value: "",
      operation: ""
    }
  }

  ngOnInit(): void {
  }

  getSubsetsOfAccession = () => {
    console.log(this.parameters);
    
    this.api.getSubsetsOfAccession(this.parameters).subscribe(
      (data) => {
        this.subsets = data
        console.log(data);
        
      },
      (error) => (console.log(error)
      )
    )
  }

}
