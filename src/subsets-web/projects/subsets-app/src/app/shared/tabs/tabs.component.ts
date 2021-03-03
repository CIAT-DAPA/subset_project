import { Component, OnInit, Input } from '@angular/core';
import { SharedService } from '../../core/service/shared.service';

@Component({
  selector: 'app-tabs',
  templateUrl: './tabs.component.html',
  styleUrls: ['./tabs.component.scss']
})
export class TabsComponent implements OnInit {
  accessions$: any = []
  headers:any = []
  ActualPage: number = 1
  constructor(private sharedService: SharedService) {
    this.headers = [
      "ID", "Number","Name", "Crop name", "Country", "DOI", "Institute", "SampStat"
    ]
   }

  ngOnInit(): void {
    this.sharedService.sendSubsetObservable.subscribe(data => {
      this.accessions$ = data
    })
  }

}
