import { Component, OnInit, Input } from '@angular/core';
import { SharedService } from '../../core/service/shared.service';
import { MatDialog, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { AccessionsDetailComponent } from '../../filter/accessions-detail/accessions-detail.component';
import { IndicatorService } from '../../indicator/service/indicator.service';

@Component({
  selector: 'app-tabs',
  templateUrl: './tabs.component.html',
  styleUrls: ['./tabs.component.scss']
})

export class TabsComponent implements OnInit {
  accessions$: any = [];
  headers:any = [];
  ActualPage: number = 1;
  /* Get accessions by page */
  properties!: any[];
  amountData:number;
  @Input() params:any;
  @Input() crops:any;
  @Input() next:any;
  @Input() previous:any;
  /* End get accessions by page */
  constructor(private sharedService: SharedService, public dialog: MatDialog, private api: IndicatorService) {
    this.headers = [
      "Number","Crop name", "Taxon","Action"
    ]
    this.amountData = 0;
   }

   openAccessionDetail(object:any) {
    const dialogRef = this.dialog.open(AccessionsDetailComponent, {
      data: {
        accession: object
      },
      width: '60%'
    });
    /* dialogRef.afterClosed().subscribe(
      data => {
        if (data) {
          this.params.longitude = data.longitude;
          this.params.latitude = data.latitude;
          this.longitudeAndLatitudeVisible = false
        }
      }
    ); */
  }

  /* Get new data accessions */
  setProperties(url: string) {
    let prop = { crop: [{"names": this.crops}], passport: [this.params] };
    console.log(prop);
    this.api.getAccessionsv1(url, prop).subscribe(response => {
      this.properties = response.results;
      this.drawTable(this.properties);
      this.setDataIndicator(this.properties);
      if (response.next) {
        // set the components next property here from the response
        this.next = response.next;
      }
      if (response.previous) {
        // set the components previous property here from the response
        this.previous = response.previous;
      }
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


    // function fetches the next paginated items by using the url in the next property
    fetchNext() {
      let nextSplit = this.next.split("/")
      console.log(nextSplit[4] + "/" + nextSplit[5])
      this.setProperties(nextSplit[4] + "/" + nextSplit[5]);
    }
  
    // function fetches the previous paginated items by using the url in the previous property
    fetchPrevious() {
      let prevSplit = this.previous.split("/")
      console.log(prevSplit[4] + "/" + prevSplit[5])
      this.setProperties(prevSplit[4] + "/" + prevSplit[5]);
    }
  /* End get new data accessions */

  ngOnInit(): void {
    this.sharedService.sendSubsetObservable.subscribe(data => {
      this.accessions$ = data
      this.amountData = this.accessions$.length
    })
  }

}
